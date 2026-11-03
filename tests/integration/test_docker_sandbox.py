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

# Test for file extraction from sandbox    

def test_artifact_reported_with_size(tmp_path: Path) -> None:
    sandbox = DockerSandbox()

    result = sandbox.run(
        code="with open('out.txt', 'w') as f: f.write('xyz')",
        workdir=tmp_path,
        config=SandboxConfig(),
    )

    assert result.exit_code == 0
    assert result.artifacts == {"out.txt": 3}

# Extra dependency installation

def test_sandbox_installs_extra_package(tmp_path: Path) -> None:
    sandbox = DockerSandbox()

    result = sandbox.run(
        code=(
            "import tabulate\n"
            "print(tabulate.tabulate([[1, 2], [3, 4]]))"
        ),
        workdir=tmp_path,
        config=SandboxConfig(
            packages=["tabulate"],
            timeout_s=120,
        ),
    )

    assert result.exit_code == 0
    assert "1" in result.stdout
    assert "3" in result.stdout

# Testing network in docker

def test_sandbox_blocks_network_access(tmp_path: Path) -> None:
    sandbox = DockerSandbox()

    result = sandbox.run(
        code=(
            "import urllib.request\n"
            "try:\n"
            "    urllib.request.urlopen('https://example.com', timeout=5)\n"
            "    print('NETWORK_ACCESS_ALLOWED')\n"
            "except Exception:\n"
            "    print('NETWORK_ACCESS_BLOCKED')\n"
        ),
        workdir=tmp_path,
        config=SandboxConfig(
            network_enabled=False,
            timeout_s=15,
        ),
    )

    assert result.exit_code == 0
    assert "NETWORK_ACCESS_BLOCKED" in result.stdout

def test_sandbox_allows_network_access(tmp_path: Path) -> None:
    sandbox = DockerSandbox()

    result = sandbox.run(
        code=(
            "import urllib.request\n"
            "response = urllib.request.urlopen("
            "'https://example.com', timeout=10)\n"
            "print(response.status)\n"
        ),
        workdir=tmp_path,
        config=SandboxConfig(
            network_enabled=True,
            timeout_s=20,
        ),
    )

    assert result.exit_code == 0
    assert "200" in result.stdout