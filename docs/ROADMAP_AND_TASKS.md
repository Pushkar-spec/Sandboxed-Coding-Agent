# Roadmap and Acceptance Criteria

## Status legend

- `DONE (snapshot)` means visible in the uploaded ZIP; re-verify before relying on it.
- `PLANNED` means not present or not wired in that snapshot.
- `BLOCKED` means prerequisite or design decision is outstanding.

## Phase 0 — Repository baseline and documentation
- [x] Python 3.12, uv project and package layout (snapshot).
- [x] Ports and Adapters ADR (0001).
- [x] Fresh container per attempt ADR (0002).
- [ ] Remove secrets from archives and verify `.env` rotation if needed.
- [ ] Reconcile Makefile formatting command with the agreed Ruff lint-only workflow.
- [ ] Re-run all checks in the actual development environment and record baseline.

**Exit criteria:** clean repository, verified test baseline, no tracked secrets, docs match code.

## Phase 1 — Sandbox foundation
Snapshot includes Docker sandbox and unit/integration tests for execution, output, timeout, limits, network, package install, artifacts, OOM and cleanup.

Before production readiness:
- [ ] Separate dependency installation network from code execution network.
- [ ] Default to network disabled.
- [ ] Add non-root execution and stronger runtime hardening.
- [ ] Add workspace path/symlink validation.
- [ ] Add disk/workspace/artifact/output quotas.
- [ ] Add cancellation and cleanup fault-injection tests.
- [ ] Review Docker isolation assumptions and stronger isolation options.

**Exit criteria:** threat model reviewed; adversarial tests pass; residual risks documented.

## Phase 2 — Application contracts and task analysis
- [ ] Review and finalize TaskSpec invariants and configuration precedence.
- [ ] Define run, attempt, failure, evaluation and terminal-result contracts.
- [ ] Implement task analyzer behind LLM port with strict schema validation.
- [ ] Add deterministic fallback behavior.
- [ ] Enforce policy ceilings independently of model output.
- [ ] Add contract tests and analyzer evaluation dataset.

**Exit criteria:** valid TaskSpec produced or safe fallback/error for malformed model outputs.

## Phase 3 — Agent orchestration and repair
- [ ] Implement bounded agent state machine/use case.
- [ ] Implement code generation prompt and validated extraction.
- [ ] Connect LLM and sandbox ports.
- [ ] Add deterministic evaluator pipeline.
- [ ] Implement failure taxonomy and repair policy.
- [ ] Enforce attempt, time, token and cost budgets.
- [ ] Record complete attempt history and structured events.
- [ ] Wire usable CLI.

**Exit criteria:** end-to-end tasks run locally, pass/fail correctly, stop at budget, and clean up.

## Phase 4 — Evaluation harness (priority)
- [ ] Versioned dataset schema and seed benchmark tasks.
- [ ] CLI runner with per-task JSONL results.
- [ ] Correctness, reliability, latency, token and cost metrics.
- [ ] Baseline report and comparison tool.
- [ ] Frozen holdout split and experiment manifest.
- [ ] Adversarial sandbox evaluation suite.
- [ ] LLM-as-a-judge only after deterministic baseline; calibration set and human agreement.
- [ ] CI regression run with a bounded smoke dataset.

**Exit criteria:** another developer can reproduce baseline and compare a candidate run.

## Phase 5 — Observability and experiment tracking
- [ ] Stable run/attempt/trace event schema.
- [ ] Optional LangSmith adapter for traces and agent trajectory inspection.
- [ ] Optional MLflow adapter for metrics, parameters and artifacts.
- [ ] Local execution unaffected when integrations are disabled/unavailable.
- [ ] Secret/source-code redaction and privacy/retention policy.
- [ ] Compare model, prompt, retry and resource strategies.

**Exit criteria:** experiment records link local benchmark rows to traces and MLflow runs without making either service mandatory.

## Phase 6 — Reliability, performance and resume evidence
- [ ] Repeatability and concurrency tests.
- [ ] Failure injection and recovery tests.
- [ ] Cost/latency optimization experiments.
- [ ] Ablation studies on meaningful agent design choices.
- [ ] Final holdout benchmark and security report.
- [ ] Architecture diagrams, ADRs and demo walkthrough.
- [ ] Resume claims tied to published experiment artifacts.

**Exit criteria:** project is demonstrable, reproducible, security limitations are clear, and claims are supported by data.

## Phase ordering rationale

Sandbox security and stable contracts come before autonomy. A correct bounded agent comes before large-scale evaluation. A baseline harness comes before tuning. Observability integrations come after event and result contracts stabilize. This prevents tool-driven architecture and makes improvements measurable.

## Component-wise execution and Ollama tasks

Follow the loop for every major component: implement a thin vertical slice, run focused tests, run a CLI/manual test, inspect outputs and failures, evaluate, fix critical issues, and document the result. Use provisional interfaces and lightweight integration checks early; do not defer all integration until the end.

Add/complete these tasks in order:
1. Define and test the provider configuration contract (provider, Ollama base URL, model tag, timeout, generation limits).
2. Implement the Ollama adapter behind the existing LLM port; retain `FakeLLM` for deterministic tests.
3. Add mocked adapter contract tests and an opt-in real Ollama smoke test.
4. Run a small, versioned model-selection benchmark before choosing a preferred model.
5. Instrument relevant LLM/agent calls with optional LangSmith tracing and track controlled model/prompt experiments in MLflow.
6. Verify that the application and test suite work with observability disabled and without Ollama for unit tests.

