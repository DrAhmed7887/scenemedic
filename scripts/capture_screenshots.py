"""Generate high-resolution architecture cards and UI screenshots for docs/README."""
from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[1]
SCREENSHOTS_DIR = REPO / "assets" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080

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


def card_architecture(path: Path) -> None:
    img, d = new_canvas()
    draw_topbar(d, "Multi-Agent Architecture & Cloud Pipeline")
    d.text((72, 110), "Vertex AI Agent Engine + BigQuery Vector Search + ClickHouse",
           font=font(FONT_BOLD, 42), fill=INK)

    # Row 1 — Autonomous Sub-Agents
    row1 = [
        ("1. Script Parser", "Document AI + Regex", ACCENT),
        ("2. Continuity Engine", "ClickHouse Cloud (MCP)", (250, 204, 21)),
        ("3. Clinical Accuracy", "BigQuery Vector Search", OK),
        ("4. Dramatization", "Voice-Preserving Rewrites", (168, 85, 247)),
    ]
    box_w, box_h = 410, 210
    gap = 26
    total_w = len(row1) * box_w + (len(row1) - 1) * gap
    x0 = (W - total_w) // 2
    y0 = 230
    for i, (title, sub, col) in enumerate(row1):
        x = x0 + i * (box_w + gap)
        d.rounded_rectangle((x, y0, x + box_w, y0 + box_h), radius=16,
                             outline=col, width=3, fill=(18, 24, 42))
        d.text((x + 22, y0 + 26), title, font=font(FONT_BOLD, 30), fill=INK)
        d.text((x + 22, y0 + 84), sub, font=font(FONT_REG, 24), fill=DIM)
        d.rectangle((x + 22, y0 + 160, x + 120, y0 + 164), fill=col)

    # Row 2 — GenMedia & Live Layer
    row2 = [
        ("5. VFX / Props", "Imagen 3 + Flash Image", ACCENT),
        ("6. Audio / Foley", "Lyria-002 Ambient Beds", ACCENT),
        ("7. Table Read", "Gemini Multi-Speaker TTS", (250, 204, 21)),
        ("8. Actor Rehearsal", "Gemini Live API (Bidirectional)", OK),
    ]
    y1 = y0 + box_h + 60
    for i, (title, sub, col) in enumerate(row2):
        x = x0 + i * (box_w + gap)
        d.rounded_rectangle((x, y1, x + box_w, y1 + box_h), radius=16,
                             outline=col, width=2, fill=(15, 20, 36))
        d.text((x + 22, y1 + 26), title, font=font(FONT_BOLD, 28), fill=INK)
        d.text((x + 22, y1 + 84), sub, font=font(FONT_REG, 24), fill=DIM)
        d.rectangle((x + 22, y1 + 160, x + 120, y1 + 164), fill=col)

    # Footer Cloud Infrastructure Details
    d.rectangle((72, H - 180, W - 72, H - 50), outline=ACCENT, width=1, fill=(13, 19, 33))
    d.text((96, H - 155), "CLOUD DEPLOYMENT TELEMETRY", font=font(FONT_BOLD, 22), fill=ACCENT)
    cloud_info = (
        "• Vertex Agent Engine: projects/159973996965/locations/us-central1/reasoningEngines/5192502486044246016\n"
        "• Grounding: BigQuery Vector Search (3072-dim gemini-embedding-001) | State: ClickHouse Cloud MCP | Cost Guard: Pub/Sub Kill-Switch"
    )
    y_text = H - 120
    for line in cloud_info.split("\n"):
        d.text((96, y_text), line, font=font(FONT_REG, 20), fill=DIM)
        y_text += 28

    img.save(path)


def card_findings(path: Path) -> None:
    img, d = new_canvas()
    draw_topbar(d, "Clinical Realism Audit · Outliers Ep 07 Scene 12")
    d.text((72, 110), "Grounded Clinical Findings & Voice-Preserving Rewrites",
           font=font(FONT_BOLD, 42), fill=INK)

    findings = [
        (WARN, "WARN", "Line 5 — \"Stable narrow-complex tach, hypotensive.\"",
         "CONTRADICTION: Tachycardia accompanied by hypotension (BP 88/54) is unstable by definition.\n"
         "GROUNDING: AHA Adult Tachycardia Algorithm (cpr.heart.org)\n"
         "REWRITE: \"Unstable narrow-complex tach. She's hypotensive.\""),
        (CRIT, "CRITICAL", "Line 6 — \"Push one of epi, IV. Now.\"",
         "CONTRAINDICATION: Epinephrine is contraindicated for narrow-complex tachycardia with pulse. First-line is vagal/adenosine 6mg.\n"
         "GROUNDING: AHA ACLS Guidelines 2025 (cpr.heart.org)\n"
         "REWRITE: \"Pads on. We're cardioverting. Now.\" / \"Sync at 100.\""),
        (CRIT, "CRITICAL", "Line 14 — \"Extubate her.\"",
         "SAFETY VIOLATION: Immediate extubation 3 minutes post-ROSC violates ATS readiness criteria (requires SBT, intact airway reflexes).\n"
         "GROUNDING: ATS Extubation Readiness Criteria (thoracic.org)\n"
         "REWRITE: \"Secure that tube. Page the ICU now.\""),
    ]
    y = 210
    for col, tag, title, body in findings:
        d.rounded_rectangle((72, y, W - 72, y + 230), radius=14,
                             fill=(18, 24, 42), outline=col, width=3)
        d.rectangle((72, y, 84, y + 230), fill=col)
        d.text((110, y + 20), tag, font=font(FONT_BLACK, 24), fill=col)
        d.text((110, y + 54), title, font=font(FONT_BOLD, 28), fill=INK)
        lines = body.split("\n")
        y_sub = y + 96
        for line in lines:
            d.text((110, y_sub), line, font=font(FONT_REG, 22), fill=DIM)
            y_sub += 36
        y += 260
    img.save(path)


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def wait_port(port: int, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError(f"Port {port} never came up")


def capture_ui_screenshots(port: int) -> None:
    print(f"Launching Streamlit on port {port}...")
    env = {**os.environ, "STREAMLIT_SERVER_HEADLESS": "true"}
    proc = subprocess.Popen(
        [str(REPO / ".venv/bin/streamlit"), "run", str(REPO / "ui/app.py"),
         "--server.port", str(port),
         "--server.headless", "true",
         "--server.address", "127.0.0.1",
         "--browser.gatherUsageStats", "false"],
        cwd=REPO, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        wait_port(port)
        print("Streamlit is up! Capturing with Playwright...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle", timeout=30_000)
            page.wait_for_timeout(2000)

            # 1. Initial UI state
            page.screenshot(path=str(SCREENSHOTS_DIR / "01_ui_initial.png"))
            print("Saved 01_ui_initial.png")

            # 2. Click canned demo (safe)
            page.get_by_role("button", name="Play canned demo (safe)").click()
            page.wait_for_timeout(3000)

            # 3. Full writers room view
            page.screenshot(path=str(SCREENSHOTS_DIR / "02_ui_full_writers_room.png"))
            print("Saved 02_ui_full_writers_room.png")

            # 4. Scroll to show findings and props in detail
            page.evaluate("window.scrollTo(0, 300)")
            page.wait_for_timeout(1000)
            page.screenshot(path=str(SCREENSHOTS_DIR / "03_ui_findings_and_props.png"))
            print("Saved 03_ui_findings_and_props.png")

            # 5. Scroll to bottom for audio bench and continuity
            page.evaluate("window.scrollTo(0, 800)")
            page.wait_for_timeout(1000)
            page.screenshot(path=str(SCREENSHOTS_DIR / "04_ui_audio_and_continuity.png"))
            print("Saved 04_ui_audio_and_continuity.png")

            browser.close()
    finally:
        proc.terminate()
        proc.wait()


def main() -> None:
    print("Generating Architecture and Findings cards...")
    card_architecture(SCREENSHOTS_DIR / "architecture_flow.png")
    card_findings(SCREENSHOTS_DIR / "clinical_audit_findings.png")
    print("Cards generated successfully.")

    try:
        port = free_port()
        capture_ui_screenshots(port)
        print("All screenshots generated successfully in assets/screenshots/!")
    except Exception as e:
        print(f"Playwright screenshot error: {e}")


if __name__ == "__main__":
    main()
