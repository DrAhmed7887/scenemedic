# Claude Code Handoff — Cloud Console Screenshot Capture

**Fires only after** both Copilot + Antigravity punch lists arrive in `docs/AUDIT_MERGED_CAPTURE_CLOUD.md`.

## Mission

Extend `scripts/capture_screenshots.py` to automatically capture 10 cloud console screenshots proving live infrastructure usage. This gives judges concrete Tech-Impl (25%) and Idea-Quality (25%) evidence for the SceneMedic Agentic Cinema submission. Also patches the stale references at `capture_screenshots.py:204-217` (the deleted duplicate PNGs).

Output: 10 new PNGs under `assets/screenshots/cloud/`, plus doc embeds in `SUBMISSION.md` and `AGENT_WORKFLOW_AND_CLOUD_TELEMETRY.md`.

## Reality check — read this before touching Playwright

Google Cloud + ClickHouse Cloud consoles gate on OAuth. Fully headless-Playwright-into-console does NOT work without stored session state (OAuth redirects break automation). Two viable patterns:

**Pattern A — CLI receipts (deterministic, no auth flow in code).**
Use `gcloud`, `bq`, and `clickhouse-connect` CLI/Python to fetch the data, render clean terminal PNGs via `rich.console.export_svg` → PNG or `Pillow`. Works for 6 of the 10 shots.

**Pattern B — Playwright + stored `storage_state`.**
Ahmed logs into GCP + ClickHouse consoles ONCE in a real browser, saves the storage state to `assets/.storage_state_gcp.json` and `assets/.storage_state_clickhouse.json` (gitignored). Playwright reuses that state for headless capture. Works for the 4 shots that need actual console UI.

Use Pattern A wherever possible. Pattern B only when the console UI itself is the evidence.

## Files likely involved

- `scripts/capture_screenshots.py` — REFACTOR (add cloud capture)
- `scripts/render_cli_receipt.py` — NEW (subprocess → terminal PNG helper)
- `scripts/capture_cloud_console.py` — NEW (Playwright + storage_state, split from main script)
- `assets/screenshots/cloud/` — NEW directory
- `assets/.storage_state_gcp.json` — NEW, gitignored, Ahmed provides
- `assets/.storage_state_clickhouse.json` — NEW, gitignored, Ahmed provides
- `.gitignore` — ADD `assets/.storage_state_*.json`
- `docs/SUBMISSION.md`, `docs/AGENT_WORKFLOW_AND_CLOUD_TELEMETRY.md` — embed new shots

## Shot list

| # | File | Method | Prereq |
|---|------|--------|--------|
| 1 | `cloud/01_gcloud_auth.png` | Pattern A: `gcloud config list` + `gcloud auth list` | `gcloud` authenticated |
| 2 | `cloud/02_agent_engine_list.png` | Pattern A: `gcloud ai reasoning-engines list --project=scenemedic-hackathon --region=us-central1` | GCP project |
| 3 | `cloud/03_bq_pubmed_schema.png` | Pattern A: `bq show --schema scenemedic-hackathon:scenemedic.pubmed_chunks` | bq CLI |
| 4 | `cloud/04_bq_vector_search_query.png` | Pattern A: run BQ vector search SQL for AHA Tachycardia, render result table | bq CLI + query file |
| 5 | `cloud/05_clickhouse_tables.png` | Pattern A: `clickhouse-connect` query `SHOW TABLES FROM scenemedic` | ClickHouse creds in `.env` |
| 6 | `cloud/06_clickhouse_maya_row.png` | Pattern A: `SELECT * FROM patient_episodes WHERE character='Maya Chen'` | ClickHouse creds |
| 7 | `cloud/07_agent_engine_console.png` | Pattern B: Playwright to Vertex AI Agent Engine detail page | `storage_state_gcp.json` |
| 8 | `cloud/08_bq_vector_search_console.png` | Pattern B: BigQuery console showing vector index on `pubmed_chunks` | `storage_state_gcp.json` |
| 9 | `cloud/09_clickhouse_cloud_console.png` | Pattern B: ClickHouse Cloud service detail page | `storage_state_clickhouse.json` |
| 10 | `cloud/10_billing_budget.png` | Pattern B: GCP Billing budget page showing $10 cap + pub/sub halt | `storage_state_gcp.json` |

## Hard constraints

1. **No live LLM calls.** Read from BigQuery and ClickHouse, do not invoke Gemini / Imagen / Lyria / TTS during capture — that costs money.
2. **No screenshots may include real secrets.** Redact any auth token, service account key, ClickHouse password, or billing email visible in a shot. Prefer masked output over post-hoc image editing.
3. **`storage_state` files are gitignored, never committed.** Verify `.gitignore` before writing them.
4. **No changes to `agents/`, `tools/`, or `ui/`.** This is a screenshot task.
5. **Idempotent.** Running the script twice produces the same shots. Overwrites, doesn't append.
6. **Skips gracefully.** If a storage_state is missing, print a clear "run manual auth first" message and skip that shot — do not fail the whole run.
7. **CLI receipts must be readable at 720p downscale.** Use a monospace font ≥18pt equivalent; dark background with high contrast.
8. **Terminal PNGs must show a fake but plausible prompt.** Not `ahmedzayed@ahmeds-macbook`; use `scenemedic@build`. Consistent across all 6 CLI shots.
9. **BigQuery vector search query must be the SAME query the demo agent runs** — read it from `tools/rag_pubmed.py` or hardcode the exact SQL from that file. Don't invent.
10. **Fix the stale references at `capture_screenshots.py:204-217`** — those save `02_ui_full_writers_room.png` (renamed), `03_ui_findings_and_props.png` (deleted), `04_ui_audio_and_continuity.png` (deleted). Update to write only one distinct UI shot at `02_ui_writers_room.png`; drop 03 and 04.

## Guidance (use judgement)

- Terminal rendering: `rich` (already a common dependency) or plain Pillow + monospace font. `rich.console.Console(record=True).export_svg()` → convert to PNG with `cairosvg` or `resvg`. Pick the path with fewest new deps.
- Vector search result table: don't dump raw JSON — format as a `rich.Table` with columns [rank, score, title, source_url]. Top 5 rows.
- Storage state auth: give Ahmed a one-liner CLI command like `.venv/bin/python scripts/capture_cloud_console.py --auth gcp` that opens a headed browser once, waits for him to complete OAuth, then saves state and exits.
- Console shot cropping: use Playwright's `locator.screenshot()` on the main content panel, not the full page — sidebar/header noise makes shots read as generic.
- File naming: zero-pad (`01_`, `02_`) so shots list in shoot-order.
- `.env` handling: fail loudly if `CLICKHOUSE_URL` etc. missing.

## Suggested workflow

1. Read `scripts/capture_screenshots.py`, `tools/clickhouse_mcp.py`, `tools/rag_pubmed.py`, `deploy/agent_engine.py`, `docs/AUDIT_MERGED_CAPTURE_CLOUD.md`.
2. Draft `scripts/render_cli_receipt.py` — one function `render(cmd: list[str], output: Path, prompt: str = "scenemedic@build") -> None` that runs the command, captures stdout, renders as PNG.
3. Draft `scripts/capture_cloud_console.py` — Playwright wrapper with `--auth {gcp,clickhouse}` mode for the one-time login, and default mode for headless captures using the saved state.
4. Refactor `scripts/capture_screenshots.py`:
   - Move UI capture out into a `capture_ui()` function.
   - Add `capture_cloud()` that dispatches to `render_cli_receipt` for shots 1-6 and `capture_cloud_console` for shots 7-10.
   - Fix the `02/03/04` stale writes → single `02_ui_writers_room.png`.
5. Update `.gitignore` for storage_state files.
6. Add doc embeds to `SUBMISSION.md` under a new "Cloud infrastructure receipts" section.
7. Run once, review all 10 PNGs, confirm no leaked secrets.

## Tests to run

- `.venv/bin/python scripts/capture_screenshots.py --dry-run` (add this flag) — must print the shot plan without executing.
- `.venv/bin/python scripts/capture_screenshots.py` — full run; expect 6-10 PNGs depending on storage_state availability.
- `file assets/screenshots/cloud/*.png` — all PNG.
- `identify -format "%wx%h\n" assets/screenshots/cloud/*.png` — all ≥1200×675 (16:9-ish, readable).
- Manual visual review: no secrets, all shots have consistent prompt string.

## Stop conditions

Stop and hand back if:
- `gcloud auth` shows no active account.
- ClickHouse creds missing from `.env`.
- Any shot would leak a secret and the redaction path isn't clean.
- Playwright storage_state approach fails on Devpost-blocked accounts.
- Console UI has changed enough that selectors don't match — flag, don't guess.

Do NOT commit to git without Ahmed's approval.

## Reference

- `docs/AGENTIC_CINEMA_JUDGING.md` — official rules (partner track is mandatory)
- `docs/PITCH.md` — v2 timeline references ClickHouse + BigQuery visually
- `docs/AUDIT_MERGED_CAPTURE_CLOUD.md` — dual-audit punch list (must exist before this fires)
