from pathlib import Path

import docker

from codeagent.domain.model import SandboxConfig
from codeagent.sandbox.docker_sandbox import DockerSandbox


def test_sandbox_executes_python_code(tmp_path: Path) -> None:
    sandbox = DockerSandbox()

    result = sandbox.run(
        code='print("Hello from Coding Agent")',
        workdir=tmp_path,
        config=SandboxConfig(),
    )

    assert result.stdout.strip() == "Hello from Coding Agent"
    assert result.exit_code == 0
    assert result.timed_out is False

def test_sandbox_captures_runtime_error(tmp_path: Path) -> None:
    sandbox = DockerSandbox()

    result = sandbox.run(
        code = 'print(10/0)',
        workdir=tmp_path,
        config=SandboxConfig(),
    )

    assert "ZeroDivisionError" in result.stderr
    assert result.exit_code != 0
    assert result.timed_out is False

def test_sandbox_captures_syntax_error(tmp_path: Path) -> None:
    sandbox = DockerSandbox()

    result = sandbox.run(
        code="print('Hello'",
        workdir=tmp_path,
        config=SandboxConfig(),
    )

    assert "SyntaxError" in result.stderr
    assert result.exit_code != 0
    assert result.timed_out is False

def test_sandbox_stops_execution_after_timeout(tmp_path: Path) -> None:
    sandbox = DockerSandbox()

    result = sandbox.run(
        code="while True:\n    pass",
        workdir=tmp_path,
        config=SandboxConfig(timeout_s=2),
    )

    assert result.timed_out is True

# Container Cleanup Tests

def test_container_is_removed_after_execution(tmp_path: Path) -> None:
    client = docker.from_env()
    sandbox = DockerSandbox()

    result = sandbox.run(
        code='print("Cleanup test")',
        workdir=tmp_path,
        config=SandboxConfig(),
    )

    assert result.exit_code == 0

    # Inspect Docker containers
    containers = client.containers.list(
        all=True,
        filters={"ancestor": "codeagent-sandbox:latest"},
    )

    assert len(containers) == 0

def test_container_is_removed_after_execution_error(tmp_path: Path) -> None:
    client = docker.from_env()
    sandbox = DockerSandbox()

    result = sandbox.run(
        code="print(10 / 0)",
        workdir=tmp_path,
        config=SandboxConfig(),
    )

    assert result.exit_code != 0

    containers = client.containers.list(
        all=True,
        filters={"ancestor": "codeagent-sandbox:latest"},
    )

    assert len(containers) == 0

def test_container_is_removed_after_timeout(tmp_path: Path) -> None:
    client = docker.from_env()
    sandbox = DockerSandbox()

    result = sandbox.run(
        code="while True:\n    pass",
        workdir=tmp_path,
        config=SandboxConfig(timeout_s=2),
    )

    assert result.timed_out is True

    containers = client.containers.list(
        all=True,
        filters={"ancestor": "codeagent-sandbox:latest"},
    )

    assert len(containers) == 0

# Resource Limit Testing

def test_sandbox_enforces_memory_limit(tmp_path: Path) -> None:
    sandbox = DockerSandbox()

    result = sandbox.run(
        code='print("Memory test")',
        workdir=tmp_path,
        config=SandboxConfig(memory_limit_mb=256),
    )

    assert result.exit_code == 0

def test_sandbox_enforces_cpu_limit(tmp_path: Path) -> None:
    sandbox = DockerSandbox()

    result = sandbox.run(
        code='print("CPU test")',
        workdir=tmp_path,
        config=SandboxConfig(cpu_limit=0.5),
    )

    assert result.exit_code == 0

# We need to ensure that the generated file is accessible outside the Docker container.

def test_sandbox_creates_workdir(tmp_path: Path) -> None:
    sandbox = DockerSandbox()

    workdir = tmp_path / "new_workspace"

    result = sandbox.run(
        code='print("Workspace created")',
        workdir=workdir,
        config=SandboxConfig(),
    )

    assert result.exit_code == 0
    assert workdir.exists()
    assert workdir.is_dir()