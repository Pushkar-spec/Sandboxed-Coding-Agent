
from pathlib import Path
from unittest.mock import MagicMock, patch

import docker
import pytest

from codeagent.domain.model import SandboxConfig
from codeagent.sandbox.docker_sandbox import DockerSandbox


@patch("codeagent.sandbox.docker_sandbox.docker.from_env")
def test_sandbox_passes_memory_limit_to_docker(mock_from_env: MagicMock, tmp_path: Path) -> None:
    mock_client = mock_from_env.return_value
    mock_container = MagicMock()

    # Simulate a container that finishes successfully.
    mock_client.containers.run.return_value = mock_container
    mock_container.status = "exited"
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = b"Memory test"

    sandbox = DockerSandbox()

    sandbox.run(
        code='print("Memory test")',
        workdir=tmp_path,
        config=SandboxConfig(memory_limit_mb=256),
    )

    docker_args = mock_client.containers.run.call_args.kwargs

    assert docker_args["mem_limit"] == "256m"


@patch("codeagent.sandbox.docker_sandbox.docker.from_env")
def test_sandbox_passes_cpu_limit_to_docker(mock_from_env: MagicMock, tmp_path: Path) -> None:
    mock_client = mock_from_env.return_value
    mock_container = MagicMock()

    mock_client.containers.run.return_value = mock_container
    mock_container.status = "exited"
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = b"CPU test"

    sandbox = DockerSandbox()

    sandbox.run(
        code='print("CPU test")',
        workdir=tmp_path,
        config=SandboxConfig(cpu_limit=0.5),
    )

    docker_args = mock_client.containers.run.call_args.kwargs

    assert docker_args["nano_cpus"] == 500_000_000

# Network isolation tests

@patch("codeagent.sandbox.docker_sandbox.docker.from_env")
def test_sandbox_disables_network_by_default(
    mock_from_env: MagicMock,
    tmp_path: Path,
) -> None:
    mock_client = mock_from_env.return_value
    mock_container = MagicMock()

    mock_client.containers.run.return_value = mock_container
    mock_container.status = "exited"
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = b"Network disabled"

    sandbox = DockerSandbox()

    sandbox.run(
        code='print("Network disabled")',
        workdir=tmp_path,
        config=SandboxConfig(),
    )

    docker_args = mock_client.containers.run.call_args.kwargs

    assert docker_args["network_mode"] == "none"


@patch("codeagent.sandbox.docker_sandbox.docker.from_env")
def test_sandbox_enables_network_when_configured(
    mock_from_env: MagicMock,
    tmp_path: Path,
) -> None:
    mock_client = mock_from_env.return_value
    mock_container = MagicMock()

    mock_client.containers.run.return_value = mock_container
    mock_container.status = "exited"
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = b"Network enabled"

    sandbox = DockerSandbox()

    sandbox.run(
        code='print("Network enabled")',
        workdir=tmp_path,
        config=SandboxConfig(network_enabled=True),
    )

    docker_args = mock_client.containers.run.call_args.kwargs

    assert docker_args["network_mode"] == "bridge"


# Output Handling Testing

@patch("codeagent.sandbox.docker_sandbox.docker.from_env")
def test_sandbox_captures_stdout_and_stderr(
    mock_from_env: MagicMock,
    tmp_path: Path,
) -> None:
    mock_client = mock_from_env.return_value
    mock_container = MagicMock()

    mock_client.containers.run.return_value = mock_container
    mock_container.status = "exited"
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.attrs = {
        "State": {
            "OOMKilled": False
        }
    }

    def mock_logs(stdout: bool, stderr: bool) -> bytes:
        if stdout:
            return b"Hello from stdout"
        if stderr:
            return b"Warning from stderr"
        return b""

    mock_container.logs.side_effect = mock_logs

    sandbox = DockerSandbox()

    result = sandbox.run(
        code="print('Hello from stdout')",
        workdir=tmp_path,
        config=SandboxConfig(),
    )

    assert result.stdout == "Hello from stdout"
    assert result.stderr == "Warning from stderr"

@patch("codeagent.sandbox.docker_sandbox.docker.from_env")
def test_sandbox_truncates_large_output(
    mock_from_env: MagicMock,
    tmp_path: Path,
) -> None:
    mock_client = mock_from_env.return_value
    mock_container = MagicMock()

    mock_client.containers.run.return_value = mock_container
    mock_container.status = "exited"
    mock_container.wait.return_value = {"StatusCode": 0}

    large_output = b"A" * 150_000
    mock_container.logs.side_effect = [
        large_output,
        b"",
    ]

    sandbox = DockerSandbox()

    result = sandbox.run(
        code="print('A' * 150000)",
        workdir=tmp_path,
        config=SandboxConfig(),
    )
    assert len(result.stdout) == 100_000

@patch("codeagent.sandbox.docker_sandbox.docker.from_env")
def test_sandbox_returns_correct_exit_code(
    mock_from_env: MagicMock,
    tmp_path: Path,
) -> None:
    mock_client = mock_from_env.return_value
    mock_container = MagicMock()

    mock_client.containers.run.return_value = mock_container
    mock_container.status = "exited"
    mock_container.wait.return_value = {"StatusCode": 1}
    mock_container.logs.return_value = b""

    sandbox = DockerSandbox()

    result = sandbox.run(
        code="raise RuntimeError('Test failure')",
        workdir=tmp_path,
        config=SandboxConfig(),
    )

    assert result.exit_code == 1

# Docker Failure Handling

@patch("codeagent.sandbox.docker_sandbox.docker.from_env")
def test_sandbox_handles_missing_image(
    mock_from_env: MagicMock,
    tmp_path: Path,
) -> None:
    mock_client = mock_from_env.return_value
    mock_client.containers.run.side_effect = docker.errors.ImageNotFound(
        "Image not found"
    )

    sandbox = DockerSandbox(image="nonexistent-image:latest")

    result = sandbox.run(
        code='print("Hello")',
        workdir=tmp_path,
        config=SandboxConfig(),
    )

    assert result.exit_code == 1
    assert "Docker image not found" in result.stderr

@patch("codeagent.sandbox.docker_sandbox.docker.from_env")
def test_sandbox_handles_docker_unavailable(
    mock_from_env: MagicMock,
    tmp_path: Path,
) -> None:
    mock_from_env.side_effect = docker.errors.DockerException(
        "Docker Engine unavailable"
    )

    with pytest.raises(docker.errors.DockerException):
        DockerSandbox()
