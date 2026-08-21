"""SceneMedic — Writers' Room UI (Streamlit).

Three panels:
  1. Script + inline findings (color-coded severity).
  2. Prop gallery (Imagen 3 ECG / monitor / imaging).
  3. Audio bench (Lyria 3 ambient bed + Gemini TTS multi-speaker read).

One-click "Play canned demo" loads the pre-baked bad ER scene so a live
network hiccup never kills the pitch.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parents[1]
DEMO_SCENE = REPO / "corpus" / "demo_scene.txt"
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
    demo = st.button("▶ Play canned demo", type="primary", use_container_width=True)
    st.divider()
    uploaded = st.file_uploader("Upload script (PDF or TXT)", type=["pdf", "txt"])
    st.divider()
    st.markdown("**Backends**")
    st.text(f"Agent Engine: {'✓' if False else 'not connected'}")
    st.text(f"ClickHouse:   {'✓' if False else 'not connected'}")


def _demo_findings() -> list[dict]:
    return [
        {
            "scene_id": "S12",
            "line_no": 112,
            "severity": "CRITICAL",
            "original": "Push one of epi, IV. Now.",
            "issue": "Epinephrine is not indicated for stable narrow-complex "
                     "tachycardia. First-line is vagal maneuvers, then adenosine "
                     "6 mg IV push. Epinephrine is for arrest or refractory "
                     "bradycardia.",
            "citation": "AHA 2020 ACLS Adult Tachycardia Algorithm",
            "citation_url": "https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines",
            "alternates": [
                "Try vagal — Valsalva. If it holds, adenosine six.",
                "Give her six of adenosine, IV push, flush behind it.",
                "Vagal first. Get me adenosine and pads.",
            ],
        },
        {
            "scene_id": "S12",
            "line_no": 128,
            "severity": "WARN",
            "original": "Charging to 360. Clear!",
            "issue": "360 J is a monophasic-defibrillator setting. Contemporary "
                     "biphasic devices start at 120–200 J for VF.",
            "citation": "AHA 2020 ACLS Defibrillation Energy",
            "citation_url": "https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines",
            "alternates": [
                "Charging to two hundred. Clear!",
                "Two hundred biphasic. Clear!",
            ],
        },
        {
            "scene_id": "S12",
            "line_no": 141,
            "severity": "CRITICAL",
            "original": "We've got her. Extubate her.",
            "issue": "Extubation three minutes post-ROSC is implausible. "
                     "Post-arrest care mandates continued ventilation, "
                     "targeted temperature management, and neurologic "
                     "assessment over hours before extubation is considered.",
            "citation": "AHA Post-Cardiac Arrest Care",
            "citation_url": "https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines",
            "alternates": [
                "She's back. Keep her tubed — call the unit, "
                "TTM protocol, thirty-six degrees.",
                "Pulses back. Sedate, keep the tube, and get us upstairs.",
            ],
        },
    ]


def _demo_continuity() -> list[dict]:
    return [
        {
            "patient": "Maya Chen",
            "flag": "Maya's LVEF is 30% (canon). At HR 182 with SBP 88 she is "
                     "borderline unstable — synchronized cardioversion, not "
                     "adenosine, would be defensible if she deteriorates.",
            "severity": "INFO",
        },
        {
            "patient": "Maya Chen",
            "flag": "Empagliflozin + hypotension — watch euglycemic DKA in a T1DM "
                     "on SGLT2 inhibitor during acute illness. Consider a VBG "
                     "line in scene.",
            "severity": "WARN",
        },
    ]


col_script, col_props, col_audio = st.columns([1.15, 1, 1], gap="large")

with col_script:
    st.subheader("Script + findings")
    script_text = DEMO_SCENE.read_text() if DEMO_SCENE.exists() else ""
    if uploaded is not None:
        script_text = uploaded.read().decode("utf-8", errors="ignore") \
            if uploaded.type == "text/plain" else "[PDF parser wires to Document AI]"
    st.code(script_text or "Load a script or press ▶ Play canned demo.",
            language="markdown")

    if demo or uploaded:
        st.markdown("### Clinical findings")
        for f in _demo_findings():
            c = SEVERITY_COLOR[f["severity"]]
            st.markdown(
                f'<div class="finding" style="border-left-color:{c};">'
                f'<span class="badge" style="background:{c}; color:white;">'
                f'{f["severity"]}</span>'
                f'<b>Line {f["line_no"]}</b> — <i>{f["original"]}</i><br>'
                f'{f["issue"]}<br>'
                f'<a href="{f["citation_url"]}" target="_blank" '
                f'style="color:#93c5fd;">{f["citation"]}</a></div>',
                unsafe_allow_html=True,
            )
            with st.expander("Suggested rewrites"):
                for alt in f["alternates"]:
                    st.write(f"— {alt}")

        st.markdown("### Continuity check")
        for c in _demo_continuity():
            color = SEVERITY_COLOR[c["severity"]]
            st.markdown(
                f'<div class="finding" style="border-left-color:{color};">'
                f'<b>{c["patient"]}</b> — {c["flag"]}</div>',
                unsafe_allow_html=True,
            )

with col_props:
    st.subheader("Prop gallery — Imagen 3")
    if demo or uploaded:
        ecg = ASSETS / "fallback_ecg.png"
        monitor = ASSETS / "fallback_monitor.png"
        cxr = ASSETS / "fallback_cxr.png"
        st.image(str(ecg) if ecg.exists() else "https://placehold.co/640x360?text=ECG+narrow+complex+tach+180",
                 caption="ECG — narrow-complex tachycardia @ 180")
        st.image(str(monitor) if monitor.exists() else "https://placehold.co/640x360?text=Bedside+monitor",
                 caption="Bedside monitor — HR 182, BP 88/54, SpO₂ 91")
        st.image(str(cxr) if cxr.exists() else "https://placehold.co/640x360?text=Post-ROSC+CXR",
                 caption="Post-ROSC CXR — ETT tip 4 cm above carina")
    else:
        st.info("Props render once the audit completes.")

with col_audio:
    st.subheader("Audio bench")
    if demo or uploaded:
        bed = ASSETS / "fallback_icu.wav"
        read = ASSETS / "fallback_read.wav"
        st.markdown("**Ambient bed — Lyria 3 (`icu_quiet`)**")
        if bed.exists():
            st.audio(str(bed))
        else:
            st.info("Pre-render `assets/fallback_icu.wav` before H55.")
        st.markdown("**Table read — Gemini TTS (multi-speaker)**")
        if read.exists():
            st.audio(str(read))
        else:
            st.info("Pre-render `assets/fallback_read.wav` before H55.")
    else:
        st.info("Audio renders after the rewrite is finalized.")

st.divider()
st.caption(
    "SceneMedic never produces real medical advice. All outputs are fictional "
    "scene assets. No real patient data. Built for the Agentic Cinema Hackathon."
)
