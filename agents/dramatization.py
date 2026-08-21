"""Dramatization Agent — rewrites flagged lines while preserving voice + tension."""
from google.adk.agents import Agent

dramatization_agent = Agent(
    name="dramatization",
    model="gemini-2.5-pro",
    description="Rewrites clinically-flagged lines with voice-preserving alternates.",
    instruction=(
        "For each finding with severity in {WARN, CRITICAL}, propose 2-3 "
        "alternate lines that (a) fix the clinical issue, (b) preserve the "
        "character's voice and the scene's dramatic beat, (c) match the "
        "original line length within +/- 30%. Return "
        "{scene_id, line_no, original, alternates[]}."
    ),
)
