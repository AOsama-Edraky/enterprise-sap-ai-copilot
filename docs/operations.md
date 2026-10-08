# Local operations and proposed service objectives

## Operator workflow

Start `python3 -m copilot serve` from the repository root. The two loopback listeners run until SIGINT/SIGTERM. A port conflict aborts startup; choose a free host or stop the conflicting service. Runtime tokens and audit logs are under ignored `.runtime/`. Delete `tokens.json` while the service is stopped to rotate demo credentials; do not publish it.

Use the operator token to query `/metrics`. Counters are process-local and reset on restart. Application request events in `.runtime/audit.jsonl` contain route/status, a server-created request ID and elapsed milliseconds. Successful answers also carry application latency. Raw prompts, tokens, PO IDs and supplier names are not logged. There is no general-purpose log-retention service: the local operator must manage the file.

`/healthz` is liveness, not readiness. Model availability is checked only when an actual answer invokes it. For an upstream error, match the request ID, inspect the sanitized error code, verify the local service/model listener and rerun an authorized request. Never interpret a healthy liveness endpoint as proof that an answer can be generated.

## Proposed production objectives (not measured SLAs)

| Objective | Proposed starting target | Required verification |
| --- | --- | --- |
| Unauthorized evidence leakage | Zero in mandatory release suite | Held-out role/tenant/company and revocation cases |
| Grounded source/citation validation | Every returned claim validates | Provider contract and malicious-output regression |
| Evidence relevance | Set with functional owner during pilot | Human labels, recall and precision over held-out questions |
| Response latency | Agree an interactive budget after measuring provider | Load tests with real SAP and model endpoints |
| Availability and recovery | Agree with ERP/AI service owners | Outage drills, alerts and rollback evidence |

Production telemetry should separate answered/abstained/refused decisions, integration/retrieval/model stage timing, token/cost budgets and dependency failures. Add tracing without business payload logging. The demo implements request-level counters and timing only.

## Rollback

For local review, stop the CLI and restore the last known-good source/fixture version. Re-run tests and evaluation before restart. Production should deploy immutable images with versioned policy indexes and an explicit rollback target; none is provisioned by this project.
