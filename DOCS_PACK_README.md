# Sandboxed Coding Agent — updated documentation pack

This archive contains Markdown documentation only. It incorporates the Ollama-first local inference decision and component-wise development/evaluation workflow.

- Ollama is the planned default for real development-time inference and experiments.
- The LLM provider interface remains provider-independent.
- `FakeLLM` remains required for deterministic unit tests and CI.
- No preferred Ollama model is selected until benchmarked on the actual hardware and task dataset.
- LangSmith and MLflow are optional, with distinct roles; neither is required for deterministic tests.
- The docs describe intended changes and do not claim that the Ollama adapter or full agent workflow is already implemented.

Start with `AGENTS.md`, `README.md`, and `MASTER_IMPLEMENTATION_ROADMAP.md`.
