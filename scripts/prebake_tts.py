"""Pre-bake the multi-speaker table read of the CORRECTED Act 2 dialogue."""
from __future__ import annotations

import os
import struct
import wave
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
os.environ.pop("GEMINI_API_KEY", None)

from google import genai
from google.genai import types

client = genai.Client(
    vertexai=True,
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
)


SCRIPT = """\
Elena: Vagal first. Get me adenosine and pads.
Raj: Adenosine is up. Six milligrams, I V push, flush behind it.
Elena: Two hundred biphasic. Clear!
Elena: She's back. Keep her tubed. Call the unit. T T M protocol, thirty-six degrees.
"""


def save_wav(pcm_bytes: bytes, path: Path, rate: int = 24000) -> None:
    """Wrap raw PCM (16-bit mono) into a WAV file."""
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm_bytes)


def main() -> None:
    cfg = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Elena",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                        ),
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Raj",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                        ),
                    ),
                ]
            )
        ),
    )

    r = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=SCRIPT,
        config=cfg,
    )

    for part in r.candidates[0].content.parts:
        if getattr(part, "inline_data", None):
            data = part.inline_data.data
            mime = part.inline_data.mime_type or ""
            out = ROOT / "assets" / "fallback_read.wav"
            if "wav" in mime or data[:4] == b"RIFF":
                out.write_bytes(data)
            else:
                # raw PCM — wrap it
                save_wav(data, out)
            print(f"OK: {len(data)} bytes (mime={mime}) -> {out}")
            return
    raise RuntimeError("no audio in TTS response")


if __name__ == "__main__":
    main()
    from tools.cost_check import log_cost

    log_cost(
        "gemini_tts_table_read",
        "gemini-2.5-flash-preview-tts",
        "generate_content:AUDIO",
        expected_usd=0.02,
        credit_expected="GenAI App Builder trial",
        status="ok" if (ROOT / "assets" / "fallback_read.wav").exists() else "error",
        note="Corrected Act 2 multi-speaker read (Elena/Raj) for demo failover",
    )
