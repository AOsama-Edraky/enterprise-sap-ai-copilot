# Security model

## Protected assets and trust assumptions

Assets are business records, policy text, credentials, authorization metadata and audit events. A remote caller can control request headers and JSON but cannot edit local files or server configuration. The local operator controls fixtures and generated tokens. Production identity, retrieval and integration services must be independently secured; this local demo does not defend against an administrator reading its files or memory.

Authorization is conjunctive: the principal's tenant must match the document or PO, the requested company must be in the principal's entitlement, and policy roles must intersect. The mock checks tenant and company again on PO lookup. The operator has no business companies. Client-supplied tenant/roles/URLs are absent from the accepted request schema.

## Threat/control traceability

| Threat | Implemented mitigation | Verification | Residual limitation |
| --- | --- | --- | --- |
| Object ID guessing | Company and tenant checks; missing/hidden record share 404 | HTTP cross-tenant and scope tests | Timing equivalence not guaranteed |
| Cross-role policy leak | Filter before scoring, statistics, top-k and prompt assembly | Role-filter and hidden-corpus tests | Local fixture files remain readable to the operator |
| Identity spoofing | Server-owned principal from opaque token; ignore identity headers | Forged-token/role/header tests | Demo tokens have no expiry; filesystem deletion rotates them |
| Confused deputy to ERP | Separate service credential plus authenticated user; independent source check | Mock credential and scope tests | Production token exchange/SoD mapping is not implemented |
| Injection in user or policy | No tools/write routes; suspicious-pattern gate; exact output renderer | Refusal and poisoned-chunk tests | Heuristic cannot detect all attacks or harmful source content |
| Hallucinated citations/facts | Current-bundle ID allowlist; exact trusted rendering | Invalid citation and invented-output tests | Model selection relevance can fail; source itself can be wrong |
| PII exposure | Project out supplier bank field at source and adapter | Field-leak checks across all evals | Not a general PII classifier |
| SSRF/redirect exfiltration | Fixed loopback base; strict PO ID; disable redirects and environment proxies | URL/PO validation tests | Privileged code can change configuration |
| Token/prompt disclosure in logs | Disable access logs; fixed structured event fields; no payload/error traces | Audit redaction test | Parser-level stdlib responses are outside application telemetry |
| Resource exhaustion | 8 KiB body, 1000-char question, read/HTTP timeouts, rate limit, eight execution slots | Size and rolling-window tests | Thread acceptance and invalid-auth attempts lack gateway-wide limits |
| Unsafe changes | Only upstream GET route; no write tool; refusal heuristic | HTTP method/refusal tests | Request heuristic may reject benign advice about approval |
| Upstream/model outage | Explicit errors; no invented answer/fallback | Failure/schema/provider tests | No retry/circuit breaker in demo |

## Deployment safety

Services bind loopback and are intended for local review. Do not expose Python's standard-library demo server to the internet. In a production design replace it with a hardened gateway/application server; enforce TLS, approved audiences/issuers, signature verification, token expiry, session revocation and authenticated service-to-service identity. Apply distributed rate limiting, bounded workers, body/header/time limits and private network egress policies.

Move credentials to managed secret storage or managed identity; do not forward these demo tokens into SAP. Use an approved SAP authorization mapping and preserve object-level restrictions even when middleware authenticates with a technical account. A technical account alone is not proof of end-user authorization.

Policies require a trusted publishing/review workflow, ACL reconciliation and deletion/revocation handling. Canary leaks and regression evaluations should block releases. Enforce retention/deletion policies for audit data and avoid unnecessary raw prompt logging. The demo makes no GDPR, Saudi PDPL, ISO 27001 or other compliance certification claim.

## Output interpretation

The model cannot cause executable operations through output in this application. It can select poorly or fail to select the right evidence. Exact policy text can still carry malicious content; no frontend should execute/render it as HTML. Treat all evidence as untrusted text, cite source versions, and make the human reviewer responsible for financial decisions.
