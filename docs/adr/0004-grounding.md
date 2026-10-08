# ADR: Constrain output and retain an offline baseline

Status: Accepted for demo. Date: 2026-10-09.

## Context

Free-form generation is hard to validate and downloaded models undermine first-run reproducibility.

## Decision

Default to deterministic extractive rendering. Optional Ollama selects IDs through a schema; trusted code checks current evidence and renders exact claims. Fail closed on model errors.

## Alternatives considered

Unrestricted generated answers with post-hoc citation checks; pretending a mock model demonstrates reasoning quality.

## Consequences

Claims have exact text provenance, with reduced fluency and reasoning scope. Model selection quality is still evaluated. Local tests do not establish real-model behavior.
