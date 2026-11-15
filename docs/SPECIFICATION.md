# Specification and Contracts

## 1. Current domain contracts in source snapshot

The current source defines the following Pydantic models in `src/codeagent/domain/model.py`:

- `SandboxConfig`: timeout, memory, CPU, network flag, extra package list.
- `SandboxResult`: stdout, stderr, exit code, duration, timeout flag, artifact path-to-size mapping, OOM flag.
- `Complexity`: simple, standard, complex.
- `Message`: role and content.
- `LLMResponse`: text and input/output token counts.
- `TaskSpec`: task, complexity, acceptance criteria, assumptions, expected artifacts, max attempts, sandbox config.

These are the actual current contracts in the snapshot. Their validation and semantics should be reviewed before the agent loop depends on them.

## 2. Target application contracts

The following are design targets, not currently implemented types. Refine them through ADRs and tests before coding.

### RunRequest
- `task`: non-empty user request.
- `run_id`: generated unique identifier.
- `workspace_policy`: controlled workspace location and permissions.
- `user_overrides`: optional bounded configuration overrides.

### TaskSpec
Should contain:
- normalized task statement;
- explicit acceptance criteria;
- expected outputs/artifacts;
- complexity classification and confidence/reason;
- attempt budget;
- sandbox policy;
- assumptions and unresolved ambiguities.

Analyzer output must be parsed and validated. Invalid or incomplete output should fall back safely or request clarification; it must not expand privileges.

### AttemptRecord
Should record:
- attempt index and stable attempt ID;
- prompt version/hash and model identifier;
- generated code reference or protected artifact;
- sandbox result;
- evaluation report;
- token usage, latency, cost estimate if available;
- timestamps and failure category.

### EvaluationReport
Should contain:
- overall status: pass, fail, or indeterminate;
- named evaluator results;
- objective evidence (test counts, exit status, artifact checks);
- judge output separately labelled as subjective;
- evaluator version and configuration.

### RunResult
Should contain:
- terminal status;
- final code/artifact references;
- bounded stdout/stderr summaries;
- attempt history summary;
- evaluation report;
- usage and timing metadata.

## 3. LLM port requirements

The LLM port should:
- accept typed messages and a prompt/system instruction;
- return normalized text or structured output plus token usage;
- expose model/provider metadata where available;
- support timeout and cancellation semantics;
- classify provider errors (rate limit, auth, timeout, invalid request, transient server error);
- avoid leaking provider SDK objects into domain/application code.

Structured outputs must be schema-validated. Never treat syntactically valid JSON as semantically safe.

## 4. Sandbox port requirements

The sandbox port should:
- receive code and a validated sandbox policy;
- execute only inside an isolated runtime;
- return bounded output and artifact metadata;
- report timeout, OOM, exit code and infrastructure errors distinctly;
- guarantee cleanup on all terminal paths;
- support cancellation;
- reject unsafe paths and enforce artifact quotas.

The current `SandboxResult` may need an explicit infrastructure-error category because an exit code alone can conflate user-code failures with Docker failures.

## 5. Configuration precedence

Target precedence:

1. hard security ceilings and platform policy;
2. explicit user overrides, after validation;
3. analyzer recommendations;
4. complexity profile defaults.

The analyzer must never grant privileges beyond platform ceilings. In particular, network, packages, CPU, memory, timeout, attempts, and concurrency require hard limits. The current `default_spec()` enables network access; revisit this before production use.

## 6. Compatibility

When changing a contract:
- update all adapters and fakes;
- add validation and contract tests;
- document migration implications;
- update ADRs if the change affects architecture;
- update evaluation dataset schemas if benchmark records change.

## LLM provider configuration requirements

The application must support provider selection through configuration rather than hard-coded provider construction in business logic. The first-class development provider is `ollama`; the provider contract remains compatible with `FakeLLM` and future adapters. Configuration must identify the provider, local base URL, model tag, request timeout, and generation limits supported by the adapter. Exact environment variable names are implementation decisions and must be documented alongside the adapter.

Failure behavior must be explicit: unavailable Ollama service, missing model, timeout, malformed/empty model response, and provider-side failure must produce actionable application errors. Do not silently fall back to another provider or model unless an explicit fallback policy is configured and recorded.

## Testing requirements

Unit tests use `FakeLLM` and must not require Ollama. Add adapter contract tests with mocked HTTP/API responses. Real Ollama smoke tests are opt-in integration tests and should skip with a clear reason when Ollama or the configured model is unavailable.

