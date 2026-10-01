<div align="center">

[![Lifecycle](https://img.shields.io/badge/●_SUPERSEDED-f59e0b?style=for-the-badge&labelColor=0f0f23)](https://github.com/beyond-repair/ADL-Governance)
[![Claim](https://img.shields.io/badge/Claim_0-22c55e?style=for-the-badge&labelColor=0f0f23)](https://github.com/beyond-repair/ADL-Governance/blob/main/docs/CLAIM_VALIDATION.md)
[![Governance](https://img.shields.io/badge/ADL--Governance-7c3aed?style=for-the-badge&labelColor=0f0f23)](https://github.com/beyond-repair/ADL-Governance)

```
LIFECYCLE   SUPERSEDED
CLAIM       0
SUCCESSOR   sovereign-clean-room
```

</div>

> **SUPERSEDED.** Canonical successor: [sovereign-clean-room](https://github.com/beyond-repair/sovereign-clean-room). No new product-feature work beyond keeping this Claim-0 prototype runnable.

---

# Gia (General Intelligence Assistant) — Claim-0 runnable sketch

**Classification:** SUPERSEDED (Sweep-113)  
**Successor:** [`sovereign-clean-room`](https://github.com/beyond-repair/sovereign-clean-room)  
**Claim level:** 0 — historical FastAPI + Vite prototype with **stub agents**. Product AGI claims are **UNSUPPORTED**.

See [CLAIM_STATUS.md](CLAIM_STATUS.md) and [GOVERNANCE.md](GOVERNANCE.md).

## What this repo contains

Nested tree `gia-general-intelligents-assistant/project/`:

- **Backend** (`backend/`): FastAPI + SQLAlchemy (aiosqlite) task API; workflow engine; stub agents (`llm`, `scraper`, `github`, `code_execution`).
- **Frontend** (`src/`): React/Vite UI that submits tasks to the API and polls status.
- Default path does **not** download Mistral or require torch/Docker/network.

## Quick start

```bash
git clone https://github.com/beyond-repair/Gia---General-Intelligence-Assistant.git
cd Gia---General-Intelligence-Assistant/gia-general-intelligents-assistant/project
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py               # http://127.0.0.1:8000
```

Smoke:

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/tasks/ \
  -H 'Content-Type: application/json' \
  -d '{"description":"Write a hello world function"}'
curl -s http://127.0.0.1:8000/tasks/
```

### Frontend

From `gia-general-intelligents-assistant/project/` (with backend running):

```bash
npm install
npm run dev                 # http://127.0.0.1:5173 — talks to API on :8000
# or production build:
npm run build
```

Optional: `VITE_API_BASE=http://127.0.0.1:8000` (default).

### Tests

```bash
cd backend
source .venv/bin/activate
pytest -q
```

## Optional live mode (not required)

| Env var | Effect |
|---------|--------|
| `GIA_USE_REAL_LLM=1` | Try loading transformers model (`GIA_LLM_MODEL`, needs optional torch stack) |
| `GIA_ALLOW_NETWORK=1` | Allow scraper / GitHub live calls |
| `GIA_ALLOW_CODE_EXEC=1` | Run generated Python via local subprocess |
| `GIA_DATABASE_URL` | Override SQLite URL (default `sqlite+aiosqlite:///./gia_tasks.db`) |

Optional packages: `pip install -r requirements-optional.txt` (still no torch by default).

## Honesty / claims

The following remain **UNSUPPORTED**:

- Autonomous general intelligence / AGI
- Local Mistral-7B as a shipped default capability
- Secure Docker sandbox as the default path
- Self-correcting adaptive intelligence beyond the stub pipeline

What **is** verified at Claim-0: create/list tasks via API; stub agents execute a fixed workflow; UI can submit and show status; unit tests pass.

## Governance

Portfolio source of truth: [`ADL-Governance`](https://github.com/beyond-repair/ADL-Governance).

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

**REWRITE · BUILD · TRANSCEND**

Governing source: [ADL-Governance](https://github.com/beyond-repair/ADL-Governance) · [Claim levels 0–5](https://github.com/beyond-repair/ADL-Governance/blob/main/docs/CLAIM_VALIDATION.md)

</div>
