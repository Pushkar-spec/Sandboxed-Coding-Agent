# Architecture Decision Records

ADRs capture decisions that materially affect architecture, security, reliability, cost, or extensibility.

## Existing decisions
- [ADR 0001 — Ports and Adapters](0001-use-ports-and-adapters.md)
- [ADR 0002 — One container per attempt](0002-one-container-per-attempt.md)

## Planned decisions to write when implementation begins
- Sandbox dependency installation vs execution network separation.
- Workspace ownership, path validation and artifact quotas.
- Agent state machine and retry/repair policy.
- Deterministic evaluation pipeline and evaluator result contract.
- CLI evaluation harness and dataset/run manifest format.
- Optional LangSmith and MLflow integration boundaries.
- Whether/when stronger isolation than Docker is required.

## ADR template

```markdown
# ADR NNNN: Short decision title

- Status: Proposed | Accepted | Superseded
- Date: YYYY-MM-DD

## Context
What problem and constraints led to this decision?

## Decision
What are we choosing?

## Alternatives considered
What realistic alternatives were evaluated and why were they rejected?

## Consequences
Benefits, costs, risks, operational implications and migration needs.

## Verification
Tests, measurements or operational evidence that validate the decision.
```
