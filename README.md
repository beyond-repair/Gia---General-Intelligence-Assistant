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

> **SUPERSEDED.** Canonical successor: [sovereign-clean-room](https://github.com/beyond-repair/sovereign-clean-room). No new feature work.

---

# Gia (General Intelligence Assistant) — SUPERSEDED

**Classification:** SUPERSEDED (Sweep-113)  
**Successor:** [`sovereign-clean-room`](https://github.com/beyond-repair/sovereign-clean-room)  
**Claim level:** 0 — historical FastAPI + Vite prototype. Product AGI claims are **UNSUPPORTED**.

See [CLAIM_STATUS.md](CLAIM_STATUS.md) and [GOVERNANCE.md](GOVERNANCE.md).

## What this repo actually contains

Nested tree `gia-general-intelligents-assistant/project/`:

- Python FastAPI sketch (`backend/app`) with agent class files (LLM, scraper, GitHub, code execution).
- React/Vite UI (`src/`) for task list / workflow visualization.
- CodeQL workflow. No unit tests. `app.models` imported by `main.py` is **not present**.
- Duplicate directory `backend ` (trailing space) with a second `run.py`.

Installation paths in older README text (`cd backend`, `cd frontend`, clone `gia.git`) do **not** match this tree. Treat them as stale.

## Features (claimed historically — not validated)

The following remain **UNSUPPORTED** until tests + listed CI + evidence exist (they do not):

- Autonomous task decomposition
- Local Mistral-7B integration
- Secure sandboxed execution
- Self-correcting workflows

## Governance

Portfolio source of truth: [`ADL-Governance`](https://github.com/beyond-repair/ADL-Governance).

No further feature work. Operator may apply the GitHub archive flag.

## License

MIT — see [LICENSE](LICENSE).


---

<div align="center">

**REWRITE · BUILD · TRANSCEND**

Governing source: [ADL-Governance](https://github.com/beyond-repair/ADL-Governance) · [Claim levels 0–5](https://github.com/beyond-repair/ADL-Governance/blob/main/docs/CLAIM_VALIDATION.md)

</div>
