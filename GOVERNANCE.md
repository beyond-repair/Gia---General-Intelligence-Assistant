# Governance — Gia---General-Intelligence-Assistant

**Sweep:** 113  
**Classification:** SUPERSEDED  
**Successor (canonical):** `beyond-repair/sovereign-clean-room`  
**Claim level:** 0 (scaffold / historical prototype)  
**GitHub archived flag:** false (operator-only; queued)

## Invariants

- This repository is **not** a validated general-intelligence system.
- README product claims (autonomous AGI-class assistant, Mistral-7B integration, sandboxed execution, self-correcting workflows) are **UNSUPPORTED** without passing tests + listed CI + measured evidence.
- Unique runtime work belongs in successor `sovereign-clean-room` (VSA core) and related ACTIVE agent surfaces, not here.
- No history rewrite. No deletion. No claim elevation in this sweep.

## Observed tree (head 63c33a3)

- Nested path `gia-general-intelligents-assistant/project/` (typo in directory name).
- Duplicate `backend` vs `backend ` (trailing space) trees.
- FastAPI `app/main.py` imports `app.models.database` / `app.models.task` — those modules are **absent** from the tree.
- Frontend is a Vite/React task UI; backend agents exist as source files only.
- Tests: none.
- Product CI: CodeQL workflow only (pre-sweep).
- `requirements.txt` pins heavy ML stack (`torch`, `transformers`) with no model artifacts in-repo.

## Allowed agent actions

Idempotent docs, claim tokens, docs-presence CI. No invented agents, no model weights, no ACTIVE promotion.
