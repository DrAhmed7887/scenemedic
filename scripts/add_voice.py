"""Add a macOS 'say' voiceover to scenemedic_pitch_demo.mp4.

Runs after generate_pitch_video.py. Rebuilds the audio track:
  narration (Samantha, rate 175) at 1.0
  ICU ambient bed (fallback_icu.wav) ducked to 0.12, fade in 2s / out 3s
Muxes over the existing video stream — no re-encode of picture.

Each section is spoken, then padded with silence to hit its exact slot,
so audio stays locked to the visual beats regardless of TTS length.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUTPUTS = REPO / "outputs"
ASSETS = REPO / "assets"
FINAL = OUTPUTS / "scenemedic_pitch_demo.mp4"
BED = ASSETS / "fallback_icu.wav"
STAGING = OUTPUTS / "voice_staging"

VOICE = "Samantha"
RATE = 175  # wpm
SR = 48_000


@dataclass(frozen=True)
class Section:
    key: str
    seconds: float
    text: str


SECTIONS: tuple[Section, ...] = (
    Section("A_title", 6.0,
            "SceneMedic. A physician-built clinical realism advisor "
            "for medical film and television."),

    Section("B_problem", 14.0,
            "Every network medical drama pays clinical consultants "
            "five thousand dollars per episode. And still ships errors "
            "that trend on medical Twitter the next morning. "
            "SceneMedic audits every clinical beat before shoot day."),

    Section("C_architecture", 18.0,
            "Built on Google ADK and deployed to Vertex Agent Engine. "
            "A parser reads the script. A continuity agent tracks every "
            "patient across every episode via ClickHouse MCP. A clinical "
            "agent grounds each finding in BigQuery vector search over "
            "PubMed. Then dramatization preserves the writer's voice."),

    Section("D_setup", 10.0,
            "Live demo. Outliers, Episode Seven, Scene Twelve. Trauma "
            "Bay Four. Maya Chen — narrow-complex tach at one-eighty-two. "
            "The script contains three planted clinical errors."),

    Section("E_ui", 70.0,
            "On the left, the parsed script. The orchestrator has "
            "already run against the canned demo — deliberately safe "
            "for stage. Three findings appear, each color-coded by "
            "severity. Line five is flagged WARN: the dialogue calls "
            "the patient stable, but a pressure of eighty-eight over "
            "fifty-four at a rate of one-eighty-two is by definition "
            "unstable. Line six is CRITICAL: pushing epinephrine into "
            "a narrow-complex tachycardia with a pulse is a fatal "
            "error. First line is adenosine six milligrams IV push, "
            "per the AHA Adult Tachycardia Algorithm. Line fourteen is "
            "CRITICAL: extubating three minutes post-ROSC violates "
            "every readiness criterion in the American Thoracic "
            "Society guidelines. Every finding carries a citation URL. "
            "No citation, no publish. In the middle column, Imagen 3 "
            "renders matching props: an ECG showing narrow-complex "
            "tach at one-eighty, a bedside monitor with the correct "
            "vitals, and a post-ROSC chest X-ray with the ETT visible. "
            "On the right, the audio bench — a Lyria ambient ICU bed "
            "and a Gemini TTS multi-speaker table read of the "
            "corrected dialogue. This is what a script doctor "
            "delivers on shoot day. In ninety seconds. Not two weeks."),

    Section("F_zooms", 18.0,
            "Zoom in on each catch. First: the hypotension "
            "contradiction — cited to the AHA algorithm. Second: the "
            "epinephrine error — cardioversion or adenosine, never "
            "epi. Third: the extubation violation. Plus the ECG and "
            "monitor props, and the table read."),

    Section("G_findings", 30.0,
            "Three catches. All grounded. All rewritten. The clinical "
            "agent cannot ship a finding without a supporting snippet "
            "from the RAG index — findings without citation URLs are "
            "filtered at the orchestrator. That is how you defeat "
            "hallucination in a high-stakes domain. Every rewrite "
            "preserves the writer's voice: the drama survives, the "
            "medicine gets fixed. Zero patient data anywhere. Public "
            "literature only. Every output is a fictional scene asset. "
            "That is the governance layer, built in from day one."),

    Section("H_close", 14.0,
            "One architecture. Three products. SceneMedic for medical "
            "drama. Forensica for crime and procedurals. VitalSigns "
            "for actor prep. The moat is not the code. A physician "
            "built it."),
)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def audio_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def tts_section(sec: Section, out_wav: Path) -> None:
    """Speak the section text and pad/trim to sec.seconds."""
    aiff = STAGING / f"{sec.key}_raw.aiff"
    raw_wav = STAGING / f"{sec.key}_raw.wav"

    run(["say", "-v", VOICE, "-r", str(RATE),
         "-o", str(aiff), sec.text])
    run(["ffmpeg", "-y", "-loglevel", "error",
         "-i", str(aiff),
         "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le",
         str(raw_wav)])

    dur = audio_duration(raw_wav)
    if dur > sec.seconds:
        # Speed up just enough to fit (rare — trim excess with atempo).
        tempo = dur / sec.seconds
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-i", str(raw_wav),
             "-filter:a", f"atempo={tempo:.4f}",
             "-t", f"{sec.seconds:.3f}",
             str(out_wav)])
    else:
        pad = sec.seconds - dur
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-i", str(raw_wav),
             "-af", f"apad=pad_dur={pad:.3f}",
             "-t", f"{sec.seconds:.3f}",
             str(out_wav)])


def concat_wavs(paths: list[Path], out: Path) -> None:
    manifest = STAGING / "concat.txt"
    manifest.write_text(
        "".join(f"file '{p.resolve()}'\n" for p in paths), encoding="utf-8"
    )
    run(["ffmpeg", "-y", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(manifest),
         "-c", "copy", str(out)])


def mix_final(video: Path, voice: Path, bed: Path, out: Path,
              duration: float) -> None:
    fade_out_start = max(0.0, duration - 3.0)
    filter_complex = (
        f"[1:a]volume=1.0[voice];"
        f"[2:a]aloop=loop=-1:size={SR * 40},"
        f"volume=0.12,"
        f"afade=in:st=0:d=2,"
        f"afade=out:st={fade_out_start:.2f}:d=3[bed];"
        f"[voice][bed]amix=inputs=2:duration=first:normalize=0[out]"
    )
    run(["ffmpeg", "-y", "-loglevel", "error",
         "-i", str(video),
         "-i", str(voice),
         "-i", str(bed),
         "-filter_complex", filter_complex,
         "-map", "0:v", "-map", "[out]",
         "-c:v", "copy",
         "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(out)])


def main() -> int:
    if not FINAL.exists():
        print(f"! {FINAL} not found — run generate_pitch_video.py first")
        return 1
    if not BED.exists():
        print(f"! {BED} not found")
        return 1

    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)

    total_target = sum(s.seconds for s in SECTIONS)

    print(f"• Synthesizing {len(SECTIONS)} sections ({total_target:.0f}s "
          f"target, voice={VOICE}, rate={RATE})")
    section_wavs: list[Path] = []
    for sec in SECTIONS:
        out = STAGING / f"{sec.key}.wav"
        tts_section(sec, out)
        actual = audio_duration(out)
        print(f"  {sec.key:14s}  {actual:6.2f}s  (slot {sec.seconds:.1f}s)")
        section_wavs.append(out)

    voice_master = STAGING / "voice_master.wav"
    print(f"• Concatenating → {voice_master.name}")
    concat_wavs(section_wavs, voice_master)

    voice_dur = audio_duration(voice_master)
    print(f"  voice track: {voice_dur:.2f}s")

    # Move current final aside as backup, then rewrite in place.
    backup = FINAL.with_name(FINAL.stem + "_silent.mp4")
    if not backup.exists():
        shutil.copy2(FINAL, backup)
        print(f"• Silent master backed up → {backup.name}")

    tmp_out = OUTPUTS / "_scenemedic_pitch_demo_mixed.mp4"
    print("• Mixing voice + ducked ICU bed, muxing over video...")
    mix_final(backup, voice_master, BED, tmp_out, duration=voice_dur)
    tmp_out.replace(FINAL)

    size_mb = FINAL.stat().st_size / 1_048_576
    print(f"\n✓ {FINAL.relative_to(REPO)}  "
          f"({voice_dur:.1f}s, {size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
