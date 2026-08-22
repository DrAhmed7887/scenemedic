"""Multi-speaker table read via Gemini TTS on Vertex."""
from __future__ import annotations

import os

from google import genai
from google.genai import types

from tools._artifact import ArtifactEnvelope, to_envelope

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
    return _client


def multi_speaker_read(script: list[dict]) -> ArtifactEnvelope:
    """Render a multi-speaker read on Vertex.

    script = [{"speaker": "Attending", "voice": "Kore", "text": "..."}, ...]
    Returns ADK-serializable envelope of raw PCM (audio/L16 24 kHz).
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
    resp = _get_client().models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=turns,
        config=cfg,
    )
    inline = resp.candidates[0].content.parts[0].inline_data
    return to_envelope(
        data=inline.data,
        mime_type=inline.mime_type or "audio/L16;codec=pcm;rate=24000",
    )
