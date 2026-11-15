# Security and Threat Model

## 1. Security objective

The system executes LLM-generated and user-influenced code. Treat all task content, generated code, package metadata, workspace files, and model outputs as untrusted. The goal is defense in depth and explicit risk reduction—not an unsupported claim that Docker alone makes arbitrary code safe.

## 2. Assets to protect

- Host machine and Docker daemon.
- API keys and environment variables.
- User files outside the per-run workspace.
- Other runs and tenants.
- Network and internal services.
- CPU, memory, disk, process table and provider budget.
- Source code and benchmark data sent to external observability services.

## 3. Threats and controls

| Threat | Required controls |
|---|---|
| Host filesystem access | Narrow per-run bind mount; path canonicalization; reject symlink/path traversal; never mount home/root or Docker socket |
| Network exfiltration/SSRF | Network disabled by default; explicit allowlist/proxy policy; block metadata/internal networks; separate dependency-fetch phase from execution |
| Container escape | Non-root user, dropped capabilities, seccomp/AppArmor/SELinux where available, no privileged mode, patched runtime; consider stronger isolation (gVisor/Firecracker) for hostile multi-tenant deployment |
| Resource exhaustion | CPU/memory/PID/time limits plus disk, output, artifact, workspace and concurrency quotas |
| Secret theft | Never pass host secrets into container; scoped ephemeral credentials only when required; secret scanning and redaction |
| Dependency supply-chain attack | Pin/lock dependencies, allowlist registries, hashes where practical, package policy, isolated build/download step |
| Prompt injection | Treat files and task content as data; enforce tool and sandbox policy outside the LLM |
| Cross-run leakage | Fresh container and workspace per attempt; cleanup and access control |
| Log/trace leakage | Redact secrets; minimize payloads; opt-in external tracing; retention and access controls |
| Malicious artifacts | Validate paths/types/sizes; do not automatically open or execute returned artifacts |

## 4. Findings from the uploaded implementation snapshot

These are code-review observations, not a penetration-test result:

1. `DockerSandbox` bind-mounts the resolved host workspace read-write. A production implementation needs stronger workspace ownership, path and symlink validation, and quotas.
2. `network_mode` becomes `bridge` when either `network_enabled` **or** `packages` is non-empty. This couples package installation to execution network access. Separate dependency installation from the untrusted execution phase.
3. `default_spec()` currently enables network access. Revisit the default to least privilege.
4. Artifact discovery recursively scans the host workspace and records file sizes, but does not yet enforce artifact count/size/total workspace quotas or robust symlink-race handling.
5. The Docker container is configured with several good hardening options (read-only root filesystem, dropped capabilities, no-new-privileges, PID/memory/CPU limits and tmpfs), but this is not equivalent to a hardened VM boundary.
6. The project archive contained a `.env` file. This documentation copy deliberately excludes it. Verify whether it contained a real credential; if exposed, rotate it. Never share future archives containing `.env`.

## 5. Required sandbox hardening before production claims

- Run as a non-root UID/GID.
- Use a dedicated workspace per run/attempt with strict canonical path checks.
- Ensure no Docker socket, host devices, host PID/IPC namespaces, or privileged mode.
- Configure seccomp and AppArmor/SELinux where supported.
- Separate dependency installation from execution; prefer prebuilt pinned images or a controlled package cache.
- Keep network disabled for execution unless task policy explicitly permits narrowly scoped access.
- Block cloud metadata endpoints and internal/private address ranges if network is allowed.
- Add disk, inode, output, artifact count/size, workspace and concurrency quotas.
- Ensure cancellation and timeout always kill the process/container and remove resources.
- Add adversarial integration tests and periodic security review.
- For public multi-tenant hostile-code execution, evaluate stronger isolation technologies and a dedicated execution host.

## 6. Security test categories

- Attempt to read host files and environment variables.
- Attempt network access, DNS, localhost, private IP and metadata endpoints.
- Attempt fork bombs, memory exhaustion, disk exhaustion and huge stdout/stderr.
- Attempt symlink/path traversal in artifact paths.
- Attempt background process persistence and cleanup bypass.
- Attempt access to Docker socket and Linux capabilities.
- Attempt malicious package install and import behavior.
- Attempt prompt injection through task text and files.
- Verify secrets are absent from prompts, logs, traces and artifacts.

A passing unit test suite is not a security certification.

## Local model and telemetry considerations

Running inference through Ollama keeps model requests on the local machine by default, but it does not make the whole workflow automatically safe. Generated code remains untrusted and must execute only inside the configured sandbox. Do not expose the Ollama API beyond trusted local interfaces unless authentication/network controls are deliberately added. Do not mount host secrets or pass credentials into model prompts or sandbox environments.

LangSmith or other hosted observability may transmit prompts, source code, generated code, traces, and tool outputs outside the machine. Treat tracing as a data-egress boundary: redact secrets, minimize captured payloads, review retention/access settings, and make tracing opt-in for sensitive runs. MLflow tracking location and artifact storage also require access control.

Model provenance matters: record the model tag and digest when available, source, quantization, and runtime version. Treat downloaded model artifacts and their metadata as dependencies to review; local execution is not a substitute for dependency and sandbox security.

