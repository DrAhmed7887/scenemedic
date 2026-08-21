# SceneMedic

Physician-built multi-agent technical advisor for medical TV/film. Ingests a script and returns a clinical-realism audit, dramatized rewrites, matching Imagen 3 props (ECGs, monitors, X-rays), Lyria 3 ambient beds, and a Gemini TTS multi-speaker table read.

Built for **Agentic Cinema — AI Agent Hackathon**.

## Stack

- **Reasoning:** Gemini 2.5 Pro via Google ADK
- **Hosting:** Vertex AI Agent Engine
- **Partner (MCP):** ClickHouse — episode continuity DB
- **Partner (obs):** Grafana Cloud — latency + tool-call traces
- **Grounding:** BigQuery Vector Search over curated PubMed/guideline corpus
- **Parsing:** Document AI (PDF / Fountain)
- **GenMedia:** Imagen 3 (props), Lyria 3 (audio beds), Gemini TTS (table read)
- **UI:** Streamlit on Cloud Run
- **Secrets:** Google Secret Manager

## Quickstart

```bash
# 1. Clone
git clone git@github.com:DrAhmed7887/scenemedic.git
cd scenemedic

# 2. Env
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # then fill values

# 3. GCP auth
gcloud auth application-default login
gcloud config set project $GOOGLE_CLOUD_PROJECT

# 4. Run locally
adk web agents/orchestrator.py

# 5. Deploy to Agent Engine
python deploy/agent_engine.py
```

## Layout

```
scenemedic/
├── agents/          # ADK sub-agents (orchestrator + specialists)
├── tools/           # Function-call tools (RAG, ClickHouse MCP, Imagen 3, Lyria 3, TTS)
├── deploy/          # Agent Engine deploy script + Cloud Run Dockerfile
├── corpus/          # Ingestion scripts for BigQuery Vector Search corpus
├── ui/              # Streamlit demo app
├── tests/           # Pytest suite
├── .env.example
├── pyproject.toml
└── README.md
```

## Environment variables

See `.env.example`. Required: `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `CLICKHOUSE_URL`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`, `BQ_CORPUS_TABLE`.

## Roadmap

72-hour hackathon sprint tracked in `../strategy.md`. Stretch: Gemini Live API rehearsal mode; Forensica sub-agent for crime-drama realism.

## License

MIT. Not medical advice. No PHI ever committed.
