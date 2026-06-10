# Flyway architecture spec — social/phenology early-warning pipeline

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 19:30 ET
**Status:** Response to `INBOX-engineer-social-early-warning-2026-06-10.md`. Source of truth for the Flyway pipeline. Slots into the Phase 4.5+ source registry as a new source type.
**Mike directive captured by engineer 2026-06-10:** "build and run daily scrapers for ALL ~100 FB/IG Pages Mike provided — the full roster is in scope, not a token subset." Roster landed at `wildlifestats/_pipeline/sources/flyway-social-seed-top100.csv` (99 US wildlife-rehab orgs, BRWC scrubbed per §19).
**Name:** Flyway (Mike-approved, 2026-06-10). WREN stays WREN; WREN answers questions about Flyway's signals.

## §1 — One paragraph

Flyway is a daily pipeline that monitors structured citizen-science anchor feeds (Journey North, eBird, iNaturalist) and a curated public-Page roster (99 US wildlife-rehab Facebook/Instagram accounts, plus keyword/hashtag discovery) for early phenology and hazard signals. Posts are scraped through Apify's official actors, dated, deduped, and passed through an LLM extraction pass that produces typed signal records — `{event_type, species, geo, date, confidence, source_url}`. A rolling baseline per (signal_type × region × week) detects early/late/spike anomalies against expectation. Flyway is generalizable — same machinery handles hummingbird arrival, baby season, monarch migration, HPAI die-offs, amphibian breeding, oiled-bird events — by swapping the vocabulary and anchor-feed taxa per signal definition. Signals surface in the secure/research tier via WREN ("is baby season early this year in the Northeast?") and as a `signals/` dashboard.

## §2 — Source registry integration

Flyway is a **source type** in the Phase 4.5+ source registry, not a single source. Three registry entries cover the surfaces:

### §2.1 `flyway-social-pages` (recurring scrape)

```json
{
  "source_id": "flyway-social-pages",
  "display_name": "Flyway — Wildlife rehab social media Pages roster",
  "url": "https://wildlifestats.org/methodology/flyway/",
  "license": "scraped-public-extracts-only",
  "license_url": "internal-tos",
  "license_allows_commercial": false,
  "license_allows_redistribution": false,
  "access_method": "apify-actor",
  "data_format": "json",
  "actor": "apify/facebook-posts-scraper",
  "alternate_actor": "apify/instagram-post-scraper",
  "refresh_cadence": "daily",
  "endpoint_config": "wildlifestats/_pipeline/sources/flyway-social-seed-top100.csv",
  "extraction_pipeline": "wildlifestats/_pipeline/flyway/extract.py",
  "extraction_schema": "wildlifestats/_pipeline/flyway/signal-schema.json",
  "baseline_storage": "secure/cube/flyway/baselines/",
  "signal_storage": "secure/cube/flyway/signals/",
  "tier": "tier2-research-and-tier3-reference",
  "anonymization_required": "post-content-not-stored-only-extracted-signals",
  "notes": "Scraped content (post text, images) is NOT stored or republished. Only extracted signal records + source_url. See §6 legal posture."
}
```

### §2.2 `flyway-phrase-search` (discovery)

```json
{
  "source_id": "flyway-phrase-search",
  "display_name": "Flyway — Discovery via public phrase/hashtag search",
  "actor": "scraper_one/facebook-posts-search",
  "alternate_actor": "powerai/facebook-post-search-scraper",
  "refresh_cadence": "weekly",
  "endpoint_config": "wildlifestats/_pipeline/flyway/phrase-search-queries.json",
  "tier": "tier1-admin-only",
  "purpose": "Surface new high-value Pages to consider promoting to the monitored roster. Output reviewed by Mike or delegated admin before any Page enters the social-pages registry.",
  "notes": "Discovery loop, not a signal source itself."
}
```

### §2.3 `flyway-anchor-feeds` (structured citizen science)

References existing citizen-science source registry entries — Journey North, eBird, iNaturalist taxa filters. Architect default: add Journey North to the source registry as a first-class citizen-science source. iNaturalist and eBird are already in the registry per Phase 4.5+ scope.

```json
{
  "source_id": "journey-north",
  "display_name": "Journey North (hummingbird/monarch migration)",
  "url": "https://journeynorth.org",
  "license": "verify-cc-by-or-direct-permission",
  "access_method": "api-or-bulk-download-tbd",
  "refresh_cadence": "daily-during-migration-season",
  "tier": "public-and-research",
  "notes": "Anchor feed for Flyway's earliest signal layer. Verify license and API status during sub-PR 4.5+f."
}
```

## §3 — Signal definition (the reusable unit)

Per the engineer's INBOX framing, a signal is:

```json
{
  "signal_id": "first-hummingbird-spring-2026",
  "signal_type": "phenology.first_of_season",
  "subject_taxa": ["Trochilidae"],
  "subject_canonical": "hummingbird_any",
  "vocabulary": ["first hummingbird", "hummers are back", "anyone seeing any yet",
                 "ruby throated arrived", "first hummer of the year"],
  "anchor_feeds": ["journey-north:hummingbird-spring", "ebird:Trochilidae", "inaturalist:taxon-7227"],
  "geography_resolution": "county",
  "season_window": {"month_start": 2, "month_end": 6},
  "baseline_period_years": 5,
  "trigger_logic": {
    "early": "first observation week N < baseline mean − 1.5 stddev",
    "late": "first observation week N > baseline mean + 1.5 stddev",
    "spike": "weekly post count > rolling 8-week mean × 3"
  },
  "active": true,
  "owner": "architect-curated"
}
```

Signal definitions live at `wildlifestats/_pipeline/flyway/signals/<signal-id>.json`. The architect ships the first batch; new signals are added by editorial curation (Mike + architect) as needed.

### §3.1 First batch of signals to define

For the Phase 4.5+f initial ship:

1. **`phenology.first_of_season.hummingbird_spring`** — ruby-throated, anna's, rufous arrival
2. **`phenology.first_of_season.monarch_spring`** — milkweed emergence, first sighting
3. **`phenology.baby_season_start.songbird`** — orphan/displacement reason in vocabulary, paired with seasonal cube data
4. **`hazard.hpai_outbreak`** — die-off vocabulary (dead bird counts, mass mortality), paired with APHIS HPAI dashboard
5. **`hazard.oiled_bird_event`** — petroleum-coated/oil-covered vocabulary, paired with NOAA stranding data
6. **`hazard.weather_kill_event`** — storm-related mass mortality, paired with NWS storm reports
7. **`phenology.amphibian_breeding_start`** — first frog calls / salamander migration
8. **`hazard.window_strike_spike`** — migration-season collision spikes, paired with bird-banding data

Eight signals is enough to validate the pipeline. The catalog grows by editorial curation.

## §4 — Extraction schema (typed signal records)

Each scraped post passes through an LLM extraction pass producing zero or one signal record:

```json
{
  "record_id": "<sha256(source_url + extracted_signal_type + extracted_date)>",
  "extracted_at": "2026-06-10T19:30:00Z",
  "source_type": "facebook|instagram|tiktok|youtube|web",
  "source_url": "https://facebook.com/page/...",
  "source_org_id": "<flyway-roster-org-id>",
  "signal_id": "phenology.first_of_season.hummingbird_spring",
  "extracted_fields": {
    "event_type": "first_of_season",
    "species_canonical": "hummingbird_any",
    "species_verbatim": "ruby-throated",
    "geo_county_fips": "51043",
    "geo_state": "VA",
    "geo_locality_verbatim": "Loudoun County",
    "event_date": "2026-04-12",
    "event_date_precision": "day|week|month",
    "confidence": 0.85
  },
  "extraction_method": "claude-haiku-flyway-extractor-v1",
  "extraction_prompt_hash": "<hash of system prompt>",
  "post_text_NOT_STORED": true,
  "license_compliance_notes": "Extract only; original post content not retained per ToS."
}
```

**No raw post text is stored.** Only the extracted typed record + `source_url` for citation. This is the legal posture per §6.

Schema lives at `wildlifestats/_pipeline/flyway/signal-schema.json`. The extraction system prompt lives at `wildlifestats/_pipeline/flyway/extraction-prompt.md`, versioned.

## §5 — Baseline + anomaly detection

The actual "early warning" is the baseline deviation, not the scrape. Per signal × region × week:

1. **Historical baseline:** rolling 5-year mean and standard deviation of weekly signal counts for the (signal_type, county_fips, week_of_year) tuple. Computed from cube data for back-years; bootstrapped during the synthetic-only era from the n=1M cube's seasonality model (since real Flyway signal history doesn't exist yet, the synthetic seasonality is the baseline for the first season).
2. **Current observation:** count of extracted signal records in the (signal_type, county_fips, week_of_year) tuple for the current week.
3. **Trigger:** per signal's `trigger_logic` block (§3 example):
   - `early`: first observation in season N occurs more than 1.5σ before mean first-observation week
   - `late`: same, after
   - `spike`: weekly count > rolling 8-week mean × 3
4. **Alert routing:** triggers produce records in `secure/cube/flyway/triggers/<YYYY-WW>.json`, surfaced on the secure/research dashboard and via WREN. Triggers do NOT auto-notify Mike; the dashboard is the surface.

Baselines update weekly. Triggers evaluate daily.

## §6 — Legal posture and ToS compliance

This is the constraint that shapes everything. Spelled out explicitly:

1. **No raw post text is stored or republished.** The Apify scrape returns post content; the extraction pass produces a typed record; the post content is discarded at extraction. Only `source_url` is retained for citation back to the original.
2. **No re-syndication of media (images, videos).** Extracted signal records do not include image URLs from the scraped post. If a signal cites visual evidence, the citation is the link to the original post.
3. **Public Pages only.** Per the engineer's INBOX: FB groups are login-walled + ToS-prohibited for automation. Skip. Public Pages and public hashtag/phrase search only.
4. **Attribution preserved.** Every signal record's `source_url` resolves back to the original poster.
5. **Take-down on request.** If an org requests removal from the Flyway roster, that org's `source_org_id` is removed from `flyway-social-seed-top100.csv` within 5 business days, and historical extracted records from that org are scrubbed from the signal store. The `secure/cube/flyway/` history file logs the removal with the date and org-id.
6. **Apify ToS compliance.** The official actors used (`apify/facebook-posts-scraper`, `apify/instagram-post-scraper`) handle the platform-side ToS at the actor layer. WildlifeStats's liability surface is the extraction-and-storage policy above.

The methodology page at `/methodology/flyway/` documents this posture publicly. The engineer ships that page in sub-PR 4.5+f.

## §7 — Cost discipline

Per the engineer's feasibility math: ~99 Pages × FB+IG, daily, date-filtered ≈ $1-2/day, ~$50/month. Plus LLM extraction at Claude Haiku tier — if 99 Pages × ~5 posts/day = ~500 posts/day, each post a ~500-token classification call at Haiku rates is well under $1/day.

**Total runtime cost target: under $100/month** including discovery loop, scrape, extraction, and baseline computation.

The cost is recurring and requires Mike's authorization to start. See §10 below.

## §8 — Storage layout

```
wildlifestats/_pipeline/sources/
  flyway-social-seed-top100.csv          # The roster (already landed)
  flyway/                                  # Architecture-A new directory
    signal-schema.json                    # Typed-record schema
    extraction-prompt.md                  # LLM extraction system prompt
    signals/                              # Per-signal definitions
      phenology.first_of_season.hummingbird_spring.json
      phenology.first_of_season.monarch_spring.json
      ... (8 total in first batch)
    phrase-search-queries.json            # Discovery query list
    actors-config.json                    # Apify actor parameters per source type

wildlifestats/_pipeline/flyway/           # Code
  extract.py                              # Post → signal-record pipeline
  baseline.py                             # Rolling baseline computation
  triggers.py                             # Anomaly detection + trigger emit
  apify_client.py                         # Apify actor wrapper
  run_daily.py                            # Daily orchestration entry point

secure/cube/flyway/                       # Output (research-tier-only)
  signals/<YYYY-WW>.json                  # Weekly signal records
  baselines/<signal-id>.json              # Per-signal historical baseline
  triggers/<YYYY-WW>.json                 # Detected anomalies
  audit/<YYYY-MM>.jsonl                   # Per-record extraction provenance

.github/workflows/
  flyway-daily.yml                        # GH Actions daily cron
```

All of `secure/cube/flyway/` is research-tier-only (Tier 2 + Tier 1). Tier 3 (member) sees aggregate trigger summaries through WREN but not individual extracted signal records.

## §9 — Surface integration

### §9.1 WREN

Once Flyway signals are flowing, WREN's data context expands to include:

- The current week's triggered signals (early/late/spike per region)
- Last 12 weeks of signal counts per region
- Per-signal baseline expectations

WREN can answer "is baby season early this year in the Northeast?" by querying the baseline + current observation for `phenology.baby_season_start.songbird` × Northeast counties × current week.

WREN's existing safety rails (§7 of WREN spec) extend to Flyway: no inventing signal counts, no clinical interpretation of die-off events, attribution preserved in answers.

### §9.2 `/secure/research/flyway/` dashboard

A simple dashboard at the research tier:

- Map: US states colored by triggered-signal density this week
- List: triggered signals by recency, with source-org and source_url linkbacks
- Per-signal time-series chart: current year vs. baseline
- Take-down request form (per §6.5)

### §9.3 `/methodology/flyway/` (public)

A public methodology page explaining what Flyway does, how the pipeline works, and the legal posture. Linked from the homepage and from the public `/methodology.html`. Engineer ships in sub-PR 4.5+f.

## §10 — Phasing (sub-PRs)

Flyway lands as Phase 4.5+f through 4.5+j (continuing the Phase 4.5+ source-registry numbering from the previously-dispatched engineer order):

| Sub-PR | Deliverable | Effort |
|---|---|---|
| **4.5+f** | Source registry entries + storage layout + methodology page + signal-schema.json + first 8 signal-definition JSON files. NO scraping yet. | ~half day |
| **4.5+g** | Apify client + extraction pipeline + LLM extraction prompt. Smoke test on 3-5 Pages × hummingbird signal. NO daily cron yet; manual run only. | ~full day |
| **4.5+h** | Baseline computation + anomaly trigger logic. Bootstrap baselines from synthetic cube seasonality. | ~half day |
| **4.5+i** | Daily GH Actions cron + commit-on-change automation for the full 99-Page roster | ~half day |
| **4.5+j** | Research-tier dashboard at `/secure/research/flyway/` + WREN context integration | ~full day |

Sub-PR 4.5+g is the **point at which recurring cost begins**. Sub-PRs 4.5+f, h, i, j either don't run Apify (f, h, j) or run it once via the existing manual smoke test (g). Mike's recurring-cost authorization (per §11) gates the transition from 4.5+i's manual cron run to its actual scheduled-cron activation.

## §11 — Mike-only decisions (surfaced now, not blocking 4.5+f)

These are §22 candidates if any block progress later. Right now they don't block — engineer can ship 4.5+f without any of these answered.

1. **Recurring-cost authorization.** ~$50-100/month for Apify + LLM extraction. Architect default: ship 4.5+f, run 4.5+g manually once for ~$5-10 of credit, present results to Mike with cost projection, then Mike authorizes the recurring spend before 4.5+i activates the daily cron.
2. **Journey North access.** Architect default: 4.5+f's source registry entry for `journey-north` includes a note "verify API access; if no API, defer to manual ingestion or skip until license clarified." Engineer documents what they find; Mike decides whether to pursue direct contact.
3. **Take-down policy turnaround.** Architect default: 5 business days (matching the secure-tier take-down policy in §5.4 of the national-research spec).
4. **Phrase-search discovery review cadence.** Architect default: weekly admin review (Mike or delegated admin). Architect prepares the queue at the cadence; Mike approves Pages into the monitored roster.

## §12 — What Flyway is NOT

- Not a real-time monitoring service (daily cadence, not hourly or live).
- Not a substitute for WHISPers, ProMED, or other official surveillance. Flyway is a complement that often surfaces earlier but with lower confidence.
- Not a publication platform for scraped content. Only extracted signals + source URLs are stored.
- Not a generic social-media analytics tool. Curated to wildlife-rehab + phenology + hazard signals.
- Not coupled to BRWC. The roster has BRWC's own org scrubbed per §19; if BRWC's BRWC-internal use needs social signal monitoring, that's a separate BRWC-lane decision.

## §13 — Cross-references

- `INBOX-engineer-social-early-warning-2026-06-10.md` — the request that produced this spec.
- `wildlifestats-engineer-order-phase4.5-source-registry-2026-06-10.md` — Phase 4.5+ source registry order; Flyway adds 4.5+f through 4.5+j to that order's tail.
- `wildlifestats-secure-tier-national-research-spec-2026-06-10.md` — surface integration at Tier 2 / Tier 3.
- `wildlifestats-wren-architecture-spec-2026-06-10.md` — WREN context integration.
- `docs/research/data-sources/03-citizen-science.md` — anchor-feed source coverage.
- `wildlifestats/_pipeline/sources/flyway-social-seed-top100.csv` — the roster.

## §14 — Engineer order

A separate engineer order (`wildlifestats-engineer-order-phase4.5+f-thru-j-flyway-2026-06-10.md`) dispatches the five sub-PRs against this spec. Engineer can begin 4.5+f the moment that order lands; later sub-PRs gate on prior merges and on Mike's cost authorization.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 19:30 ET
