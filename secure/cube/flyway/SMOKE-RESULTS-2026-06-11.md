# Flyway smoke test — 2026-06-11 (Phase 4.5+g)

Authorized by Mike (~$5-10 one-time Apify). Run under `/secure/` (404 to public).

## What ran
- **Apify scrape (official actors):** `apify/facebook-posts-scraper` on 4 roster
  Pages (lindsaywildlife, WildCareBayArea, wildbirdfund, waldenspuddle) +
  `apify/instagram-post-scraper` on 2 (lindsaywildlife, wildbirdfund), date-
  filtered to recent posts. **47 posts** (31 FB + 16 IG). Token via `APIFY_TOKEN`
  env var only — never read from disk, printed, or committed.
- **Extraction:** `extract.py`. Offline vocabulary matcher → **0 records** (real
  posts don't use the narrow seed phrases). LLM-tier extraction (session Claude
  model applying `extraction-prompt.md`; `ANTHROPIC_API_KEY` env-shadowed in the
  Claude Code shell, so done inline — production `extract.py --extractor llm`
  calls Haiku via the API) → **6 baby-season records**.

## Findings
- **0 hummingbird-arrival signals** — correct: June is past the Feb-May arrival
  window. To catch hummingbird arrival, scrape the spring window.
- **6 `phenology.baby_season_start.songbird` records** (NY + TN), e.g. Wild Bird
  Fund's "patient #5,000, +12% YoY," an American kestrel nestling in Brooklyn, a
  red-winged blackbird fledgling in Prospect Park; Walden's Puddle "baby season"
  intake. Seasonally correct (June = peak baby season).
- **Correct negatives:** a bird-feeder care post (window-collision *advice*, not
  an event) and a single gull collision (individual case, not a *spike*) were
  not fired — the LLM extractor discriminates events from advisories.
- **Key lesson:** the offline matcher is a deterministic CI/test backend only;
  real-world recall requires the LLM extractor. The vocabulary lists are a
  starting prior, not the matcher.

## Cost
- Apify ≈ **~$0.30** (FB ~$0.22 + IG ~$0.05 + a wasted sync-timeout start).
- LLM: $0 actual (session model); production Haiku est. < $0.01 for 47 posts.
- **Total well under the $5-10 authorization.** Daily 99-Page recurring cron
  (Phase 4.5+i) stays DISABLED until Mike authorizes the ~$50-100/mo recurring
  spend.

## No raw content stored
`secure/cube/flyway/audit/smoke-2026-06.jsonl` — 46 lines, `post_text_NOT_STORED:
true` on every one, no raw post text or media retained. Only extracted fields +
`source_url` for attribution.
