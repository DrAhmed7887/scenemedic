"""Audio Agent — ambient beds (Lyria 3) + multi-speaker table read (Gemini TTS)."""
from google.adk.agents import Agent

from tools.lyria3 import generate_bed
from tools.gemini_tts import multi_speaker_read

audio_agent = Agent(
    name="audio",
    model="gemini-2.5-flash",
    description="Generates ambient scene beds and a multi-speaker table read.",
    instruction=(
        "For each scene: (1) call generate_bed with a mood label matching "
        "scene tone (icu_quiet | code_blue | family_meeting | or_procedure). "
        "(2) After dramatization returns alternates, run multi_speaker_read "
        "on the revised dialogue with distinct voices per character."
    ),
    tools=[generate_bed, multi_speaker_read],
)
