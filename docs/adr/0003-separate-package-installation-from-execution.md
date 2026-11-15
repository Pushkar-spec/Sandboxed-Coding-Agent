# ADR 0003: Separate Dependency Installation from Untrusted Execution

- Status: Proposed
- Date: 2026-11-15

## Context

The current Docker sandbox selects bridge networking when either `network_enabled` is true or the requested package list is non-empty. This means requesting an extra Python package also grants network access to the container process that subsequently executes generated code.

Dependency installation and execution have different trust requirements. Package download needs controlled egress; arbitrary generated code should normally have no network.

## Decision

Propose a two-stage workflow:
1. Resolve/install dependencies in a controlled build or preparation stage with restricted registry access and pinned requirements where possible.
2. Execute user-generated code in a fresh runtime with network disabled by default.

The exact implementation may use prebuilt immutable images, a controlled package cache, or a dedicated dependency-preparation container. Select after measuring complexity and security.

## Alternatives considered

- Keep the current combined network behavior: simplest, but gives untrusted code network access.
- Enable bridge networking only during pip install within the same container: harder to enforce a reliable network transition and risks process/network races.
- Prebuild immutable task images: strongest repeatability, but can increase image/build complexity.
- Separate installer container and execution container: clear trust boundary, but adds lifecycle and artifact transfer complexity.

## Consequences

- Better least-privilege execution policy.
- More reproducible dependencies when versions/hashes are pinned.
- Additional image/cache management and setup latency.
- Must define package allowlists, registry policy, and cache integrity.

## Verification

Add tests proving that package preparation can succeed while the execution phase cannot access the network. Add dependency pinning and malicious package tests where feasible.
