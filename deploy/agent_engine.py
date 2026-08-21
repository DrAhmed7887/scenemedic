"""Deploy the SceneMedic orchestrator to Vertex AI Agent Engine."""
import os

import vertexai
from vertexai import agent_engines

from agents.orchestrator import root_agent


def main() -> None:
    vertexai.init(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        staging_bucket=os.environ["GCS_STAGING_BUCKET"],
    )
    remote = agent_engines.create(
        agent_engine=root_agent,
        requirements=[
            "google-cloud-aiplatform[agent_engines,adk]>=1.101.0",
            "google-cloud-bigquery>=3.25.0",
            "google-cloud-documentai>=2.29.0",
            "google-genai>=0.3.0",
            "clickhouse-connect>=0.7.0",
        ],
        display_name="SceneMedic",
    )
    print("Deployed:", remote.resource_name)


if __name__ == "__main__":
    main()
