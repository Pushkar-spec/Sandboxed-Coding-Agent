# Operations and Observability

## 1. Operating model

The first supported operating mode is local CLI execution. Do not introduce a distributed worker platform until concurrency or hosted operation is a demonstrated requirement.

## 2. Configuration

- Validate configuration at startup.
- Keep secrets in environment variables or a local secret manager, never in source or task workspaces.
- Separate model, sandbox, evaluation, and observability configuration.
- Apply hard policy ceilings after user/analyzer configuration.
- Make optional integrations explicitly opt-in.

## 3. Structured events

Emit events for:
- run accepted / completed / failed / cancelled;
- analysis started / completed;
- LLM request started / completed / failed;
- attempt started / completed;
- sandbox started / stopped / timed out / OOM;
- evaluator started / completed / errored;
- repair decision and reason.

Every event should include stable run/task/attempt IDs, timestamp, duration, component, status, and safe error category.

## 4. Metrics

Track task success, attempt count, retry recovery, model latency, sandbox duration, evaluation duration, token usage, estimated cost, timeout rate, infrastructure failure rate, and security test outcomes.

## 5. Tracing and privacy

LangSmith tracing and MLflow tracking are optional. Before enabling them:
- decide whether source code, task text, prompts and outputs may leave the machine;
- redact credentials and personal data;
- minimize payloads and avoid capturing full workspace contents by default;
- define retention, access controls, deletion and self-hosting requirements;
- record trace IDs locally for correlation.

## 6. Failure handling

Distinguish model/provider errors, sandbox infrastructure errors, code errors, evaluator errors and policy denials. Do not convert unknown exceptions into a passing result. Ensure cleanup and preserve a concise diagnostic record.

## 7. Production readiness gates

- sandbox hardening and adversarial testing complete;
- resource quotas and concurrency controls enforced;
- secrets and trace privacy reviewed;
- reproducible benchmark baseline established;
- regression evaluation in CI;
- operational logs and metrics validated;
- documented backup/retention policy if persistent storage is added;
- incident and dependency update process defined.
