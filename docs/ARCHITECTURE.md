# SceneMedic — Architecture

```mermaid
flowchart TB
    subgraph Client["Client / Writers' Room UI"]
        UI[Streamlit on Cloud Run<br/>Upload PDF/Fountain]
    end

    subgraph AgentEngine["Vertex AI Agent Engine (ADK)"]
        ORCH[Orchestrator<br/>Gemini 2.5 Pro]

        subgraph Ingest["Ingestion"]
            PARSE[Script Parser<br/>Document AI]
        end

        subgraph Reason["Clinical Reasoning"]
            CLIN[Clinical Accuracy<br/>RAG grounded]
            CONT[Continuity<br/>MCP -> ClickHouse]
            DRAM[Dramatization<br/>Voice-preserving rewrites]
        end

        subgraph Media["GenMedia"]
            VFX[VFX/Props<br/>Imagen 3]
            SND[Foley + Score<br/>Lyria 3]
            TTS[Table Read<br/>Gemini TTS multi-speaker]
        end

        LIVE[Rehearsal<br/>Gemini Live API - stretch]
    end

    subgraph Data["Grounding + State"]
        BQ[(BigQuery Vector Search<br/>PubMed + Guidelines)]
        CH[(ClickHouse<br/>Episode canon)]
        SM[Secret Manager]
    end

    OBS[Grafana Cloud<br/>latency + tool traces]

    UI --> ORCH
    ORCH --> PARSE --> CONT --> CLIN --> DRAM
    CLIN --> BQ
    CONT -.MCP.-> CH
    DRAM --> VFX
    DRAM --> SND
    DRAM --> TTS
    ORCH -.stretch.-> LIVE
    AgentEngine --> OBS
    AgentEngine --> SM
    ORCH --> UI
```

## Layers

| Layer | Component | Tech |
|---|---|---|
| UI | Uploader + Realism Report viewer | Streamlit on Cloud Run |
| Orchestration | Root agent + 6 sub-agents | Google ADK, Gemini 2.5 Pro |
| Hosting | Serverless agent runtime | Vertex AI Agent Engine |
| Grounding | Semantic search over clinical corpus | BigQuery Vector Search + `text-embedding-004` |
| State | Per-series/per-patient canon | ClickHouse via MCP toolset |
| GenMedia | Props, ambient audio, table read | Imagen 3, Lyria 3, Gemini TTS |
| Observability | Latency + tool-call traces | Grafana Cloud |
| Secrets | Runtime keys | Google Secret Manager |

## Data flow (Hero journey)

1. Writer uploads `Ep07.pdf` → Cloud Run.
2. UI calls Agent Engine endpoint with a GCS URI.
3. Parser Agent → Document AI → scene manifest.
4. Continuity Agent → ClickHouse (via MCP) → prior canon.
5. Clinical Agent → BigQuery RAG → findings JSON.
6. Dramatization Agent → alternate lines JSON.
7. VFX Agent → Imagen 3 → prop GCS URIs.
8. Audio Agent → Lyria 3 beds + Gemini TTS table read.
9. Orchestrator assembles Realism Report bundle.
10. (Stretch) Actor launches Live API rehearsal on-scene.
