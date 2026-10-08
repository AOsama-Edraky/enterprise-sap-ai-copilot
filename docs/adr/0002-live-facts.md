# ADR: Live ERP facts, retrieved policies

Status: Accepted for demo. Date: 2026-10-09.

## Context

Indexed transaction data can lag ERP and inadvertently expand access.

## Decision

Use a typed, fixed-route adapter for PO facts; retrieve only small versioned policy chunks. Known exception codes enrich search.

## Alternatives considered

Embed every ERP row or let the model generate OData queries.

## Consequences

Live facts and policy versions are independently visible. This reduces transaction staleness but does not make two sources transactionally consistent.
