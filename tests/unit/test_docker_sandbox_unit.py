
from pathlib import Path
from unittest.mock import MagicMock, patch

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
