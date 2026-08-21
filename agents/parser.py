"""Script Parser Agent — ingests PDF/Fountain and returns scene manifest."""
from google.adk.agents import Agent

from tools.document_ai import parse_script

parser_agent = Agent(
    name="script_parser",
    model="gemini-2.5-flash",
    description="Parses a submitted script into scenes, characters, and dialogue.",
    instruction=(
        "Use parse_script to extract the raw structure, then normalize each "
        "scene into {scene_id, location, time, characters[], beats[]}. Tag "
        "medical beats (procedures, drug names, vitals, diagnoses) with "
        "beat.kind='medical'."
    ),
    tools=[parse_script],
)
