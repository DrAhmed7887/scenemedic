"""Lyria-002 ambient bed generator via Vertex REST :predict.

Uses ADC (google.auth) so it works inside Agent Engine (no gcloud shell).
Returns an ADK-serializable envelope, not raw bytes.
"""
from __future__ import annotations

import base64
import os

import google.auth
import google.auth.transport.requests
import requests

from tools._artifact import ArtifactEnvelope, to_envelope

_MODEL = os.getenv("LYRIA_MODEL", "lyria-002")

MOOD_PROMPTS = {
    "icu_quiet": (
        "sparse cinematic ambient, low drone, occasional monitor pulse, "
        "no melody, tense but calm hospital nightshift"
    ),
    "code_blue": (
        "high-tension cinematic score, driving low strings, urgent "
        "percussive pulses, medical emergency"
    ),
    "family_meeting": (
        "warm quiet piano bed, sustained strings, hopeful but restrained, "
        "hospital chapel"
    ),
    "or_procedure": (
        "hushed procedural score, low synth pad, ticking rhythmic element, "
        "surgical focus"
    ),
}


def _adc_token() -> str:
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def generate_bed(mood: str, seed: int = 42) -> ArtifactEnvelope:
    """Return an ambient bed envelope keyed by mood label."""
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    prompt = MOOD_PROMPTS.get(mood, mood)
    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}"
        f"/locations/{location}/publishers/google/models/{_MODEL}:predict"
    )
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {_adc_token()}"},
        json={
            "instances": [{"prompt": prompt}],
            "parameters": {"sample_count": 1, "seed": seed},
        },
        timeout=120,
    )
    r.raise_for_status()
    pred = r.json()["predictions"][0]
    b64 = pred.get("bytesBase64Encoded") or pred.get("audio_bytes")
    if not b64:
        raise RuntimeError(f"no audio payload; keys={list(pred.keys())}")
    data = base64.b64decode(b64)
    return to_envelope(data=data, mime_type="audio/wav")
