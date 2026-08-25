# Copilot Pre-Audit — Pitch Video v2 refactor

**Tag:** `pre-audit-pitch-v2-copilot`
**Fires before:** any Claude Code edits to `scripts/generate_pitch_video.py` for the v2 refactor.
**Merge protocol:** output punch list to `docs/AUDIT_COPILOT_PITCH_V2.md`. Ahmed merges Copilot + Antigravity findings into `docs/AUDIT_MERGED_PITCH_V2.md` before Claude Code fires.

## Context to load first

1. `scripts/generate_pitch_video.py` — full file (638 lines).
2. `docs/PITCH.md` — v2 timeline and VO script (source of truth).
3. `docs/HANDOFF_CLAUDE_CODE_PITCH_V2.md` — the refactor spec Claude Code will follow.
4. `docs/PITCH_VIDEO_RUBRIC.md` — 10-point scoring rubric.
5. `docs/AGENTIC_CINEMA_JUDGING.md` — official Devpost rules.
6. `ui/app.py` — Streamlit UI being screen-recorded.
7. `assets/fallback_icu.wav`, `assets/screenshots/` — existing assets.

## Your job

Produce a punch-list that catches issues BEFORE Claude Code writes a single line. Focus areas, in priority order:

### P0 — will break the build or violate hackathon rules

1. Any timeline math in `docs/PITCH.md` that doesn't sum to ≤175s (2:55 with buffer).
2. Any overlay timestamp in `PITCH.md` that doesn't align to an actual moment in the Playwright reel — verify by reading `capture_ui()` and the scroll pattern in `generate_pitch_video.py`.
3. Any Google service overlay scheduled at a time when that service isn't actually invoked in the demo path (`agents/orchestrator.py` + `ui/app.py`).
4. Missing partner-track callout for ClickHouse MCP.
5. Any code path in the current `generate_pitch_video.py` that ffprobe/ffmpeg would fail on given the new mix step (VO + bed + burned captions in one pass).
6. Hardcoded font paths (`/System/Library/Fonts/Supplemental/*`) that would break in CI or on a different macOS version. Flag and propose fallback.
7. Assertion missing: final MP4 must be ≤175s. Flag if `main()` doesn't enforce this.

### P1 — will lose scoring points

1. Ken Burns durations that read as trailer-pacing (>5s per still) rather than demo-pacing. Cross-check against the 10-point rubric row 5 (end-to-end journey ≤90s).
2. Any Ken Burns zoom on a card that doesn't have an on-screen citation or agent handoff to justify the hold.
3. Cold-open logic — v2 spec wants a UI frame at 0:00-0:07. Verify Playwright can capture a still frame BEFORE the walkthrough starts. If not, flag the capture-order refactor.
4. VO-to-caption drift risk — the current spec has captions and VO in separate data structures. Recommend a single source of truth pattern (e.g. one Python list of dataclass entries with `start`, `end`, `text`, `overlays`).
5. Overlay layering — swimlane + service badge + captions all landing at the same timestamp. Verify ffmpeg z-order and readability.

### P2 — cleanup opportunities (only if trivial)

1. Duplicate ffmpeg invocations that could share a filtergraph.
2. Type annotations missing on new-looking function signatures.
3. Print statements that should be logging (`generate_pitch_video.py` uses `print` throughout — see `~/.claude/rules/python/hooks.md` warning).

## What NOT to do

- Do NOT edit any files. Punch list only.
- Do NOT propose architectural rewrites. The existing `png_to_clip` / `webm_to_clip` / `concat` / `mix_music` pipeline is fine; extend it.
- Do NOT flag test coverage as P0 — this is a render script, not a service; existing `tests/test_smoke.py` coverage is sufficient at this scope.
- Do NOT recommend switching from Playwright to another capture tool. It works.
- Do NOT recommend switching from Pillow to another image library.
- Do NOT audit `agents/` or `tools/` unless a specific caller in `generate_pitch_video.py` interacts with them.

## Output format

Write to `docs/AUDIT_COPILOT_PITCH_V2.md`:

```markdown
# Copilot Punch List — Pitch Video v2

## P0 (blockers)
- [ ] <finding> — file:line — <one-line fix>
- [ ] ...

## P1 (scoring)
- [ ] ...

## P2 (cleanup, optional)
- [ ] ...

## Assumptions I made
- <any place where the spec was ambiguous and I picked an interpretation>

## Things I didn't audit
- <scope I explicitly stayed out of>
```

## Stop condition

Return the punch list within one pass. Do not iterate. Do not ask me questions — flag ambiguity in "Assumptions I made."
