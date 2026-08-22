"""End-to-end demo: parse the demo scene → RAG → Clinical → Dramatization.

This is the pipeline the ADK orchestrator will run in the deployed
Agent Engine build. Running it directly here proves the components
work in sequence and produces a concrete Realism Report the UI can
display.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
os.environ.pop("GEMINI_API_KEY", None)

from google import genai
from google.genai import types

from tools.rag_pubmed import search_pubmed

client = genai.Client(
    vertexai=True,
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
)


SCRIPT = (ROOT / "corpus" / "demo_scene.txt").read_text()

CLINICAL_PROMPT = """\
You are SceneMedic's Clinical Accuracy Agent — a board-certified emergency
physician reviewing a medical drama script for realism. Below is:
(A) The scene.
(B) Grounded guideline snippets retrieved from a curated PubMed / ACLS / ATLS
    corpus. Use ONLY these for citations. Do not invent citation URLs.

Task:
For each medically inaccurate BEAT, output a JSON object with:
  scene_id, line_no (approximate line in scene), severity (INFO|WARN|CRITICAL),
  original (the exact wrong line), issue (concise explanation),
  citation_title (from retrieved snippets), citation_url (from retrieved snippets).

Return ONLY a JSON array of findings. No prose.
"""


DRAMATIZATION_PROMPT = """\
You are SceneMedic's Dramatization Agent. Below are clinical findings
against a scene, and the original scene. For each CRITICAL and WARN finding,
propose 2-3 alternate lines that:
  1. Fix the clinical issue,
  2. Preserve the character's voice and the dramatic beat,
  3. Match the original line length within +/- 30%.

Return ONLY a JSON array of {scene_id, line_no, original, alternates: [str]}.
"""


def rag_context(queries: list[str], k: int = 3) -> list[dict]:
    seen: dict[str, dict] = {}
    for q in queries:
        for h in search_pubmed(q, k=k):
            if h["url"] not in seen:
                seen[h["url"]] = h
    return list(seen.values())


def clinical_findings(scene: str, snippets: list[dict]) -> list[dict]:
    context = "\n\n".join(
        f"[{i+1}] {s['title']}\n{s['snippet']}\nurl: {s['url']}"
        for i, s in enumerate(snippets)
    )
    resp = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=(
            f"{CLINICAL_PROMPT}\n\n=== SCENE ===\n{scene}"
            f"\n\n=== GROUNDED SNIPPETS ===\n{context}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
        ),
    )
    return json.loads(resp.text)


def dramatize(scene: str, findings: list[dict]) -> list[dict]:
    resp = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=(
            f"{DRAMATIZATION_PROMPT}\n\n=== SCENE ===\n{scene}"
            f"\n\n=== FINDINGS ===\n{json.dumps(findings, indent=2)}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.5,
        ),
    )
    return json.loads(resp.text)


def main() -> None:
    print("=" * 60)
    print("SceneMedic — end-to-end orchestrator run")
    print("=" * 60)

    queries = [
        "epinephrine for stable narrow complex tachycardia",
        "biphasic defibrillation energy VF",
        "post-ROSC extubation timing targeted temperature management",
        "adenosine dose narrow complex tachycardia",
        "ACLS cardiac arrest algorithm",
    ]
    print(f"\n[1/3] retrieving RAG context ({len(queries)} queries)...")
    snippets = rag_context(queries, k=3)
    print(f"  -> {len(snippets)} unique guideline snippets")

    print("\n[2/3] running Clinical Accuracy Agent (gemini-2.5-pro)...")
    findings = clinical_findings(SCRIPT, snippets)
    print(f"  -> {len(findings)} findings")
    for f in findings:
        print(f"  [{f.get('severity','?')}] L{f.get('line_no','?')}: "
              f"{f.get('original','')[:70]}")

    print("\n[3/3] running Dramatization Agent (gemini-2.5-pro)...")
    rewrites = dramatize(SCRIPT, findings)
    print(f"  -> {len(rewrites)} rewrite bundles")

    report = {
        "script": SCRIPT,
        "rag_snippets": snippets,
        "findings": findings,
        "rewrites": rewrites,
    }
    out = ROOT / "outputs" / "realism_report.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
    from tools.cost_check import log_cost

    log_cost("orchestrator_rag", "gemini-embedding-001", "embed_content",
             0.0, "AI Studio free tier",
             note="5 RAG queries + 51-chunk corpus scan (BQ Always Free)")
    log_cost("orchestrator_clinical", "gemini-2.5-pro", "generate_content",
             0.02, "GenAI App Builder trial",
             note="Clinical Accuracy Agent findings")
    log_cost("orchestrator_dramatize", "gemini-2.5-pro", "generate_content",
             0.02, "GenAI App Builder trial",
             note="Dramatization Agent rewrites")
