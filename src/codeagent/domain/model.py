# defines the data going into and coming out of a sandbox.

from enum import StrEnum

from pydantic import BaseModel, Field


class SandboxConfig(BaseModel):
    """Resource and permission settings for one sandbox execution."""

    timeout_s: int = Field(default=30, gt=0)  # maximum permitted execution time in seconds
    memory_limit_mb: int = Field(default=512, gt=0)  # memory limit for the container in MB
    cpu_limit: float = Field(default=1.0, gt=0)
    network_enabled: bool = False  # Whether network access is requested for this execution.
    # Additional packages requested for the execution environment.
    packages: list[str] = Field(default_factory=list)



class SandboxResult(BaseModel):
    """Structured outcome of a sandbox execution."""

    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    duration_s: float = Field(default=0.0, ge=0)
    timed_out: bool = False
    artifacts: dict[str, int] = Field(default_factory=dict)
    oom_killed: bool = False

class ComplexityProfile(StrEnum): # for assigining a complexity profile
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

DEFAULT_RESOURCE_CONFIGS: dict[ComplexityProfile, SandboxConfig] = {
        ComplexityProfile.LOW: SandboxConfig(
            timeout_s=30,
            memory_limit_mb=256,
            cpu_limit=0.5,
        ),
        ComplexityProfile.MEDIUM: SandboxConfig(
            timeout_s=60,
            memory_limit_mb=512,
            cpu_limit=1.0,
        ),
        ComplexityProfile.HIGH: SandboxConfig(
            timeout_s=120,
            memory_limit_mb=1024,
            cpu_limit=2.0,
        ),
    }

class Message(BaseModel):
    role: str
    content: str

class LLMResponse(BaseModel):
    text: str
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)

# input_tokens and output_tokens: Help us track API usage and eventually estimate costs.