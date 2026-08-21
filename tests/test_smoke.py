"""Smoke tests — imports only. Real integration tests come with a live GCP project."""


def test_orchestrator_import() -> None:
    from agents.orchestrator import root_agent
    assert root_agent.name == "scenemedic_orchestrator"


def test_subagent_names() -> None:
    from agents.orchestrator import root_agent
    names = {a.name for a in root_agent.sub_agents}
    assert names >= {
        "script_parser",
        "continuity",
        "clinical_accuracy",
        "dramatization",
        "vfx_props",
        "audio",
    }
