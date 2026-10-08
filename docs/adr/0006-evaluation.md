# ADR: Make failures and evidence reviewable

Status: Accepted for demo. Date: 2026-10-09.

## Context

A successful sample answer says little about access leaks, source errors or model quality.

## Decision

Version scenarios, test HTTP and security boundaries, gate CI on decisions/evidence, retain baseline results and emit safe request IDs/counters.

## Alternatives considered

LLM-only judging or a single happy-path notebook.

## Consequences

Reproducible contract evidence. Neither a small synthetic dataset nor one local latency measurement establishes general model quality, business value or production readiness.
