"""Generate and mix the complete 3-minute pitch voiceover into the video."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[1]
load_dotenv(REPO / ".env")

from google import genai
from google.genai import types

OUTPUTS = REPO / "outputs"
STAGING = OUTPUTS / "voice_staging"
VIDEO_SILENT = OUTPUTS / "scenemedic_pitch_demo.mp4"
VIDEO_VOICED = OUTPUTS / "scenemedic_pitch_demo_voiced.mp4"
ASSETS = REPO / "assets"
ICU_BED = ASSETS / "fallback_icu.wav"

VOICE = "Puck"  # Professional, confident narrator voice

SEGMENTS = [
    {
        "id": "A_title",
        "start_sec": 0.5,
        "text": "SceneMedic. A physician-built clinical realism advisor for medical film and television. Built by Doctor Ahmed Zayed.",
    },
    {
        "id": "B_problem",
        "start_sec": 6.5,
        "text": "Medical dramas spend five thousand dollars per episode on clinical consultants, yet fatal errors still trend on medical Twitter every Monday morning. SceneMedic is the technical advisor Hollywood actually needs: an agentic system that audits every clinical beat before shoot day.",
    },
    {
        "id": "C_architecture",
        "start_sec": 26.5,
        "text": "SceneMedic is built on the Google Agent Development Kit and deployed to Vertex AI Agent Engine. A parser extracts the script structure. A continuity agent, grounded in ClickHouse via MCP, tracks patient canon across seasons. Our clinical accuracy agent audits every medical beat against PubMed in BigQuery Vector Search. And our dramatization agent rewrites flagged lines while preserving the writer's authentic voice.",
    },
    {
        "id": "D_setup",
        "start_sec": 56.5,
        "text": "Let's see it live on Episode seven, Scene twelve. Maya Chen arrives in Trauma Bay four in severe tachycardia. The script contains three planted clinical errors.",
    },
    {
        "id": "UI_walkthrough",
        "start_sec": 67.0,
        "text": "In the Writers' Room interface, we trigger the audit. Immediately, SceneMedic flags the medical dialogue. First, line five: the script calls the rhythm stable, but with a blood pressure of eighty-eight over fifty-four, it is definitionally unstable. Next, line six: pushing one milligram of epinephrine for SVT is a fatal error. ACLS guidelines mandate adenosine or synchronized cardioversion. Notice the three voice-preserving rewrites generated instantly. Third, line fourteen: extubating three minutes post-cardiac arrest violates extubation readiness criteria. Alongside the dialogue, SceneMedic renders photorealistic on-set props: a rhythm-matched ECG strip, bedside monitor readouts, and chest X-rays, plus a multi-speaker audio table read.",
    },
    {
        "id": "E_findings",
        "start_sec": 137.0,
        "text": "All three clinical catches are grounded in real medical literature from the American Heart Association and the American Thoracic Society, with zero hallucinated citations. The dramatizations preserve the scene's high-stakes urgency while ensuring absolute clinical defensibility.",
    },
    {
        "id": "F_close",
        "start_sec": 167.0,
        "text": "One architecture powers three products: SceneMedic for medical dramas, Forensica for crime procedurals, and VitalSigns for actor rehearsal. The moat is not the code. A physician built it. Thank you.",
    },
]


def _get_client() -> genai.Client:
    return genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )


def synthesize_segment(client: genai.Client, text: str, out_wav: Path) -> None:
    cfg = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)
            )
        ),
    )
    resp = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=text,
        config=cfg,
    )
    part = resp.candidates[0].content.parts[0]
    raw_data = part.inline_data.data
    mime = part.inline_data.mime_type or "audio/L16;rate=24000"

    raw_path = out_wav.with_suffix(".raw")
    raw_path.write_bytes(raw_data)

    # Convert PCM to standard WAV (24kHz mono)
    if "pcm" in mime or "L16" in mime:
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-f", "s16le", "-ar", "24000", "-ac", "1",
                "-i", str(raw_path),
                "-ar", "44100", "-ac", "2",
                str(out_wav)
            ],
            check=True
        )
    else:
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", str(raw_path),
                "-ar", "44100", "-ac", "2",
                str(out_wav)
            ],
            check=True
        )


def main() -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    client = _get_client()

    print("• Checking narration segments...")
    wav_files = []
    for seg in SEGMENTS:
        wav_path = STAGING / f"{seg['id']}.wav"
        if wav_path.exists() and wav_path.stat().st_size > 0:
            print(f"  ✓ [{seg['start_sec']:5.1f}s] {seg['id']} (cached)")
        else:
            print(f"  - [{seg['start_sec']:5.1f}s] {seg['id']} (synthesizing) ...")
            synthesize_segment(client, seg["text"], wav_path)
        wav_files.append((seg["start_sec"], wav_path))

    # Assemble full 180s voice track
    print("• Assembling aligned 180s voice track...")
    inputs = []
    filter_parts = []
    for i, (start_sec, p) in enumerate(wav_files):
        inputs.extend(["-i", str(p)])
        delay_ms = int(start_sec * 1000)
        filter_parts.append(f"[{i}:a]adelay={delay_ms}|{delay_ms}[a{i}]")

    amix_inputs = "".join(f"[a{i}]" for i in range(len(wav_files)))
    filter_str = ";".join(filter_parts) + f";{amix_inputs}amix=inputs={len(wav_files)}:dropout_transition=0:normalize=0[voout]"

    voice_track = STAGING / "full_voiceover.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            *inputs,
            "-filter_complex", filter_str,
            "-map", "[voout]",
            "-t", "180",
            str(voice_track)
        ],
        check=True
    )

    print("• Mixing voiceover, ambient ICU bed, and video...")
    # Voice track @ 1.0 vol, ICU Bed @ 0.15 vol
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(VIDEO_SILENT),
            "-i", str(voice_track),
            "-stream_loop", "-1", "-i", str(ICU_BED),
            "-filter_complex",
            "[1:a]volume=1.0[v_aud];"
            "[2:a]volume=0.15,afade=in:st=0:d=2,afade=out:st=177:d=3[m_aud];"
            "[v_aud][m_aud]amix=inputs=2:duration=first:dropout_transition=0[final_aud]",
            "-map", "0:v", "-map", "[final_aud]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-t", "180",
            str(VIDEO_VOICED)
        ],
        check=True
    )

    # Also update master video
    shutil.copy(VIDEO_VOICED, VIDEO_SILENT)

    size_mb = VIDEO_VOICED.stat().st_size / 1_048_576
    print(f"\n✓ Complete pitch video with voiceover: {VIDEO_VOICED.relative_to(REPO)} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
