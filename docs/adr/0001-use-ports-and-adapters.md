# ADR 0001: Use Ports and Adapters Architecture

- **Status:** Accepted
- **Date:** 2026-10-29

## Context

The Coding Agent must interact with external systems, including an LLM provider and Docker-based sandboxes.

Directly coupling the agent's core logic to specific SDKs would make testing, debugging, and replacing these integrations more difficult.

For example, testing agent behavior should not require a real LLM API call or a running Docker container for every unit test.

## Decision

Use a Ports and Adapters architecture.

The core application logic will depend on interfaces (ports) rather than directly on external implementations.

Adapters will implement those interfaces for specific technologies, such as:

- An LLM provider adapter for Anthropic.
- A sandbox adapter for Docker.
- Fake adapters for deterministic testing.

The core application will coordinate these components without needing to know the details of their underlying SDKs.

## Consequences

### Positive

- Core logic can be tested independently of external services.
- External providers can be replaced with less impact on the application.
- Dependencies and responsibilities are easier to understand.
- Integration tests can target real adapters while unit tests use fakes.

### Trade-offs

- Additional interfaces and abstractions must be maintained.
- Small operations may require more files and indirection.
- Interfaces should be introduced where they provide a meaningful boundary, not for every function.

## Implementation notes

The exact interfaces and adapters will be introduced incrementally as the sandbox and agent components are implemented.
