# Agentic Cinema — Hackathon Resources Guide

Curated stack for building agentic workflows and movie studio tools with Gemini + Google Cloud Agent Builder.

## The Challenge

Code a functional, production-ready AI agent or multi-agent network — powered by Gemini and Google Cloud Agent Builder — that integrates a Partner Entity's product or MCP server to solve critical bottlenecks across the entertainment and media value chain (filmmakers, screenwriters, studio crews, or fans).

---

## Phase 1 — Core Frameworks & Environment

- **Managed setup**: Gemini Enterprise Agent Platform API Setup — central control panel for all Google Cloud agent configurations.
- **Low-code path**: Agent Builder Guide — playbooks, managed grounding, out-of-the-box data stores.
- **Developer SDK**: Gemini Enterprise Agent Platform SDK for Python — client library for custom agent logic, tool calls, API integrations.
- **Agent Starter Pack**: Agent Engine Getting Started — initialize the first custom agent backend.
- **Cloud access & credits**:
  - Free trial: `cloud.google.com/free`
  - $100 hackathon credits via Hackathon Credit Form (1–5 business days).

---

## Phase 2 — Action Mechanisms & Data Connectivity (GenMedia Focus)

### Script processing & document grounding
- Document & PDF Analysis — Document Processing Guide (parse PDF scripts, schedules, box office reports).
- RAG with BigQuery — Q&A over script DBs with LangChain + BigQuery Vector Search.
- Zero-config grounding — Agent Builder Data Stores Overview (Vertex AI Search data stores).

### Video analysis & VFX (multimodal storyboarding)
- Multimodal introduction — Gemini Multimodal Use Cases.
- Video transcription — Video Transcription Notebook (timestamped transcripts + speaker annotations).
- Video captioning — Video Captioning Notebook (metadata for searchable libraries).
- Visual VFX — Imagen 3 Image Generation Guide (mood boards, concept art, storyboard panels).

### Audio & speech generation (Lyria + Gemini TTS)
- Lyria 3 Music Generation Guide (soundtracks, sound effects).
- Gemini 3.1 Flash TTS Tutorial (expressive speech, multi-speaker).
- Multi-Speaker Podcast Notebook.
- Multimodal Sentiment Analysis (compare audio tone vs script text).

---

## Phase 3 — Partner Integration & Infrastructure

- IBM
- Grafana Labs
- Parallel
- ClickHouse
- Replit (with hackathon credit request form)

---

## Phase 4 — Reasoning, State, & Logic Hosting

Build natively with the Agent Development Kit (ADK) instead of external wrappers.

**Install:**
```bash
pip install "google-cloud-aiplatform[agent_engines,adk]>=1.101.0"
```

### Native ADK & Agent Engine tutorials
- Introduction to Agent Engine — Python functions as tools, wrap and serialize.
- Deploying ADK Agents to Agent Engine — serverless Vertex AI deployment.
- Live API on Agent Engine — bidirectional voice via WebSockets (e.g., interactive script rehearsal).
- Google Maps Agent Tutorial — blueprint for external tools + image/satellite APIs.
- MCP Database Toolbox — SQL grounding via Model Context Protocol.

### Agent tools & function calling
- Introduction to Function Calling.
- Forced Function Calling Guide (always-run safety checks).
- Multimodal Function Calling (trigger DB updates from visual video cues).

---

## Phase 5 — Deployment & Safety

- Agent Deployment — Agent Builder Deployment Guide (web chat or REST endpoint).
- Logic hosting — Cloud Run Quickstart (serverless custom backends, tool servers).
- Studio secrets — Secret Manager Guide (partner API keys).
- Safety & guardrails — Gemini Safety Settings (moderation filters).
