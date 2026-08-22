"""Lyria-002 ambient bed generator via Vertex REST :predict.

Uses Application Default Credentials (ADC) instead of `gcloud auth
print-access-token` so it works inside the Agent Engine runtime, which
has no interactive gcloud shell.
"""
from __future__ import annotations

import base64
import os

import google.auth
import google.auth.transport.requests
import requests

_PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
_LOC = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
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


def generate_bed(mood: str, seed: int = 42) -> bytes:
    """Return audio bytes (WAV) for an ambient bed keyed by mood label."""
    prompt = MOOD_PROMPTS.get(mood, mood)
    url = (
        f"https://{_LOC}-aiplatform.googleapis.com/v1/projects/{_PROJECT}"
        f"/locations/{_LOC}/publishers/google/models/{_MODEL}:predict"
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
    return base64.b64decode(b64)
