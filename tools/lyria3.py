"""Lyria 3 ambient bed generator."""
from vertexai.preview.generative_models import GenerativeModel

_lyria = GenerativeModel("lyria-3")

MOOD_PROMPTS = {
    "icu_quiet": "sparse cinematic ambient, low drone, occasional monitor pulse, "
                  "no melody, tense but calm hospital nightshift",
    "code_blue": "high-tension cinematic score, driving low strings, urgent "
                  "percussive pulses, medical emergency",
    "family_meeting": "warm quiet piano bed, sustained strings, hopeful but "
                       "restrained, hospital chapel",
    "or_procedure": "hushed procedural score, low synth pad, ticking rhythmic "
                     "element, surgical focus",
}


def generate_bed(mood: str, duration_s: int = 30) -> bytes:
    """Return audio bytes for an ambient bed keyed by mood label."""
    prompt = MOOD_PROMPTS.get(mood, mood)
    resp = _lyria.generate_content(
        {"prompt": prompt, "duration_seconds": duration_s,
         "genre": "cinematic_ambient"}
    )
    return resp.audio_bytes  # type: ignore[attr-defined]
