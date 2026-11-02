# defines the data going into and coming out of a sandbox.


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
    artifacts: list[str] = Field(default_factory=list)
