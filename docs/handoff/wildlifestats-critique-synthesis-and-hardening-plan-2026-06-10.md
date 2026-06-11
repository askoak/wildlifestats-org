# Critique synthesis + hardening plan

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 22:10 ET
**Status:** Synthesis of five parallel expert critique agents (saved under `docs/research/critique/0[1-5]-*.md`). Drives the Phase 4.6 hardening engineer order.
**Mike directive 2026-06-10 21:50 ET:** "Spin up one or more agents to do a critical review of the plan with expert context in data science ai machine learning llms etc wildlife research and critique the current build and plans. We want it hardened for capacity and sellable demos on the live website with made up and partially sourced corpus data."

## §1 — One paragraph

Five adversarial critique agents (data-science, AI safety, wildlife research, product/UX, engineering/ops) read the full spec corpus + the live site and produced ~17,000 words of structured criticism. The findings are largely additive rather than overlapping — each lens caught distinct failure modes. The most damaging single finding: **"calibrated against published wildlife rehabilitation literature" is unsupported prose** — no parameter in the synthetic cube ties to a named publication, sample size, or fit statistic. The most demo-critical finding: **the site ships the single-file cube (Architecture A), not the sharded cube (Architecture B)** that the spec recommends — `Cache-Control: max-age=0` on a 24.5 MB file blows out mobile demo-day load times. The most likely-to-actually-bite finding: **the WREN spec is ambiguous about Edge Function vs. Serverless Function**, and Edge Functions have a 50ms hard limit while Anthropic calls take 200ms–3s. If the engineer builds the wrong type, WREN times out on every request.

Two findings reached cross-critique consensus and are the highest-confidence items: **(1) Flyway's baseline must come from real eBird/Journey North historical data, not bootstrapped from the synthetic cube's invented seasonality** (data-science #2 + wildlife-research #6), and **(2) the parameter provenance table is required — cite the literature you claim to calibrate against** (data-science #1 + wildlife-research #2).

## §2 — What each critique found (one-paragraph summary each)

### §2.1 Data-science critique (`01-data-science.md`)

3,200 words. Central charge: the calibration language is fiction. The ±5–10% uniform jitter produces too-clean marginal distributions; the year-over-year weights (2020 dip, 2021 rebound) are asserted not cited; the species-archetype probabilities are architect judgment with no fit; the k-anonymity framework fails for rural single-organization counties regardless of cell-count threshold; the DOI placeholder `10.xxxx` is theatrical; the Flyway bootstrap from synthetic seasonality is self-licking. Top fix: build a parameter provenance table that converts "calibrated against" from fiction to fact (1-2 work sessions).

### §2.2 AI-safety critique (`02-ai-safety.md`)

4,815 words. Central charge: WREN's hallucination defense is conditional on architecture choices the spec doesn't pin down. Specifically: "quote, don't paraphrase" prevents wrong numbers but not wrong interpretive prose around right numbers; "structural rejection of invalid query plans" only works if plan-generation and summary-generation are separate LLM calls (the spec permits one round-trip); Wildlife911 safety rails are prompt-only with no output classifier; cost counter has a race condition; Flyway extraction will hallucinate `geo_county_fips` for ambiguous posts and contaminate the baseline; the OpenAI→Claude safety transfer for Wildlife911 is unverified. Top fix: two-phase LLM call with template-enforced summaries; add an output-layer safety classifier.

### §2.3 Wildlife-research critique (`03-wildlife-research.md`)

3,200 words narrative + extensive citations. Central charge: the schema fails immediately on a wildlife biologist's first inspection. `infectious_disease` as a single category collapses HPAI, rabies, WNV, lepto — the One Health page promises cross-species disease pattern analysis the data layer can't support; `marine` is a mixed-level class (marine mammals are still mammals); `deceased` should split into `dead_on_arrival` and `died_in_care`; `lead_toxicosis` is missing as its own category despite being the most-cited specific toxicology in the rehab literature; `iʻiwi` in the Hawaii synthetic table is ESA-Threatened and Section 10-permit-restricted — listing it as a routine admission archetype signals the team didn't talk to Hawaiian bird conservation biologists; the 1M cube implies 111K/year vs. FWS's 500K+/year figure (factor-of-five undercount, undocumented). Top fix: split `infectious_disease` into surveillance-relevant subcategories; cite the calibration literature; fix the taxonomy.

### §2.4 Product/UX critique (`04-product-ux.md`)

2,800 words. Central charge: the design competence is real but nothing on the live site survives a 30-minute institutional demo. Synthetic-data disclaimers disappear once a user scrolls into the cube — a screenshot of any result contains no "SYNTHETIC" label; `/data` shows "Loading the dataset…" with no progress indicator or timeout; About is two sentences with no contact path so a convinced buyer has no follow-up channel; there are zero CTAs anywhere; Wildlife911 is the genuinely useful 80-year-old-volunteer feature but it's absent from the live UX entirely (returns 404); mobile is untested. Top fix: persistent "SYNTHETIC DATA" watermark on every cube cell + CSV header comment.

### §2.5 Engineering/ops critique (`05-engineering-ops.md`)

3,887 words with live-site measurements. Central charge: the spec contains an architectural ambiguity that will sink WREN if not corrected — Edge Function vs. Serverless Function — and Netlify free tier blows the demo at 50K visitors. Live measurements: cube is 24.5 MB uncompressed (3.82 MB brotli), `Cache-Control: max-age=0,must-revalidate` (terrible for static files), all shard files 404 (Architecture B was specified, A shipped), `/secure/` returns plain 404 not auth redirect (Phase 5 not live), no monitoring exists. Flyway LLM extraction has no cost ceiling; WREN's Blobs counter has a multi-region race; bulk download rate limits are by API call count not row count (1M rows exfiltrable in one day at the published limits). Top fix: pin the WREN function type, ship sharded cube, set Cache-Control, upgrade to Netlify Pro.

## §3 — The consensus findings (highest confidence)

Two findings appeared in two critiques independently, derived from different reasoning chains. These are the strongest items:

### §3.1 Flyway baseline must use real history (DS #2 + Wildlife #6)

The Flyway spec's §5 "bootstrap baselines from synthetic cube seasonality (since real Flyway signal history doesn't exist yet)" creates a circular detection loop — the invented seasonality becomes the norm against which real social-media observations are evaluated. eBird has 20+ years of first-of-season data per species per county; Journey North has 30+ years for hummingbird/monarch arrivals. Both are downloadable. The Flyway baseline must be built from these real-history sources, not from the synthetic cube.

**Action:** Flyway spec §5 rewritten — Phase 4.5+h consumes eBird EBD + Journey North historical CSVs to build per-(signal, county, week) baselines. Phase 4.5+g smoke-test still produces signals; Phase 4.5+i daily cron still ships disabled until Mike authorizes cost. The change is in the baseline source only.

### §3.2 Parameter provenance table (DS #1 + Wildlife #2)

The methodology page and the Phase 3 spec both use "calibrated against published wildlife rehabilitation literature" without a single named citation. Critics named the specific papers that would credibly anchor the priors:

- Henger et al. 2021 (PLoS ONE, n=58,185 New York records) for admission-reason and outcome distributions
- McRuer et al. 2017 (J Wildlife Diseases) for cat-predation rates with explicit facility-level caveat
- FWS 2024 Conservation Value of Wildlife Rehabilitation for national admission totals
- Loss et al. 2013 (Nature Communications) for cat-mediated bird mortality context

The fix is one work-session: a table with one row per probability parameter, citing source publication, year, sample size, and whether the parameter is a direct estimate or a judgment consistent with that source. Where the honest answer is "architect judgment," say so. That language is defensible. The current language is not.

**Action:** Phase 3 spec gets a new §13 "Parameter provenance" with the citation table. Methodology page renders the table publicly.

## §4 — Top 12 hardening priorities (architect's ranked synthesis)

Drawing from 35 individual rankings across five critiques, deduplicated and ranked by combined impact-per-effort. Items 1-7 are pre-demo blockers; items 8-12 are pre-research-credibility blockers.

| # | Priority | Source critiques | Effort | Impact |
|---|---|---|---|---|
| 1 | **Pin WREN function type** (Serverless Function for Anthropic proxy, not Edge Function) | Eng #1 | 30 min spec | Demo-killer averted |
| 2 | **Synthetic data watermark** — persistent "SYNTHETIC DATA" badge on every cube cell, choropleth, chart, and as `# SYNTHETIC` first row of every CSV download | Product #1, Wildlife #6 (Flyway disclaim) | 1 day | Reputational-risk hardened |
| 3 | **Sharded cube actually ships** + `Cache-Control: max-age=86400` on cube files | Eng #3, Eng #7 | 1 day | Demo-day load time 3-10s → 0.1s |
| 4 | **Parameter provenance table** added to Phase 3 spec + rendered on methodology page | DS #1, Wildlife #2 | 1 work session | Calibration language goes from fiction to fact |
| 5 | **Flyway baseline switches to eBird EBD + Journey North historical** | DS #2, Wildlife #6 | 1-2 days (data pipeline addition) | Anomaly detection becomes meaningful in Year 1 |
| 6 | **Schema fix v1.2** — split `infectious_disease` into surveillance subcategories; rename `deceased` to `died_in_care` + add `dead_on_arrival`; drop `marine` class (use `habitat_guild` dimension); add `lead_toxicosis`/`rodenticide_toxicosis` reasons | Wildlife #1,3,4 | 1 day (regenerate cube) | Schema becomes vet-credible |
| 7 | **Two-phase WREN LLM call** — query-plan generation (call 1) → cube execution → template-enforced summary generation (call 2) | AI #1 | 1 day (Phase 7c) | Hallucination defense becomes real |
| 8 | **Wildlife911 static landing at `/wildlife911/`** with VA edition guidance + AnimalHelpNow CTA for non-VA users — even before the full pill ships | Product #4 | 1 day | PhD-to-grandma promise demonstrably real |
| 9 | **About page rewrite + contact path** + partnership CTA on Governance page | Product #3, #5 | 4 hours | Conversion path exists |
| 10 | **Adversarial test set** for WREN safety rails (20+ jailbreak/role-play/multi-step rephrasings beyond the 35-question baseline) | AI #3 | 1 day | Unknown-behavior safety surfaced before Mike's demo |
| 11 | **Reconcile the 111K vs 500K/year national figure** in methodology + Hawaii archetype scrub (drop `iʻiwi` ESA-Threatened from active probability table) | Wildlife #5, #7 | 4 hours | Disease-ecology / Hawaiian-conservation audiences not lost on first inspection |
| 12 | **Real Zenodo DOI minted** for the current cube snapshot — replaces `10.xxxx/wildlifestats.snapshot.2026Q2` placeholder | DS #4 | 1 hour | Theatrical citation gap closed |

## §5 — What gets pushed to a later phase (deliberate deferrals)

Critique items NOT in the top 12 — still real, but lower ratio of impact to effort or appropriate later:

- **Rural-county k-anonymity** (DS #3) — only matters when real partner data ships; today the synthetic data has no partner identity to protect. Deferral OK.
- **Overdispersion in synthetic variance** (DS #5) — a statistician would catch this in deep inspection, but the parameter provenance table (item #4) addresses the more visible weakness first. Queued.
- **Output-layer safety classifier for Wildlife911** (AI #2) — prompt-only is sufficient for the initial Phase 7g ship; the classifier is a Phase 7g.6 follow-on once real adversarial traffic surfaces.
- **Atomic cost counter** (AI #4, Eng #4 partial) — race window is small at Haiku rates; cost ceiling stays conservative until traffic scale justifies the rebuild. Note documented; revisit at scale.
- **Confidence-gated Flyway geo** (AI #6) — implemented in Phase 4.5+g acceptance criteria, but only matters at scale. Reasonable to defer to Phase 4.5+h baseline build where it integrates naturally.
- **Bulk download row/byte limits** (Eng #5) — meaningful when real partner data flows; before that the only exfiltratable data is synthetic. Queue for Phase 5e (Tier 2 API).
- **Voice-transition cue for Wildlife911** (AI #7) — UX polish; rolls into Phase 7g.3 public surface naturally.
- **One Health page data visualization** (Product #6) — nice but the schema fix (#6) is the gate; viz is naturally Phase 7c follow-on.
- **Mobile audit + accessibility** (Product #7) — Phase 7e already plans WCAG 2.1 AA; mobile becomes a explicit acceptance criterion there.

These nine items roll into Phase 7.x and Phase 5.x follow-ons rather than the immediate hardening order.

## §6 — Cost & timeline

The 12 top-priority items add roughly **6-8 engineer-days** of work, spread across:

- ~3 days infrastructure/UX (#1, #2, #3, #8, #9, #12)
- ~2 days data-pipeline (#5, #6)
- ~1 day spec/doc (#4, #11)
- ~2 days WREN + safety (#7, #10) — gated on Phase 7c-7d which are already queued

No new tool credits, no Mike-only decisions, no partnership work. All items are within engineer autonomous authority. The hardening engineer order dispatches as Phase 4.6 (capacity + demo-readiness hardening), parallel to and not blocking the existing engineer queue.

## §7 — Recommendation

Dispatch the Phase 4.6 hardening order immediately and let the engineer interleave it with their existing queue. The most demo-critical items (1, 2, 3, 8, 9) are all sub-day tasks that an engineer can interleave between phases without disrupting the larger build. The schema fix (#6) is the only architecturally substantial change and requires cube regeneration; that ships as a clean Phase 4.6 sub-PR.

Critique appendices saved at `docs/research/critique/0[1-5]-*.md`. Each is a standalone read with primary-source citations. They are the canonical record of why each hardening item exists.

## §8 — Cross-references

- All five critique reports: `docs/research/critique/0[1-5]-*.md` (committed in this batch)
- Phase 4.6 engineer order (dispatching in this batch): `wildlifestats-engineer-order-phase4.6-hardening-2026-06-10.md`
- Affected specs: Phase 3 cube spec (adds §13 provenance), Flyway spec (rewrites §5 baseline), WREN spec (pins function type, adds two-phase call to Phase 7c), Secure tier spec (queues row/byte limits to Phase 5e)
- Live site after hardening: `https://wildlifestats.netlify.app/` will reflect items 1, 2, 3, 8, 9, 11, 12 directly; items 4, 5, 6, 7, 10 are infrastructure / pipeline / methodology updates with secondary user-visible effects

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 22:10 ET
