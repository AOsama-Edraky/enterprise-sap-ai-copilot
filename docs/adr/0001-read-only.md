# ADR: Read-only evidence assistant

Status: Accepted for demo. Date: 2026-10-09.

## Context

Financial mutation amplifies the cost of tool-routing and model errors.

## Decision

Ship one read operation and retain the established SAP approval workflow. The model has no tool definitions or write credential.

## Alternatives considered

An autonomous approval agent and a full chat platform.

## Consequences

This is an evidence assistant. A future action capability must have deterministic validation, business authorization, human approval, idempotency and reconciliation; it cannot be enabled by a prompt change.
