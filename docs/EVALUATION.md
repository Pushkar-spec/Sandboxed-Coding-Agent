# Evaluation Strategy and Experiment System

## 1. Purpose

The evaluation system is a core product capability. It must answer: **Does this coding agent solve tasks correctly, reliably, safely, efficiently, and reproducibly—and did a change genuinely improve it?**

A CLI harness is mandatory. LangSmith and MLflow are optional integrations that add observability and experiment management; they do not replace the local evaluator.

## 2. Evaluation layers

### A. Deterministic correctness
- Compile/syntax validation.
- Unit tests and hidden tests where available.
- Exact output / property-based checks.
- Artifact existence, type, schema and content checks.
- Acceptance-criteria checks with objective oracles.

### B. LLM behavior
- Structured output validity.
- Instruction adherence.
- Correctness against reference tests.
- Hallucinated APIs or unsupported assumptions.
- Prompt robustness and response consistency.

### C. Agentic behavior
- Task completion rate.
- Planning/specification quality.
- Tool/action selection correctness.
- Recovery after execution errors.
- Retry usefulness and no-progress retry rate.
- Correct stop/termination decisions.
- Trajectory efficiency and unnecessary actions.

### D. Sandbox and security
- Isolation policy tests.
- Network policy compliance.
- Resource limit enforcement.
- Cleanup and cross-attempt isolation.
- Adversarial code containment.

### E. Efficiency and operations
- End-to-end latency and per-stage latency.
- Input/output tokens and estimated cost.
- Attempts per task and cost per successful task.
- Timeout, infrastructure error and provider error rates.
- Concurrency and resource utilization.

### F. RAG evaluation (conditional)
The current baseline does not contain a RAG subsystem. Do not implement RAG only to claim RAG metrics. If retrieval is later introduced, add:
- retrieval precision/recall or hit-rate against labelled relevant chunks;
- context precision/relevance;
- context recall/coverage;
- answer faithfulness/groundedness;
- answer relevance;
- context utilization and retrieval latency.

The RAG Triad is typically context relevance, groundedness/faithfulness, and answer relevance. It evaluates retrieval-grounded answering, not the entire coding agent.

## 3. Dataset design

Use versioned JSONL datasets with stable task IDs and explicit splits:

```text
evals/
  datasets/
    v1/
      coding_tasks.jsonl
      debugging_tasks.jsonl
      multi_step_tasks.jsonl
      adversarial_tasks.jsonl
      manifest.json
  schemas/
  evaluators/
  metrics/
  runners/
  experiments/
  reports/
```

Each task record should define:
- stable ID and category/difficulty;
- user task prompt;
- acceptance criteria;
- test/oracle reference;
- expected artifacts;
- allowed capabilities (network/packages);
- resource budget;
- tags and dataset version.

Keep development, validation and frozen holdout sets separate. Prevent benchmark tasks or expected outputs from leaking into the model prompt.

## 4. Metrics and definitions

| Metric | Definition |
|---|---|
| Task success rate | Successful tasks / attempted tasks |
| First-attempt success | Tasks passing on first attempt / attempted tasks |
| Pass@k | Probability at least one of k independent samples passes; state sampling assumptions |
| Repair success rate | Failed first attempts that pass after repair / failed first attempts eligible for repair |
| Retry efficiency | Successful repairs relative to extra attempts/cost |
| Instruction adherence | Criteria satisfied / criteria evaluated, with scoring rubric |
| Evaluator agreement | Agreement between automated judge and human-labelled subset |
| Sandbox security pass rate | Adversarial tests meeting defined containment expectations / tests run |
| Median / p95 latency | End-to-end duration distribution |
| Cost per success | Total model cost / successful tasks |
| Token usage | Input/output tokens per task and per successful task |

Do not collapse all dimensions into one score without reporting the components.

## 5. Experiment protocol

For a valid comparison:
1. State a hypothesis and primary metric before running.
2. Freeze dataset version and task IDs.
3. Change one principal variable (model, prompt, temperature, retry policy, resource profile, evaluator, retrieval setting).
4. Keep other configuration fixed.
5. Run paired comparisons on identical tasks.
6. Repeat runs if stochasticity matters.
7. Record failures, timeouts, cost and latency—not only successes.
8. Report sample size and uncertainty; avoid strong claims from tiny samples.
9. Use validation data for tuning and holdout data for final confirmation.
10. Preserve raw records, config, prompt hashes and code revision.

Example report table (illustrative schema, not project results):

| Experiment | Config | N | Success | First-pass | Median cost | p95 latency |
|---|---|---:|---:|---:|---:|---:|
| baseline | prompt-v1, max_attempts=3 | — | — | — | — | — |
| treatment | prompt-v2, max_attempts=3 | — | — | — | — | — |

A resume statement such as “improved task success from X% to Y%” is allowed only after a reproducible experiment with actual values, task count, dataset version, and controlled conditions.

## 6. Evaluator architecture

Prefer deterministic evaluators first:
1. process/exit status;
2. compile and test suite;
3. artifact validation;
4. task-specific objective checks;
5. optional rubric/judge evaluation.

Each evaluator returns a typed result with evaluator name/version, pass/fail/indeterminate, score if applicable, evidence, duration, and error details. Evaluator failure must never be silently interpreted as success.

LLM-as-a-judge requirements:
- version and hash the judge prompt;
- use a rubric with explicit anchors;
- calibrate against human-labelled examples;
- monitor judge-human agreement and disagreement;
- test position/model bias where relevant;
- keep judge output separate from deterministic ground truth;
- cap judge calls and cost.

## 7. Tooling: CLI, LangSmith, MLflow

### CLI evaluation harness — required
Runs locally and in CI, loads datasets, executes tasks, invokes evaluators, and writes JSONL/CSV/Markdown reports. It must work without cloud observability.

Proposed commands (exact CLI syntax to be finalized during implementation):
```bash
uv run python -m evals.run --dataset evals/datasets/v1/coding_tasks.jsonl
uv run python -m evals.run --dataset evals/datasets/v1/debugging_tasks.jsonl --limit 20
uv run python -m evals.compare --baseline runs/baseline.jsonl --candidate runs/candidate.jsonl
```

### LangSmith — optional tracing and agent evaluation
Use for LLM call traces, tool/action trajectories, debugging, dataset curation and judge-based evaluation. It is not the source of truth for deterministic sandbox tests.

### MLflow — optional experiment tracking
Use for parameters, metrics, artifacts, model/prompt/config comparisons, and reproducible experiment records.

### Integration design
- Keep interfaces provider-neutral.
- Local run must continue if optional observability is disabled or unavailable.
- Attach stable `run_id`, `task_id`, `attempt_id`, dataset version and trace IDs.
- Redact secrets and sensitive code; define retention and export policy before enabling hosted services.
- Avoid duplicate sources of truth: local raw results remain exportable; external platforms index/visualize them.

## 8. Initial implementation plan

Start small; do not create empty abstractions for every possible metric:
- dataset schema and a small hand-labelled seed dataset;
- deterministic task runner and result schema;
- baseline runner and JSONL output;
- correctness, reliability, latency and token/cost metrics;
- comparison/report generation;
- adversarial sandbox suite;
- optional LLM judge after deterministic baselines are stable;
- LangSmith and MLflow adapters after run/trace contracts stabilize.

## 9. Reproducibility manifest

Every run should record:
- run ID and timestamp;
- git commit;
- dataset version and task IDs;
- model provider/model/version;
- prompt template version/hash;
- decoding parameters;
- agent and evaluator versions;
- sandbox image digest and resource policy;
- environment/dependency lock version;
- random seed where applicable;
- raw per-task outcomes, traces, latency, tokens, cost;
- failures and skipped tasks with reasons.
