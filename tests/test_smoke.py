"""Smoke tests — imports + Agent Engine deploy-time schema serialization.

These run without network access. Real integration tests live in a
separate suite gated on a live GCP project.
"""
from __future__ import annotations

import inspect
import json
import os
from typing import get_type_hints

import pytest


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


def test_tool_modules_import_without_env() -> None:
    """Lazy-init clients: import must succeed even with no GCP env vars."""
    saved = {k: os.environ.pop(k, None)
             for k in ("GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION")}
    try:
        import importlib
        for mod in ("tools.rag_pubmed", "tools.imagen3",
                    "tools.gemini_tts", "tools.lyria3",
                    "tools.clickhouse_mcp", "tools.document_ai"):
            importlib.reload(importlib.import_module(mod))
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


def test_genmedia_tools_return_json_envelopes() -> None:
    """GenMedia tool signatures must return the ADK-serializable envelope,
    not raw bytes. Bytes don't survive JSON transport in Agent Engine."""
    from tools import gemini_tts, imagen3, lyria3
    from tools._artifact import ArtifactEnvelope

    for fn in (imagen3.generate_prop, lyria3.generate_bed,
               gemini_tts.multi_speaker_read):
        hints = get_type_hints(fn)
        assert hints.get("return") is ArtifactEnvelope, (
            f"{fn.__module__}.{fn.__name__} must return ArtifactEnvelope "
            f"(got {hints.get('return')})"
        )


def test_continuity_dispatcher_returns_typed_empty() -> None:
    """lookup_patient_canon must always return the same schema shape."""
    saved = os.environ.pop("CLICKHOUSE_URL", None)
    try:
        os.environ["CLICKHOUSE_URL"] = "https://invalid-host-that-cannot-resolve:8443"
        os.environ.setdefault("CLICKHOUSE_USER", "default")
        os.environ.setdefault("CLICKHOUSE_PASSWORD", "no")
        from tools.clickhouse_mcp import lookup_patient_canon

        r = lookup_patient_canon("Nobody Real")
        assert set(r.keys()) >= {
            "found", "name", "age", "sex", "diagnoses",
            "medications", "last_labs", "notes",
        }
        assert r["found"] is False
    finally:
        if saved is not None:
            os.environ["CLICKHOUSE_URL"] = saved


def test_mcp_dispatcher_forces_native_in_managed_runtime() -> None:
    """When any managed-runtime marker is set, MCP must be disabled."""
    os.environ["K_SERVICE"] = "test-agent-engine"
    try:
        from tools.clickhouse_mcp import _mcp_available
        assert _mcp_available() is False
    finally:
        os.environ.pop("K_SERVICE", None)
