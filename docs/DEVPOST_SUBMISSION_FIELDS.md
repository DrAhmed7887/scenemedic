# Devpost Submission Fields — SceneMedic

Paste-ready copy for the Agentic Cinema Hackathon Devpost submission page. Verify each field against the live Devpost form before submitting — Devpost occasionally adds/renames fields.

> **⚠️ Do not submit without:** (1) VO recorded + pitch v2 rendered + uploaded to YouTube, (2) ClickHouse MCP partner track selected in the form, (3) public GitHub repo pushed with all Google + partner services imported and called in code, (4) Devpost `Built With` tags matched to the list below.

---

## 1. Project name

```
SceneMedic
```

Tagline field (≤80 chars):

```
The physician-built clinical-realism advisor for medical film & TV.
```

## 2. Elevator pitch (≤200 chars)

```
Every network drama pays clinical consultants $5,000 an episode and still ships errors. SceneMedic is a multi-agent system that audits every clinical beat before shoot day — grounded, cited, voice-preserving.
```

## 3. Inspiration (≤1,500 chars)

```
Medical drama consultants charge $5,000+ per episode and still ship errors that trend on medical Twitter the next morning. As a practicing physician of twelve years, I've watched the same three mistakes repeat across every show — wrong drug for the wrong rhythm, physiologically impossible recoveries, procedures dramatized as if they finished in six seconds.

The consultants aren't bad. There are just too many scenes, too many episodes, too many parallel productions for any one physician to audit line-by-line at the speed television ships. That's not a labor problem — it's an orchestration problem.

SceneMedic is what happens when a physician-engineer builds the consultant Hollywood actually needs: a multi-agent system that reads every scene against real medical literature, checks it against every prior episode's canon, and rewrites flagged lines in the writer's own voice. Not to replace the consultant — to give the consultant a workbench.
```

## 4. What it does (≤3,000 chars)

```
SceneMedic ingests a script scene (PDF, Fountain, or plain text) and runs it through a six-agent pipeline on Google ADK + Vertex AI Agent Engine:

1. Script Parser Agent — Document AI deconstructs scenes into characters, dialogue, vitals, procedures.

2. Continuity Engine — queries ClickHouse Cloud (via the ClickHouse MCP server and native driver) for each character's prior canon: baseline labs, chronic conditions, prior episode outcomes. If a scene contradicts established canon, the agent flags it.

3. Clinical Accuracy Agent — queries BigQuery Vector Search over 3,072-dim gemini-embedding-001 embeddings of PubMed / ACLS / ATLS / Sepsis-3 literature. Every clinical beat must retrieve a supporting citation URL. If retrieval returns nothing, the finding drops out at the orchestrator — zero hallucination discipline.

4. Dramatization Agent — proposes 2-3 voice-preserving rewrites per finding, each within ±30% of the original line length. Uses Gemini 2.5 Pro with a voice-fingerprint prompt derived from prior episodes.

5. VFX & Props Agent — Imagen 3 regenerates bedside monitors with rhythm-matched ECGs, chest X-rays, drug labels, and other set pieces that would otherwise be filmed with generic stock footage.

6. Audio & Foley Agent — Lyria-002 generates 30-second ambient beds (ICU quiet, code-blue tension, family-meeting silence). Gemini multi-speaker TTS renders full table reads of revised scenes with distinct Attending, Resident, and patient voices.

Delivered through a Streamlit "Writers' Room" UI: uploaded scene on the left, ranked findings with citations and rewrites in the center, generated props and audio table read on the right. Cost governance is a first-class citizen — every model invocation is written to an append-only cost ledger, and a $10 monthly budget cap fires a Pub/Sub → Cloud Function kill-switch at 100%.

Same architecture, three products: SceneMedic (medical drama), Forensica (crime + procedurals), VitalSigns (actor prep via Gemini Live API).
```

## 5. How we built it (≤2,500 chars)

```
Backbone: Google ADK (google-adk, google-cloud-aiplatform, google-genai) with a Gemini 2.5 Pro orchestrator that dispatches to specialist sub-agents. Deployed to Vertex AI Agent Engine as a persistent reasoning engine (projects/159973996965/locations/us-central1/reasoningEngines/5192502486044246016).

Grounding: BigQuery Vector Search over the pubmed_chunks table (3,072-dim gemini-embedding-001), with the orchestrator's zero-citation-zero-output rule enforced at the tool-boundary.

Canon: ClickHouse Cloud accessed via the official ClickHouse MCP server (mcp-clickhouse) in the ADK toolset, with a clickhouse-connect native driver fallback for Streamlit-hosted paths where MCP isn't available. Tables: patient_episodes, series_canon.

VFX: Imagen 3 (gemini-2.5-flash-image) for medical props, ECG strips, chest X-rays.

Audio: Lyria-002 for ambient beds via Vertex REST :predict; Gemini 2.5 Flash Preview TTS for multi-speaker table reads.

UI: Streamlit with server-side ADK invocation, canned-demo mode for stage-safe presentation, offline fallback bed if generation stalls.

Governance: Secret Manager for keys, Cloud Function billing halt, cost ledger to outputs/cost_log.jsonl. Grafana Cloud traces for observability.

Repo: Python 3.11, pytest for smoke tests, Playwright for UI capture, ffmpeg for pitch reel rendering.
```

## 6. Challenges we ran into (≤1,500 chars)

```
The hardest engineering problem was voice preservation — every writer's room has a distinctive dialogue register, and a rewrite that reads as generic ChatGPT loses the room. Solved by seeding the Dramatization Agent with a voice fingerprint derived from prior episodes and enforcing ±30% line-length constraints on rewrites.

The hardest product problem was zero-hallucination discipline in a domain where a wrong drug dose can leak into a shot on screen and mislead viewers. Solved by making retrieval the gate: if the Clinical Accuracy Agent's vector search returns nothing, the finding is dropped at the orchestrator boundary, never surfaced. No exceptions.

The hardest UX problem was making multi-agent orchestration visible to a non-technical writers' room — six agents doing six different jobs can easily read as a black box. Solved by rendering the swimlane trace and per-agent latency inline in the Writers' Room UI.
```

## 7. Accomplishments (≤1,000 chars)

```
- Six-agent pipeline fully deployed to Vertex AI Agent Engine, verified live via session-based stream_query.
- BigQuery vector search grounding with real 3,072-dim embeddings against ACLS/PubMed corpus; top match score 0.888 on AHA Adult Tachycardia Algorithm for the demo scene.
- ClickHouse MCP integration with dual-mode (MCP toolset + native driver) so the same code runs locally and on Agent Engine.
- Physician-authored voice canon for the demo series ensuring rewrites read as continuous with the writers' room, not generic AI.
```

## 8. What we learned (≤1,000 chars)

```
Grounding is a product decision, not a technical one. A citation-required orchestrator is measurably less impressive at first glance than one that "always has an answer" — until the first hallucination reaches a shot on screen. The moat in healthcare-adjacent creative AI isn't model choice; it's the discipline to drop outputs the retrieval layer can't justify.

Multi-agent architectures also earn their weight only when the handoffs are visible. Six agents in a black box scores the same as one; six agents whose reasoning shows up as swimlane traces in the UI is a different product.
```

## 9. What's next (≤1,000 chars)

```
- Forensica (crime procedurals): swap the medical canon for forensic/legal canon; same architecture.
- VitalSigns (actor prep): live rehearsal with a Gemini Live API attending physician who responds in character; the actor practices bedside manner against a real clinical persona.
- Pilot conversation with two US network showrunners already in motion.
```

## 10. Built With — tag list

Paste these exact tag names into Devpost's Built With field:

```
google-adk
google-cloud-vertex-ai
vertex-ai-agent-engine
gemini
gemini-2.5-pro
gemini-2.5-flash-image
gemini-tts
imagen-3
lyria
bigquery
bigquery-vector-search
clickhouse
clickhouse-mcp
document-ai
cloud-run
secret-manager
pub-sub
cloud-functions
streamlit
python
playwright
ffmpeg
```

## 11. Try it out — URLs

```
GitHub: https://github.com/DrAhmed7887/scenemedic
Demo video: {{YouTube URL — paste after uploading pitch v2}}
Live agent: (Vertex Agent Engine resource, not publicly invocable — see repo for smoke-test script)
```

## 12. Team

```
Ahmed Zayed, MBBCh
Practicing physician (12 years) · Clinical AI engineer · RWTH Aachen M.Sc. Data Science (Winter 26/27)
```

## 13. Partner track selection (mandatory dropdown)

Select: **ClickHouse**

Justification field (if prompted):

```
SceneMedic uses ClickHouse Cloud as the continuity canon store for characters and series state across episodes. The Continuity Agent queries it via the official ClickHouse MCP server (mcp-clickhouse) inside the ADK toolset, with a clickhouse-connect native driver as fallback for hosted Streamlit paths. Tables: scenemedic.patient_episodes, scenemedic.series_canon. See tools/clickhouse_mcp.py in the repo — the MCP wiring is a first-class code path, not a shim.
```

## 14. Region / eligibility check

- Country of residence at submission: **Spain** (Ahmed relocated 2026-08).
- Verify against Devpost §Rules exclusion list (currently excludes Italy, Brazil, Quebec, Iran, Russia, and others). Spain is eligible.
- Age: over 18. Yes.
- Team size: 1. Under the max-4 cap. Yes.

## 15. Pre-submission gate

Do NOT click Submit until:

- [ ] Pitch v2 MP4 rendered (`outputs/scenemedic_pitch_v2.mp4`)
- [ ] Pitch v2 uploaded to YouTube, unlisted-or-public, English audio + burned captions
- [ ] YouTube URL pasted in field 11
- [ ] Public GitHub repo pushed with all secrets removed (`.env` gitignored, `assets/.storage_state_*.json` gitignored)
- [ ] Every named Google service (ADK, Vertex Agent Engine, Gemini 2.5 Pro, Gemini 2.5 Flash Image, BigQuery Vector Search, Imagen 3, Lyria-002, Gemini TTS) has a live call-site in the pushed repo — not just README mention
- [ ] ClickHouse MCP has a live call-site in the pushed repo
- [ ] Video runtime ≤ 2:55 (verified with ffprobe)
- [ ] Devpost `Built With` tags match the list in field 10
- [ ] Partner track = ClickHouse selected
- [ ] Cloud-receipts screenshots embedded in SUBMISSION.md (Lane B deliverable)
