"""Multi-speaker table read via Gemini TTS."""
from google.genai import Client

_c = Client()


def multi_speaker_read(script: list[dict]) -> bytes:
    """Render a multi-speaker read.

    script = [{"speaker": "Attending", "voice": "Kore", "text": "..."}, ...]
    """
    cfg = {
        "response_modalities": ["AUDIO"],
        "speech_config": {
            "multi_speaker_voice_config": {
                "speaker_voice_configs": [
                    {
                        "speaker": s["speaker"],
                        "voice_config": {
                            "prebuilt_voice_config": {"voice_name": s["voice"]}
                        },
                    }
                    for s in script
                ]
            }
        },
    }
    turns = "\n".join(f'{s["speaker"]}: {s["text"]}' for s in script)
    resp = _c.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=turns,
        config=cfg,
    )
    return resp.candidates[0].content.parts[0].inline_data.data  # type: ignore[attr-defined]
