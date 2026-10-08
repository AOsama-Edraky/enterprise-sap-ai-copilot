# Validation report

Validation date: 2026-10-09 Cairo (2026-10-08 UTC). Runtime: Python 3.12.14 in the build environment.

| Check | Observed result |
| --- | --- |
| Automated unit, HTTP integration and security tests | 37 passed |
| Versioned synthetic evaluation cases | 16 / 16 passed, extractive mode |
| Persistent API startup on 8080 and mock SAP on 8081 | Passed |
| Bearer-authenticated PO answer via persistent API | Passed |
| Operator metrics via persistent API | Passed |
| Generated credential file permissions | 0600 verified |
| Graceful SIGINT shutdown | Passed |
| Archive extracted into a clean temporary directory | Tests, evaluation and demo run successfully |
| Local Markdown file references | Resolved |

The baseline report retains individual scenario checks and measured request times. These are tiny synthetic contract cases; they do not establish semantic reasoning quality, production latency, general accuracy or financial correctness.

## Verification still required in target environments

- Real Ollama model execution: not run. Provider request/response and authorized context contracts are covered by mocks.
- Docker build/run: not run; no Docker executable was available.
- GitHub Actions Python matrix: configured, not run on GitHub. Only Python 3.12.14 was executed locally.
- SAP and Azure integration: proposed and documented, not connected or deployed.
- Arabic queries, large corpora, distributed scale and adversarial content beyond the small regression suite: not assessed.

The source is published in the owner-created public repository `AOsama-Edraky/enterprise-sap-ai-copilot`. The existing `mostafa300/entifaa` repository remains untouched. GitHub-hosted CI results must be checked independently of the local baseline.
