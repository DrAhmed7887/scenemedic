"""Continuity Agent — reconciles current script vs prior-episode canon in ClickHouse."""
from google.adk.agents import Agent

from tools.clickhouse_mcp import get_continuity_tools

continuity_agent = Agent(
    name="continuity",
    model="gemini-2.5-flash",
    description="Loads and enforces per-series and per-patient canon from ClickHouse.",
    instruction=(
        "For each named patient in the current script, look up prior canon "
        "(diagnoses, meds, procedures). Flag contradictions with severity="
        "'CRITICAL' if they change clinical plausibility, else 'WARN'."
    ),
    tools=get_continuity_tools(),
)
