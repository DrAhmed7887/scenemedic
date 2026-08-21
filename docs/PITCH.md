# SceneMedic — 3-Minute Pitch Script

## Beat sheet

**0:00–0:20 — Hook**
> "Medical dramas pay clinical consultants $5,000 an episode, and still ship errors that trend on medical Twitter the next morning. I'm Ahmed Zayed — physician, informatics engineer — and I built the consultant Hollywood actually needs."

**0:20–1:00 — Architecture flyover**
Show the ARCHITECTURE.md mermaid diagram.
> "SceneMedic is a multi-agent system on Google ADK and Vertex Agent Engine. A parser reads the script. A continuity agent — grounded in ClickHouse via MCP — knows every patient's history across every episode. A clinical accuracy agent audits every medical beat against a curated PubMed corpus in BigQuery Vector Search. Then a dramatization agent rewrites flagged lines while preserving the writer's voice."

**1:00–2:20 — Live demo**
- Upload `Ep07_bad_scene.pdf` in the Streamlit UI.
- Findings appear: **CRITICAL — wrong drug for narrow-complex tach**; **WARN — extubation 3 min post-ROSC implausible**.
- Show alternate rewrites populate under each finding.
- Imagen 3 regenerated ECG appears matching the corrected rhythm.
- Play 8-second multi-speaker TTS table read of the fixed Act 2 dialogue.
- Play 5-second Lyria 3 ICU bed underneath.

**2:20–2:50 — Stretch**
> "For actors prepping the role, SceneMedic goes further — live rehearsal with a Gemini Live API attending physician who responds in character."
Play 15-second live-API voice clip.

**2:50–3:00 — Close**
> "Same architecture, three products: SceneMedic for medical drama. Forensica for crime. VitalSigns for actor prep. The moat isn't the code — it's a physician built it. Thank you."

## Delivery notes
- Never say "AI" in the hook — say "consultant."
- Never apologize on demo latency; if a call hangs, cut to the pre-recorded backup.
- If asked about PHI: "No real patient data anywhere. Corpus is public literature. Every output is a fictional scene asset. That's why I built the governance layer."
- If asked about hallucination: "The clinical agent can only cite what the RAG tool returned. Findings without a citation URL are filtered out at the orchestrator."

## Backups
- Pre-recorded 60-second screencast of the full flow.
- 6 pre-generated Imagen 3 prop images in `docs/assets/` in case generation stalls on stage.
- Pre-rendered Lyria 3 + TTS clips as fallback audio.
