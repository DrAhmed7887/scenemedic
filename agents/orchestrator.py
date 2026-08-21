"""SceneMedic root orchestrator agent."""
from google.adk.agents import Agent

from .clinical import clinical_agent
from .continuity import continuity_agent
from .dramatization import dramatization_agent
from .parser import parser_agent
from .vfx import vfx_agent
from .audio import audio_agent

INSTRUCTION = """You are SceneMedic, a physician-grade technical advisor for
medical TV and film. Given a script, coordinate sub-agents to:
  1. Parse the script into scene/character/dialogue structure.
  2. Load continuity canon from ClickHouse.
  3. Audit clinical realism against grounded sources.
  4. Propose voice-preserving dramatized rewrites for each flag.
  5. Generate matching visual props via Imagen 3.
  6. Generate ambient beds and a multi-speaker table read.
  7. Return a single Realism Report bundle.

Rules:
  - Never invent citations. Only cite what the RAG tool returned.
  - If clinically uncertain, flag WARN with the source of doubt.
  - Never produce real medical advice framing; outputs are fictional scene assets.
"""

root_agent = Agent(
    name="scenemedic_orchestrator",
    model="gemini-2.5-pro",
    description="Runs a clinical-realism audit + GenMedia bundle on a submitted script.",
    instruction=INSTRUCTION,
    sub_agents=[
        parser_agent,
        continuity_agent,
        clinical_agent,
        dramatization_agent,
        vfx_agent,
        audio_agent,
    ],
)
