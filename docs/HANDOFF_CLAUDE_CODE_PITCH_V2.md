# Claude Code Handoff — Pitch Video v2 refactor

**Trigger only after both Copilot + Antigravity punch lists arrive** (per the dual-audit rule). Do not begin edits before both audits complete and are merged into `docs/AUDIT_MERGED_PITCH_V2.md`.

## Mission

Refactor `scripts/generate_pitch_video.py` from a silent 182s reel to a fully compliant Agentic Cinema demo video: 2:52 total, English VO + burned captions, on-screen multi-agent swimlane overlay, on-screen Google-service lower-thirds at each call-site, ClickHouse MCP partner-track callout.

Output: `outputs/scenemedic_pitch_v2.mp4` (1920×1080, 30fps, H.264 + AAC, ≤50MB for Devpost upload comfort).

## Current state

- `scripts/generate_pitch_video.py` — 638 lines, produces silent 182s reel with ICU bed.
- `docs/PITCH.md` — v2 script with per-timestamp VO copy, overlays, and captions.
- `assets/voiceover/ahmed_vo_master.wav` — Ahmed's raw VO recording (single unbroken take, 48kHz preferred).
- `outputs/scenemedic_pitch_demo.mp4` — v1 silent reel (keep as backup, do NOT overwrite).
- `assets/fallback_icu.wav` — existing Lyria-002 ICU bed.

## Files likely involved

- `scripts/generate_pitch_video.py` (primary — refactor)
- `scripts/vo_align.py` (NEW — VO-to-timeline alignment helper, see below)
- `scripts/render_captions.py` (NEW — SRT/ASS generation from `PITCH.md` table)
- `assets/voiceover/ahmed_vo_master.wav` (NEW — Ahmed provides)
- `assets/voiceover/vo_segments/` (NEW — auto-sliced per section)
- `assets/overlays/swimlane_4agent.png` (NEW — pre-rendered swimlane graphic; render at 1920×1080 with transparent lanes lighting up as separate PNG frames or as an SVG-to-PNG sequence)
- `assets/overlays/service_lowerthirds/` (NEW — one PNG per Google service: `vertex.png`, `bigquery.png`, `imagen3.png`, `lyria002.png`, `gemini_tts.png`)
- `assets/overlays/partner_clickhouse.png` (NEW)
- `docs/PITCH.md` (READ ONLY — source of truth for timings + VO copy)
- `outputs/scenemedic_pitch_v2.mp4` (target)

## Hard constraints

1. **Do NOT overwrite `outputs/scenemedic_pitch_demo.mp4`** — that's the v1 backup. Write to `_v2.mp4`.
2. **Do NOT change any agent code under `agents/` or `tools/`** — this is a video-render task only. If a bug in an agent surfaces, flag it and stop.
3. **Do NOT introduce new external dependencies** without a justified reason. Playwright, Pillow, ffmpeg (subprocess) are already in use — extend those. Adding whisper for VO alignment is acceptable only if `python-webvtt` or manual timestamp table proves insufficient.
4. **≤2:55 total runtime.** Assert on the ffprobe duration at the end and fail the build if over.
5. **Aspect ratio 16:9, resolution 1920×1080, fps 30, codec H.264 (yuv420p), audio AAC 48kHz.** Match Devpost/YouTube/Vimeo expectations.
6. **English captions burned into the video** (not sidecar SRT). Use the exact VO copy from `docs/PITCH.md`.
7. **Do NOT scrape or make live API calls** during the render. The demo is offline-safe. All assets are pre-baked.
8. **Do NOT run the deployed Streamlit against live GCP** during the render — use `--server.headless` local Streamlit with the canned demo path already wired in `ui/app.py`.
9. **Do NOT change the Lyria model ID.** `tools/lyria3.py:17` uses `lyria-002` — that's correct; Devpost's Lyria 3 mention is aspirational, keep `lyria-002` in code.
10. **No hardcoded paths outside `REPO = Path(__file__).resolve().parents[1]`.**

## Guidance (not hard rules — use judgement)

- The existing `png_to_kenburns`, `png_to_clip`, `webm_to_clip`, `concat`, `mix_music` helpers are good — extend, don't rewrite.
- For the swimlane overlay: the cheapest correct approach is 4 pre-rendered PNGs (each lane lit up in sequence) that ffmpeg overlays on the Playwright reel via `overlay=x:y:enable='between(t,X,Y)'` filter expressions. Don't build a real-time renderer.
- For service lower-thirds: same overlay pattern, 5 PNGs, appearing at their assigned timestamps.
- For captions: cheapest correct approach is drawtext filter with a hardcoded table of `(start, end, text)` triples derived from `PITCH.md`. Don't build an SRT parser unless the table gets unwieldy.
- For VO alignment: since Ahmed reads at his own pace, cut the master VO into 15 segments (one per row in PITCH.md), let the editor slot each segment at its assigned timestamp with a small time-stretch (±10% max) using ffmpeg's `atempo` filter. If a segment is >10% off, flag it and don't ship — ask Ahmed to re-record that section.
- For the ICU bed: keep the existing `mix_music` pattern but drop VO segments in as a second audio track, mix at −4 dB VO / −18 dB bed. Fade bed to −24 dB during VO, back to −18 dB in gaps.
- Preserve the existing `card_*` renderers — the v2 timing changes durations but not the card content.

## Suggested workflow

1. Read `docs/PITCH.md`, `docs/PITCH_VIDEO_RUBRIC.md`, `docs/AGENTIC_CINEMA_JUDGING.md`, this file. In that order.
2. Read `scripts/generate_pitch_video.py` end-to-end.
3. Read the merged audit doc `docs/AUDIT_MERGED_PITCH_V2.md`. Address every P0 and P1 punch-list item before writing new code.
4. Draft `assets/overlays/*.png` (swimlane frames + service badges + partner badge) with Pillow — put the render logic in a new `scripts/render_overlays.py`. These are one-shot; commit the PNGs.
5. Write `scripts/vo_align.py` — cuts `assets/voiceover/ahmed_vo_master.wav` into 15 segments matching the `PITCH.md` table.
6. Refactor `scripts/generate_pitch_video.py`:
   - Add a top-level `TIMELINE` constant mirroring the `PITCH.md` table (single source of truth).
   - Add overlay + caption + VO handling to the ffmpeg pipeline.
   - Adjust `card_*` clip durations per the new table.
   - Trim the Playwright walkthrough to hit the exact 20s + 12s + 20s + 8s + 12s + 10s sub-segments.
7. Assert final duration ≤175s at the end.
8. Run the test suite; add one new test that ffprobe-validates the final MP4 (duration, codec, aspect ratio).
9. Verify the final MP4 plays in QuickTime, VLC, and Chrome. Manual step.

## Tests to run

- `.venv/bin/pytest tests/` — must pass, including any new duration assertion.
- `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 outputs/scenemedic_pitch_v2.mp4` — must return ≤175.
- `ffprobe -v error -select_streams v:0 -show_entries stream=width,height,codec_name,r_frame_rate outputs/scenemedic_pitch_v2.mp4` — must return 1920x1080, h264, 30/1.
- Visual sanity check: play the MP4 end-to-end once, confirm every overlay lands, captions are readable at 720p downscale.

## Stop conditions

Stop and hand back to Ahmed (do NOT keep iterating) if:
- Ahmed's VO recording doesn't exist at `assets/voiceover/ahmed_vo_master.wav`.
- Any VO segment needs >10% time-stretch to fit the table (means the read pace is off — Ahmed re-records).
- ffmpeg overlay filter fails on any timestamp.
- Final MP4 exceeds 175s despite trims.
- Any agent code under `agents/` or `tools/` would need to change for the render to work.

Do NOT commit to git without Ahmed's explicit approval — this workspace follows the Cowork rule "do not submit, push, publish without approval."

## Reference

- `docs/PITCH.md` — timeline source of truth
- `docs/PITCH_VIDEO_RUBRIC.md` — 10-point scoring rubric
- `docs/AGENTIC_CINEMA_JUDGING.md` — official rules gate
- `docs/AUDIT_MERGED_PITCH_V2.md` — Copilot + Antigravity punch lists (created before this handoff runs)
