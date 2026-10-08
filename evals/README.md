# Evaluation methodology

`scenarios.json` is a versioned set of 16 synthetic scenarios. `python3 -m copilot eval` starts the real local HTTP stack with fresh generated credentials and checks HTTP status, answer decision, required citation IDs, exact rendering, authorized policy evidence and prohibited sentinel data. The process exits nonzero if any case fails.

`baseline-results.json` records the **extractive** provider on this environment. It is a contract baseline, not a real LLM accuracy result. The provider-contract tests mock Ollama output; downloaded-model execution remains unverified. Run `COPILOT_PROVIDER=ollama python3 -m copilot eval --output evals/ollama-results.json` on a suitable host to measure the actual model, retaining its name/version, hardware and configuration with the results.

The suite covers EG/SA receipt exceptions, approval threshold, finance role access, beta-tenant threshold, cross-company/cross-tenant denial, unknown objects, write refusal, instruction injection, out-of-domain questions, no-evidence abstention, malformed PO IDs and operator restrictions. Fault injection and poisoned-document checks live in the automated tests.

Exact rendering is a structural property, not semantic correctness. The fixture corpus is tiny and the cases are not held out from development. A production quality assessment must add unseen paraphrases, ambiguous and multi-intent questions, incorrect/stale source content, Arabic queries, large ACL sets and permission revocation. Measure retrieval precision/recall, answer relevance, unsupported claims, abstention calibration and task completion with human reviewers. Include the deterministically correct baseline so any model complexity must justify its cost.

Latency in this file is per-request local wall time. The reported p95 uses the nearest-rank sample of only 16 requests; it includes fast denial/refusal cases and is not a production answer-latency estimate. No quality score or latency SLA is claimed.
