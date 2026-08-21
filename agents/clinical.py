"""Clinical Accuracy Agent — audits medical beats against grounded sources."""
from google.adk.agents import Agent

from tools.rag_pubmed import search_pubmed

clinical_agent = Agent(
    name="clinical_accuracy",
    model="gemini-2.5-pro",
    description="Audits medical dialogue and procedure beats for clinical realism.",
    instruction=(
        "For each medical beat: identify the claim, the intervention, and the "
        "expected physiologic response. Compare against results from "
        "search_pubmed. Return findings as JSON list of "
        "{scene_id, line_no, severity in [INFO,WARN,CRITICAL], claim, "
        "issue, rationale, citation_url}. Never fabricate a citation_url."
    ),
    tools=[search_pubmed],
)
