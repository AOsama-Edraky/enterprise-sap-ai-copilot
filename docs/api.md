# Local API contract

`GET /healthz` is unauthenticated and reports local process liveness only. It does not check model readiness. `GET /metrics` requires an operator bearer token and returns in-memory route/status counters. Errors are JSON with `error` and `request_id`; responses carry `X-Request-ID` and `Cache-Control: no-store`.

## POST /v1/ask

Bearer authentication and `Content-Type: application/json` are required. No fields outside this schema are accepted. Duplicate keys and control characters in questions are rejected.

| Field | Type | Requirement |
| --- | --- | --- |
| `company_code` | string | Required; two capital letters plus two digits; authorized for principal |
| `question` | string | Required; 3–1000 trimmed characters; supported English procurement vocabulary |
| `purchase_order` | string | Optional; exactly 10 digits; a single authorized PO |

```json
{"company_code":"EG01","purchase_order":"4500001001","question":"Why is this order blocked?"}
```

Success (HTTP 200) is `answered`, `abstained` or `refused`. `evidence` is empty for abstention/refusal. Policy IDs are versioned by source metadata; PO citations identify the requested resource and its change timestamp. Latency is application elapsed time, not token generation latency alone.

```json
{
  "status": "answered",
  "answer": "Exact authorized evidence text [evidence-id]",
  "evidence": [{"id":"evidence-id","text":"Exact authorized evidence text","source":{"kind":"policy","title":"Policy title","version":"demo-policy-v1"}}],
  "provider": "extractive",
  "latency_ms": 1.0,
  "notice": "Synthetic demo. Evidence supports human review; no SAP writes are performed.",
  "request_id": "server-generated-id"
}
```

| HTTP status | Meaning |
| --- | --- |
| 400 | Invalid schema/JSON/question/PO |
| 401 | Missing or invalid bearer token |
| 403 | Unauthorized company or operator role |
| 404 | Unknown route or missing/inaccessible PO |
| 405 | Method unsupported; no write operation |
| 413 | Body exceeds 8192 bytes or empty body |
| 415 | JSON content type required |
| 429 | Authenticated subject exceeds 30 requests / 60 seconds |
| 502 | Upstream invalid/HTTP failure or model output invalid |
| 503 | Upstream unavailable/timeout or all execution slots occupied |
| 500 | Unexpected application failure, with no internal detail exposed |

## Mock SAP contract

`GET /odata/PurchaseOrders('4500001001')?company=EG01` requires both the user's bearer token and an internal `X-Service-Token`. Returned `value` is one projected object, not an OData collection. The synthetic bank field never crosses this boundary. No `$filter`, list-all, pagination or mutation endpoint is implemented. Caller identity and company are validated independently.
