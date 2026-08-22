"""On-set prop generator via Vertex `gemini-2.5-flash-image` (nano-banana)."""
from __future__ import annotations

import os

from google import genai
from google.genai import types

from tools._artifact import ArtifactEnvelope, to_envelope

_MODEL = os.getenv("IMAGE_MODEL", "gemini-2.5-flash-image")
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Lazy singleton so import doesn't require env vars."""
    global _client
    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
    return _client


def generate_prop(prompt: str) -> ArtifactEnvelope:
    """Generate a photorealistic on-set prop image.

    Returns an ADK-serializable envelope: {mime_type, base64, size_bytes}.
    """
    resp = _get_client().models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]),
    )
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None):
            return to_envelope(
                data=part.inline_data.data,
                mime_type=part.inline_data.mime_type or "image/png",
            )
    raise RuntimeError("no image part returned from model")
