# Winning Hackathon Pitch Video Rubric

Research pass, 2026-08-23. Every source below was fetched (not just search-listed). Videos that 404'd, or that only appeared as search-result titles, were dropped. Companion to `AGENTIC_CINEMA_JUDGING.md` (official rules) and `PITCH.md` (current draft script).

## Sources

- Agentic Cinema Hackathon rules — https://agentic-cinema.devpost.com/ · Four equal-weight criteria (Tech Impl / Design / Potential Impact / Quality of Idea); ≤3:00 demo; "not a cinematic trailer."
- Agentic Cinema resources — https://agentic-cinema.devpost.com/resources · Framework tutorials only; no video guidance.
- ADK Hackathon 2025 rules — https://googlecloudmultiagents.devpost.com/rules · Sibling rubric: Tech 50% / Innovation 30% / Demo+Docs 20%; ≤3:00 hard cap.
- ADK Hackathon 2025 results — https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights · All 5 named winners used explicit multi-agent orchestration.
- SalesShortcut Devpost (ADK grand prize) — https://devpost.com/software/salesshortcut/ · 34 agents visible on screen; founder VO screencast; pitch: https://www.youtube.com/watch?v=UxP3iDqRKZ0.
- GKE Hackathon 2025 recap — https://siliconangle.com/2025/11/14/gke-hackathon-winner-agentic-ai-kubeconna/ · Judge: "multi-agent architectures … the new big thing"; winners visibly showed A2A handoff.
- Devpost "6 tips for a winning demo video" — https://info.devpost.com/blog/6-tips-for-making-a-hackathon-demo-video · Lead with pitch in the first seconds; show the app running, not slides.
- Devpost "How to win a hackathon: 5 judges" — https://info.devpost.com/blog/hackathon-judging-tips · Balance all criteria; recycled/template projects lose fast.
- JetBrains "Notes from the judging table" — https://blog.jetbrains.com/ai/2026/06/how-to-win-a-hackathon-notes-from-the-judging-table/ · State problem in first 30 s; show one thing working in ~90 s.
- Dabit3 "Killer pitch/demo" gist — https://gist.github.com/dabit3/caef5eee4753dd7d23767bc31e70da28 · 15-20 s hook, solution 30-40 s, live demo 60-120 s; narrative > features.
- Colosseum submission workshop — https://blog.colosseum.com/perfecting-your-hackathon-submission/ · "Clear narrative > professional editing"; flashy-with-no-substance loses.
- Michael Seibel / YC seed pitch — https://www.saastr.com/the-y-combinator-guide-to-perfectly-pitching-your-seed-stage-startup-with-michael-seibel/ · Lead with strongest point; jargon signals insecurity.
- YC Demo Day 60-s format — https://www.flowjam.com/blog/yc-demo-day-presentation-format-15-slide-script-that-wins-checks · First 10-15 s = pre-recorded product clip.
- Out-of-Pocket 2025 Healthcare AI hackathon — https://www.outofpocket.health/p/oops-2025-healthcare-ai-hackathon-projects · All 5 named winners used founder VO over live UI; Code Blue Co-pilot and AdvocateGPT closest SceneMedic analogs.

## The 10-point rubric

Each item = 1 point; verifiable, not vibes.

1. **First-frame hook lands in ≤7 s** — product name + one-line "what it is" visible or spoken by 0:07. Judges make the skip call in the first 10 s (JetBrains, YC).
2. **Problem stated with a citable number in ≤20 s** — dollar/hour/error stat with source, not adjectives (JetBrains, Colosseum).
3. **A live artefact appears by 0:45** — UI, terminal, or agent trace on screen — not a slide, not a diagram (JetBrains, Devpost tips).
4. **Multi-agent handoff is visibly shown, not just described** — swimlane, chat log, or trace timeline that shows ≥2 agents passing state. ADK winners all did this; a single-agent visual fails the "multi-agent network" criterion (ADK results, GKE recap).
5. **One end-to-end user journey completes on screen** — input → agent reasoning → tool call → output — inside a single unbroken take of ≤90 s (Dabit3, JetBrains).
6. **Grounding/anti-hallucination shown, not asserted** — citation URLs, source snippets, or "no-citation → dropped" filter visible in the UI. Especially load-bearing for healthcare (Out-of-Pocket winners: Code Blue, AdvocateGPT).
7. **Google services named on screen at the moment they're used** — "Vertex Agent Engine", "BigQuery Vector Search", "Imagen 3" as overlays, not buried in a diagram (ADK rules 50% weight on Tech Impl).
8. **Partner track called out in-video** — "Powered by ClickHouse MCP" or "Parallel Search API" title card. Mandatory for Agentic Cinema submission; also gives Tech Impl points.
9. **Runs ≤2:55 with a 5-second safety margin** — 3:00 is a hard cutoff; anything after is unscored (Agentic Cinema rules).
10. **English audio or English captions the whole way** — required if not English audio; silent video fails the language rule (Agentic Cinema rules).

## Pattern analysis

**Winners.** All 5 ADK-2025 winners + 5 Out-of-Pocket healthcare winners open with *problem + a number*, cut to *founder-narrated UI recording*, end on a *named vertical* (K-12 Brazil, SDR reps, pediatric parents) — never "AI for X". Multi-agent submissions show a **visual trace of agents talking** (swimlane, log tail, graph) — not a static PNG. Healthcare AI winners all used founder VO; none TTS; none silent.

**Losers.** Architecture-first (mermaid at 0:20 before anything runs) tanks Design + Potential Impact. Slide-decks with no live artefact fail Devpost's "show it running" rule. Silent Ken-Burns trailers read as marketing — Agentic Cinema rules disallow the cinematic-trailer framing. Feature-list VO ("8 agents, 4 tools, 3 modalities…") loses to journey VO ("here's a bad scene → what the continuity agent flags → the rewritten line").

## Voiceover verdict

Silent + music-bed is wrong here. Three reasons: (1) **Rules** — "demo video, not cinematic trailer" + captions/English audio requirement; silent Ken Burns reads as trailer. (2) **Rubric** — Design + Potential Impact = 50% of score; both need narration to explain *why* each on-screen event matters. (3) **Peer signal** — 0/10 winners surveyed (5 ADK + 5 healthcare) used silent or TTS; all used founder VO over screencast.

**Recommendation: Ahmed's own voice, one unbroken take, unpolished on purpose.** Not TTS. Not motivational. Register: physician case handover — direct, quiet, factual. ICU bed under VO at −18 dB. Fallback if audio isn't clean by deadline: burn narrator captions on-screen, drop bed to −24 dB.

## Score: current SceneMedic pitch plan

Scoring the plan in the task brief (A→F, silent, 182 s). Because the *newer* PITCH.md draft already patches several of these, both scores are given.

| # | Criterion | Task-brief plan | PITCH.md draft | Fix |
|---|---|---|---|---|
| 1 | Hook ≤7 s | 0 (name only, no "what it is") | 1 | Land "the consultant Hollywood actually needs" by 0:07, over Title B-roll. |
| 2 | Problem + citable stat ≤20 s | 1 (has $5k) | 1 | Keep — add source line ("Ep budget reference: WGA/Variety, 2024") in caption. |
| 3 | Live artefact ≤0:45 | 0 (architecture starts at 0:20; UI at 0:48) | 0 | Swap order: cold-open a 6-s UI frame at 0:07, defer architecture to 0:38. |
| 4 | Multi-agent handoff visible | 0 (only described in card) | 0 | Add a 4-agent swimlane overlay on the UI during 1:15-1:35 that lights up as each agent fires. |
| 5 | End-to-end journey ≤90 s | 1 (Playwright reel is 70 s) | 1 | Keep — but narrate it. |
| 6 | Grounding shown | 0 (silent = no citation callout) | 1 | Zoom Ken Burns on a citation URL card at 2:05; VO: "no-citation findings drop out." |
| 7 | Google services on-screen | 0 (no on-screen labels) | 0 | Burn text overlays ("Vertex Agent Engine", "BigQuery Vector Search", "Imagen 3") at the moment each is invoked. |
| 8 | Partner track called out | 0 (no track picked) | 0 | Pick ClickHouse MCP; add a 1-frame "Partner: ClickHouse MCP" lower-third at 0:35. |
| 9 | ≤2:55 | 0 (182 s = 3:02) | 0 | Trim to 2:52; drop one Ken Burns card. |
| 10 | English audio/captions | 0 (silent, no captions) | 1 | Add Ahmed VO + burn captions. |

**Score: 2 / 10** (task-brief plan) · **5 / 10** (PITCH.md draft). Both fail the Agentic Cinema rules gate at rows 8, 9, 10 individually.

## Top 5 changes to make (ranked)

1. **Kill the silent reel — record Ahmed VO end-to-end.** One-take narration over the existing timeline. Physician-handover register, not marketing. Blocks 3 rules failures at once (rows 4, 6, 10). Fallback = burned narrator captions.
2. **Trim to 2:52 and cold-open on the UI.** Cut the current A-title card from 6 s to 2 s; move the first UI frame to 0:07 (row 3, row 9). Move Architecture flyover (C, 0:20-0:38) to *after* the UI opens — the diagram lands harder once judges have seen the product move.
3. **Overlay a 4-agent swimlane on the Playwright reel at 1:15-1:35.** Four lanes (Parser → Continuity → Clinical → Dramatization), each lighting up as its agent fires, with the ClickHouse and BigQuery tool-call badges appearing on the correct lane. Solves rows 4, 7, 8 in a single asset. This is the single highest-leverage change against the ADK-winner pattern.
4. **Burn service-name lower-thirds at the exact moment each Google service is called.** "Vertex Agent Engine" (0:52), "BigQuery Vector Search" (1:18), "Imagen 3" (1:41), "Lyria" (1:52), "Gemini TTS" (1:58). Row 7 — cheap points on the 25%-weighted Tech Impl criterion.
5. **Zoom Ken Burns on a citation URL at 2:05 and let the VO say "no citation → dropped."** Turns the current prop-gallery zoom into a grounding proof. Row 6. Load-bearing for a healthcare submission where hallucination is the obvious judge worry.

Every item above maps to an exact timestamp in the existing 182-s reel; none require re-shooting the UI walkthrough. Estimated re-render time: one afternoon.
