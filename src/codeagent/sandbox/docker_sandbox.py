# docker_sandbox.py will contain the concrete implementation of our Sandbox port.

import contextlib
import time
from pathlib import Path

import docker
from docker.errors import DockerException, ImageNotFound
from docker.models.containers import Container

from codeagent.domain.model import SandboxConfig, SandboxResult


class DockerSandbox:  # it is the adapter for the port we created in port.py
    """Execute Python code inside a Docker container."""

    def __init__(self, image: str = "codeagent-sandbox:latest") -> None:
        self.image = image
        self.client = docker.from_env()
        # Think of self.client as the Python application's connection to Docker.
        #  Through it, we can create containers, retrieve their logs, stop them, and remove them.

    def _discover_artifacts(self, workdir: Path, code_file: Path) -> dict[str, int]:
        """Discover files generated during sandbox execution."""
        artifacts: dict[str, int] = {}

        for path in workdir.rglob("*"):
            if path.is_file() and not path.is_symlink() and path != code_file:
                relative_path = path.relative_to(workdir).as_posix()
                artifacts[relative_path] = path.stat().st_size

        return artifacts
    
    def run(
        self,
        code: str,
        workdir: Path,
        config: SandboxConfig,
    ) -> SandboxResult:
        workdir = workdir.resolve()
        workdir.mkdir(parents=True, exist_ok=True)

        code_file = workdir / "main.py"
        code_file.write_text(code, encoding="utf-8")

        container: Container | None = None  # It means the variable can hold 
        # either a Docker Container object or None.
        start_time = time.monotonic()

        try:
            container = self.client.containers.run(
                image=self.image,

                command=[
                    "python",
                    "-c",
                    (
                        "import os, runpy, subprocess, sys; "
                        "packages = sys.argv[1:]; "
                        "target = '/tmp/python-packages'; "
                        "os.makedirs(target, exist_ok=True); "
                        "subprocess.run("
                        "[sys.executable, '-m', 'pip', 'install', "
                        "'--disable-pip-version-check', '--no-cache-dir', "
                        "'--target', target, *packages], "
                        "check=True"
                        ") if packages else None; "
                        "sys.path.insert(0, target); "
                        "runpy.run_path('/workspace/main.py', run_name='__main__')"
                    ),
                    *config.packages,
                ],

                working_dir="/workspace",
                volumes={
                    str(workdir): {
                        "bind": "/workspace",
                        "mode": "rw",
                    }
                },
                detach=True,
                network_mode=(
                    "bridge" if config.network_enabled or config.packages else "none"
                ),
                # We added config.packages because it tells Docker which additional Python libraries
                #  the user wants installed before their code executes.
                mem_limit=f"{config.memory_limit_mb}m",
                nano_cpus=int(config.cpu_limit * 1_000_000_000),
                pids_limit=64,
                read_only=True,
                tmpfs={"/tmp": "rw,noexec,nosuid,size=64m"},
                security_opt=["no-new-privileges:true"],
                cap_drop=["ALL"],
            )

            try:
                deadline = time.monotonic() + config.timeout_s

                while True :
                    container.reload()

                    if container.status == 'exited':
                        break
                    if time.monotonic() >= deadline:
                        container.kill()
                        container.wait()

                        return SandboxResult(
                            stderr=f"Execution timed out after {config.timeout_s} seconds.",
                            duration_s=time.monotonic() - start_time,
                            timed_out=True,
                        )
                    time.sleep(0.1)

                result = container.wait()

                container.reload()
                oom_killed = container.attrs.get("State", {}).get("OOMKilled", False)

            except DockerException as exc:
                return SandboxResult(
                    stderr=f"Docker execution failed: {exc}",
                    duration_s=time.monotonic() - start_time,
                    exit_code=1,
                )
            
            logs = container.logs(stdout=True, stderr=False).decode(
                "utf-8", errors="replace"
            )
            error_logs = container.logs(stdout=False, stderr=True).decode(
                "utf-8", errors="replace"
            )

            exit_code = result.get("StatusCode", 1)
            if oom_killed:
                error_logs += "\nContainer terminated due to memory limit (OOM)."

            return SandboxResult(
                stdout=logs[:100_000],
                stderr=error_logs[:100_000],
                exit_code=exit_code,
                duration_s=time.monotonic() - start_time,
                artifacts=self._discover_artifacts(workdir, code_file),
            )

        except ImageNotFound:
            return SandboxResult(
                stderr=f"Docker image not found: {self.image}",
                duration_s=time.monotonic() - start_time,
                exit_code=1,
            )
        except DockerException as exc:
            return SandboxResult(
                stderr=f"Docker execution failed: {exc}",
                duration_s=time.monotonic() - start_time,
                exit_code=1,
            )
        finally:
            if container is not None:
                with contextlib.suppress(DockerException):
                    container.remove(force=True)
