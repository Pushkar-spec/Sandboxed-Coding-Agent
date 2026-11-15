# ADR 0005: Ollama-first local LLM development

- **Status:** Proposed
- **Date:** 2026-11-16

## Context

The project needs real LLM behavior during development and repeatable model/prompt experiments, while keeping the MVP time-conscious and avoiding unnecessary dependence on hosted inference. The existing architecture uses an LLM port and has a `FakeLLM` adapter for tests.

## Decision

Use Ollama as the default local inference runtime for development, manual CLI workflows, end-to-end testing, and model experiments. Implement it as an adapter behind the existing LLM port. Keep provider selection/configuration outside domain logic. Retain `FakeLLM` for deterministic unit tests and CI. Hosted providers may be added later as separate adapters but are not required for the MVP.

Do not nominate a default model before benchmarking candidate models on the project's versioned task set and actual hardware. Record model identity (tag and digest where available), quantization, runtime version, prompt and dataset versions, hardware, metrics, latency, and failure categories.

## Consequences

### Benefits
- Real model calls can run locally without making core orchestration provider-specific.
- Unit tests and CI remain deterministic and do not need model downloads or a running inference service.
- Model choice is evidence-based rather than based on reputation or assumptions.
- Future hosted providers can reuse the same port.

### Costs and risks
- Local models may have lower quality or slower inference than hosted models, depending on hardware and model size.
- Model downloads consume disk space; inference consumes RAM/VRAM and can have significant cold-start latency.
- Ollama service availability and model presence must be checked and reported clearly.
- Local inference does not remove the need to sandbox generated code.
- Optional hosted tracing can still transmit prompts and code outside the machine; redact sensitive data and review privacy settings.

## Alternatives considered

1. **Hosted provider only:** potentially strong model quality and simpler local hardware requirements, but introduces API credentials, network dependency, and usage cost.
2. **Ollama-specific calls inside orchestration:** simple initially, but couples business logic to one provider and makes tests and future providers harder.
3. **FakeLLM only:** deterministic, but cannot validate real model behavior or produce meaningful model/prompt evaluation.

## Validation

The decision is validated when the Ollama adapter passes mocked contract tests, a real local smoke test succeeds when configured, the unit suite passes without Ollama, and a small reproducible benchmark compares candidate models on identical tasks.
