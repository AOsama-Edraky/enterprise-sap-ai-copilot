# Production integration plan

This is a proposed implementation path, not a deployed architecture. Validate APIs and authentication against the target SAP edition/release and organizational security policy.

| Local seam | Proposed enterprise replacement | Acceptance evidence needed |
| --- | --- | --- |
| Opaque demo authenticator | Entra ID / SAP Cloud Identity Services plus validated JWT middleware | Issuer/audience/signature/expiry tests; tenant and entitlement mapping |
| `SAPClient` mock contract | Read-only CAP / Cloud SDK integration on BTP using approved destinations | Approved communication arrangement; real API contract/schema; source authorization denials |
| Synthetic `ExceptionCode` | Approved business mapping from PO, invoice and goods-receipt facts | Functional review; no assumption this field exists in a standard SAP PO API |
| JSON policy chunks | Reviewed ingestion pipeline carrying source ACLs, hashes, versions and expiry | Permission revocation and deletion tests; approved owner workflow |
| BM25 index | Azure AI Search hybrid lexical/vector retrieval with mandatory ACL filtering | Recall/relevance benchmark; filtering and no-leak gates; freshness tests |
| Local Ollama selection | Approved managed enterprise model endpoint via a new provider adapter | Data handling review; measured model-specific output and selection performance |
| JSON audit/counters | Controlled audit store and OpenTelemetry/Application Insights | Retention/access tests; trace correlation; redacted error reporting |
| Local execution slots/rate limit | Gateway-wide quotas and bounded application workers | Load, timeout, denial-of-service and backpressure tests |

## SAP boundary

Use SAP Business Accelerator Hub and the target system to choose the released purchase-order API. The mock route `/odata/PurchaseOrders('...')` and its `value` object are deliberately OData-shaped, not a claim of compatibility with a specific SAP endpoint. Missing-receipt or invoice-block information may require additional released APIs and business mapping; do not assume it comes directly from purchase-order master data.

A BTP integration service can use Destination Service through SAP Cloud SDK. Select an auth flow appropriate to the system and communication arrangement, preserving the end user's permitted scope. SAP documents user-dependent destination authentication and principal propagation, but eligibility and setup vary. For on-premise/private networks assess Cloud Connector requirements separately. For technical-account integration, enforce an independently validated end-user/company policy at the integration boundary and document which SAP permissions it can exercise.

Pin released API versions, validate response schemas, project data early, set timeouts, and implement bounded retry only for idempotent reads. Add contract tests against a sandbox. Never accept an arbitrary model-generated endpoint, filter or resource URL.

## Retrieval and model boundary

Build source ACL fields into the search schema and construct every filter server-side. Microsoft's security-filter pattern simulates document authorization through query filters; it does not authenticate a caller. Make gateway identity and entitlement handling explicit. For features advertised as native ACL support, validate availability and support for the chosen region/source/API before relying on them.

Keep endpoint allowlists, TLS verification, provider limits and data minimization. The current `local_url` explicitly prevents cloud endpoints: replacing it requires a separate production transport implementation, not just setting an Azure URL. No Azure resources, model deployment, embeddings or managed identities are provisioned here.

## Pilot and release gates

1. Functional owner confirms source semantics, exception mapping and policy applicability.
2. Security owner confirms identity, source authorization, ACL ingestion, egress and audit handling.
3. Product/AI engineer runs held-out queries, paraphrases, Arabic queries, ambiguous questions, poisoned content and permission-revocation cases.
4. SRE verifies load, latency, outage behavior and rollback; metrics distinguish failures/refusals from successful answers.
5. A small human-reviewed pilot measures time to find evidence and correction rate against the existing workflow. Business value must be measured, not assumed.

## Primary technical references

Reviewed 2026-10-09; follow current official documentation before implementing production features.

- [SAP Cloud SDK destination connectivity](https://sap.github.io/cloud-sdk/docs/js/features/connectivity/destinations)
- [SAP S/4HANA Cloud API-access service and principal propagation](https://help.sap.com/docs/btp/sap-business-technology-platform/create-service-instance-to-consume-sap-s-4hana-cloud-apis)
- [Azure AI Search security-filter pattern](https://learn.microsoft.com/en-us/azure/search/search-security-trimming-for-azure-search)
- [Ollama chat API and structured output contract](https://docs.ollama.com/api/chat)
