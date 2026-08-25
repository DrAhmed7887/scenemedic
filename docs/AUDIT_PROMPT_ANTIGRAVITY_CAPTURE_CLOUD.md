# Antigravity Pre-Audit — Cloud Console Screenshot Capture

**Tag:** `pre-audit-capture-cloud-antigravity`
**Fires before:** any edits to `scripts/capture_screenshots.py` or new capture scripts.
**Output:** `docs/AUDIT_ANTIGRAVITY_CAPTURE_CLOUD.md`. Merged with Copilot into `docs/AUDIT_MERGED_CAPTURE_CLOUD.md`.

## Load first

1. `docs/HANDOFF_CLAUDE_CODE_CAPTURE_CLOUD.md`.
2. `docs/AGENTIC_CINEMA_JUDGING.md` (25% Tech Impl + 25% Idea Quality lens).
3. `docs/PITCH_VIDEO_RUBRIC.md` (row 7: services named at moment invoked; row 8: partner track visible).
4. `docs/SUBMISSION.md`.
5. Existing `assets/screenshots/01_ui_initial.png` and `02_ui_writers_room.png` — for context on visual style.

## Your job — judge-perception lens

Play a Google Cloud judge who has already watched the video and is now scrolling the README + SUBMISSION.md looking for proof. Each cloud screenshot has to earn its slot. Focus:

### P0 (auto-skip risk)

1. **Do these 10 shots actually prove infrastructure exists, or do they read as staged screenshots?** For each shot 1-10, imagine what a skeptical judge sees. Does shot 4 (BQ vector search result) show a real query returning a real match, or a hand-typed table? Flag any shot whose "authenticity signal" is weak.
2. **Are the CLI receipts (shots 1-6) recognizably real gcloud/bq/clickhouse output, or do they look like decorative terminal art?** Terminal PNGs can slide into "fake" territory. Flag if the proposed rendering strips too much of the raw output.
3. **Does the ClickHouse partner track evidence actually land?** Shots 5, 6, 9 are the ClickHouse story. Are three shots the right count, or is one Cloud console + one Maya row enough?
4. **Missing shot: multi-agent orchestration trace.** The pitch rubric row 4 wants "multi-agent handoff visible." Neither the video swimlane (a pre-rendered PNG) nor any of the 10 cloud shots proves the agents actually talked to each other in real invocation logs. Flag whether a Vertex Agent Engine invocation trace should be added.
5. **Secret redaction reads as evidence, not censorship.** If a shot has "REDACTED" bars everywhere, judges assume "this isn't real." Flag any shot where redaction would consume >20% of the image.

### P1 (scoring drift)

1. **Consistency with the video overlays.** The pitch v2 burns service badges at specific timestamps (Vertex Engine 0:52, BQ VS 1:18, ClickHouse MCP 1:22, Imagen 3 1:41, Lyria-002 1:52, Gemini TTS 1:58). Do the cloud shots cover the same services in the same order?
2. **Grafana Cloud absence.** Docs mention Grafana Cloud traces. If no Grafana shot exists in the 10, is that OK, or is it a missing signal for a judge scoring Design (25%)?
3. **Billing budget shot (10) framing** — showing a $10 cap is a governance flex, but too much emphasis on cost caps could signal "toy project, no real load." Where should this shot live in the doc — SUBMISSION.md top or telemetry appendix?
4. **The `scenemedic@build` fake prompt convention** — is that credible, or does it read as staged? Alternative: use `scenemedic@vertex-shell` or leave the real hostname (redacted username only).
5. **Shot 6 (Maya Chen canon row) — is the row content itself convincing?** Judges will read it. Verify the schema + data would look like a real production row, not a hackathon fixture.

### P2 (polish)

1. Directory naming — `assets/screenshots/cloud/` vs `assets/screenshots/infrastructure/` vs `docs/cloud_receipts/`.
2. Doc embed placement — inline in SUBMISSION.md sections, or separate `docs/CLOUD_RECEIPTS.md` referenced from SUBMISSION.md.
3. Whether the README needs a subset of the 10 shots or just links to SUBMISSION.md.

## What NOT to do

- Don't audit Python code style — Copilot has that lane.
- Don't propose additional cloud services to prove (already at 10 shots).
- Don't propose animated GIFs or video captures instead of stills.
- Don't propose replacing screenshots with a live-hosted dashboard link — judges review async, they need static proof.

## Output format

```markdown
# Antigravity Punch List — Cloud Capture

## P0 (judge skip)
- [ ] <finding> — shot #X — <fix>

## P1 (scoring)
- [ ] ...

## P2 (polish)
- [ ] ...

## Judge role-play notes
- <2-3 sentence "what I felt scrolling these 10 shots">

## Assumptions I made

## Things I didn't audit
```

Stop condition: one pass, no back-and-forth.
