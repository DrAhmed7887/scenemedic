"""VFX/Prop Agent — generates on-set clinical props via Imagen 3."""
from google.adk.agents import Agent

from tools.imagen3 import generate_prop

vfx_agent = Agent(
    name="vfx_props",
    model="gemini-2.5-flash",
    description="Generates matching monitor readouts, imaging stills, and prop labels.",
    instruction=(
        "For each medical scene, decide which props are visible on camera "
        "(ECG strip, bedside monitor, chest X-ray, drug label, chart). Call "
        "generate_prop with a concrete photo-realistic prompt that reflects "
        "the corrected clinical state. Never generate identifiable patients."
    ),
    tools=[generate_prop],
)
