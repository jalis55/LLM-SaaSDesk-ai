# FlowDesk AI — Fictional RAG Knowledge Base

Version: 1.0 (2026-11-01). All content is synthetic and for learning/testing only. No domain, email, compliance claim, or API endpoint represents a real service.

## Contents
- 12 Markdown files (policies, features, integrations, API, support)
- 2 TXT files (FAQ, troubleshooting)
- 2 PDF guides (onboarding and administration)
- `evaluation_questions.jsonl` — questions and expected answers for later evaluation; **do not ingest this file**.

## Install
1. Back up your existing `data/documents/` directory; the package defines a canonical replacement dataset.
2. Extract the contents of `documents/` into `data/documents/`.
3. Remove unrelated test documents (for example, `test_doc.pdf`) from the ingestion directory.
4. Run `uv run python -m app.ingestion.test_manual` and your chunking test again.

## Known limitations
All product facts are invented. Content is designed to be consistent, not to substitute for real legal, security, or commercial policies. Some facts intentionally repeat across files to test retrieval. The evaluation set includes unanswerable questions.
