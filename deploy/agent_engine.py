"""Deploy the SceneMedic orchestrator to Vertex AI Agent Engine.

Prereqs (one-time):
  gsutil mb -p scenemedic-hackathon -l us-central1 gs://scenemedic-staging-hackathon
  # grant compute SA the roles it needs at runtime:
  SA=159973996965-compute@developer.gserviceaccount.com
  PROJECT=scenemedic-hackathon
  BUCKET=gs://scenemedic-staging-hackathon
  gsutil iam ch serviceAccount:$SA:roles/storage.objectAdmin $BUCKET
  for R in roles/bigquery.user roles/bigquery.dataViewer roles/aiplatform.user; do
    gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$SA" --role=$R --condition=None
  done

Required env vars (loaded from local .env, then forwarded to the runtime):
  GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION,
  BQ_CORPUS_DATASET, BQ_CORPUS_TABLE, GCS_STAGING_BUCKET
Optional:
  CLICKHOUSE_URL/USER/PASSWORD/DATABASE
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

import vertexai
from vertexai import agent_engines


REQUIREMENTS = [
    "google-cloud-aiplatform[agent_engines,adk]>=1.101.0",
    "google-genai>=1.0.0",
    "google-cloud-bigquery>=3.25.0",
    "google-cloud-documentai>=2.29.0",
    "google-auth>=2.29",
    "clickhouse-connect>=0.7.0",
    "requests>=2.31",
    "pypdf>=4.2",
    "pydantic>=2.7",
]

REQUIRED = ("GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION", "GCS_STAGING_BUCKET")


def _validate_env() -> dict[str, str]:
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        print(f"ERROR: missing required env vars: {', '.join(missing)}", file=sys.stderr)
        print("Set them in .env or export before running.", file=sys.stderr)
        sys.exit(2)
    return {k: os.environ[k] for k in REQUIRED}


def main() -> None:
    env = _validate_env()
    project = env["GOOGLE_CLOUD_PROJECT"]
    location = env["GOOGLE_CLOUD_LOCATION"]
    staging = env["GCS_STAGING_BUCKET"]

    # Import after env validation so a missing env var doesn't blow up
    # at import time with an unfriendly KeyError.
    from agents.orchestrator import root_agent

    vertexai.init(project=project, location=location, staging_bucket=staging)

    env_vars: dict[str, str] = {
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
        extra_packages=["./agents", "./tools"],
    )
    print("Deployed:", remote.resource_name)
    print("Env vars set:", sorted(env_vars.keys()))


if __name__ == "__main__":
    main()
