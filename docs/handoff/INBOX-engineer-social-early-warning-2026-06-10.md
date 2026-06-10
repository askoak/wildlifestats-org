# INBOX — Flyway: social / phenology early-warning pipeline (engineer → architect, spec request)

**Working name: Flyway** (Mike-approved 2026-06-10). Assistant stays WREN; WREN answers questions against Flyway's signals.

**From:** WildlifeStats Engineer, `soar-aspen-beryl-heron`
**To:** WildlifeStats Architect, `measured-fern-jasper-thrush`
**Date:** 2026-06-10
**Status:** Request for spec. Mike originated this in live conversation; engineer captured feasibility + framing. Architect owns the actual spec (cadence, schema, baseline method, source registry, storage, legal posture).

## The concept (Mike)

Get an *earlier read* on wildlife phenology + hazard events than published news by monitoring social signals daily. Two layers:

1. **Structured citizen-science anchors (primary, high-trust):**
   - **Journey North** — purpose-built crowdsourced hummingbird/monarch migration map; first-of-season sightings. Cleanest "early/late" signal.
   - **eBird** (Cornell; Merlin is the consumer app on top of it) — arrival/abundance + API, geo/date-clean.
   - **iNaturalist** — API, research-grade observations with taxon + lat/lon + date; good first-of-season, extends beyond birds.
2. **Facebook / Instagram public Pages + keyword/hashtag (supplementary; earlier, broader, noisier).**

Mike's key framing: it is a **generalizable template, not a hummingbird feature**. Hummingbird arrival is instance #1; the same machinery applies to baby season, monarch migration, HPAI die-offs, amphibian breeding, oiled-bird / weather-kill events.

## The reusable unit — a "signal definition"

```
signal = {
  vocabulary:    ["first hummingbird", "hummers are back", "anyone seeing any yet", ...],
  anchor_feeds:  [journey-north, ebird, inaturalist taxon],
  geography:     county/state resolution,
  season_baseline: rolling expectation per signal × region × week,
  trigger_logic: early | late | spike vs baseline
}
```

Swap vocabulary + anchor feed → new subject, same pipeline.

## Engineer feasibility findings (Apify)

- **FB Pages:** `apify/facebook-posts-scraper` (official, 78k users, 99.8% success) — Page URLs → captions/dates/reactions/links/transcripts. ~$0.005/post → ~$0.0008 at volume; optional date-filter add-on (last 24-48h only).
- **IG:** `apify/instagram-post-scraper` (official, 99.9%) + a hashtag scraper for `#hummingbirdmigration` etc.
- **FB keyword/phrase search:** `scraper_one/facebook-posts-search` / `powerai/facebook-post-search-scraper` (search public posts by phrase/hashtag) — for DISCOVERY.
- **Cost:** ~200 Pages × FB+IG, daily, date-filtered ≈ **~$1-2/day (~$50/mo)**. `APIFY_TOKEN` already in env (BRWC social-corpus precedent).

## The four-part architecture (value is in 2-4, not the scrape)

1. **Source registry** — curated list of public Pages/handles + hashtags + anchor-feed taxa. *This is an editorial/curation call, the real product; garbage list = garbage signal.* Seed from `docs/research/data-sources/`.
2. **Daily scrape** — Apify actors, date-filtered, dedup by post id, cron (GH Actions or Apify scheduler).
3. **Signal extraction (LLM)** — each post → typed record {event_type, species, geo, date, confidence}. Haiku-tier classify. Raw posts are not a signal; extracted records are.
4. **Baseline + anomaly detection** — rolling baseline per signal × region × week; flag early/late/spike. *This is the actual "early warning" — you detect the deviation, which is what beats the news cycle.*

## The FB reality to bake into the spec — discover → curate → monitor funnel

FB **groups** are login-walled + ToS-barred to automation (skip; documented gap, same as BRWC). So: keyword/hashtag **search** surfaces both signal-posts and high-value public Pages → promote best sources into a monitored Page list → those get the reliable daily date-filtered pull. Search discovers; Page-monitoring tracks.

## Design constraints (real, not ceremony)

- **Do not republish** scraped post content (copyright/ToS). Extract signals + link to source; don't mirror text.
- Social volume = posting effort, not events. The step-4 baseline is what corrects the density/demographic bias.

## Decisions needed (architect + Mike)

- Source-list curation (editorial — which Pages/handles/hashtags, national coverage).
- Recurring-cost authorization (~$50/mo ballpark; Mike).
- Extraction schema + which signal_types ship first.
- Baseline method + storage (new pipeline source type feeding the secure/research tier; WREN can later answer "is baby season early this year?").
- Where it surfaces (secure/research tier per the national-research spec).

## Engineer offer

I can run a **proof-of-concept** (one-off, a few cents) against 3-5 public wildlife Pages + a hummingbird phrase search, run the extraction pass, and show real typed early-warning records — as soon as there's a starter Page/handle list (the one piece I shouldn't invent). Architect: fold this into the Phase 4.5+ source registry as a `social-early-warning` / `phenology-signal` source type and spec stages.

— Engineer `soar-aspen-beryl-heron`, 2026-06-10

## HARD SCOPE (Mike, 2026-06-10) — full roster, not a sample

- The pipeline must **build and run daily scrapers for ALL ~100 FB/IG Pages Mike provided** — the full roster is in scope, not a token subset. The 3-5 page proof-of-concept is a smoke test of the extract->baseline chain ONLY; it is NOT the deliverable scope.
- **Roster location: NOT in this repo as of this commit.** Mike referenced ~100 pages "sent earlier" but they did not reach the engineer lane and are not on `main`. Engineer needs Mike to point to the list (re-send into the engineer session, or name the file/session that holds it). Until then the roster is a known gap; bank it into the source registry the moment it lands.
- Structured anchors to pair with the social roster, already in `docs/research/data-sources/03-citizen-science.md`: iNaturalist (§1.1), eBird (§1.2), FeederWatch (§2.1), NestWatch (§2.2), HerpMapper, COASST, WHISPers. **Add Journey North** (hummingbird/monarch migration map) — not yet in the corpus. **CBC/Audubon is scrape-prohibited** (corpus line 353) — read-by-permission only, not a scrape target.

## UPDATE 2026-06-10 — roster LANDED + name approved

- **Name:** Flyway (Mike-approved). 
- **Roster landed:** `wildlifestats/_pipeline/sources/flyway-social-seed-top100.csv` — 99 US wildlife-rehab orgs with FB/IG/TikTok/YouTube handles + an `Apify Search Query` column. Mike-provided seed; **1 row (BRWC's own org) scrubbed** per §19 lane separation. The earlier "roster not in this lane" gap is now CLOSED.
- A second Mike file (`brwc-educational-replies_2026-06-08.csv`) is **BRWC-lane content and stays out of the WildlifeStats lane** — not ingested into Flyway. (If WREN ever wants BRWC tone examples, that's a separate decision via the auth-gated tier, not the public Flyway.)
- POC remains ready to fire (3-5 of the 99 pages + a hummingbird phrase search → extraction pass) on Mike's go / recurring-cost OK. Architect: spec the scrape cadence + per-source registry JSON + extraction schema + baseline method.

## Architect Resolution (2026-06-10 19:30 ET, `measured-fern-jasper-thrush`)

Flyway spec landed: `docs/handoff/wildlifestats-flyway-spec-2026-06-10.md`. Engineer order dispatched: `docs/handoff/wildlifestats-engineer-order-phase4.5+f-thru-j-flyway-2026-06-10.md` — five sub-PRs (f → j) covering source registry + extraction + baseline + cron-but-disabled + dashboard/WREN integration.

Key design decisions made in the spec, all of which match what you proposed:

- **Generalizable signal-definition format** per your `signal = {...}` framing, stored as one JSON per signal under `wildlifestats/_pipeline/sources/flyway/signals/`. First batch is eight signals (hummingbird spring, monarch spring, baby season songbird, HPAI outbreak, oiled bird, weather kill, amphibian breeding, window strike spike).
- **No raw post text stored.** Extracted typed records + `source_url` only. Apify scrape returns post content, extractor produces the typed record, post content is discarded. Methodology page at `/methodology/flyway/` documents the legal posture publicly.
- **Daily cron ships disabled** (workflow_dispatch only) in sub-PR 4.5+i. Mike authorizes the ~$50-100/month recurring spend before activation. Smoke test (3-5 Pages × hummingbird, ~$5-10 one-off) is sub-PR 4.5+g and waits for Mike's go signal too.
- **Surface at the secure/research tier** per the national-research spec. WREN data context expands to include Flyway signals when 4.5+j ships.
- **Baseline bootstrap from synthetic cube seasonality** for the first season (since real Flyway history doesn't exist yet).
- **BRWC scrubbed from roster** per your §19 enforcement; that decision stands.

Proceed with 4.5+f when the engineer-lane slow-pace cadence picks it up. No further architect input needed for 4.5+f → 4.5+h. Surface INBOX for: (a) Mike's smoke-test cost authorization at 4.5+g boundary, (b) Mike's recurring-cost authorization at 4.5+i boundary, (c) Journey North access-path findings whenever you investigate them.

INBOX closed. Engineer may move this file to `closed/` after committing 4.5+f's first commit (per the standard INBOX-resolution pattern).

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 19:30 ET
