# ADR 0004: CLI-First Evaluation with Optional Observability Integrations

- Status: Proposed
- Date: 2026-11-15

## Context

The project needs repeatable benchmark execution, CI regression checks, and detailed agent traces. LangSmith and MLflow provide useful hosted/self-hosted capabilities, but tying core evaluation to either service would make local runs fragile and couple the application to external vendors.

## Decision

Build a local CLI evaluation harness as the source of truth for benchmark execution and raw results. Define optional adapters:
- LangSmith for LLM/tool traces, trajectory inspection and selected dataset/judge workflows.
- MLflow for experiment parameters, metrics, artifacts and comparisons.

The core evaluation schema and runner must work with both integrations disabled.

## Alternatives considered

- CLI only: simplest and fully local, but less convenient for trace inspection and experiment dashboards.
- LangSmith-only: strong tracing and agent evaluation, but not a replacement for deterministic sandbox checks or general experiment artifact tracking.
- MLflow-only: strong experiment tracking, but not a complete agent trajectory debugger.
- Mandatory dual integration: feature-rich but adds cost, secrets, privacy concerns and operational dependencies.

## Consequences

- Reproducible local/CI runs remain available.
- Integration credentials and data export are opt-in.
- A stable event/result schema is required before adapters are implemented.
- Sensitive task content and source code require redaction, retention and access policies.

## Verification

Run the full benchmark with no external integration configured. Then enable each adapter independently and verify stable run/task/attempt correlation and redaction.
