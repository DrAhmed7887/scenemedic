"""Generate the 3-minute SceneMedic pitch reel (silent + music bed).

Sections
--------
A  0:00-0:06   Title card
B  0:06-0:26   The $5,000/episode problem
C  0:26-0:56   Architecture flyover
D  0:56-2:16   Streamlit walkthrough (Playwright screen record)
E  2:16-2:46   Props + audio bench
F  2:46-3:00   Roadmap + close

Voiceover is intentionally deferred; final track is silent + Lyria ICU bed.
"""
from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[1]
OUTPUTS = REPO / "outputs"
STAGING = OUTPUTS / "video_staging"
FINAL_MP4 = OUTPUTS / "scenemedic_pitch_demo.mp4"
ASSETS = REPO / "assets"
ICU_BED = ASSETS / "fallback_icu.wav"

W, H = 1920, 1080
FPS = 30

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

BG = (10, 15, 28)
INK = (232, 236, 243)
DIM = (146, 158, 178)
ACCENT = (99, 179, 237)
CRIT = (239, 88, 88)
WARN = (245, 158, 11)
OK = (74, 222, 128)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def new_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def draw_topbar(d: ImageDraw.ImageDraw, label: str) -> None:
    d.rectangle((0, 0, W, 6), fill=ACCENT)
    d.text((72, 40), "SceneMedic", font=font(FONT_BOLD, 32), fill=ACCENT)
    d.text((W - 72 - d.textlength(label, font=font(FONT_REG, 22)), 46),
           label, font=font(FONT_REG, 22), fill=DIM)


def text_block(d: ImageDraw.ImageDraw, x: int, y: int, text: str,
               fnt: ImageFont.FreeTypeFont, fill=INK, line_gap: int = 12,
               max_w: int | None = None) -> int:
    lines = text.split("\n") if max_w is None else _wrap(text, fnt, max_w)
    cy = y
    for line in lines:
        d.text((x, cy), line, font=fnt, fill=fill)
        bbox = fnt.getbbox(line)
        cy += (bbox[3] - bbox[1]) + line_gap
    return cy


def _wrap(text: str, fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words, out, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


# ---------- Card renderers ----------

def card_title(path: Path) -> None:
    img, d = new_canvas()
    draw_topbar(d, "Agentic Cinema Hackathon · 2026")
    d.text((72, 380), "SceneMedic", font=font(FONT_BLACK, 168), fill=INK)
    d.text((72, 580),
           "Physician-built clinical realism advisor for medical film & TV.",
           font=font(FONT_REG, 44), fill=DIM)
    d.rectangle((72, 720, 260, 724), fill=ACCENT)
    d.text((72, 760), "Dr. Ahmed Zayed", font=font(FONT_BOLD, 40), fill=INK)
    d.text((72, 820), "MBBCh · Clinical AI · RWTH Aachen (Winter 26/27)",
           font=font(FONT_REG, 28), fill=DIM)
    img.save(path)


def card_problem(path: Path) -> None:
    img, d = new_canvas()
    draw_topbar(d, "The problem")
    d.text((72, 200), "$5,000 / episode.",
           font=font(FONT_BLACK, 148), fill=CRIT)
    d.text((72, 400),
           "Every network drama pays clinical consultants five figures per",
           font=font(FONT_REG, 42), fill=INK)
    d.text((72, 460),
           "episode — and still ships errors that trend on medical Twitter",
           font=font(FONT_REG, 42), fill=INK)
    d.text((72, 520), "the next morning.", font=font(FONT_REG, 42), fill=INK)
    d.text((72, 700),
           "SceneMedic is the consultant Hollywood actually needs:",
           font=font(FONT_BOLD, 38), fill=DIM)
    d.text((72, 760),
           "an agentic system that audits every clinical beat before shoot day.",
           font=font(FONT_REG, 34), fill=DIM)
    img.save(path)


def card_architecture(path: Path) -> None:
    img, d = new_canvas()
    draw_topbar(d, "Architecture")
    d.text((72, 130), "Multi-agent on Google ADK + Vertex Agent Engine",
           font=font(FONT_BOLD, 44), fill=INK)

    # Row 1 — Ingest / Reasoning / Media agents
    row1 = [
        ("Parser", "Document AI", ACCENT),
        ("Continuity", "MCP → ClickHouse", (250, 204, 21)),
        ("Clinical", "BigQuery Vector RAG", OK),
        ("Dramatization", "Voice-preserving rewrite", (168, 85, 247)),
    ]
    box_w, box_h = 400, 200
    gap = 32
    total_w = len(row1) * box_w + (len(row1) - 1) * gap
    x0 = (W - total_w) // 2
    y0 = 260
    for i, (title, sub, col) in enumerate(row1):
        x = x0 + i * (box_w + gap)
        d.rounded_rectangle((x, y0, x + box_w, y0 + box_h), radius=18,
                             outline=col, width=4, fill=(18, 24, 42))
        d.text((x + 24, y0 + 26), title, font=font(FONT_BOLD, 36), fill=INK)
        d.text((x + 24, y0 + 92), sub, font=font(FONT_REG, 26), fill=DIM)
        d.rectangle((x + 24, y0 + 150, x + 100, y0 + 154), fill=col)

    # Row 2 — GenMedia
    row2 = [
        ("Imagen 3", "ECGs / CXRs / props"),
        ("Lyria-002", "ICU ambient beds"),
        ("Gemini TTS", "Multi-speaker table read"),
        ("Gemini Live", "Rehearsal (stretch)"),
    ]
    y1 = y0 + box_h + 80
    for i, (title, sub) in enumerate(row2):
        x = x0 + i * (box_w + gap)
        d.rounded_rectangle((x, y1, x + box_w, y1 + box_h), radius=18,
                             outline=ACCENT, width=2, fill=(15, 20, 36))
        d.text((x + 24, y1 + 26), title, font=font(FONT_BOLD, 34), fill=INK)
        d.text((x + 24, y1 + 92), sub, font=font(FONT_REG, 26), fill=DIM)

    d.text((72, H - 90),
           "Grounding · BigQuery Vector Search over PubMed & ACLS · "
           "ClickHouse canon per series/patient · Grafana Cloud traces",
           font=font(FONT_REG, 24), fill=DIM)
    img.save(path)


def card_ep_setup(path: Path) -> None:
    img, d = new_canvas()
    draw_topbar(d, "Live demo · Outliers · Ep 07 · Scene 12")
    d.text((72, 240), "Trauma Bay 4.", font=font(FONT_BLACK, 132), fill=INK)
    d.text((72, 400),
           "Maya Chen, 34, T1DM, LVEF 30%.",
           font=font(FONT_REG, 44), fill=DIM)
    d.text((72, 470),
           "Narrow-complex tachycardia at 182. BP 88/54. SpO₂ 91% on 4L.",
           font=font(FONT_REG, 38), fill=DIM)
    d.text((72, 640),
           "The script has three clinical errors.",
           font=font(FONT_BOLD, 44), fill=WARN)
    d.text((72, 710),
           "SceneMedic catches all of them, grounds each finding in a",
           font=font(FONT_REG, 32), fill=INK)
    d.text((72, 760),
           "citation, and rewrites the dialogue in the writer's voice.",
           font=font(FONT_REG, 32), fill=INK)
    img.save(path)


def card_findings(path: Path) -> None:
    img, d = new_canvas()
    draw_topbar(d, "Findings · Ep 07 · Scene 12")
    d.text((72, 130), "3 catches · all cited · all rewritten",
           font=font(FONT_BOLD, 44), fill=INK)

    findings = [
        (WARN, "WARN",
         "Line 5 — \"Stable narrow-complex tach, hypotensive.\"",
         "Hypotension makes this tach unstable by definition. "
         "Source: AHA Adult Tachycardia Algorithm."),
        (CRIT, "CRITICAL",
         "Line 6 — \"Push one of epi, IV. Now.\"",
         "Epinephrine is wrong for narrow-complex tach with a pulse. "
         "Adenosine 6 mg IV push is first-line. Epi is for arrest."),
        (CRIT, "CRITICAL",
         "Line 14 — \"Extubate her.\"",
         "Immediate extubation 3 min post-ROSC violates every readiness "
         "criterion. Source: ATS Critical Care Guidelines."),
    ]
    y = 240
    for col, tag, title, body in findings:
        d.rounded_rectangle((72, y, W - 72, y + 200), radius=14,
                             fill=(18, 24, 42), outline=col, width=3)
        d.rectangle((72, y, 84, y + 200), fill=col)
        d.text((110, y + 22), tag, font=font(FONT_BLACK, 26), fill=col)
        d.text((110, y + 62), title, font=font(FONT_BOLD, 32), fill=INK)
        for i, line in enumerate(_wrap(body, font(FONT_REG, 26), W - 220)):
            d.text((110, y + 110 + i * 36), line,
                   font=font(FONT_REG, 26), fill=DIM)
        y += 220
    img.save(path)


def card_close(path: Path) -> None:
    img, d = new_canvas()
    draw_topbar(d, "Roadmap · Close")
    d.text((72, 220), "One architecture. Three products.",
           font=font(FONT_BLACK, 96), fill=INK)

    lanes = [
        ("SceneMedic", "Medical drama · shipping", OK),
        ("Forensica", "Crime + procedurals · next", ACCENT),
        ("VitalSigns", "Actor prep · Gemini Live API", (168, 85, 247)),
    ]
    box_w, box_h = 560, 220
    gap = 40
    total = len(lanes) * box_w + (len(lanes) - 1) * gap
    x0 = (W - total) // 2
    y0 = 440
    for i, (title, sub, col) in enumerate(lanes):
        x = x0 + i * (box_w + gap)
        d.rounded_rectangle((x, y0, x + box_w, y0 + box_h), radius=20,
                             outline=col, width=4, fill=(18, 24, 42))
        d.text((x + 30, y0 + 40), title, font=font(FONT_BOLD, 48), fill=INK)
        d.text((x + 30, y0 + 120), sub, font=font(FONT_REG, 30), fill=DIM)

    d.text((72, 800), "The moat is not the code.",
           font=font(FONT_REG, 40), fill=DIM)
    d.text((72, 860), "A physician built it.",
           font=font(FONT_BLACK, 60), fill=INK)
    img.save(path)


# ---------- Streamlit + Playwright capture ----------

def free_port() -> int:
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def wait_port(port: int, timeout: float = 60.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError(f"Port {port} never came up")


def start_streamlit(port: int) -> subprocess.Popen:
    env = {**os.environ, "STREAMLIT_SERVER_HEADLESS": "true"}
    return subprocess.Popen(
        [str(REPO / ".venv/bin/streamlit"), "run", str(REPO / "ui/app.py"),
         "--server.port", str(port),
         "--server.headless", "true",
         "--server.address", "127.0.0.1",
         "--browser.gatherUsageStats", "false"],
        cwd=REPO, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


@dataclass
class Capture:
    webm_path: Path
    duration_target: float
    stills: dict[str, Path]


def _shot_element(page, selector: str, out: Path,
                  pad: int = 24) -> Path | None:
    loc = page.locator(selector).first
    try:
        loc.scroll_into_view_if_needed(timeout=4_000)
    except Exception:
        return None
    page.wait_for_timeout(400)
    box = loc.bounding_box()
    if not box:
        return None
    scroll_y = page.evaluate("window.scrollY")
    clip = {
        "x": max(0, box["x"] - pad),
        "y": max(0, box["y"] - pad),
        "width": min(W - max(0, box["x"] - pad), box["width"] + 2 * pad),
        "height": min(H - max(0, box["y"] - pad), box["height"] + 2 * pad),
    }
    # bounding_box is viewport-relative in Playwright, so clip.y already
    # accounts for the current scroll — page.screenshot uses viewport coords.
    _ = scroll_y  # not needed, but kept for clarity
    page.screenshot(path=str(out), clip=clip)
    return out


def capture_ui(port: int, out_dir: Path) -> Capture:
    out_dir.mkdir(parents=True, exist_ok=True)
    stills: dict[str, Path] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": W, "height": H},
            device_scale_factor=1,
            record_video_dir=str(out_dir),
            record_video_size={"width": W, "height": H},
        )
        page = ctx.new_page()
        page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle",
                  timeout=45_000)
        page.wait_for_timeout(3_000)

        # Trigger canned demo (safe mode).
        page.get_by_role("button", name="Play canned demo (safe)").click()
        page.wait_for_timeout(4_000)

        # Slowly scroll through findings — the main walkthrough recording.
        for y in range(0, 2200, 220):
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1_400)

        # Scroll back to top so the stills capture the fresh state.
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(2_000)

        video_handle = page.video

        # --- Targeted stills for Ken Burns zoom-ins ---
        # Each finding card (there are 3).
        findings = page.locator("div.finding")
        for i in range(min(3, findings.count())):
            out = out_dir / f"still_finding_{i}.png"
            loc = findings.nth(i)
            try:
                loc.scroll_into_view_if_needed(timeout=4_000)
                page.wait_for_timeout(300)
                box = loc.bounding_box()
                if box:
                    pad = 24
                    clip = {
                        "x": max(0, box["x"] - pad),
                        "y": max(0, box["y"] - pad),
                        "width": min(W - max(0, box["x"] - pad),
                                     box["width"] + 2 * pad),
                        "height": min(H - max(0, box["y"] - pad),
                                      box["height"] + 2 * pad),
                    }
                    page.screenshot(path=str(out), clip=clip)
                    stills[f"finding_{i}"] = out
            except Exception:
                continue

        # Prop gallery — locate by the subheader text.
        try:
            prop_header = page.get_by_text("Prop gallery", exact=True).first
            prop_header.scroll_into_view_if_needed(timeout=4_000)
            page.wait_for_timeout(400)
            box = prop_header.bounding_box()
            if box:
                clip = {
                    "x": max(0, box["x"] - 24),
                    "y": max(0, box["y"] - 24),
                    "width": 700,
                    "height": 900,
                }
                # constrain to viewport
                clip["width"] = min(clip["width"], W - clip["x"])
                clip["height"] = min(clip["height"], H - clip["y"])
                out = out_dir / "still_props.png"
                page.screenshot(path=str(out), clip=clip)
                stills["props"] = out
        except Exception:
            pass

        # Audio bench — locate by the subheader text.
        try:
            audio_header = page.get_by_text("Audio bench", exact=True).first
            audio_header.scroll_into_view_if_needed(timeout=4_000)
            page.wait_for_timeout(400)
            box = audio_header.bounding_box()
            if box:
                clip = {
                    "x": max(0, box["x"] - 24),
                    "y": max(0, box["y"] - 24),
                    "width": 700,
                    "height": 600,
                }
                clip["width"] = min(clip["width"], W - clip["x"])
                clip["height"] = min(clip["height"], H - clip["y"])
                out = out_dir / "still_audio.png"
                page.screenshot(path=str(out), clip=clip)
                stills["audio"] = out
        except Exception:
            pass

        ctx.close()
        browser.close()
        assert video_handle is not None
        src = Path(video_handle.path())
        dst = out_dir / "ui_capture.webm"
        shutil.move(str(src), dst)
        return Capture(dst, duration_target=70.0, stills=stills)


# ---------- ffmpeg helpers ----------

def png_to_kenburns(png: Path, seconds: float, out: Path,
                     zoom_end: float = 1.15, direction: str = "in") -> None:
    """Turn a still image into a subtly zooming clip (Ken Burns).

    Card is scaled to cover 1920x1080 (max preserving aspect) then zoompan
    animates from 1.0→zoom_end (`in`) or zoom_end→1.0 (`out`).
    """
    frames = max(2, int(round(seconds * FPS)))
    if direction == "in":
        z_expr = f"'min(1.0+on*({zoom_end - 1.0})/{frames - 1},{zoom_end})'"
    else:
        z_expr = (f"'max({zoom_end}-on*({zoom_end - 1.0})/{frames - 1},1.0)'")
    x_expr = "'iw/2-(iw/zoom/2)'"
    y_expr = "'ih/2-(ih/zoom/2)'"
    vf = (
        # First scale image up to a working res so zoompan has pixels to spare.
        f"scale=iw*4:ih*4,"
        f"zoompan=z={z_expr}:x={x_expr}:y={y_expr}"
        f":d={frames}:fps={FPS}:s={W}x{H},"
        f"format=yuv420p"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-loop", "1", "-framerate", str(FPS), "-i", str(png),
         "-vf", vf,
         "-t", f"{seconds:.3f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-r", str(FPS),
         str(out)],
        check=True,
    )


def png_to_clip(png: Path, seconds: float, out: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-loop", "1", "-i", str(png),
         "-c:v", "libx264", "-t", f"{seconds:.3f}",
         "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black",
         "-preset", "medium", "-crf", "20",
         str(out)],
        check=True,
    )


def webm_to_clip(webm: Path, target_seconds: float, out: Path) -> None:
    # Get real duration
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(webm)],
        capture_output=True, text=True, check=True,
    )
    real = float(probe.stdout.strip())
    setpts = target_seconds / real
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(webm),
         "-filter:v",
         f"setpts={setpts:.4f}*PTS,"
         f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
         f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black",
         "-an", "-r", str(FPS),
         "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-preset", "medium", "-crf", "20",
         "-t", f"{target_seconds:.3f}",
         str(out)],
        check=True,
    )


def concat(clips: list[Path], out: Path) -> None:
    manifest = STAGING / "concat.txt"
    manifest.write_text(
        "".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(manifest),
         "-c", "copy", str(out)],
        check=True,
    )


def mix_music(silent_video: Path, bed: Path, duration: float, out: Path) -> None:
    # Loop the 32-second bed, low volume, fade in/out.
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-i", str(silent_video),
         "-stream_loop", "-1", "-i", str(bed),
         "-filter_complex",
         f"[1:a]volume=0.35,afade=in:st=0:d=2,"
         f"afade=out:st={max(0, duration - 3):.2f}:d=3[aud]",
         "-map", "0:v", "-map", "[aud]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(out)],
        check=True,
    )


# ---------- Main ----------

def main() -> None:
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)
    OUTPUTS.mkdir(exist_ok=True)

    cards = [
        ("A_title.png", card_title, 6.0),
        ("B_problem.png", card_problem, 20.0),
        ("C_architecture.png", card_architecture, 30.0),
        ("D_ep_setup.png", card_ep_setup, 10.0),
        ("E_findings.png", card_findings, 20.0),
        ("F_close.png", card_close, 14.0),
    ]

    print("• Rendering title cards...")
    png_paths = {}
    for name, renderer, _ in cards:
        p = STAGING / name
        renderer(p)
        png_paths[name] = p

    print("• Booting Streamlit...")
    port = free_port()
    streamlit_proc = start_streamlit(port)
    ui_capture: Capture | None = None
    try:
        wait_port(port, timeout=60)
        time.sleep(4)  # Streamlit needs another beat after port is open.
        print(f"  Streamlit up on :{port}")

        print("• Capturing UI walkthrough via Playwright...")
        ui_capture = capture_ui(port, STAGING)
    finally:
        streamlit_proc.terminate()
        try:
            streamlit_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            streamlit_proc.kill()

    assert ui_capture is not None

    print("• Encoding title-card clips...")
    clip_paths: list[Path] = []
    # A · title
    a = STAGING / "A.mp4"; png_to_clip(png_paths["A_title.png"], 6.0, a); clip_paths.append(a)
    # B · problem (14s, was 20)
    b = STAGING / "B.mp4"; png_to_clip(png_paths["B_problem.png"], 14.0, b); clip_paths.append(b)
    # C · architecture (18s, was 30)
    c = STAGING / "C.mp4"; png_to_clip(png_paths["C_architecture.png"], 18.0, c); clip_paths.append(c)
    # D · ep setup
    d = STAGING / "D.mp4"; png_to_clip(png_paths["D_ep_setup.png"], 10.0, d); clip_paths.append(d)

    # UI walkthrough — 70s scroll of the writers' room UI
    print("• Encoding UI walkthrough clip...")
    ui_clip = STAGING / "UI.mp4"
    webm_to_clip(ui_capture.webm_path, target_seconds=70.0, out=ui_clip)
    clip_paths.append(ui_clip)

    # --- Ken Burns zoom-ins (18s total) ---
    print("• Encoding zoom-in stills...")
    zoom_specs = [
        ("finding_0", 4.0, "in"),   # WARN — hypotension contradiction
        ("finding_1", 5.5, "in"),   # CRITICAL — epi for narrow-complex tach
        ("finding_2", 4.0, "in"),   # CRITICAL — extubation criteria
        ("props",     3.0, "out"),  # ECG / monitor / CXR
        ("audio",     1.5, "in"),   # audio bench
    ]
    zoom_actual = 0.0
    for key, dur, direction in zoom_specs:
        still = ui_capture.stills.get(key)
        if still is None or not still.exists():
            print(f"  ! missing still: {key} (skipping {dur}s)")
            continue
        out = STAGING / f"Z_{key}.mp4"
        png_to_kenburns(still, dur, out, direction=direction)
        clip_paths.append(out)
        zoom_actual += dur

    # E · findings summary
    e = STAGING / "E.mp4"; png_to_clip(png_paths["E_findings.png"], 30.0, e); clip_paths.append(e)
    # F · close
    f = STAGING / "F.mp4"; png_to_clip(png_paths["F_close.png"], 14.0, f); clip_paths.append(f)

    total = int(round(6 + 14 + 18 + 10 + 70 + zoom_actual + 30 + 14))
    print(f"• Concatenating {len(clip_paths)} clips ({total}s)...")
    silent = STAGING / "silent_master.mp4"
    concat(clip_paths, silent)

    print("• Mixing ICU ambient bed...")
    mix_music(silent, ICU_BED, duration=float(total), out=FINAL_MP4)

    size_mb = FINAL_MP4.stat().st_size / 1_048_576
    print(f"\n✓ {FINAL_MP4.relative_to(REPO)}  ({total}s, {size_mb:.1f} MB)")


if __name__ == "__main__":
    sys.exit(main())
