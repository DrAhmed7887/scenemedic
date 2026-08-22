"""Deploy the SceneMedic orchestrator to Vertex AI Agent Engine.

Prereqs (one-time):
  gsutil mb -p scenemedic-hackathon -l us-central1 gs://scenemedic-staging-hackathon
  SA=159973996965-compute@developer.gserviceaccount.com
  PROJECT=scenemedic-hackathon
  BUCKET=gs://scenemedic-staging-hackathon
  gsutil iam ch serviceAccount:$SA:roles/storage.objectAdmin $BUCKET
  for R in roles/bigquery.user roles/bigquery.dataViewer roles/aiplatform.user; do
    gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$SA" --role=$R --condition=None
  done

Required env (loaded from local .env, then forwarded to the runtime):
  GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, GCS_STAGING_BUCKET
Optional:
  BQ_CORPUS_DATASET, BQ_CORPUS_TABLE
  CLICKHOUSE_URL / USER / PASSWORD / DATABASE
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[1]
load_dotenv(REPO / ".env")

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


def _source_dirs() -> list[str]:
    """Return the SOURCE directories to tar into the container.

    CRITICAL: agent_engines.create() tars extra_packages preserving the
    caller's path exactly. Passing an ABSOLUTE path (str(REPO/'tools'))
    puts /Users/…/scenemedic/tools/ inside the tar — the container
    untars into /code/Users/…/ and 'tools' is never on PYTHONPATH.

    Fix: chdir(REPO) so relative names like "agents" / "tools" become
    the tar's top-level entries, which unpack cleanly into /code/agents/
    and /code/tools/ on the container root sys.path.

    Also purge __pycache__ so we don't ship 3.14 bytecode into a 3.12
    runtime.
    """
    import shutil
    dirs = [REPO / "agents", REPO / "tools"]
    for d in dirs:
        if not (d / "__init__.py").exists():
            raise RuntimeError(f"{d} missing __init__.py — deploy would fail")
        cache = d / "__pycache__"
        if cache.exists():
            shutil.rmtree(cache)
    os.chdir(REPO)
    return ["agents", "tools"]


def main() -> None:
    env = _validate_env()
    project = env["GOOGLE_CLOUD_PROJECT"]
    location = env["GOOGLE_CLOUD_LOCATION"]
    staging = env["GCS_STAGING_BUCKET"]

    src_dirs = _source_dirs()

    # Import after env validation so the friendly error path runs
    # before any implicit import-time env access.
    from agents.orchestrator import root_agent

    vertexai.init(project=project, location=location, staging_bucket=staging)

    # GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION are RESERVED by
    # Agent Engine — the runtime injects them automatically. Passing
    # them here would raise FAILED_PRECONDITION.
    env_vars: dict[str, str] = {
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
        extra_packages=src_dirs,
    )
    print("Deployed:", remote.resource_name)
    print("Env vars set:", sorted(env_vars.keys()))


if __name__ == "__main__":
    main()
