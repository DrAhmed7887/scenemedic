"""Callable orchestrator for in-process Streamlit use.

Mirrors the ADK graph but runs synchronously so the UI can drive it
without spinning up an Agent Engine session. When we deploy to Agent
Engine, ui/app.py switches to hitting the remote endpoint instead.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_ROOT / ".env")
os.environ.pop("GEMINI_API_KEY", None)

from google import genai
from google.genai import types

from tools.clickhouse_mcp import lookup_patient_canon
from tools.rag_pubmed import search_pubmed

_client = genai.Client(
    vertexai=True,
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
)


@dataclass(frozen=True)
class RealismReport:
    script: str
    snippets: list[dict] = field(default_factory=list)
    continuity: list[dict] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)
    rewrites: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "script": self.script,
            "rag_snippets": self.snippets,
            "continuity": self.continuity,
            "findings": self.findings,
            "rewrites": self.rewrites,
        }


_DEFAULT_QUERIES = [
    "epinephrine for stable narrow complex tachycardia",
    "biphasic defibrillation energy VF",
    "post-ROSC extubation timing targeted temperature management",
    "adenosine dose narrow complex tachycardia",
    "ACLS cardiac arrest algorithm",
]

_CLINICAL_PROMPT = """\
You are SceneMedic's Clinical Accuracy Agent — a board-certified emergency
physician reviewing a medical drama script for realism.

Task: For each medically inaccurate BEAT in the scene, output a JSON object with:
  scene_id, line_no, severity (INFO|WARN|CRITICAL),
  original (the exact wrong line),
  issue (concise explanation),
  citation_title (from retrieved snippets — must be one of them),
  citation_url (from retrieved snippets — must be one of them).

Rules:
  - Cite ONLY the retrieved snippets. Never invent citations.
  - Return ONLY a JSON array of findings, no prose.
"""

_DRAMATIZATION_PROMPT = """\
You are SceneMedic's Dramatization Agent. For each CRITICAL and WARN finding,
propose 2–3 alternate lines that (a) fix the clinical issue, (b) preserve the
character's voice and the dramatic beat, (c) match original length within +/- 30%.

Return ONLY a JSON array of {scene_id, line_no, original, alternates: [str]}.
"""


def _rag_context(queries: list[str], k: int = 3) -> list[dict]:
    seen: dict[str, dict] = {}
    for q in queries:
        for h in search_pubmed(q, k=k):
            if h["url"] not in seen:
                seen[h["url"]] = h
    return list(seen.values())


def _generate_json(prompt: str, temperature: float = 0.0) -> list[dict]:
    resp = _client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=temperature,
        ),
    )
    return json.loads(resp.text)


def _continuity_scan(script: str) -> list[dict]:
    """Simple name-based canon check. Returns list of contradictions."""
    out: list[dict] = []
    script_lc = script.lower()
    for candidate in ("Maya Chen", "Marcus Bell", "Priya Rao"):
        if candidate.lower() in script_lc:
            canon = lookup_patient_canon(candidate)
            if canon.get("found"):
                out.append(
                    {
                        "patient": candidate,
                        "canon": {
                            "diagnoses": canon["diagnoses"],
                            "medications": canon["medications"],
                            "last_labs": canon["last_labs"],
                        },
                        "notes": canon.get("notes", ""),
                    }
                )
    return out


def run(script: str, queries: list[str] | None = None) -> RealismReport:
    """Full pipeline: continuity + RAG → Clinical → Dramatization."""
    queries = queries or _DEFAULT_QUERIES

    snippets = _rag_context(queries, k=3)
    continuity = _continuity_scan(script)

    ctx = "\n\n".join(
        f"[{i+1}] {s['title']}\n{s['snippet']}\nurl: {s['url']}"
        for i, s in enumerate(snippets)
    )
    findings = _generate_json(
        f"{_CLINICAL_PROMPT}\n=== SCENE ===\n{script}"
        f"\n\n=== GROUNDED SNIPPETS ===\n{ctx}"
    )
    rewrites = _generate_json(
        f"{_DRAMATIZATION_PROMPT}\n=== SCENE ===\n{script}"
        f"\n\n=== FINDINGS ===\n{json.dumps(findings, indent=2)}",
        temperature=0.5,
    )
    return RealismReport(
        script=script,
        snippets=snippets,
        continuity=continuity,
        findings=findings,
        rewrites=rewrites,
    )
