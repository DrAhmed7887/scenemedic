"""On-set prop generator via Vertex `gemini-2.5-flash-image` (nano-banana).

The `imagen-3.0-*` model endpoints require per-project allowlisting; the
Gemini 2.5 Flash Image model is broadly available under the GenAI App
Builder credit and is what we ship the demo on.
"""
from __future__ import annotations

import os
from pathlib import Path

from google import genai
from google.genai import types

_c = genai.Client(
    vertexai=True,
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
)
_MODEL = os.getenv("IMAGE_MODEL", "gemini-2.5-flash-image")


def generate_prop(prompt: str, save_to: str | None = None) -> bytes:
    """Generate a photorealistic on-set prop image.

    If `save_to` is provided, writes the PNG to that path and also returns
    the bytes. Otherwise returns bytes only.
    """
    resp = _c.models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]),
    )
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None):
            data = part.inline_data.data
            if save_to:
                Path(save_to).parent.mkdir(parents=True, exist_ok=True)
                Path(save_to).write_bytes(data)
            return data
    raise RuntimeError("no image part returned from model")
