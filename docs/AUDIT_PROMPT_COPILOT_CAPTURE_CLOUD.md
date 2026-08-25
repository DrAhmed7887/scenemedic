# Copilot Pre-Audit — Cloud Console Screenshot Capture

**Tag:** `pre-audit-capture-cloud-copilot`
**Fires before:** any edits to `scripts/capture_screenshots.py` or new capture scripts.
**Output:** `docs/AUDIT_COPILOT_CAPTURE_CLOUD.md`. Merged with Antigravity into `docs/AUDIT_MERGED_CAPTURE_CLOUD.md`.

## Load first

1. `scripts/capture_screenshots.py` (current — 220 lines-ish).
2. `docs/HANDOFF_CLAUDE_CODE_CAPTURE_CLOUD.md` (refactor spec).
3. `tools/clickhouse_mcp.py`, `tools/rag_pubmed.py`, `deploy/agent_engine.py`.
4. `.env.example`.
5. `.gitignore`.

## Your job

Code-change lens. Focus areas:

### P0 (blockers)

1. Secret leakage risk — any code path that could write a `CLICKHOUSE_PASSWORD`, service account key, or auth token to a PNG. Read every subprocess.run/print/rich.log in the proposed shot 1-6 path.
2. `storage_state` files hitting git — verify the `.gitignore` addition covers both files, and that no other pattern (e.g. `assets/**` includes) counteracts it.
3. Any hardcoded absolute path (e.g. font paths, gcloud path) that would break outside Ahmed's Mac.
4. Existing `capture_screenshots.py:204-217` writing to deleted files (`03_ui_findings_and_props.png`, `04_ui_audio_and_continuity.png`) — verify the refactor removes these writes cleanly, not just comments them out.
5. `bq` / `gcloud` / `clickhouse-connect` dependency — verify they're already in `requirements.txt` / `pyproject.toml` or flag as missing.
6. Any query in the shot list that would incur BigQuery Vector Search cost >$0.10 per capture run — flag with cost estimate.

### P1 (correctness)

1. Idempotence — running the script twice must produce byte-identical PNGs (modulo timestamps). Flag any nondeterministic pattern (dict iteration order, timezone-in-output, PID in prompt).
2. `--dry-run` flag actually skips all side effects — no BQ query, no ClickHouse SELECT, no filesystem write.
3. Terminal PNG font rendering — is there a fallback if the chosen monospace font isn't installed on macOS? (SF Mono is default; still verify.)
4. Playwright timeouts — proposed shot 7-10 each need a `wait_for_load_state("networkidle")` before screenshot, or they'll capture loading spinners.
5. BigQuery vector search SQL — verify it matches whatever `tools/rag_pubmed.py` actually runs. If the SQL diverges, judges see one thing in the doc and something else in the code.
6. `capture_ui()` split — verify the current UI capture logic (existing Streamlit + Playwright path) is preserved bit-for-bit, just moved into a function. No behavior drift.

### P2 (cleanup, optional)

1. `subprocess.run(check=True)` vs manual error handling — pick one, be consistent.
2. Type annotations on new functions.
3. `print()` vs `logging` for the new CLI receipt output.

## What NOT to do

- Don't propose replacing Playwright with Puppeteer/Selenium.
- Don't propose replacing `rich` with a custom renderer if Rich already installed.
- Don't audit console UI selectors — Antigravity handles the visual/UX lens.
- Don't audit `agents/` or `tools/` beyond the specific call sites the capture script hits.

## Output format

Same structure as the pitch-video audit:

```markdown
# Copilot Punch List — Cloud Capture

## P0
- [ ] <finding> — file:line — <fix>

## P1
- [ ] ...

## P2
- [ ] ...

## Assumptions I made

## Things I didn't audit
```

Stop condition: one pass, no back-and-forth.
