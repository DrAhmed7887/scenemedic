# SceneMedic

**A physician-built multi-agent technical advisor on Google Cloud that turns rough medical-drama scripts into clinically bulletproof shooting drafts — with matching ECGs, ICU soundscapes, and a multi-voice table read — in under 10 seconds.**

Built for the **Agentic Cinema — AI Agent Hackathon**.

> Devpost submission text: [docs/SUBMISSION.md](docs/SUBMISSION.md) · Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · Sprint checklist: [docs/SPRINT.md](docs/SPRINT.md) · Pitch beat sheet: [docs/PITCH.md](docs/PITCH.md)

**Deployed on Vertex Agent Engine:** `projects/159973996965/locations/us-central1/reasoningEngines/5192502486044246016`

---

## The demo in one screenshot's worth of words

Give SceneMedic a bad ER scene where the attending "pushes 1 of epi" for a stable narrow-complex tachycardia, defibrillates at 360 J biphasic, and extubates the patient 3 minutes post-ROSC — SceneMedic returns:
- **CRITICAL** / L6 — "Push one of epi, IV. Now." — Epinephrine is not indicated for stable narrow-complex tachycardia. First-line: vagal, then adenosine 6 mg IV push. → cited to AHA ACLS.
- **CRITICAL** / L14 — "Extubate her." — Immediate extubation after ROSC is inappropriate. → cited to ATS extubation criteria.
- **WARN** / L5 — "Stable narrow-complex tach, hypotensive." — Internal contradiction: hypotension makes this unstable. → cited to AHA Tachycardia Algorithm.

Plus:
- 3 voice-preserving rewrites per finding.
- A photorealistic ECG monitor prop matching the corrected rhythm.
- A 30 s ICU ambient bed.
- A multi-speaker table read of the corrected Act 2 with distinct Attending/Resident voices.

## Stack

| Layer | Tech |
|---|---|
| Reasoning + orchestration | Google ADK + Gemini 2.5 Pro on Vertex AI Agent Engine |
| Grounding | BigQuery Vector Search + `gemini-embedding-001` (3072-dim), 51-chunk seeded corpus |
| Continuity DB (partner) | **ClickHouse Cloud** via MCP toolset with native `clickhouse-connect` fallback |
| Visual props | Imagen 3 / `gemini-2.5-flash-image` (nano-banana) |
| Ambient audio | `lyria-002` via Vertex REST `:predict` |
| Table read | `gemini-2.5-flash-preview-tts` multi-speaker |
| UI | Streamlit 3-panel Writers' Room (LIVE + canned-demo failover) |
| Cost safety | `EXCLUDE_ALL_CREDITS` budget + Pub/Sub → Cloud Function billing kill-switch |

## Quickstart

```bash
git clone https://github.com/DrAhmed7887/scenemedic.git
cd scenemedic

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # fill in

gcloud auth application-default login
gcloud config set project scenemedic-hackathon

# One-time corpus + canon seeding
python corpus/ingest_pubmed.py --input corpus/seed.jsonl
# then paste corpus/canon_seed.sql into your ClickHouse Cloud SQL console

# Run the UI
streamlit run ui/app.py
```

## Repo layout

```
scenemedic/
├── agents/          # Orchestrator + 6 sub-agents (ADK) + live.py callable
├── tools/           # RAG (BQ), ClickHouse MCP + native, Imagen 3, Lyria, TTS
├── corpus/          # Seed JSONL + demo scene + ClickHouse canon SQL
├── assets/          # Pre-baked demo fallbacks (ECG, monitor, CXR, WAVs)
├── deploy/          # Vertex Agent Engine deploy script
├── ui/              # Streamlit 3-panel Writers' Room
├── scripts/         # prebake_lyria / prebake_tts / run_orchestrator
├── docs/            # SUBMISSION, PITCH, SPRINT, ARCHITECTURE
├── tests/           # Smoke tests
└── outputs/         # Realism reports + cost logs (gitignored)
```

## Zero-hallucination discipline

- Every finding must cite a URL that appears in the retrieved BigQuery snippet payload. Prompts explicitly forbid invention.
- Every rewrite must fix the flagged clinical issue while preserving the character's voice and beat length within ±30%.
- No real patient data is ever used. All patients are fictional (Maya Chen, Marcus Bell, Priya Rao).
- SceneMedic never produces medical advice framing. Outputs are scene assets, not clinical guidance.

## Cost safety

Because SceneMedic runs on Vertex against the GenAI App Builder trial credit, we set up:
- `EXCLUDE_ALL_CREDITS` $10 monthly budget scoped to project `scenemedic-hackathon`
- Alerts at 25 / 50 / 75 / 90 / 100 %
- Pub/Sub topic `billing-halt` → Cloud Function `billing-halt` (ACTIVE) that unlinks billing from the project at the 100 % threshold
- Session log at `outputs/cost_log.jsonl` for post-hoc reconciliation

Run `python -m tools.cost_check` before any batch of paid operations.

## License

MIT. Built by Dr. Ahmed Zayed (MBBCh, MSc Applied Health Informatics candidate — RWTH Aachen) for the Agentic Cinema Hackathon.
