"""Shared helper: wrap raw bytes into an ADK-serializable JSON envelope.

Raw `bytes` don't survive cross-agent JSON serialization inside Vertex
Agent Engine. All GenMedia tools return this envelope instead.

For very large payloads (>4 MB Lyria WAVs), consider uploading to
GCS and returning {"gcs_uri": ...} — kept as a follow-up.
"""
from __future__ import annotations

import base64
from typing import TypedDict


class ArtifactEnvelope(TypedDict):
    mime_type: str
    base64: str
    size_bytes: int


def to_envelope(data: bytes, mime_type: str) -> ArtifactEnvelope:
    return {
        "mime_type": mime_type,
        "base64": base64.b64encode(data).decode("ascii"),
        "size_bytes": len(data),
    }


def from_envelope(env: ArtifactEnvelope) -> bytes:
    return base64.b64decode(env["base64"])
