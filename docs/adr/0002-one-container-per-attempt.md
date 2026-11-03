
# ADR 0002: One Container per Attempt, Configured per Run

## Status

Accepted

## Context

The Coding Agent needs to execute user-submitted Python code in an isolated environment.

User-submitted code is untrusted and may:
- Consume excessive memory or CPU.
- Run indefinitely.
- Attempt to access the network.
- Create files or processes.
- Interfere with other execution attempts.

The sandbox must enforce resource limits and isolate each execution attempt.

## Decision

We will use one Docker container per execution attempt.

Each container will be configured using the SandboxConfig supplied to that execution.

The configuration includes:
- Execution timeout
- Memory limit
- CPU limit
- Network access
- Additional Python packages

After execution, the container will be removed, regardless of whether execution succeeds, fails, or times out.

## Alternatives Considered

### 1. Reusing a persistent container

A single container could be reused for multiple execution attempts.

Rejected because execution state, files, processes, and other side effects could leak between attempts.

### 2. One container per execution attempt

A new container is created for every execution and removed afterward.

Accepted because it provides better isolation and allows resource limits to be configured independently for every attempt.

## Consequences

### Positive

- Each execution gets an isolated container.
- Resource limits can differ between attempts.
- Execution state does not persist in the container between attempts.
- Containers are cleaned up after execution.
- Failures in one execution are less likely to affect another.

### Negative

- Creating containers introduces execution overhead.
- Docker image availability is required.
- Package installation can increase execution time.
- Container isolation alone is not a complete security boundary against every possible attack.

## Implementation

The decision is implemented by DockerSandbox.

The run() method:
1. Creates the execution workspace.
2. Writes submitted code to main.py.
3. Starts a Docker container with the supplied SandboxConfig.
4. Monitors execution and enforces timeout.
5. Collects stdout, stderr, exit code, duration, and artifacts.
6. Detects memory-limit termination.
7. Removes the container.

## Verification

The implementation is verified through unit and integration tests covering:
- Successful execution
- Runtime and syntax errors
- Timeout enforcement
- Memory and CPU limits
- Network isolation
- Additional package installation
- Artifact discovery
- Container cleanup
