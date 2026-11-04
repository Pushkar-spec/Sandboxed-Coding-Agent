from dataclasses import dataclass

from codeagent.domain.model import Complexity, SandboxConfig, TaskSpec


@dataclass(frozen=True)
class Profile:
    max_attempts: int
    timeout_s: int
    memory_limit_mb: int
    cpu_limit: float

"""
frozen=True simply means:Once you create a profile, you cannot change its values.
"""

PROFILES: dict[Complexity, Profile] = {
    Complexity.SIMPLE: Profile(
        max_attempts=3,
        timeout_s=15,
        memory_limit_mb=256,
        cpu_limit=0.5,
    ),
    Complexity.STANDARD: Profile(
        max_attempts=4,
        timeout_s=60,
        memory_limit_mb=512,
        cpu_limit=1.0,
    ),
    Complexity.COMPLEX: Profile(
        max_attempts=6,
        timeout_s=180,
        memory_limit_mb=1024,
        cpu_limit=2.0,
    ),
}

def default_spec(task: str) -> TaskSpec: # for fallback -> if analyzer fails.
    """Return a standard fallback specification when task analysis is unavailable."""

    profile = PROFILES[Complexity.STANDARD]

    return TaskSpec(
        task=task,
        complexity=Complexity.STANDARD,
        max_attempts=profile.max_attempts,
        sandbox=SandboxConfig(
            timeout_s=profile.timeout_s,
            memory_limit_mb=profile.memory_limit_mb,
            cpu_limit=profile.cpu_limit,
            network_enabled=True,
        ),
    )