# Interview demonstration

## Ten-minute walkthrough

| Time | Show | Architectural point |
| --- | --- | --- |
| 0–1 min | Problem, scope and synthetic provenance | A useful business decision and an honest boundary |
| 1–3 min | `python3 -m copilot demo`; blocked order plus cited receipt policy | Live transaction facts and document retrieval are different sources |
| 3–5 min | Cross-company and cross-tenant tests; role-filter test | Security precedes context assembly, with source-side enforcement |
| 5–7 min | `providers.py`, one ADR, and optional Ollama contract | Model authority is bounded; exact rendering trades fluency for provenance |
| 7–9 min | Tests and baseline evaluations; outage test | Evidence of behavior and transparent gaps |
| 9–10 min | Production mapping and pilot gates | Delivery ownership across functional, AI, security and operations teams |

## Likely questions

**Why no vector database?** The corpus is five curated policy rules. BM25 is cheap and reproducible. A real corpus needs a held-out retrieval benchmark; adopt hybrid search when it measurably improves recall under the same ACL rules.

**Is this generative AI?** The optional mode invokes a local LLM with retrieved evidence and a schema-constrained selection task. The trusted answer is extractive. The default mode does not use an LLM. Explain that deliberate tradeoff; do not claim the default proves model reasoning.

**How do you stop prompt injection?** There is no write-capable tool and no model-generated executable action. ACL filtering limits context, ID validation limits output provenance, and text rendering avoids HTML execution. Pattern matching is only a heuristic. Malicious source content and relevance errors still need corpus governance and evaluation.

**How does SAP authorization survive middleware?** The demo authenticates the caller at both boundaries and checks tenant/company. In production choose supported delegated identity or an explicit authorized integration policy. A broadly privileged technical user does not automatically preserve the caller's SAP access rights.

**Why a mock?** It makes the case study reproducible and publishable without disclosing customer information. The mock is a contract seam, not proof the chosen real SAP API has the same fields. Released APIs and exception mapping must be verified in a sandbox.

**How would you lead delivery?** Define functional source semantics with the SAP owner, assign API/ACL contracts to the integration and AI engineers, have security review identity and egress, and have operations validate load and failure modes. Use the evaluation suite as a release gate and human pilot evidence to prioritize improvements. These are proposed leadership practices, not a claim a team delivered this demo.

**What do the metrics prove?** Only local contract behavior on a tiny synthetic dataset. Exact-rendering checks prove provenance by construction. They do not prove relevance, real-model quality, Arabic performance, SLA or financial correctness.

## Defensible portfolio wording

“Built a reproducible SAP procurement evidence copilot case study with a typed API integration boundary, tenant/company/role-filtered retrieval, optional local LLM evidence selection, strict citation validation, safe telemetry and automated security/evaluation gates. Documented the production path to SAP BTP and Azure AI services.”

Describe it as an independent synthetic portfolio implementation. Do not add production deployment, customer adoption, commercial savings, certification or measured LLM accuracy until you have evidence.

## Next extension with the greatest value

Run the real-model suite and add a small held-out relevance dataset with ambiguous questions and human judgments. Then compare BM25 to hybrid retrieval. This strengthens the evidence more than adding agents, a dashboard or infrastructure before evaluating the core behavior.
