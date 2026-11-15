# AGENTS.md — Sandboxed Coding Agent

This repository is the **Sandboxed Coding Agent** project. Treat the checked-in source code as the implementation source of truth and the documentation as the intended design and delivery contract. If code and docs disagree, do not silently choose one: report the mismatch and propose the smallest safe reconciliation.

## Product goal

Build a reliable coding agent that accepts a programming task, plans an execution specification, generates code with an LLM, executes untrusted code in an isolated sandbox, evaluates the result, and uses bounded repair attempts when appropriate.

This is intended to become a production-minded, resume-ready engineering project. Two learning and delivery priorities are mandatory:

1. **System design:** explain component boundaries, data flow, state transitions, failure modes, alternatives, trade-offs, security and operational implications.
2. **LLM evaluation:** build a reproducible evaluation harness and use measured experiments to justify changes. Do not claim improvements without benchmark evidence.

## Repository facts at the documentation baseline

The uploaded source snapshot contains:
- Python 3.12 project managed with `uv`.
- Ports and Adapters interfaces for `LLM` and `Sandbox`.
- Pydantic domain models: `SandboxConfig`, `SandboxResult`, `Complexity`, `Message`, `LLMResponse`, `TaskSpec`.
- Complexity profiles and a standard fallback `TaskSpec`.
- `FakeLLM` and a Gemini adapter.
- Docker sandbox execution with per-attempt containers, configured CPU/memory/time limits, process limit, read-only root filesystem, dropped capabilities, `no-new-privileges`, temporary filesystem, output truncation, artifact discovery, timeout handling, OOM reporting and cleanup.
- Unit and Docker integration tests.
- Existing ADRs 0001 and 0002.

The snapshot does **not** yet contain a wired task analyzer, complete agent loop, evaluator pipeline, repair orchestration, CLI workflow, benchmark harness, or LangSmith/MLflow integrations. The package entry point currently prints a placeholder greeting. Re-check the repository before treating this inventory as current.

## Non-negotiable engineering rules

- Keep domain logic independent of provider SDKs, Docker SDK, storage, and observability vendors.
- Define ports at stable boundaries; avoid abstractions that add indirection without a real seam.
- Use typed Pydantic models or explicit dataclasses for cross-component contracts. Validate all LLM-generated structured data before using it.
- Treat model output, task descriptions, files in a workspace, package names, and generated code as untrusted input.
- Never execute generated code on the host.
- Do not claim Docker alone is a complete hostile-code security boundary. Document residual risks and deployment assumptions.
- Keep network access disabled by default. Package installation and execution networking must be separate, explicit policies; do not enable broad network access merely because packages were requested.
- Enforce hard ceilings on attempts, time, memory, CPU, process count, output size, artifact count/size, workspace size, and concurrency.
- Ensure cleanup occurs on success, failure, timeout, cancellation, and unexpected exceptions.
- Do not expose API keys, environment variables, host paths, or sensitive source code in logs/traces.
- Use deterministic tests for logic and objective correctness wherever possible. Use LLM-as-a-judge only as a calibrated supplemental evaluator.
- Every benchmark run must record dataset version, task IDs, model/provider/model version, prompt version/hash, parameters, code revision, environment, seed where applicable, metrics, and run timestamp.
- Keep LangSmith and MLflow optional. Core CLI evaluation must work without either service.
- Do not add RAG solely to claim RAG expertise. If retrieval is introduced, add a dedicated RAG evaluation suite and document why retrieval is needed.

## Required workflow for AI coding tools

Before editing:
1. Read `README.md`, `docs/PROJECT_OVERVIEW.md`, `docs/ARCHITECTURE.md`, `docs/SPECIFICATION.md`, `docs/SECURITY.md`, `docs/EVALUATION.md`, `docs/ROADMAP_AND_TASKS.md`, and relevant ADRs.
2. Inspect the current implementation and tests; do not assume docs describe code accurately.
3. State the intended change, affected components, contracts, risks, and tests.
4. For material design changes, propose an ADR before or alongside implementation.

During implementation:
- Work on one bounded roadmap task at a time.
- Preserve existing public contracts unless the task explicitly changes them.
- Add/update tests with the implementation.
- Keep changes small and reviewable.
- Do not add dependencies without explaining why, alternatives, maintenance cost, and whether the dependency is optional.
- Do not introduce LangGraph, a database, Redis, a web API, or a RAG subsystem merely because they appear in generic agent architectures. Add them only when a defined requirement justifies the complexity.

After implementation:
1. Run relevant tests, then the full local check suite where possible.
2. Report exact commands and actual results. Distinguish tests not run from passing tests.
3. Review security, failure paths, resource bounds, observability/privacy, and backward compatibility.
4. Update documentation, roadmap status, ADRs, and evaluation records.
5. Never invent benchmark results or mark a task complete without evidence.

## Evaluation discipline

- The benchmark dataset is versioned and has a frozen holdout split.
- Use paired comparisons on the same task IDs when comparing configurations.
- Change one principal variable per experiment unless explicitly running a factorial/multi-factor experiment.
- Report sample count, aggregate and per-category results, failures, latency, token usage, and cost where available.
- Report uncertainty (for example confidence intervals) when sample sizes support it; do not overstate small-sample results.
- Keep raw run artifacts and machine-readable results. A chart without underlying data is insufficient.
- Treat judge scores as noisy measurements; calibrate against human labels and monitor judge disagreement/bias.
- A performance improvement must not hide regressions in security, cost, latency, or difficult task categories.

## Code quality

- Python target: 3.12+.
- Use type annotations and keep mypy strict.
- Follow Ruff lint rules configured in `pyproject.toml`.
- Tests use pytest. Docker integration tests may require a working Docker daemon and should be reported separately from unit tests.
- Avoid changing formatting policy unless the task requires it and the trade-off is explained.

## Secret handling

- Never read, print, copy, or commit `.env` contents.
- `.env` is local-only and must remain ignored. If a real key was ever included in an archive or commit, rotate it.
- Use `.env.example` for variable names and safe placeholders only.

## Local LLM development policy (Ollama-first)

Use Ollama as the default runtime for real development-time LLM calls and model experiments. Keep the application dependent on the existing provider port/interface, not on Ollama-specific APIs. The Ollama adapter belongs at the infrastructure boundary. Do not let Ollama configuration or response types leak into domain models or orchestration logic.

Keep `FakeLLM` for deterministic unit tests and CI. Unit tests must not require an Ollama daemon, model download, network access, or a particular model response. Use Ollama for manual CLI tests, end-to-end runs, prompt experiments, and benchmark runs. Hosted providers are optional future adapters, not a requirement for the MVP.

Do not select or describe a model as the project default until it has been benchmarked on the actual development hardware and task dataset. Record the exact Ollama model tag/digest (where available), quantization, Ollama version, prompt version, dataset version, hardware, latency, success metrics, and failure categories. Never fabricate evaluation improvements.

## Component-wise delivery loop

Work on one major component at a time: (1) implement the smallest useful slice, (2) run focused unit tests, (3) run its CLI/manual test where applicable, (4) inspect failures and outputs, (5) evaluate with deterministic checks and/or LangSmith where LLM behavior is involved, (6) track comparable experiments in MLflow when model/prompt/configuration comparisons are being made, (7) fix critical issues, and (8) update docs before moving on. Lightweight integration checks are allowed as soon as two components have a provisional contract. Do not build the entire system before testing it.

Use LangSmith for traces, datasets, and LLM/agent trajectory evaluation when it adds value; use MLflow for controlled experiment records, parameters, metrics, and artifacts. Neither is required for deterministic utility tests. Review trace privacy before sending prompts, source code, or user data to a hosted observability service; redact secrets.

