"""Deploy the SceneMedic orchestrator to Vertex AI Agent Engine.

Prereq (one-time):
  gsutil mb -p scenemedic-hackathon -l us-central1 gs://scenemedic-staging-hackathon

Prereq env vars (baked into the deployed runtime):
  GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION,
  BQ_CORPUS_DATASET, BQ_CORPUS_TABLE,
  (optional) CLICKHOUSE_URL/USER/PASSWORD/DATABASE.
"""
from __future__ import annotations

import os

import vertexai
from vertexai import agent_engines

from agents.orchestrator import root_agent


REQUIREMENTS = [
    "google-cloud-aiplatform[agent_engines,adk]>=1.101.0",
    "google-genai>=1.0",
    "google-cloud-bigquery>=3.25.0",
    "google-cloud-documentai>=2.29.0",
    "clickhouse-connect>=0.7.0",
    "python-dotenv>=1.0",
    "requests>=2.31",
    "pypdf>=4.2",
    "pydantic>=2.7",
]


def main() -> None:
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    staging = os.getenv("GCS_STAGING_BUCKET", f"gs://scenemedic-staging-hackathon")

    vertexai.init(project=project, location=location, staging_bucket=staging)

    env_vars = {
        "GOOGLE_CLOUD_PROJECT": project,
        "GOOGLE_CLOUD_LOCATION": location,
        "BQ_CORPUS_DATASET": os.getenv("BQ_CORPUS_DATASET", "scenemedic"),
        "BQ_CORPUS_TABLE": os.getenv("BQ_CORPUS_TABLE", "pubmed_chunks"),
    }
    for k in ("CLICKHOUSE_URL", "CLICKHOUSE_USER", "CLICKHOUSE_PASSWORD",
              "CLICKHOUSE_DATABASE"):
        if os.getenv(k):
            env_vars[k] = os.environ[k]

    remote = agent_engines.create(
        agent_engine=root_agent,
        requirements=REQUIREMENTS,
        display_name="SceneMedic",
        env_vars=env_vars,
        runtime_python_version="3.12",
    )
    print("Deployed:", remote.resource_name)
    print("Env vars set:", list(env_vars.keys()))


if __name__ == "__main__":
    main()
