# ADR: Authorize before retrieval

Status: Accepted for demo. Date: 2026-10-09.

## Context

Post-filtering a model response cannot undo exposure of unauthorized context.

## Decision

Use a server-owned principal. Apply tenant/company/role filters before statistics, scoring and top-k. Recheck object access at the source boundary.

## Alternatives considered

Client-provided ACL filters and answer-time redaction.

## Consequences

More secure context assembly, with explicit entitlement lifecycle obligations. A production search filter is not an identity authenticator; gateway authentication and authoritative permission mapping remain required.
