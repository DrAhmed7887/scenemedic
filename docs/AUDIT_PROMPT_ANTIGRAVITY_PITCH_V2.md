# Antigravity Pre-Audit — Pitch Video v2 refactor

**Tag:** `pre-audit-pitch-v2-antigravity`
**Fires before:** any Claude Code edits to `scripts/generate_pitch_video.py` for the v2 refactor.
**Merge protocol:** output punch list to `docs/AUDIT_ANTIGRAVITY_PITCH_V2.md`. Ahmed merges Copilot + Antigravity findings into `docs/AUDIT_MERGED_PITCH_V2.md` before Claude Code fires.

## Context to load first

1. `scripts/generate_pitch_video.py` — full file.
2. `docs/PITCH.md` — v2 timeline and VO script.
3. `docs/HANDOFF_CLAUDE_CODE_PITCH_V2.md` — the refactor spec.
4. `docs/PITCH_VIDEO_RUBRIC.md`, `docs/AGENTIC_CINEMA_JUDGING.md`.
5. `docs/ARCHITECTURE.md`, `docs/AGENT_WORKFLOW_AND_CLOUD_TELEMETRY.md`.
6. `outputs/scenemedic_pitch_demo.mp4` (v1) — watch it. This is what we're replacing.
7. `assets/screenshots/` — v1 stills, will inform overlay design.

## Your job — different lens from Copilot

Copilot is auditing the code-change surface. **You audit the judge-perception surface.** Play a Google Cloud judge who is watching 476 submissions in 3 days and has 15 seconds per pitch to decide "keep watching or skip."

Focus areas, in priority order:

### P0 — auto-DQ or auto-skip

1. **Ambiguity in whether the video actually shows the multi-agent handoff.** Watch v1. Then read v2 spec. Would a judge see agents talking to each other, or would they see cards describing them? If the latter, flag it hard. This is the #1 differentiator per `PITCH_VIDEO_RUBRIC.md` row 4.
2. **Cold-open credibility.** v2 opens on a UI frame with a red CRITICAL badge before Ahmed even speaks. Is that frame legible at 720p downscale? Does it read as "product working" or "screenshot of a slide"?
3. **VO register mismatch.** Read the VO copy in `PITCH.md`. Does it match "physician case-handover — direct, quiet, factual"? Flag any line that reads as marketing, motivational, or LinkedIn-influencer voice (Ahmed's hard NO).
4. **Missing "why should we believe this" moment.** In v1 there's no grounding proof visible. v2 adds a citation zoom at 2:10. Verify that moment is actually convincing to a judge — is the URL readable? Does the VO frame it as an anti-hallucination guarantee, not a feature?
5. **Partner-track callout timing.** ClickHouse MCP is called out at 0:35 for 3s. Is 3s enough for a judge to register? Is the lower-third readable at 720p?
6. **The 5,000-dollar claim.** Judges will notice unsourced stats. `PITCH.md` v2 adds "WGA/Variety 2024" caption. Verify this citation actually exists and is loadable — if not, propose a substitute or trim the claim.

### P1 — scoring drift

1. **Design criterion (25%)** — the current v1 uses a monochrome palette. Is that "coherent product experience" or "engineering render"? Flag if the palette needs adjustment for the Design 25% weight.
2. **Potential Impact criterion (25%)** — does the VO name a specific vertical (medical drama writers' rooms — Grey's, House, ER) or does it stay abstract? Winners named their vertical (per ADK 2025 pattern).
3. **Ken Burns pacing** — 4s on WARN, 5.5s on CRITICAL, 4s on CRITICAL, 3s on props. Watch v1 and judge whether this rhythm holds attention or drags.
4. **Google-service badge coherence** — 5 services flashed in 66s (0:52 → 1:58). Does that read as "look how many Google things we use" (loser pattern per rubric) or "each service earns its moment"?
5. **Closing card impact** — "The moat isn't the code. A physician built it." is currently in v1. Verify it lands after the VO, not before.

### P2 — small polish

1. Font choice (Arial Bold/Black) — is it too corporate? Is there a better free web font available?
2. ICU ambient bed volume during VO — spec says −18 dB bed / −24 dB during VO. Verify audible-under-VO without being distracting.
3. Byline placement.

## What NOT to do

- Do NOT audit code style. Copilot has that lane.
- Do NOT propose architectural changes to `agents/` or `tools/`.
- Do NOT propose changes to the VO copy itself except to flag register violations (Ahmed writes his own VO copy).
- Do NOT recommend adding a founder-team montage, roadmap animation, or "raising a round" language.
- Do NOT recommend adding music transitions/stingers — the ICU bed is the whole score.

## Output format

Write to `docs/AUDIT_ANTIGRAVITY_PITCH_V2.md`:

```markdown
# Antigravity Punch List — Pitch Video v2

## P0 (judge auto-DQ or auto-skip)
- [ ] <finding> — timestamp:XX — <one-line fix>
- [ ] ...

## P1 (scoring drift)
- [ ] ...

## P2 (polish, optional)
- [ ] ...

## Judge role-play notes
- <2-3 sentence "what I felt watching this" from the judge POV>

## Assumptions I made
- <ambiguity + interpretation>

## Things I didn't audit
- <scope I explicitly stayed out of>
```

## Stop condition

One pass. No questions back — flag ambiguity in "Assumptions I made." Do not edit any file.
