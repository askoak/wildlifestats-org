# Adversarial Critique #1 — Data Science & Statistics
**WildlifeStats National Research Framework**
**Reviewer role:** Senior data scientist / statistician, PhD-level epidemiology and survey statistics
**Sources reviewed:** Phase 3 cube spec (2026-06-10), Phase 3 Amendment 1M (2026-06-10), Phase 4.5 pipeline spec (2026-06-10), Flyway spec (2026-06-10), Data Sources Master Plan (2026-06-10), Secure Tier spec (2026-06-10), live site at wildlifestats.netlify.app
**Date:** 2026-06-10

---

## Executive Summary

WildlifeStats has a professionally structured spec stack and a clean public presentation. The methodology page is honest about synthetic origins, the k-suppression logic is documented, and the deterministic build is a genuine reproducibility affordance most comparable projects skip. Those are real strengths.

What the spec stack does not have is citations. It has citation-shaped prose in their place. The calibration language — "calibrated against published wildlife rehabilitation literature," "consistent with patterns described in the peer-reviewed literature" — appears on the methodology page, in the governance page framing, and is implied throughout the spec. No citation in any of the six spec documents links a specific parameter choice to a specific published source. This is not a minor documentation gap; it is the central vulnerability. A statistician reviewing this framework for a grant application, a journal submission, or a funding decision will ask for the citations behind the numbers within the first five minutes, and they will not find them.

What follows is a systematic accounting of where the framework is defensible, where it is theatrical, and what it would take to survive expert scrutiny.

---

## 1. Synthetic n=1,000,000 Cube Fidelity

### 1.1 "Calibrated against published wildlife rehabilitation literature" — is it?

The methodology page says the model's shapes are "set to be consistent with patterns described in the published wildlife rehabilitation and wildlife-health literature, including the peer-reviewed analyses of multi-year rehabilitation admission records (for example, studies in *PLOS ONE* and the *Journal of Wildlife Rehabilitation*)." This is the entire citation apparatus on the public-facing page. The spec documents are no better: the Phase 3 spec (§5.1) asserts "slight upward trend... to reflect documented increases in wildlife rehabilitation case loads" with no citation. The amendment (§2) cites "WRMD's organizational count" for the 2,200-organization figure, but the admission-reason table (§6), outcome table (§7), and species-archetype probabilities (§4) carry zero citations.

"Calibrated against" implies a quantitative fitting process — observed data, estimated parameters, goodness-of-fit statistics. What the spec describes is expert-opinion parameterization with hand-tuned probability tables. That is a legitimate and defensible methodology in synthetic-data generation, but it needs to be called what it is. "Consistent with broad patterns described in the literature" is accurate. "Calibrated against" is not. A reviewer at *Journal of Wildlife Diseases* will flag this in round one.

The strongest published baselines for US wildlife rehabilitation admission patterns are:
- Shannon et al. (2014), PLOS ONE — multi-center wildlife rehabilitation analysis
- Sleeman (2008), Journal of Wildlife Diseases — national wildlife health surveillance framing
- WRMD aggregate annual reports — species mix, outcome distributions
- National Wildlife Rehabilitators Association (NWRA) annual census data

None of these are cited or named in the specs. The methodology page gestures at them generically. If those sources actually drove the parameter choices, citing them takes an hour. If they didn't, "calibrated against" is fiction.

### 1.2 Variance structure

The cube is aggregate cell counts, not individual records. The "jitter" described in Phase 3 §8 is ±5–10% on the final `n` per cell, drawn from a seeded RNG. This produces a cube that looks noisy at the cell level. A statistician examining the marginal distributions — total admissions by month, by state, by species class — will find them suspiciously smooth. The underlying model is a deterministic composite index (state allocation) feeding deterministic archetype weights (species) feeding deterministic seasonal curves (month). The jitter operates after these deterministic assignments, not on the generative process itself. The result is a cube whose aggregate marginals closely track the model's analytical expectations with minimal overdispersion.

Real wildlife rehabilitation data is highly overdispersed relative to a Poisson model. Admission counts are driven by discrete events — a storm, an HPAI outbreak, a cat predation wave — that create clustered, correlated counts that a jitter layer on top of deterministic weights cannot replicate. The Phase 3 spec uses Poisson-jitter language loosely; the actual implementation (±5–10% on final `n`) is not a Poisson draw; it is uniform noise on a fixed number. A reviewer looking at the variance-to-mean ratio across comparable cells will notice this. It will read as too clean.

### 1.3 Year-over-year weights: the 2020 dip and 2021 rebound

Phase 3 §5.1 specifies:
```
2020: 0.92,  // pandemic dip (real centers documented this)
2021: 1.05,  // post-pandemic rebound
```

The comment says "real centers documented this." No citation is provided. The claim is plausible — human activity reductions during COVID-19 likely reduced vehicle strikes; volunteer center shutdowns likely reduced intake; finders staying home likely increased orphan presentations — but these effects cut in opposite directions, and aggregate intake trends during 2020 varied by species class, geography, and center size. The WRMD consortium is the only organization with the aggregated data to confirm the net direction and magnitude of the 2020 effect. That data is not publicly available. Without a published source, these weights are invented with a plausible story attached. A reviewer will ask for the citation and there isn't one.

The 2021 "rebound" to 1.05 — above 2019's baseline of 1.00 — requires a specific mechanism. Wildlife populations do not rebound from reduced human mortality in one year. Intake counts could rebound if finder reporting increased. That's speculative without data. The weights 0.92 and 1.05 look precise; they are not grounded.

### 1.4 Seasonality model

Phase 3 §5.2 defines three latitude bands with different peak months and amplitude multipliers. The structure is ecologically reasonable — baby season does peak later at higher latitudes — but every number in the table (peak month = June at lat ≥ 42°; amplitude = 2.5×; AK amplitude = 3.0×) is an architect's estimate, not a fit to data. The correct citation here would be something like LaHaye et al. or Barber et al. on latitude-dependent breeding phenology, or NWRA survey data on intake seasonality by region. Neither is cited. The methodology page describes the structure in plain English without asserting it is measured.

This is actually the area where "consistent with broad patterns" is most defensible — the directional claim (later peak further north) is well-established in ornithology and mammalogy. The problem is the specific multipliers. A 2.5× vs. 3.0× difference between mid-latitude and Alaska implies quantitative precision that the spec cannot support.

### 1.5 Species-archetype probability tables

Phase 3 §4 defines fourteen biogeographic regions with "class-stratified species probability table[s]." The spec gives qualitative descriptions ("Higher: passerines, raptors; Lower: reptiles") and says "Each region defines a class-stratified species probability table." The full tables are in `wildlifestats/_build/species-archetypes.json`, committed to the repo but not quoted in the spec.

The probability tables are the most directly auditable component of the cube. A reviewer from a regional wildlife rehabilitation organization can look at the Pacific Northwest archetype and immediately tell you whether the raptor-to-passerine ratio is plausible. The spec gives no provenance for how these ratios were set — no citation to regional rehabilitation center reports, no reference to eBird or GBIF occurrence data, no NWRA survey. The methodology page says the tables are "committed at `wildlifestats/_build/species-archetypes.json`" and that they are auditable, which is good, but audit requires a ground-truth comparison and none is provided.

### 1.6 "Where did n=12,450 for AL come from?"

This is the exact question a data director at a foundation or a peer reviewer will ask. The answer, from the Amendment §5's meta example, is: Alabama's share of the 1,000,000 total, derived from the 60/30/10 composite index (Census population + land area + federally protected land area), then distributed across counties. The composite weight for Alabama is deterministic and reproducible. But the composite index itself has no citation for why it is 60/30/10 rather than 50/40/10 or 70/20/10. The weights are plausible and the spec explains them in §3.1, but "plausible" is not "validated." A statistician will ask whether the composite-index weights were tested against any known distribution of rehabilitation center locations or intake volumes. They were not.

The answer to "where did n=12,450 come from?" is therefore: the deterministic model says so, given these unchosen-but-undocumented weights. That's honest but not defensible as "calibrated."

---

## 2. K-Suppression Policy

### 2.1 k=10 public, k=5 research-tier, k=1 admin. Where does k=5 come from?

The Secure Tier spec §4.2 states: "k=5 cell suppression at Tier 2, vs. k=10 at Tier 3 and public." The choice of k=10 for the public tier is consistent with federal statistical standards — the US Census Bureau's rule-of-three is more conservative; NCES uses k=3 in some contexts; k=10 is common in public health disclosure limitation (see CDC WONDER and state vital statistics tables). k=10 is defensible.

k=5 at Tier 2 is less standard. The Secure Tier spec §10 notes this: "Some researchers will argue k=3 is acceptable for synthetic data; some partners will demand k=10 even for anonymized records." That footnote acknowledges the uncertainty without resolving it. The choice of k=5 appears to be an architect's judgment call split-the-difference decision. There is no citation to a federal standard, published data-sharing framework, or privacy literature supporting k=5 as the appropriate threshold for anonymized wildlife rehabilitation records under a data-use agreement.

The appropriate comparison standard would be the HIPAA Safe Harbor (k not specified but cell sizes of 1–2 in a combination of quasi-identifiers are considered re-identifying) or the data-sharing frameworks used by WRMD, NEON, or eBird for research-tier access. None are cited. The Secure Tier spec's own framing — "some partners will demand k=10 even for anonymized records" — suggests the architect knows this is contested and has not resolved it.

### 2.2 Does county_fips + species_canonical + month achieve k-anonymity for low-prevalence species?

No. And this is the most serious technical flaw in the suppression framework.

The Secure Tier spec §4.2 defines the re-identification risk combination as: "Month + county_fips + species (canonical) + reason + outcome." The spec asserts that suppressing combinations with ≤ 4 records achieves k=5 anonymity for partner organizations. But k-anonymity in this context is being applied at the wrong level. The threat model for wildlife rehabilitation records is not re-identification of individual animals (which have no privacy interests); it is re-identification of the *contributing rehabilitation center*.

Consider: if a given county has only one licensed wildlife rehabilitation organization, then any record attributed to that county is effectively attributed to that organization, regardless of k-suppression on the cell count. In rural counties — which this cube explicitly covers ("every county in the US... even tiny ones," Phase 3 §3.2) — there may be zero to one rehabilitation organizations. For low-prevalence species in a rural county (e.g., a manatee admission in a coastal Florida county with one marine rehabilitation center), even a cell count of 5 or 10 unambiguously points to a single organization.

The spec does not address this. "County FIPS" is the geographic resolution for Tier 2 anonymized records (Secure Tier §4.1). For many counties, county FIPS is sufficient to identify the contributing partner. The correct approach would be geographic generalization (roll up to multi-county regions for rural areas) combined with cell suppression. This is standard in health data de-identification (Sweeney 2002; Benitez & Malin 2010). Neither is cited or implemented.

For the synthetic-only era, this is moot — there are no real partners to re-identify. But the spec is presenting this framework as production-ready for real partner data, and the suppression mechanism fails on first contact with sparse rural records.

---

## 3. Reproducibility Claims

### 3.1 "Same seed → byte-identical output" — does sharded architecture preserve this?

Phase 3 Amendment §4.6 states: "running `python generate_synthetic_cube.py --seed 42 --n 1000000 --output-mode sharded --out-dir data/cube/` twice produces byte-identical output. The shard files are written in deterministic state-postal-code order; cells within each shard are sorted by (year, month, county_fips, class, species, reason, outcome)."

The determinism claim is plausible if implemented correctly, but the sharded architecture introduces a subtle failure mode. In sharded mode, the spec says the generator writes "51 files" in deterministic postal-code order. But the reproducibility of individual state shards depends on whether the RNG is advanced per-state (state-local seed derived from master seed + state index) or globally (a single RNG stream feeding all states in sequence). If it's globally sequential, then changing the allocation to one state (e.g., by updating the Census population data) would shift the RNG state for all subsequent states, breaking determinism for every downstream shard. The spec does not specify which RNG threading model is used. For a reproducibility claim to hold at the byte level, this needs to be explicit in the spec.

The amendment's framing — "Determinism preserved" — is stated but not mechanically justified for the sharded case. For the single-file case, byte-identical output from a fixed seed with a fixed RNG library version is trivial to guarantee. For the sharded case, it requires an explicit commitment about how state-level RNG seeds are derived from the master seed. That commitment is absent.

Additionally: NumPy's PCG64 stream is described as "stable across versions" on the methodology page. This is correct for the same NumPy major.minor version, but NumPy's release history includes documented instances of bit-generator behavior changes across minor versions. The spec pins `numpy==1.26.4`, which addresses this, but the methodology page says "NumPy's PCG64 random stream is stable across versions" which is an overstatement that will be challenged by anyone who has debugged a NumPy RNG portability issue.

### 3.2 DOI-stamped quarterly snapshots: real or theatrical?

The Secure Tier spec §5.3 describes quarterly DOI issuance via "DataCite (free for the first 100/year on the EZID service)." The citation snippet template shows `Snapshot DOI: 10.xxxx/wildlifestats.snapshot.2026Q2`. The `10.xxxx` placeholder is not a real DOI prefix; it is a template variable that has not been filled.

As of the spec date (2026-06-10), EZID — the California Digital Library's identifier service — is not offering new DOI registrations to the general public; EZID's free service was restructured and new registrations require institutional affiliation. DataCite requires a member fee (~$500–2,000/year for small organizations). The architecture assumes a free DOI workflow that may not be operational at the claimed cadence without either a CDL institutional relationship or a DataCite membership fee.

The spec notes this as a "Mike-only decision" (§10, item 1): "Architect default: EZID + DataCite. Cost: free for the first 100 DOIs/year, then nominal." The assumption that EZID is freely available is outdated. Zenodo (as the spec mentions as an alternative) is the currently operational free DOI workflow for research datasets, but the spec treats it as a lower-prestige option: "simpler integration, less institutional gravitas." For a demo-stage platform, Zenodo is the appropriate choice; the EZID default is likely not executable without a CDL institutional relationship that does not currently exist.

More fundamentally: the quarterly snapshot DOI workflow is entirely unbuilt. Phase 5f ("Bulk download infrastructure + quarterly snapshots + DOI integration") is a future phase. The governance page refers to DOI-cited downloads as a near-term feature; the methodology page implies the dataset has citeable provenance now. A CIO looking at this at demo time will see citation-format language on the live site and a `10.xxxx` placeholder in the spec. That is theatrical.

---

## 4. Flyway Baseline — The Self-Licking Ice Cream Problem

Flyway spec §5.1 describes the baseline computation for anomaly detection:

> "Computed from cube data for back-years; **bootstrapped during the synthetic-only era from the n=1M cube's seasonality model** (since real Flyway signal history doesn't exist yet, the synthetic seasonality is the baseline for the first season)."

This is the framework's most serious statistical design flaw, and it deserves direct language: the Flyway anomaly detection is circular during the synthetic-only era. The synthetic seasonality model is an invented curve (latitude-banded Poisson-jitter, no primary data). That same curve is then used as the baseline against which real social-media signals are evaluated for "early," "late," or "spike" status. Any real-world deviation from the invented baseline will produce a trigger — but the trigger is measuring deviation from a fabricated expectation, not from a measured historical norm.

The trigger logic in Flyway §3 uses standard deviation thresholds: "early: first observation week N < baseline mean − 1.5σ." During the synthetic-only era, the baseline mean and σ are computed from the synthetic cube's seasonality model, which has no real variance — its σ is the model's own jitter, not the natural year-to-year variability of actual phenological events. Real first-of-season events (hummingbird arrivals, baby season onset) have genuine year-to-year standard deviations of 1–3 weeks at the regional level, driven by climate variability. The synthetic σ will almost certainly be too small (the jitter is ±5–10% on counts, not on timing), making every real-world deviation appear anomalous. The "early warning" system will fire constantly during the bootstrapping period and provide no actionable signal.

The spec acknowledges this indirectly: "since real Flyway signal history doesn't exist yet, the synthetic seasonality is the baseline for the first season." But it doesn't flag this as a limitation that makes the early-warning function non-operational until real baseline data accumulates. In a public-facing research framework, presenting Flyway alerts during the synthetic-only era as scientifically meaningful would be misleading.

The correct approach is to use the anchor feeds (eBird, iNaturalist, Journey North) as the baseline, not the synthetic cube. eBird has 2B+ observations with 20+ years of history; Journey North has 30+ years of documented first-of-season arrivals. These are genuine historical baselines against which current social-media signals can be compared. The spec mentions these anchor feeds in §2.3 but does not make them the primary baseline source. Instead, the synthetic cube is the bootstrap, and the citizen-science feeds are supplementary signals. This is backwards.

---

## 5. Mixing Synthetic + Real + Scraped Social into One Cube

The Data Sources Master Plan §7.5 states: "License enforcement at build time — the public cube only carries CC0, CC-BY, public domain, and explicitly-permitted CC-BY-NC-with-attribution data. Anything more restrictive flows to the secure tier only."

This is the routing policy. But the Phase 4.5+ pipeline spec describes a future state where the "public cube" would contain cells derived from:
- The n=1M synthetic cube (no real data, CC-BY-4.0)
- GBIF/iNaturalist occurrence records (CC0/CC-BY, real observational data)
- USGS WHISPers mortality events (public domain, real surveillance data)
- eBird checklists (research agreement, different unit of observation)
- Flyway social-media signal extractions (scraped-public-extracts-only, no redistribution)
- Eventually, partner rehabilitation intake records (partner DSA, real clinical data)

These sources have fundamentally different observation processes, units of measurement, and statistical properties. GBIF records are occurrence observations, not admission records. WHISPers events are mass mortality events, not individual intakes. eBird checklists are detection/non-detection lists. None of these map cleanly onto the wildlife rehabilitation intake schema defined in Phase 3 §2. Normalizing them all into a `year × month × county × species × reason × outcome × disposition` cell forces square data into a round schema: a WHISPers die-off event has no `outcome` in the rehabilitation sense; a GBIF occurrence has no `admission_reason`.

The pipeline spec §4 addresses the mapping problem: "Value normalization... maps partner free-text values to the canonical enumeration." But enumeration mapping is not the problem. The problem is conceptual incoherence: a cell in the mixed cube labeled `reason: infectious_disease, outcome: deceased, n=47` in 2022 for Florida waterfowl could be 47 rehabilitation intakes, or 47 individual carcasses from a WHISPers-reported die-off, or 47 eBird detections that were flagged as dead birds, all living in the same cube cell with no way to distinguish them. A researcher querying this cube without knowing the source provenance would misinterpret the count. 

The pipeline's provenance layer (Data Sources §7.4: "every cube cell knows which source(s) contributed, with what license") is the right design, but it is a planned future feature, not a shipped one. At demo time, the cube is purely synthetic and this issue is moot. But the architecture as planned creates a mixed-provenance cube that a statistician would refuse to analyze without source-level disaggregation.

The Flyway signal extraction adds a further complication. The Flyway spec §4 produces `extracted_fields` including `confidence: 0.85` — LLM extraction confidence scores. Mixing LLM-extracted social media signal (confidence 0.5–0.9) with cleaned federal surveillance data (much higher reliability) in the same analytical surface, without clear source-layer separation in the UI, would be methodologically indefensible for any serious research application. The spec correctly routes Flyway signals to the research tier only, not the public cube. But the boundary is managed by access tier rather than by explicit methodological separation in the cube schema, and that distinction will blur when the research-tier UI presents mixed-source queries.

---

## 6. Demo-Readiness

### 6.1 The question a CIO would ask

"You say this is calibrated against published wildlife rehabilitation literature. Can you show me the table of parameter sources — each number in your probability tables, the citation that grounds it, and the fit statistic?"

There is no such table. The methodology page says "calibrated against" and points at the committed generator script. A CIO reviewing this for a $500K grant decision wants to see the equivalents of a methods section from a peer-reviewed paper: prior distributions with literature citations, goodness-of-fit against held-out data, and an explicit uncertainty quantification on the synthetic-to-real gap. None of these exist.

A secondary question: "How do you know n=1,000,000 is the right size? Where does the confidence interval on national wildlife rehabilitation intake volumes come from?" The Amendment §2 argues this from a calculation: 2,200 orgs × 500–1,000 cases/year × 5–15 active years = "a credible national real-data cube projects to ~5–15M records." These three numbers are cited to "published rehab-center annual reports" (generically) and WRMD's organizational count (not a primary citation to a published source). The arithmetic is plausible but the inputs are undocumented.

### 6.2 What a peer reviewer at Journal of Wildlife Diseases would flag

A JWD reviewer would flag, in order:

1. **"Calibrated against" without a calibration method.** JWD requires methods sections to specify how parameter estimates were obtained. "Expert judgment consistent with the literature" is acceptable if stated as such; "calibrated against" implies a formal fitting procedure that does not exist.

2. **No uncertainty quantification on the synthetic data.** The validation tests (Phase 3 §11) check structural integrity — is the total within ±5,000, are all enums valid — but they do not check whether the generated distributions are plausibly within the confidence intervals of real rehabilitation admission data. There is no test like "are the marginal species distributions within ±20% of the NWRA census estimates?" because NWRA census estimates are not included in the validation suite.

3. **Jitter as the sole variance model.** The ±5–10% cell-level jitter does not model the epidemiologically relevant variance structure: outbreak clustering, center-level heterogeneity, interannual climate variability. JWD reviewers will recognize this immediately.

4. **The Flyway self-referential baseline.** A methods section that says "we use our synthetic model as the baseline for anomaly detection" would be rejected or sent back for major revision in any surveillance methods paper.

5. **Missing data handling at county level.** The spec acknowledges that some counties will receive records via the 50% uniform allocation even if they have no wildlife rehabilitation centers. This creates artificial rural coverage that is not representative of real intake patterns. The methodology page's "known limitations" section does not mention this.

6. **The 2020 pandemic weights as unverified claims.** JWD is an epidemiology journal; it will ask for the data behind any claim that the 2020 pandemic produced a specific directional effect on wildlife rehabilitation intake nationally.

---

## Top 7 Hardening Priorities (ranked by impact-per-effort)

**1. Build the parameter provenance table (highest impact, lowest effort)**
Create a single document — one row per probability parameter, with the source publication, the year, the sample size, and whether the parameter is a direct estimate from that source or a judgment consistent with it. This takes one to two focused work sessions and transforms "calibrated against" from fiction into fact. If the honest answer for many parameters is "architect judgment consistent with broad literature patterns," say that explicitly. That is defensible. The current language is not.

**2. Replace the Flyway synthetic bootstrap with eBird/Journey North historical baselines**
Before Flyway generates a single alert, its baseline must come from real phenological data with ≥5 years of history. eBird's full observation history for Trochilidae by county is downloadable and provides exactly the baseline Flyway needs for hummingbird arrival signals. Journey North has 30 years of first-of-season data. Using the synthetic cube as the baseline during the first season makes every Flyway alert meaningless and potentially misleading. Implementing the eBird baseline is a one-time data pipeline addition (not recurring cost); it should precede the first Flyway run regardless of whether the recurring scrape is authorized.

**3. Fix the k-anonymity analysis for rural counties**
The suppression framework applies k at the cell count level but ignores the population-size of the contributor pool. Commission or conduct a basic geographic analysis: for how many US counties does a single rehabilitation organization hold state permit? (NWRA and state wildlife agency permit databases partially answer this.) For those counties, county_fips is insufficient as a geographic resolution for partner anonymization, and the k=5 threshold is irrelevant — the partner is identifiable regardless of count. The fix is geographic generalization for single-organization counties, which is a standard cell-suppression technique in health data (analogous to census tract aggregation in HIPAA safe harbor).

**4. Replace the DOI placeholder with an operational Zenodo workflow before demo**
The `10.xxxx/wildlifestats.snapshot.2026Q2` placeholder is visible in the spec and will be asked about at any serious demo. Zenodo is free, operational, and accepts dataset deposits with automatic DOI assignment. Depositing the current synthetic cube as a Zenodo record takes under an hour and produces a real, citable DOI. This closes the theatrical citation gap immediately and provides a genuine reproducibility artifact before any foundation review. EZID should be evaluated separately with realistic cost information; Zenodo should be the operational default now.

**5. Add overdispersion to the variance model**
The ±5–10% uniform jitter produces implausibly smooth marginal distributions. Adding a negative-binomial draw at the cell level (with a dispersion parameter derived from published within-center interannual variation — WRMD annual reports provide year-to-year variance at the center level) would produce a statistically credible variance structure with minimal code change. This is a generator script modification, not an architectural change. A statistician examining the cube's marginal distributions will currently recognize it as too-clean synthetic data within minutes; this change makes it pass a more rigorous inspection.

**6. Separate the provenance layer in the cube schema before mixing sources**
Before any real data — GBIF, WHISPers, eBird, partner records — enters the cube alongside synthetic records, add a `source_ids: []` field to every cell and render it in the public UI and the download. A researcher must be able to filter to "synthetic only," "federal surveillance only," or "partner records only" without inferring it from tier membership. The Phase 4.5+ pipeline spec already requires a provenance layer (§7.4); it should be a hard acceptance criterion for any source addition, not a future feature. Mixing sources in an opaque cube is the fastest path to a methodological retraction.

**7. State the calibration limits explicitly in the methodology page**
The existing "Known limitations" section on the methodology page is good but stops short. It should explicitly state: (a) the year-over-year trend weights, including the 2020 pandemic dip, are expert estimates pending validation against real multi-center data; (b) the species-archetype probability tables represent author judgment based on biogeographic literature and are not fitted to observed rehabilitation intake distributions; (c) during the synthetic-only era, Flyway baselines are modeled, not measured, and anomaly signals during this period should not be interpreted as statistically validated departures from historical norms. This language protects the framework against the most obvious peer-review objections and can be added in less than an hour.

---

*Critique authored for internal architect use. All spec quotations are from the cited documents dated 2026-06-10. Line numbers and section references correspond to the raw file versions reviewed.*
