# SceneMedic — 2:52 Pitch Video (v2, VO-timed)

> **Version note.** Supersedes the silent 182s v1 reel. v1 scored 5/10 on the pitch rubric and failed 3 hard rules (length >3:00, no captions, no partner track callout). v2 targets 9/10 on `PITCH_VIDEO_RUBRIC.md` and passes all Agentic Cinema rules gates.

## Rules-gate compliance (from `AGENTIC_CINEMA_JUDGING.md`)

- **Length:** 2:52 (5s safety margin under the 3:00 hard cap).
- **Language:** English VO + burned-in English captions.
- **Format:** Demo, not trailer — VO narrates reasoning steps, tool calls, and outputs.
- **Partner track:** ClickHouse MCP — called out on-screen at 0:35 and 1:22.
- **Google services:** Vertex Agent Engine (0:52), BigQuery Vector Search (1:18), Imagen 3 (1:41), Lyria-002 (1:52), Gemini TTS (1:58) — each burned as an on-screen lower-third the moment its call fires.

## Timeline

| Time | Duration | Section | On-screen | Voiceover (Ahmed) | Overlays |
|------|----------|---------|-----------|-------------------|----------|
| 0:00 | 2s | **A · Cold-open** | Streamlit UI frame — a finding card mid-render, red CRITICAL badge visible | *(none — 2s of ICU bed at 0 dB, then duck to −18 dB)* | Product name lower-left: "SceneMedic" |
| 0:02 | 5s | **A · Hook** | Same UI, camera holds | "Medical dramas pay clinical consultants five thousand dollars an episode. And still ship errors that trend on medical Twitter the next morning." | Caption bar bottom |
| 0:07 | 8s | **A · Identity** | Cut to Title card (existing `card_title`) | "I'm Ahmed Zayed — physician, informatics engineer. I built the consultant Hollywood actually needs." | Byline: "MBBCh · Clinical AI · RWTH Aachen (Winter 26/27)" |
| 0:15 | 20s | **B · Problem stakes** | Existing `card_problem` — "$5,000 / episode" | "The consultant reads three episodes a week. They miss the ones that ship. And nobody has time to audit line-by-line — so bad medicine trends and viewers stop trusting the show." | Source caption: "WGA/Variety 2024" |
| 0:35 | 3s | **B · Partner reveal** | Full-screen partner lower-third | "Powered by ClickHouse MCP for cross-episode canon." | "Partner track: ClickHouse MCP" |
| 0:38 | 12s | **C · Architecture flyover** | Existing `card_architecture`, but trimmed to 12s | "Multi-agent on Google ADK and Vertex Agent Engine. Four reasoning agents. Four GenMedia agents. Every finding cites its source or it drops out." | Service badges highlight as named |
| 0:50 | 8s | **D · Episode setup** | Existing `card_ep_setup` | "Live demo. Outliers, Episode 07, Scene 12. Maya Chen — thirty-four, type 1 diabetes, ejection fraction thirty. Narrow-complex tach at 182. The script has three errors." | Vitals table |
| 0:58 | 20s | **UI · Upload + parse** | Playwright reel — script uploads, parser fires | "Script Parser Agent reads the scene. Document AI extracts characters, vitals, dialogue." | Overlay: "Agent 1 · Parser · Document AI" (0:58-1:02) |
| 1:18 | 12s | **UI · Continuity + Clinical** | Playwright reel continues — findings populate | "Continuity Engine queries ClickHouse — Maya's LVEF was thirty at end of last season, so 'stable narrow-complex tach' contradicts our own canon. Clinical Accuracy Agent queries BigQuery Vector Search over ACLS and PubMed." | Swimlane overlay lights up: Parser → Continuity → Clinical; badges "ClickHouse MCP" + "BigQuery Vector Search" |
| 1:30 | 20s | **UI · Findings zoom** | Ken Burns on `still_finding_0` and `still_finding_1` | "Finding one — warning. Hypotension makes this tach unstable by definition. Finding two — critical. Epinephrine is wrong for narrow-complex tach with a pulse. Adenosine six milligrams IV push. Source: AHA Adult Tachycardia Algorithm." | Citation URL card highlighted |
| 1:50 | 8s | **UI · Rewrite** | Ken Burns on `still_finding_2` — third finding + alternate rewrites | "Third finding — critical. Extubation three minutes post-ROSC. Dramatization Agent proposes three voice-preserving rewrites, each within thirty percent of the original line length." | Overlay: "Agent 4 · Dramatization" |
| 1:58 | 12s | **UI · GenMedia** | Ken Burns on `still_props` (fast) + `still_audio` | "Imagen 3 regenerates the bedside monitor with a rhythm-matched ECG. Gemini multi-speaker TTS reads the corrected Act 2 with distinct Attending, Resident, and patient voices. Lyria-002 lays an ICU ambient bed underneath." | Sequential badges: "Imagen 3" → "Gemini TTS" → "Lyria-002" |
| 2:10 | 10s | **UI · Grounding proof** | Zoom on citation URL card | "Every finding cites its source. If the retrieval tool returns nothing, the finding drops out at the orchestrator. No citation, no output. That's the moat for healthcare." | Overlay: "Grounding: no-citation → dropped" |
| 2:20 | 12s | **E · Findings summary** | Existing `card_findings`, trimmed to 12s | "Three catches. All cited. All rewritten in the writer's voice. From upload to shot-ready assets in under two minutes on live cloud." | — |
| 2:32 | 8s | **F · Roadmap** | Existing `card_close` — SceneMedic / Forensica / VitalSigns | "One architecture. Three products. SceneMedic for medical drama. Forensica for crime. VitalSigns for actor prep with Gemini Live API." | — |
| 2:40 | 12s | **F · Close** | Same card holds, byline centered | "The moat isn't the code. A physician built it. Thank you." | End card: "scenemedic.dev · YouTube · GitHub" |
| 2:52 | — | END | | | |

**Total: 172s = 2:52.** 8s buffer under 3:00 cap.

## VO recording brief (Ahmed)

- **Register:** physician case-handover — direct, quiet, factual. Not motivational. Not marketing.
- **Mic:** whatever's cleanest — MacBook internal is fine if the room is quiet. Distance ~15cm. Pop-filter improvised (thin cloth) if plosives spike.
- **Take:** one unbroken read of all VO lines from the table above, in order, with 2-3s gaps between sections. Re-record any line that stumbles; keep the full session file so the editor can pick.
- **Timing:** don't worry about hitting exact timestamps — the editor time-aligns to the table. Read at your natural pace.
- **File:** save as `assets/voiceover/ahmed_vo_master.wav`, 48kHz/24-bit if possible. If your mic can't, 44.1/16 is fine — no MP3.
- **Fallback:** if audio can't be cleaned by deadline, ship burned narrator captions with the same wording; drop the ICU bed to −24 dB. Deliverable path: `docs/CAPTIONS_ONLY_FALLBACK.md` (to be drafted by Claude Code if triggered).

## Delivery notes (retained from v1)

- Never say "AI" in the hook — say "consultant."
- Never apologize on demo latency; if a call hangs, cut to the pre-recorded backup.
- If asked about PHI: "No real patient data anywhere. Corpus is public literature. Every output is a fictional scene asset. That's why I built the governance layer."
- If asked about hallucination: "The clinical agent can only cite what the RAG tool returned. Findings without a citation URL are filtered out at the orchestrator."

## Backups

- Pre-recorded 60-second screencast of the full flow (existing).
- 6 pre-generated Imagen 3 prop images in `docs/assets/` in case generation stalls on stage (existing).
- Pre-rendered Lyria-002 + TTS clips as fallback audio (existing).
- **Captions-only fallback cut** (new — see fallback note above).
