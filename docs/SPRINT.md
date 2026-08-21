# SceneMedic — 72h Sprint Checklist

Target: working Agent Engine deployment + 3-min demo video + repo pushed.

## H0–H4 — Foundation
- [ ] Redeem $100 hackathon GCP credits (billing account attached).
- [ ] Redeem Replit credits.
- [ ] `gcloud services enable aiplatform bigquery documentai secretmanager run`.
- [ ] Create GCS staging bucket: `gs://scenemedic-staging-$PROJECT`.
- [ ] Create Vertex AI Document AI processor (form parser) → save `DOCAI_PROCESSOR_ID`.
- [ ] Provision ClickHouse Cloud dev tier → save connection env vars.
- [ ] Provision Grafana Cloud free tier → save API key.
- [ ] Fill `.env` from `.env.example`.

## H4–H12 — Corpus + RAG
- [x] Curate 50 gold-standard clinical snippets in `corpus/seed.jsonl` (ACLS + Sepsis-3 + Trauma/Tension Pneumo).
- [ ] `python corpus/ingest_pubmed.py --input corpus/seed.jsonl`.
- [ ] Smoke test `search_pubmed("narrow complex tachycardia")` returns ≥3 hits with `Adult Tachycardia Algorithm — stable narrow-complex` in top-3.
- [x] Demo scene locked at `corpus/demo_scene.txt` (Maya Chen — 3 planted errors: epi for stable SVT, 360 J biphasic, extubation 3 min post-ROSC).
- [x] ClickHouse continuity canon seeded via `corpus/canon_seed.sql` (Maya Chen, Marcus Bell, Priya Rao).

## H12–H24 — Parser + Continuity
- [ ] Wire Document AI parser end-to-end on a 3-scene test script.
- [ ] Load fictional show bible into ClickHouse (`patients`, `episodes`, `scenes` tables).
- [ ] Continuity Agent flags one canned contradiction correctly.

## H24–H36 — GenMedia layer
- [ ] Confirm Imagen 3 access; ship 4 prompt templates (ECG, monitor, X-ray, drug label).
- [ ] Confirm Lyria 3 allowlist; ship 4 mood presets.
- [ ] Multi-speaker TTS working with 4 distinct voices on Act 2 revision.

## H36–H48 — UI + Deploy
- [ ] Streamlit uploader with 3-panel output (annotated script, prop gallery, audio player).
- [ ] `python deploy/agent_engine.py` → resource name captured.
- [ ] Cloud Run for the Streamlit UI.
- [ ] Grafana dashboard: latency + tool-call traces.
- [ ] All secrets in Secret Manager, none in `.env` on prod.

## H48–H60 — Hero demo prep
- [ ] Curate the demo bad-ER scene (wrong drug + wrong rhythm + impossible timeline).
- [ ] Rehearse 3-min pitch:
  - 0:00–0:20 hook (real cost of medical errors on TV, MD credibility)
  - 0:20–1:00 architecture flyover
  - 1:00–2:20 live demo (upload → findings → generated ECG → TTS)
  - 2:20–2:50 stretch (Live API rehearsal snippet)
  - 2:50–3:00 close (roadmap: Forensica, VitalSigns)
- [ ] Record backup screencast.

## H60–H72 — Polish + submit
- [ ] Safety guardrails: Gemini safety settings tight, PHI refusal, no medical-advice framing.
- [ ] README architecture section + install steps.
- [ ] Public repo (or private-with-access for judges).
- [ ] 3-min video uploaded.
- [ ] Devpost submission form complete.
- [ ] Buffer for one broken tool call at H70.

## Stop condition
Working deployment + video + repo pushed. **Do not add features after H60.**
