# Project Overview

## 1. Product vision

Build a coding agent that accepts a programming task, converts it into an explicit execution specification, generates a solution, executes it in a constrained Docker environment, evaluates the result, and performs a limited repair cycle when useful.

The project should demonstrate both sound system design and disciplined LLM evaluation. A successful demo is not enough: the system should produce measurable, reproducible evidence about task success, reliability, security, latency, and cost.

## 2. User workflow (target)

1. User submits a natural-language coding task.
2. Task analyzer creates a validated `TaskSpec` containing requirements, acceptance criteria, complexity, attempt budget, and sandbox policy.
3. Agent asks the LLM to generate code against the task specification.
4. Sandbox executes the code in a fresh, constrained environment.
5. Evaluators assess process outcome, tests, artifacts, and task-specific criteria.
6. If unsuccessful and attempts remain, the agent diagnoses the failure and generates a repair.
7. Agent returns code, execution output, artifacts, evaluation summary, and run metadata.

This is the target flow. Each stage must be marked implemented only after it exists and has tests.

## 3. Scope

### Initial scope
- Python coding tasks.
- Gemini as the first live LLM adapter, behind a provider-neutral port.
- Docker-based isolated execution.
- Bounded retries and resource budgets.
- Objective evaluation through tests and explicit acceptance checks.
- CLI as the first user interface and evaluation entry point.
- Local machine-readable benchmark output.

### Later scope, only when justified
- Additional LLM providers.
- LangSmith tracing and dataset/trajectory evaluation.
- MLflow experiment tracking.
- Persistent run history or a database.
- Parallel execution and worker queue.
- Retrieval over project files or documentation, if context limits or task requirements justify it.
- Web interface or hosted deployment.

### Explicit non-goals for the first production-minded version
- Arbitrary unrestricted execution on the host.
- Unbounded autonomous loops.
- Broad network access by default.
- A web-scale distributed platform before single-run correctness and security are established.
- RAG solely to use RAG metrics.
- Claiming full hostile-code isolation from Docker alone.

## 4. Quality attributes

| Attribute | Target design concern | Evidence |
|---|---|---|
| Correctness | Task completion and acceptance criteria | Golden task suite |
| Security | Untrusted code containment and least privilege | Threat tests and security review |
| Reliability | Predictable failure handling and cleanup | Fault-injection and repeated runs |
| Reproducibility | Identical benchmark inputs and recorded config | Run manifests and dataset versions |
| Efficiency | Avoid wasteful tokens, retries and execution | Latency/cost metrics |
| Extensibility | Provider and evaluator adapters | Contract tests and fake adapters |
| Observability | Understand each model/tool/action | Structured traces and run events |

## 5. Resume evidence strategy

Resume claims must be generated from actual project evidence:
- architecture diagrams and ADRs;
- security test results;
- benchmark datasets and versioned run artifacts;
- controlled model/prompt/strategy comparisons;
- LangSmith traces and MLflow experiment records, if integrations are implemented;
- reproducible commands and CI results.

Do not insert hypothetical percentage improvements into the resume. Use actual baseline and treatment results, sample sizes, and evaluation definitions.

## Development inference strategy

Ollama is the default local inference runtime for development and model experimentation. The application remains provider-independent through the LLM port. This allows the project to use local models without coupling core logic to Ollama, and leaves room for hosted adapters later. `FakeLLM` is retained for deterministic tests and CI.

Model choice is an experiment, not an assumption. Benchmark candidate models on the same task set and configuration before choosing a preferred model.

## Delivery method

The project is developed component by component. Each component must have focused tests and a practical CLI/manual check where relevant. Analyze outcomes and fix important defects before moving to the next major component. Use small integration checks as soon as contracts between components exist.

