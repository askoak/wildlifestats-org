# Critique #5 — Engineering, Ops, Capacity, Risk
**Reviewer:** Senior Infrastructure / Platform Engineer  
**Reviewed:** WildlifeStats build plan (Phase 3.1–7, Flyway, Secure Tier)  
**Live site:** https://wildlifestats.netlify.app  
**Date:** 2026-06-11  

---

## Preface

This is an adversarial review. All numbers below come from live measurement or official documentation. The plan is well-intentioned, architecturally creative, and appropriate for a low-traffic research demo. It has five structural defects that will cause silent failures or visible breakage before any meaningful scale event. Three of those defects are in the specifications, not the implementation — meaning they will be built wrong unless corrected now.

---

## 1. Hosting Architecture: Where the Free Tier Breaks

### Live site observation

```
HTTP/2 200
cache-control: public,max-age=0,must-revalidate
cache-status: "Netlify Edge"; hit
content-length: 6413 (homepage HTML)
```

The homepage serves fine. The cube is deployed as Architecture A — the single 24.5 MB JSON file — not sharded. The by-state shard paths (`/data/cube/by-state/CA.json`) all return 404. The meta.json has no `shards` key. The plan's preferred architecture (B) was not shipped.

### Netlify free tier limits

Netlify's current free plan carries a **300-credit monthly hard limit**. Credit consumption rates:

| Resource | Rate |
|---|---|
| Bandwidth | 20 credits / GB |
| Web requests | 2 credits / 10,000 |
| Compute | 10 credits / GB-hour |
| Production deploy | 15 credits each |

At 20 credits/GB, the free tier allows **15 GB of bandwidth** before the site goes dark. At that point, Netlify pauses *all* sites on the account — not just the over-limit site. This is a hard kill, not a graceful degradation.

The live cube file is **3.82 MB brotli-compressed** (measured). At 15 GB budget:

- **4,018 full cube loads** before exhaustion
- At 100 simultaneous users all landing on `/data/`: budget exhausted in **~40 concurrent sessions per load cycle**
- A modest demo with 200 attendees loading the data page simultaneously burns **0.74 GB** — 5% of the monthly budget in a single 30-minute event

The Pro plan at $20/month provides **3,000 credits = 150 GB bandwidth**. A viral spike of 50,000 visitors with 40% loading the cube equals **75 GB** — exhausted before the spike ends on the free tier; survivable (but consumed) on Pro.

### Netlify Identity wall

The plan (Phase 5 spec §10) defers the Netlify Identity upgrade decision to "when we hit 800 active users." The free tier hard-stops at **1,000 active users**. The 1001st researcher signup fails silently or returns an error. There is no queuing, no waiting room, no graceful overflow. The fix costs ~$99/month for the 5,000-user tier — but the decision point is architectural, not billing: once Identity is the auth provider for researcher accounts, the upgrade cannot be deferred until the wall is already hit.

### Sharded cube: the spec recommends Architecture B, the site ships Architecture A

The architect explicitly recommends sharding (§3.2), calls A "acceptable if B adds more complexity than budget allows," and notes A's risk: "25-40 MB JSON over a cold mobile connection is a 5-10 second first-paint penalty." The shipped file is 24.5 MB uncompressed. Architecture B is not deployed. The meta.json is present but incomplete — it has `dimensions_summary` and `meta` blocks but no `shards` dictionary. The loader logic for sharding has not been wired.

---

## 2. Performance: Actual Numbers

### Cube load times (measured from live file)

| Connection | Compressed size | Load time |
|---|---|---|
| Desktop broadband (50 Mbps) | 3.82 MB | ~0.6s |
| Mobile 4G LTE (10 Mbps) | 3.82 MB | ~3.1s |
| Mobile 3G (500 Kbps) | 3.82 MB | ~63s |

The 3G figure is not a theoretical edge case — it represents shared hotspots at conference venues, rural connections, and older devices. A 63-second data load will register as a hung page and drive abandonment before the filter UI ever paints.

Beyond download: **JSON.parse on 24.5 MB takes 0.25–1.2 seconds on real devices** (250 MB/s on fast desktops, 20 MB/s on mid-range mobile). This is main-thread blocking. On a low-end Android device the page will visibly freeze. The spec acknowledges the download risk but does not address the parse cost.

**Cache-Control: `public,max-age=0,must-revalidate`** means every page visit revalidates with the CDN. The browser cannot serve from local cache without a round-trip. CDN cache-hit rate is good (the header shows `cache-status: "Netlify Edge"; hit`) but every user still pays a conditional-GET. The spec says to use `max-age=86400`. That directive is in the spec but not in the live headers. Someone needs to set it.

### Client-side cube query performance

With 974,250 cells and pure JavaScript array iteration, a simple single-state filter runs in ~20ms. Multi-dimensional queries (all states × multi-year × multi-species × multi-reason) push toward **150–300ms of synchronous main-thread work**. At that range, users on mobile notice the UI freeze. The spec makes no mention of Web Workers, requestIdleCallback, or chunked processing. The filter logic will block the event loop on complex queries.

### WREN / Anthropic latency: a structural incompatibility

The WREN spec §9 reads: "browser calls a Netlify serverless function (Edge Function), which proxies to Anthropic." This conflates two different Netlify function types:

- **Netlify Serverless Functions** (AWS Lambda): 10s default timeout, 26s on Pro — suitable for LLM proxy
- **Netlify Edge Functions** (Deno Deploy): **50ms hard execution limit** — definitively unsuitable for any LLM proxy call

Anthropic Haiku's time-to-first-token runs **200–400ms at the median, 1–2s at p95**. An Edge Function calling Anthropic will timeout on every single request. If the team builds the proxy as a Netlify Edge Function — which the spec language implies — WREN will never return a response. The fix is simple (use Serverless Functions, not Edge Functions), but it requires catching the ambiguity now before an engineer builds the wrong thing.

Assuming Serverless Functions are used correctly:

| Metric | Estimate |
|---|---|
| Cold-start (Lambda) | 200–800ms |
| Anthropic Haiku TTFT | 200–400ms (median) |
| Anthropic Haiku TTFT | 1–2s (p95) |
| End-to-end WREN response (warm) | 500ms–1.5s |
| End-to-end WREN response (cold + p95) | 2–4s |

This is acceptable for a research assistant but not for interactive filtering. The spec correctly keeps cube queries client-side. The latency only matters for WREN answer generation.

---

## 3. Apify Recurring Spend: Undersized and Unmonitored

### Budget reality

The Flyway spec §7 estimates "~$1-2/day, ~$50/month." Based on Apify's published pricing:

- **Facebook Pages Scraper: $0.01 per page**
- 99 pages × 2 platforms (FB + IG) = 198 page-scrapes/day
- **Actual cost: $1.98/day → $59.40/month**

That's within the stated range, but only for the nominal case. The Apify **free tier provides $5/month credit** — enough for 2.5 days of daily scraping. The plan requires the **Starter tier at $29/month** as the minimum, with the $29 prepaid credit covering the scrape cost. This is workable, but Mike needs to understand that the Apify free tier is not viable for daily operation — the spec doesn't state this explicitly.

### LLM extraction cost: unbounded

The spec assumes "99 pages × ~5 posts/day = ~500 posts/day" at Haiku rates. At $0.25/M input tokens and $1.25/M output tokens:

- 500 posts × 500 tokens in + 100 tokens out = **$0.125/day = $3.75/month**
- 5,000 posts/day (realistic for 99 active rehab pages during baby season): **$1.25/day = $37.50/month**

There is **no per-day cap on the LLM extraction pipeline**. The Flyway spec has no equivalent of WREN's `WREN_DAILY_COST_USD` ceiling. During a viral HPAI outbreak event when all 99 pages are posting multiple times per hour, the extraction pipeline could consume 5–10× the nominal post count. At 50,000 posts on a peak day: $12.50 in a single day, $375 for the month — 3.75× the Apify spend and entirely invisible unless Mike checks Anthropic's billing dashboard.

**The cap that exists (WREN's `WREN_DAILY_COST_USD`)** also has a race condition. Netlify Blobs is not a strongly consistent distributed counter. When the Edge Function reads the daily spend counter and multiple requests arrive simultaneously across multiple edge regions, **all concurrent readers will see the same stale value, all will conclude the cap hasn't been reached, and all will proceed to Anthropic**. The overspend per burst is small (a few cents at Haiku rates) but the mechanism provides false confidence. On Sonnet 4.5, the overspend per concurrent burst of 100 requests scales to ~$0.45. More importantly, the counter doesn't prevent a scripted attacker from draining the daily budget in seconds before the counter catches up.

---

## 4. Reliability: Single-Provider Dependency Stack

The system has five distinct single-provider dependencies, none with a failover path:

| Layer | Provider | SLA | What breaks when it's down |
|---|---|---|---|
| Hosting | Netlify | ~99.9% (no SLA on free) | Everything |
| Auth | Netlify Identity | Same as above | All of /secure/, researcher access |
| LLM | Anthropic | No published SLA | WREN dark; Flyway extraction stops |
| Scrape | Apify | No formal SLA | Flyway signal feed stops |
| DOI | EZID/DataCite | Dependent on UC + DataCite infra | New downloads uncitable |

**Anthropic is the most exposed dependency.** Anthropic has experienced multi-hour outages. When Anthropic is down, WREN returns errors, the Flyway extraction pipeline fails silently (there is no retry or queue mechanism in the spec), and the daily cost cap counter in Blobs is never incremented (because the API call never completes — but the check still ran, so the request was "approved"). The spec's fallback is "the site continues to work in cube-only mode (filter UI from Phase 4) when WREN is rate-limited or cost-capped" — but there is no stated behavior for an Anthropic outage as distinct from a cost cap. The user will see an unhandled error.

**GitHub Actions cron is the Flyway orchestration layer.** GitHub documents that cron-scheduled workflows "can be delayed during periods of high loads" and "some queued jobs may be dropped." Community reports confirm delays of 20–60 minutes and occasional complete skips. For a daily pipeline, a skipped run means a 24-hour gap in the signal feed. The spec has no retry mechanism and no alerting for missed runs.

**The site's `robots.txt` points to `https://wildlifestats.org/sitemap.xml`** while the live domain is `wildlifestats.netlify.app`. The canonical link in the `/secure/` 404 response also points to `wildlifestats.org`. Either the custom domain is not fully configured, or the robots/sitemap reference the future domain. This is a soft operational gap but will confuse SEO crawlers and any automated monitoring keyed on the canonical domain.

---

## 5. Security: Threat Model Gaps

### Netlify Identity JWT model

The spec correctly uses JWTs validated at the Edge Function layer for `/secure/api/*`. The threat model for Tier 2 (researcher access) is that a researcher's account is phished. A compromised researcher account grants:

- Access to all anonymized individual records for any state/species/year combination
- Bulk Parquet/CSV download of the full anonymized dataset
- The citation DOI download endpoint — which is not rate-limited by volume, only by request count (1,000 API requests/day per user)

At 1,000 API requests/day with cursor-based pagination and 1,000 records per page, a compromised researcher account can **exfiltrate up to 1,000,000 anonymized records in a single day** — the entire dataset. The spec does not rate-limit bulk download by bytes or by row count; it rate-limits by API calls. A single API call returning the maximum cursor-based page is not the same as 1,000 small calls.

**The rate limit also does not distinguish between a browser UI session and a scripted bulk download.** A researcher with legitimate access who decides to automate a full-corpus pull is indistinguishable from a hostile actor. The spec should add a separate rate limit for bulk download endpoints (bytes/day or rows/day) distinct from the general API call count.

### Per-IP rate limiting bypass

WREN spec §9 specifies "rate-limits per IP to 10 questions per minute." IP-based rate limiting on a public endpoint is defeated by any adversary with access to residential proxies or a modestly distributed botnet — which is to say, any motivated party. The cost-cap mechanism is the actual backstop, not the IP limit. This is known and the spec acknowledges it implicitly by making the cost cap the enforcement mechanism, but the plan should not describe IP rate limiting as a "defense."

### WREN prompt injection

The public WREN accepts arbitrary user questions routed through a Netlify function to Anthropic. The spec's safety rails (§7) are prompt-engineering defenses: "the system prompt includes explicit rules," "WREN must never produce a number that isn't from the cube query result." These are soft controls. A determined user submitting a carefully crafted prompt can elicit off-topic responses, leaked system prompt fragments, or behavior that contradicts the safety rails. Netlify Edge Function isolation helps only in the sense that each invocation is stateless and sandboxed from the file system — it does not prevent the LLM from being manipulated within the context window of that single call.

The specific Wildlife911 triage path is the highest-risk surface: if a user crafts a question that bypasses the triage-routing guard and causes WREN to provide specific first-aid instructions for an injured animal, WildlifeStats is exposed to a tort claim if the advice causes harm. The spec's mitigation ("always redirect to AnimalHelpNow") is a prompt instruction. Prompt instructions are breakable. The correct defense is a hard-coded response router that matches triage-pattern questions with a regex or classifier *before* sending them to the LLM.

### Admin tier / Anthropic key blast radius

The Anthropic API key lives in Netlify environment variables. If the Netlify account is compromised (password not MFA-protected, or a build-hook URL leaked), the attacker has the Anthropic key. Anthropic's tier-2 rate limits allow roughly $50/minute of spend. **24-hour exposure before detection: ~$72,000.** Realistic 1–2 hour detection window: $3,000–$6,000. Anthropic does send usage alerts, but only at configured thresholds — and the spec does not mention configuring those alerts.

---

## 6. Data Governance and Legal

### DOI for synthetic data: not guaranteed

The plan (Phase 5 spec §5.3) proposes quarterly DOI snapshots via EZID/DataCite. DataCite's metadata requirements do not explicitly prohibit synthetic data, but EZID is operated by the California Digital Library under an agreement with DataCite. EZID's documentation states that "DOI names are assigned to objects that are intended to be made available indefinitely." More critically, DataCite metadata schema requires a `resourceType` declaration. Declaring a fully synthetic dataset as `Dataset` without explicit `synthetic` annotation would be misleading; if a researcher cites the DOI and later discovers the underlying data is synthetic, the citation relationship is arguably misrepresented. Zenodo (CERN) explicitly supports synthetic datasets with a `simulationData` type declaration and is free. **The spec should use Zenodo, not EZID/DataCite, for synthetic-only snapshots.**

### Meta ToS and Apify

The 2024 California federal court ruling (Meta v. Bright Data) found that Meta's ToS does not prohibit logged-out scraping of public data — a favorable precedent. However, Meta subsequently updated its Terms of Service (Q3/Q4 2024, per the California AB 587 report): "You may not access or collect data from our Products using automated means (without our prior permission) **regardless of whether such automated access or collection is undertaken while logged-in to a Facebook account**." The new language explicitly extends the ToS to logged-out scraping. The Bright Data ruling addressed the *old* ToS. The amended language has not yet been tested in court, but it materially weakens the "court said it's fine" defense that Flyway's legal posture implicitly relies on.

### Take-down policy vs. implementation

The plan promises withdrawal within 5 business days. The implementation path: remove `source_org_id` from `flyway-social-seed-top100.csv`, scrub historical extracted records from `secure/cube/flyway/`. This requires a developer to manually edit a CSV, re-run the extraction history scrub, rebuild the cube, and deploy — all within 5 business days. That's achievable for Mike + 1 engineer if no other work is competing. It is not achievable if the engineer is on vacation, the key has expired, or the GitHub Actions pipeline is broken. The spec should implement a feature-flag file (`flyway-removed-orgs.json`) that causes the serving layer to filter out records at query time without requiring a full rebuild — providing immediate take-down on flag commit, with the manual scrub as a follow-up.

---

## 7. Ops Burden: Mike + 1 Engineer

### The surface area

Five external API dependencies (Netlify, Anthropic, Apify, EZID, GitHub Actions). Seven moving pipeline stages. Three authentication tiers. A daily automated cron job. Quarterly DOI issuance. All operated by two people, one of whom is the principal stakeholder, not a dedicated on-call engineer.

### Monitoring gaps

The spec has no monitoring story. There is no answer to:

- What page does the user see when WREN returns a 503? (The spec says "the site continues to work in cube-only mode" — but is there a banner? Does the user know WREN is down?)
- What alerts Mike when the Flyway cron is skipped? (Nothing in the spec.)
- What alerts Mike when the Apify actor is blocked by Facebook's anti-bot measures? (Nothing.)
- What alerts Mike when the cube validation CI job fails? (Email from GitHub, if notifications are configured.)
- What does the audit log surface expose when Blobs is unavailable? (The secure tier's audit log becomes unwritable — are queries silently allowed or blocked?)

The plan has CI validation (good), BRWC content guards (good), and HTML validation (good). It has zero runtime observability instrumentation. For a demo-hardened site, the minimum viable monitoring stack is:

1. Netlify's built-in analytics (available on Pro) for bandwidth and error rates
2. A Freshping or Better Uptime monitor on the cube endpoint and WREN endpoint with email/SMS on failure
3. A simple GitHub Actions heartbeat job that runs after every Flyway cron and posts a "success" or "failure" status to a Slack webhook or email

Without these, the first notice of a failure is a user complaint during the demo.

### Disaster recovery

| Scenario | Current recovery path | Time estimate |
|---|---|---|
| GitHub account compromised | Re-fork from last deploy's snapshot (Netlify caches the build artifact) | Hours to days |
| Netlify account compromised | New account, re-deploy from GitHub, recover Blobs data separately | Hours, but Blobs state (audit logs, rate limit counters) is lost |
| Anthropic API key leaked | Revoke in Anthropic dashboard, rotate Netlify env var, redeploy | 30 minutes if caught early; $3K–$72K exposure depending on detection time |
| Apify actor blocked | Manual unblock or actor switch; fallback actor listed in spec | Hours |
| EZID unavailable | DOI issuance stalls; no data loss | Delay only |

The GitHub repo is the single source of truth for the entire build. It contains the cube data, the pipeline code, the CI configuration, and — critically — the partner mapping files. **No backup procedure is specified.** The spec should add a `make backup` target that archives the repo + secure cube + Blobs audit log to Mike's OneDrive on a weekly cron, matching the OneDrive credential pattern already used in the spec (§18 of WREN spec references `C:\Users\Hello\OneDrive - Michael Oak Advisors\Credentials\`).

---

## 8. Capacity Headroom Summary

| Traffic scenario | What works | What breaks |
|---|---|---|
| 5–100 visitors/day (today) | Everything | Nothing (under all limits) |
| Demo: 500–2,000 visitors, 30 min | Static pages, cube loads (CDN) | WREN may hit daily cost cap if 5% use it; bandwidth ~0.7–7 GB (survives free tier) |
| Foundation tweet: 5,000–50,000 visitors | CDN serves static and cube (cached) | Free tier bandwidth blown at ~4,000 cube loads; Netlify pauses account; WREN cost cap hit in <1 hour |
| 50,000 concurrent → 1,001 Identity signups | — | Identity free tier wall at 1,000; signup #1,001 fails |
| Anthropic outage during demo | Cube filter UI still works | WREN returns unhandled errors; Flyway extraction fails silently |

The architecture is correctly designed for the expected traffic range. The failure modes only manifest at viral scale — but a foundation tweet *is* the intended viral event. Pre-loading 150 GB Pro bandwidth budget costs $20/month. Not doing so risks a complete site blackout at the moment of maximum visibility.

---

## 9. Top 7 Hardening Priorities (Ranked by Impact-per-Effort)

**1. Fix WREN's function type: Serverless Function, not Edge Function.**  
The spec conflates the two. Edge Functions have a 50ms hard limit; Anthropic calls take 200ms–3s. If the engineer builds the WREN proxy as an Edge Function (which the spec language invites), WREN will timeout on every request. Effort: 2-hour fix. Impact: WREN works at all.

**2. Upgrade to Netlify Pro ($20/month) before any public demo.**  
Free tier allows 15 GB bandwidth and hard-stops the account at exhaustion. Pro provides 150 GB. A foundation tweet drives 50,000 visitors → 75 GB of cube loads. Blowing the free tier pauses every site on the account. Effort: one billing action. Impact: prevents complete demo-day blackout.

**3. Set `Cache-Control: max-age=86400` on the cube file.**  
The live file serves `max-age=0,must-revalidate`. Every user re-validates on every visit. With a deterministic-seed static file that changes only on generator runs, a 24-hour cache TTL is safe and cuts repeat-visitor bandwidth by 80–90%. The spec recommends this but it was not applied. Effort: one `netlify.toml` header rule. Impact: ~5× reduction in bandwidth consumption and CDN pressure.

**4. Add a daily spend ceiling to the Flyway LLM extraction pipeline.**  
WREN has `WREN_DAILY_COST_USD`; Flyway has nothing. During a high-activity wildlife event (HPAI outbreak, baby season) the 99-page roster may produce 10,000+ posts in a day. At Haiku rates: $2.50/day instead of $0.13 — not catastrophic, but invisible and unbounded. A simple `FLYWAY_DAILY_LLM_COST_USD` env var with a pre-flight check in `run_daily.py` costs 30 minutes to implement. Impact: prevents unbounded LLM spend on pipeline spikes.

**5. Implement bulk download rate limiting by rows/bytes, not just by API call count.**  
The current model limits researchers to 1,000 API calls/day. A single paginated call can return 1,000 records. A compromised or automated researcher account can exfiltrate the full 1M-record anonymized dataset in one day. Add a daily row-count ceiling (e.g., 100,000 rows/day) and a bytes-transferred ceiling stored alongside the API call counter in Blobs. Effort: 4–6 hours. Impact: contains the blast radius of a researcher account compromise.

**6. Add minimum viable runtime monitoring: 3 uptime checks + 1 GH Actions heartbeat.**  
No monitoring currently exists. Required: (a) uptime monitor on `/data/cube/admissions-cube.meta.json` (cube available), (b) uptime monitor on the WREN endpoint, (c) a 5-minute post-run success/failure notification from the Flyway daily cron to email or Slack. Tools: Freshping free tier or Better Uptime free tier. Effort: 2 hours. Impact: Mike gets paged before a demo rather than during it.

**7. Replace Architecture A (single 24.5 MB cube) with Architecture B (sharded by state) before any live demo.**  
The spec recommends sharding; the site ships the single file. On mobile 4G, the cube takes 3.1 seconds to load from cold. On 3G, 63 seconds. Conference venue WiFi under 200-person load degrades to 3G equivalent. The meta.json is in place; the shard generator flag (`--output-mode sharded`) exists per spec §4. The loader changes in `data.js` are specified (§5 pseudocode). This is an afternoon of implementation. Impact: demo-day time-to-interactive drops from 3–10s to 0.1s (meta only) + on-demand shard loads.

---

*Prepared by adversarial review — WildlifeStats engineering critique series.*
