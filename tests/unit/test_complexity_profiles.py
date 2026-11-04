from codeagent.domain.model import Complexity
from codeagent.domain.profiles import PROFILES, default_spec


def test_all_complexity_profiles_have_configurations() -> None:
    assert len(PROFILES) == 3

    assert Complexity.SIMPLE in PROFILES
    assert Complexity.STANDARD in PROFILES
    assert Complexity.COMPLEX in PROFILES


def test_simple_complexity_resources() -> None:
    config = PROFILES[Complexity.SIMPLE]

    assert config.timeout_s == 15
    assert config.memory_limit_mb == 256
    assert config.cpu_limit == 0.5


def test_standard_complexity_resources() -> None:
    config = PROFILES[Complexity.STANDARD]

    assert config.timeout_s == 60
    assert config.memory_limit_mb == 512
    assert config.cpu_limit == 1.0


def test_complex_complexity_resources() -> None:
    config = PROFILES[Complexity.COMPLEX]

    assert config.timeout_s == 180
    assert config.memory_limit_mb == 1024
    assert config.cpu_limit == 2.0

def test_default_spec_uses_standard_profile() -> None:
    spec = default_spec("Write a palindrome checker")

    assert spec.task == "Write a palindrome checker"
    assert spec.complexity == Complexity.STANDARD
    assert spec.max_attempts == 4

    assert spec.sandbox.timeout_s == 60
    assert spec.sandbox.memory_limit_mb == 512
    assert spec.sandbox.cpu_limit == 1.0
    assert spec.sandbox.network_enabled is True