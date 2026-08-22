"""Session-based smoke test of the deployed Agent Engine."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

import vertexai
from vertexai import agent_engines

RN = os.getenv(
    "AGENT_ENGINE_RESOURCE",
    "projects/159973996965/locations/us-central1/reasoningEngines/5192502486044246016",
)


def main() -> None:
    vertexai.init(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )
    engine = agent_engines.get(RN)

    print("=== engine callable methods ===")
    for m in sorted(dir(engine)):
        if not m.startswith("_") and callable(getattr(engine, m, None)):
            print(f"  {m}")

    print("\n=== creating session ===")
    sess = engine.create_session(user_id="hackathon-smoke")
    sid = sess.get("id")
    print(f"  session_id: {sid}")

    print("\n=== streaming query ===")
    count = 0
    for event in engine.stream_query(
        user_id="hackathon-smoke",
        session_id=sid,
        message="Reply in one sentence: what is SceneMedic?",
    ):
        count += 1
        if count <= 4:
            summary = str(event)[:220]
            print(f"  event {count}: {summary}")
    print(f"\ntotal events streamed: {count}")

    engine.delete_session(user_id="hackathon-smoke", session_id=sid)
    print("session cleaned up")


if __name__ == "__main__":
    main()
