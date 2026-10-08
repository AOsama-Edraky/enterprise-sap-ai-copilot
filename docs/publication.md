# Separate GitHub repository publication

Suggested new repository: `enterprise-sap-ai-copilot` under `AOsama-Edraky`. This project does not alter or depend on `mostafa300/entifaa`.

The owner created the separate repository at https://github.com/AOsama-Edraky/enterprise-sap-ai-copilot. The prepared source was uploaded through the authenticated GitHub connection after write access was enabled. The entifaa repository remains untouched. The commands below are retained for reproducing publication to a new repository; do not run the repository-creation command against this existing repository.

## GitHub CLI path

Extract the archive, enter the `enterprise-sap-ai-copilot` directory, review the README and license, and run:

```bash
python3 -m unittest discover -s tests -v
python3 -m copilot eval

git init -b main
git add .
git diff --cached --stat
git commit -m "Add synthetic enterprise SAP AI copilot portfolio"

# This next command creates a PUBLIC repository and uploads the source.
# Run it only when you intend to publish publicly.
gh repo create AOsama-Edraky/enterprise-sap-ai-copilot \
  --public --source=. --remote=origin --push \
  --description "Authorization-aware SAP procurement evidence copilot with synthetic data, bounded RAG and architecture decision records"
```

To review privately first, replace `--public` with `--private`. Git commit uses your locally configured identity. No credentials, customer data, generated tokens or audit logs belong in a commit. The archive excludes runtime files and bytecode; `.gitignore` preserves that boundary after local use.

## If a new empty repository already exists

```bash
git remote add origin https://github.com/AOsama-Edraky/enterprise-sap-ai-copilot.git
git push -u origin main
```

Use the exact URL from the newly created repository if its owner/name differs. Do not point `origin` to `entifaa`. Avoid overwriting a populated remote: reconcile its contents in a branch/PR first.

## Repository settings and presentation

- Run GitHub Actions and inspect all Python matrix results after publication.
- Add topics such as `enterprise-ai`, `rag`, `sap`, `solution-architecture`, `ai-security` and `portfolio`.
- Pin the repository to your profile, linking it as a synthetic architecture case study.
- Keep source mode and evaluation results explicit. Do not add an unearned CI badge or advertise real-model accuracy from the extractive baseline.
- Review MIT licensing and attribution before publication; change the license if that is not your intended reuse policy.
