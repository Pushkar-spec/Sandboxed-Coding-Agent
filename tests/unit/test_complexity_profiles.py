from codeagent.domain.model import (
    ComplexityProfile,
    DEFAULT_RESOURCE_CONFIGS,
)


def test_all_complexity_profiles_have_configurations() -> None:
    assert len(DEFAULT_RESOURCE_CONFIGS) == 3

    assert ComplexityProfile.LOW in DEFAULT_RESOURCE_CONFIGS
    assert ComplexityProfile.MEDIUM in DEFAULT_RESOURCE_CONFIGS
    assert ComplexityProfile.HIGH in DEFAULT_RESOURCE_CONFIGS


def test_low_complexity_resources() -> None:
    config = DEFAULT_RESOURCE_CONFIGS[ComplexityProfile.LOW]

    assert config.timeout_s == 30
    assert config.memory_limit_mb == 256
    assert config.cpu_limit == 0.5


def test_medium_complexity_resources() -> None:
    config = DEFAULT_RESOURCE_CONFIGS[ComplexityProfile.MEDIUM]

    assert config.timeout_s == 60
    assert config.memory_limit_mb == 512
    assert config.cpu_limit == 1.0


def test_high_complexity_resources() -> None:
    config = DEFAULT_RESOURCE_CONFIGS[ComplexityProfile.HIGH]

    assert config.timeout_s == 120
    assert config.memory_limit_mb == 1024
    assert config.cpu_limit == 2.0