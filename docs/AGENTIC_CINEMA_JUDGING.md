# Google Agentic Cinema Hackathon — Judging & Submission Reference

Compiled 2026-08-23 from official Devpost pages. First edition — no prior winners exist.

## Official rules (verified URLs)
- Rules: https://agentic-cinema.devpost.com/rules
- Overview / tracks: https://agentic-cinema.devpost.com/
- Resources: https://agentic-cinema.devpost.com/resources
- Analog rubric (ADK Hackathon 2025): https://googlecloudmultiagents.devpost.com/
- ADK 2025 winners recap: https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights

Key facts:
- Sponsor: Google LLC · Administrator: Devpost
- Submission window: 27 Jul 2026 – 9 Sep 2026, 2:00 PM PDT
- Judging window: 23 Sep – 7 Oct 2026
- Team size: max 4
- Project must be newly built during the contest period, running on web, Android, or iOS
- Public repo required (GitHub/GitLab/Bitbucket) with open-source license; Google + partner services must be **imported and called** in code — README mention is insufficient
- Prohibited AI stacks: AWS, Microsoft, OpenAI, Anthropic models/frameworks
- Prize pool $75,000 (five tracks × $7.5k / $4.5k / $3k)

## Video specs
- **Length:** ≤3 minutes. Anything past 3:00 is not evaluated ("only the first 3 minutes will be evaluated").
- **Type:** *Demo* video, not a cinematic trailer. Verbatim: "a demo video showing your project/agent functioning as built — not a cinematic trailer."
- **Upload target:** YouTube **or** Vimeo, publicly visible. No direct MP4 upload, no Devpost self-host.
- **Language:** English **or** English subtitles (captions required if audio is not English).
- **Resolution / aspect ratio:** Not specified in the rules. Follow YouTube/Vimeo standard (1080p, 16:9).
- **Content prohibitions:** no third-party ads, no unlicensed footage, no IP/privacy violations, no derogatory content.

## Judging rubric with weights
Four criteria, **equal weight** (25% each) per official Rules §"Judging Criteria":
1. **Technological Implementation** — "How well is the project built, and how effectively does it use Google Cloud and the Partner services?"
2. **Design** — "Does the project deliver a complete, coherent product experience not just a technical proof of concept?"
3. **Potential Impact** — "Does the project make a credible, specific case for solving a real problem for a real audience and does the solution actually address it based on what's demonstrated?"
4. **Quality of the Idea** — "Is this a creative, non-obvious use of Google Cloud and the Partner services and does the team show genuine understanding of the problem space?"

Two-stage process: Stage 1 pass/fail viability screen (may be automated); Stage 2 scored on the four criteria.

## What "agentic" means in the rubric
Official language from the resources page: build "a functional, production-ready AI agent **or multi-agent network**—powered by Gemini and Google Cloud Agent Builder." So a single agent + tools *technically qualifies*, but the framing ("multi-agent network", "agentic workflow") and the sibling ADK-2025 rubric which explicitly rewards "multiple agents collaborating" strongly favour multi-agent orchestration. Judges want visible reasoning steps, tool use via external integrations, and error recovery (per Devpost coverage of judging).

## Google services mentioned as scored
Explicitly named on the official pages:
- **Gemini Enterprise Agent Platform** (mandatory backbone)
- **Google Cloud Agent Builder** / Agent Engine
- **Google ADK** (SDKs: `google-adk`, `google-genai`, `google-generativeai`, `google-cloud-aiplatform`)
- **BigQuery** (RAG for script/media databases)
- **Lyria 3** (music generation) — note: newer than SceneMedic's Lyria-002
- **Gemini TTS** (speech)
- **Imagen 3** (VFX / concept art)
- **Cloud Run** (serverless hosting)
- **Secret Manager** (credentials)
- **Gemini multimodal** (video analysis / transcription)
- **Gemini safety settings** (moderation)

## Partner tracks (must pick exactly one)
IBM (IBM Bob), Grafana Labs (Grafana Cloud MCP server, runtime), Parallel (Search API, runtime), ClickHouse (official MCP server, runtime), Replit (Replit Agent in dev; project hosted on Replit). **SceneMedic does not currently declare a partner track — this is a submission gap.**

## Winner patterns
No prior Agentic Cinema edition exists. Closest analog is ADK Hackathon 2025 (476 submissions, 10,432 participants). Common traits of winners (SalesShortcut grand prize, Energy Agent AI, Edu.AI, GreenOps, Nexora-AI):
- **Explicit multi-agent orchestration** — planner + specialist agents + tool-callers, not a single agent
- **Architecture diagram shown in-video and in repo** (ADK 2025 required it; Agentic Cinema does not explicitly require it but the "Demo and Documentation" DNA carries over)
- **Named vertical / audience** — sales SDR, energy customer ops, Brazilian K-12, cloud FinOps, personalised tutoring. Vague "AI for X" pitches lost.
- **Live-looking demo** of the agent taking an input, reasoning, calling tools, producing an output — narrated over screen recording
- **Explicit callouts of Google services** on-screen (ADK, Vertex, BigQuery, Gemini model IDs)

## Gaps in the current SceneMedic submission
Against the current plan (silent 182 s reel, 6 cards + UI walkthrough + Ken Burns):

1. **Video is 182 s = 3:02 → over the hard 3:00 cap.** Anything past 3:00 will not be scored. Trim to ≤2:55 with buffer.
2. **Silent reel violates the "demo video, not cinematic trailer" rule.** Judges want to see the agent *functioning*. A voice-over (or on-screen narration captions) explaining reasoning steps and tool calls is expected. Silent Ken Burns reads as "trailer."
3. **English subtitles required** if the video has no English audio. Silent + no captions = fails the language rule.
4. **No architecture diagram in plan.** Not mandatory here (unlike ADK 2025), but the Design + Technological Implementation criteria are much easier to score high on with a visible diagram — include one on-screen frame.
5. **No partner track selected.** Mandatory. Pick one — ClickHouse MCP is the natural fit for the BigQuery Vector Search story (swap or dual-wire), or Parallel Search API for evidence retrieval on medical realism. Without a partner track the submission is disqualified.
6. **Lyria-002 vs Lyria 3.** Official resources reference Lyria 3. Confirm model ID or expect a Stage-1 viability question.
7. **"Agentic-ness" must be visible.** The reel must show multi-agent handoff on screen (Director → Specialist → Critic, or equivalent) — not just cards describing it. This is the #1 differentiator against the ADK-2025 winner set.
8. **Live UI walkthrough is good** — keep it; that is the "functioning as built" evidence Rule §Video Requirements demands.
9. **Repo must import and call every named Google service.** Confirm `google-adk`, `google-cloud-aiplatform`, Imagen 3, Lyria, Gemini TTS all have live call-sites, not just README mentions.
10. **Ineligibility check.** Rules exclude residents of several countries incl. Italy, Brazil, Quebec, Iran, Russia, etc. Ahmed (Egypt / Spain-bound) is eligible; confirm any teammate residencies before submitting.
