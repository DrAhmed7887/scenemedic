"""SceneMedic — Writers' Room UI (Streamlit).

Modes:
  - LIVE  → runs agents.live.run() against the demo scene or uploaded script.
  - CANNED DEMO → shows pre-computed findings for stage safety.

Layout: three panels — script + findings, prop gallery, audio bench.
"""
from __future__ import annotations

import io
import json
import time
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parents[1]
DEMO_SCENE = REPO / "corpus" / "demo_scene.txt"
CACHED_REPORT = REPO / "outputs" / "realism_report.json"
ASSETS = REPO / "assets"

SEVERITY_COLOR = {"CRITICAL": "#dc2626", "WARN": "#f59e0b", "INFO": "#2563eb"}


st.set_page_config(page_title="SceneMedic", layout="wide", page_icon="🩺")
st.markdown(
    """
    <style>
      .block-container {padding-top: 1.2rem;}
      .finding {padding: 0.6rem 0.8rem; border-radius: 6px;
                border-left: 4px solid; margin-bottom: 0.5rem;
                background: #0b1220; color: #e5e7eb; font-size: 0.92rem;}
      .badge {display:inline-block; padding: 0.1rem 0.5rem; border-radius: 4px;
              font-size: 0.72rem; font-weight: 700; margin-right: 0.4rem;}
      h1, h2, h3 {letter-spacing: -0.02em;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("SceneMedic")
st.caption(
    "Physician-built multi-agent technical advisor for medical film & TV. "
    "Upload a script → get a clinical-realism audit, dramatized rewrites, "
    "matching props, and a multi-speaker table read."
)

with st.sidebar:
    st.header("Session")
    run_live = st.button("▶ Run LIVE orchestrator", type="primary",
                          use_container_width=True)
    canned = st.button("▶ Play canned demo (safe)", use_container_width=True)
    st.divider()
    uploaded = st.file_uploader("Upload script (TXT / Fountain / PDF)",
                                 type=["txt", "fountain", "md", "pdf"])
    st.divider()
    st.markdown("**Backends**")
    st.text(f"Project: scenemedic-hackathon")
    st.text(f"Vertex:  us-central1")


def _script_text(uploaded_file) -> str:
    if uploaded_file is None:
        return DEMO_SCENE.read_text()
    if uploaded_file.type == "text/plain" or uploaded_file.name.endswith((".txt", ".fountain", ".md")):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    # PDF path — use the tool's parser
    from tools.document_ai import parse_script
    tmp = REPO / "outputs" / f"_upload_{int(time.time())}.pdf"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_bytes(uploaded_file.read())
    pages = parse_script(str(tmp))["pages"]
    return "\n\n".join(p["text"] for p in pages)


def _load_report(script: str, live: bool) -> dict | None:
    if live:
        with st.status("Running orchestrator...", expanded=True) as status:
            st.write("• Loading continuity canon (ClickHouse fallback: native)")
            st.write("• Retrieving grounded RAG context")
            st.write("• Clinical Accuracy Agent — gemini-2.5-pro")
            st.write("• Dramatization Agent — gemini-2.5-pro")
            from agents.live import run
            report = run(script)
            status.update(label="Orchestrator complete", state="complete")
        return report.to_dict()
    if CACHED_REPORT.exists():
        return json.loads(CACHED_REPORT.read_text())
    return None


col_script, col_props, col_audio = st.columns([1.15, 1, 1], gap="large")


with col_script:
    st.subheader("Script + findings")
    script_text = _script_text(uploaded)
    st.code(script_text or "Load a script or press ▶.", language="markdown")

    report: dict | None = None
    if run_live or (uploaded and not canned):
        report = _load_report(script_text, live=True)
    elif canned:
        report = _load_report(script_text, live=False)

    if report:
        st.markdown("### Clinical findings")
        for f in report.get("findings", []):
            c = SEVERITY_COLOR.get(f.get("severity", "INFO"), "#2563eb")
            st.markdown(
                f'<div class="finding" style="border-left-color:{c};">'
                f'<span class="badge" style="background:{c}; color:white;">'
                f'{f.get("severity","INFO")}</span>'
                f'<b>Line {f.get("line_no","?")}</b> — '
                f'<i>{f.get("original","")}</i><br>'
                f'{f.get("issue","")}<br>'
                f'<a href="{f.get("citation_url","#")}" target="_blank" '
                f'style="color:#93c5fd;">{f.get("citation_title","source")}</a></div>',
                unsafe_allow_html=True,
            )
            rewrites = [r for r in report.get("rewrites", [])
                        if r.get("line_no") == f.get("line_no")]
            if rewrites:
                with st.expander("Suggested rewrites"):
                    for r in rewrites:
                        for alt in r.get("alternates", []):
                            st.write(f"— {alt}")

        if report.get("continuity"):
            st.markdown("### Continuity canon")
            for c in report["continuity"]:
                st.markdown(
                    f'<div class="finding" style="border-left-color:#2563eb;">'
                    f'<b>{c["patient"]}</b> — '
                    f'{", ".join(c["canon"].get("diagnoses", []))}<br>'
                    f'<small>{c.get("notes","")}</small></div>',
                    unsafe_allow_html=True,
                )


with col_props:
    st.subheader("Prop gallery")
    if report:
        for name, caption in [
            ("fallback_ecg.png", "ECG scene — narrow-complex tachycardia @ 180"),
            ("fallback_monitor.png", "Bedside monitor — HR 182, BP 88/54, SpO₂ 91"),
            ("fallback_cxr.png", "Post-ROSC CXR — ETT visible"),
        ]:
            p = ASSETS / name
            if p.exists():
                st.image(str(p), caption=caption)
    else:
        st.info("Props render once the audit completes.")


with col_audio:
    st.subheader("Audio bench")
    if report:
        for name, label in [
            ("fallback_icu.wav", "Ambient bed — Lyria-002 (icu_quiet)"),
            ("fallback_read.wav", "Table read — Gemini TTS multi-speaker"),
        ]:
            p = ASSETS / name
            st.markdown(f"**{label}**")
            if p.exists():
                st.audio(str(p))
            else:
                st.warning(f"Missing: {name}")
    else:
        st.info("Audio renders after the rewrite is finalized.")


st.divider()
st.caption(
    "SceneMedic never produces real medical advice. All outputs are fictional "
    "scene assets. No real patient data. Built for the Agentic Cinema Hackathon."
)
