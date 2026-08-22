"""Pre-bake the Lyria ambient bed fallback asset."""
from __future__ import annotations

import base64
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
os.environ.pop("GEMINI_API_KEY", None)

import requests

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOC = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


def main() -> None:
    token = subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()

    prompt = (
        "sparse cinematic ambient bed, low drone, occasional monitor pulse, "
        "no melody, tense but calm hospital ICU nightshift"
    )
    out = ROOT / "assets" / "fallback_icu.wav"

    for model in ["lyria-002", "lyria-preview-001", "lyria-realtime-exp"]:
        url = (
            f"https://{LOC}-aiplatform.googleapis.com/v1/projects/{PROJECT}"
            f"/locations/{LOC}/publishers/google/models/{model}:predict"
        )
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json={
                "instances": [{"prompt": prompt}],
                "parameters": {"sample_count": 1, "seed": 42},
            },
            timeout=120,
        )
        if r.status_code == 200:
            pred = r.json().get("predictions", [{}])[0]
            b64 = pred.get("bytesBase64Encoded") or pred.get("audio_bytes")
            if b64:
                data = base64.b64decode(b64)
                out.write_bytes(data)
                print(f"OK  {model}: {len(data)} bytes -> {out}")
                return
            print(f"ERR {model}: 200 but no audio payload: keys={list(pred.keys())}")
        else:
            print(f"ERR {model}: {r.status_code} {r.text[:200]}")

    print("Lyria unavailable — will need to fall back to a CC0 stock ambient WAV.")


if __name__ == "__main__":
    main()
    from tools.cost_check import log_cost

    log_cost(
        "lyria_icu_bed",
        "lyria-002",
        ":predict",
        expected_usd=0.06,
        credit_expected="GenAI App Builder trial",
        status="ok" if (ROOT / "assets" / "fallback_icu.wav").exists() else "error",
        note="30s ICU ambient bed for demo failover",
    )
