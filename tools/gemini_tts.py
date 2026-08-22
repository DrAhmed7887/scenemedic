"""Multi-speaker table read via Gemini TTS on Vertex."""
from __future__ import annotations

import os

from google import genai
from google.genai import types

_c = genai.Client(
    vertexai=True,
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
)


def multi_speaker_read(script: list[dict]) -> bytes:
    """Render a multi-speaker read on Vertex.

    script = [{"speaker": "Attending", "voice": "Kore", "text": "..."}, ...]
    Returns raw PCM (audio/L16 24 kHz) bytes.
    """
    cfg = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker=s["speaker"],
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=s["voice"]
                            )
                        ),
                    )
                    for s in script
                ]
            )
        ),
    )
    turns = "\n".join(f'{s["speaker"]}: {s["text"]}' for s in script)
    resp = _c.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=turns,
        config=cfg,
    )
    return resp.candidates[0].content.parts[0].inline_data.data
