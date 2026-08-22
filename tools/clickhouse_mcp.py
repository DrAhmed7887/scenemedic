"""ClickHouse continuity — dual-mode (native + MCP toolset).

Agent Engine's serverless runtime may not have `uvx` available, so MCP
subprocess mode can fail there. This module exposes:

- `clickhouse_toolset`   — MCP-based toolset for local ADK web / dev.
- `lookup_patient_canon` — native ADK function tool, safe in Agent Engine.
- `get_continuity_tools()` — dispatcher: returns MCP tools if available,
                             else the native tool.
"""
from __future__ import annotations

import logging
import os
import shutil
from typing import Any

import clickhouse_connect

log = logging.getLogger(__name__)


def _client() -> clickhouse_connect.driver.Client:
    return clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_URL"].replace("https://", "").replace(":8443", ""),
        port=8443,
        username=os.environ["CLICKHOUSE_USER"],
        password=os.environ["CLICKHOUSE_PASSWORD"],
        database=os.getenv("CLICKHOUSE_DATABASE", "scenemedic"),
        secure=True,
    )


def lookup_patient_canon(patient_name: str) -> dict[str, Any]:
    """Return canonical clinical state for a recurring character.

    Returns {"found": bool, "name": str, "age": int, "sex": str,
    "diagnoses": [str], "medications": [str], "last_labs": {str: str},
    "notes": str}.
    """
    empty: dict[str, Any] = {
        "found": False,
        "name": patient_name,
        "age": 0,
        "sex": "",
        "diagnoses": [],
        "medications": [],
        "last_labs": {},
        "notes": "",
    }
    q = """
    SELECT name, age, sex, diagnoses, medications, last_labs, notes
    FROM patient_canon
    WHERE lower(name) = lower(%(name)s)
    LIMIT 1
    """
    try:
        res = _client().query(q, parameters={"name": patient_name})
        if not res.result_rows:
            return empty
        row = res.result_rows[0]
        return {
            "found": True,
            "name": row[0],
            "age": row[1],
            "sex": row[2],
            "diagnoses": list(row[3]),
            "medications": list(row[4]),
            "last_labs": dict(row[5]),
            "notes": row[6],
        }
    except Exception as e:
        log.warning("clickhouse lookup failed: %s", e)
        return {**empty, "error": str(e)}


def _mcp_available() -> bool:
    return shutil.which("uvx") is not None and os.getenv("SCENEMEDIC_USE_MCP") == "1"


def get_continuity_tools() -> list:
    """Return the best-available continuity toolset for this runtime."""
    if _mcp_available():
        try:
            from google.adk.tools.mcp_tool import MCPToolset, StdioServerParameters

            toolset = MCPToolset(
                connection_params=StdioServerParameters(
                    command="uvx",
                    args=["mcp-clickhouse"],
                    env={
                        "CLICKHOUSE_HOST": os.getenv("CLICKHOUSE_URL", ""),
                        "CLICKHOUSE_USER": os.getenv("CLICKHOUSE_USER", ""),
                        "CLICKHOUSE_PASSWORD": os.getenv("CLICKHOUSE_PASSWORD", ""),
                        "CLICKHOUSE_DATABASE": os.getenv("CLICKHOUSE_DATABASE", "scenemedic"),
                    },
                ),
            )
            return list(toolset.get_tools())
        except Exception as e:
            log.warning("MCP toolset init failed, falling back to native: %s", e)
    return [lookup_patient_canon]
