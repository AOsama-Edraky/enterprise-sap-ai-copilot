# ADR: Minimize runtime and use BM25

Status: Accepted for demo. Date: 2026-10-09.

## Context

A small interview demonstration should be reproducible without cloud resources or dependency installation.

## Decision

Use Python standard library, two real HTTP boundaries in one process and scope-local BM25 over curated atomic policy chunks.

## Alternatives considered

Kubernetes, vector infrastructure, complex agent frameworks and full SAP deployment.

## Consequences

Very low setup cost; lexical search is limited for paraphrases and multilingual use. The HTTP runtime is local only. Production hybrid retrieval and an ASGI server are future substitutions, not implemented features.
