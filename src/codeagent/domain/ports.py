# defines the interface that any sandbox implementation must follow.

from pathlib import Path
from typing import Protocol

from codeagent.domain.model import SandboxConfig, SandboxResult


class Sandbox(Protocol):
    """Contract for executing code in an isolated environment."""

    def run(self, code: str, workdir: Path, config: SandboxConfig) -> SandboxResult:
        #  self refers to the object implementing the method.

        ...
        # ... -> Ellipsis, Here, they indicate that the method body is intentionally omitted.
        # The protocol describes the required method but doesn't implement its behavior.
