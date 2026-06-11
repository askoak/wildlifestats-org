# Critique #3 — Wildlife Research Credibility & One Health
**Reviewer perspective:** Senior wildlife disease ecologist, PhD, 15+ years USGS NWHC / equivalent; publications in Journal of Wildlife Diseases, EcoHealth, Emerging Infectious Diseases; fluent in One Health, rehabilitation-medicine literature, and the WRMD data ecosystem.

**Subject:** WildlifeStats build plan — adversarial critique from a wildlife-research-credibility standpoint.
**Live site reviewed:** https://wildlifestats.netlify.app (data, methodology, governance, one-health, wildlife, parks pages)
**Docs reviewed:** Synthetic cube spec (Phase 3 + Amendment 1M), Flyway spec, Data Sources Master Plan, all seven appendices, Wildlife911 VA YAML.
**Date of review:** 2026-06-10

---

## Opening Assessment

WildlifeStats is well-intentioned and shows genuine familiarity with the landscape — WRMD, WILD-ONe, USGS WHISPers, the Levy/Loss debate, APHIS HPAI, the importance of the rehab network as a sentinel surveillance layer. The architecture thinking is sophisticated. But the first-ship public dataset is a sophisticated house of cards: 1,000,000 synthetic records built on undocumented priors, presented in a framework that claims to be "calibrated against published wildlife rehabilitation literature" without naming a single paper in the spec. When an institutional buyer or a peer reviewer pulls that thread, the whole credibility narrative unravels fast. The problems below are not fatal — most are fixable — but they need to be addressed before this goes in front of foundations, agencies, or USGS NWHC staff.

---

## 1. Schema Credibility

### 1.1 Admission reason taxonomy

The cube spec's enumeration — `vehicle_strike`, `window_strike`, `predation`, `entanglement`, `orphan_displacement`, `habitat_disruption`, `anthropogenic_poisoning`, `infectious_disease`, `other_trauma`, `unknown` — is directionally defensible but has holes that any rehab vet will immediately notice.

**Lead poisoning is missing as a named category.** It is collapsed into `anthropogenic_poisoning` at 4% base rate. That is methodologically indefensible for a national research framework. Lead toxicosis is the single most documented specific toxicological admission cause in the published rehabilitation literature. It is the primary cause of intoxication in bald eagles, golden eagles, and California condors (Redig & Arent 2008, cited in the [FWS Conservation Value of Wildlife Rehabilitation report](https://www.fws.gov/sites/default/files/documents/2024-12/conservation-value-of-wildlife-rehabilitation.pdf)). At the [Wildlife Center of Virginia](https://wildlifecenter.org/lead-in-animals) — one of the most data-rich rehabilitation facilities in the country and the source of the McRuer 2017 study — 75% of bald eagles admitted over a 10-year period had measurable lead in blood. Anticoagulant rodenticide poisoning is a separate, well-characterized admission pathway in the urban raptor population (Murray 2017 found 96% of 94 birds of prey admitted to a Massachusetts clinic had detectable anticoagulants). Lead and rodenticides are not the same biological mechanism, the same geographic pattern, or the same public-health story as, say, `habitat_disruption`. Collapsing them under `anthropogenic_poisoning` destroys the One Health signal entirely.

**Electrocution is absent.** Power-line electrocution is a documented admission category for large raptors and waterfowl across the American West, tracked explicitly in USGS NWHC mortality records and in the [New York rehabilitation dataset (Henger et al., PLoS ONE, 2021)](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0257675). It is operationally distinct from vehicle strike — different species (eagles, herons, large buteos), different geography (transmission corridors, not roads), and different rehabilitation prognosis.

**Entanglement subtypes matter clinically.** The spec lists `entanglement` as a single top-level reason with a 5% base rate (bumped for marine). But fishing-line entanglement in songbirds around backyard feeders, gill-net bycatch of diving seabirds, and ghost-gear entanglement of sea turtles have radically different outcome profiles, geographic signals, and policy relevance. For the One Health and marine hazard signals the framework wants to surface, collapsing these is noise pollution.

**The `predation` category is taxonomically ambiguous.** Predation by what? Cat predation is the dominant and contested signal — McRuer et al. 2017 found cat interaction was the third-greatest cause of mammal admissions (14.8%) and second greatest cause of avian mortality (80.8% of cat-presented birds did not survive) at one facility. The data-sources master plan eventually creates a separate `cat_predation_admission` reason enumeration in the cube for the public `/wildlife/cats/` page, but the spec as written doesn't include it in the primary reason enumeration. A reviewer would call this out: if you're treating domestic cat predation as epidemiologically distinct from, say, hawk predation — which is biologically justified — it needs to be in the schema, not in footnotes.

**Comparison to WRMD field structure:** WRMD's actual data model uses free-text fields with controlled vocabulary for "circumstances of rescue," not a locked enumeration. Published analyses that use WRMD data (e.g., [Henger et al. 2021, PLoS ONE](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0257675)) categorize admission reasons into: trauma (including collision, entanglement, companion-animal attack, gunshot, trapping), orphaning, habitat loss, infectious disease, and poisoning/toxin — six groupings from fifteen primary WRMD codes. WildlifeStats's enumeration is a reasonable approximation of that structure, but loses important sub-categories that the literature already treats as distinct. A WRMD data manager would also note that the spec never cites WRMD's actual data dictionary, which is publicly documented.

### 1.2 Outcome enumeration

The cube defines outcomes as `released`, `transferred`, `deceased`, `in_care`, `euthanized`, with `deceased` described in the spec commentary as "includes died-in-care." This is operationally wrong by the standards of every state wildlife rehabilitation reporting form in the country.

**Dead on arrival (DOA) and died-in-care are clinically and epidemiologically distinct.** The [Georgia DNR annual rehabilitation log](https://gadnrle.org/sites/default/files/le/pdf/Special-Permits/ANNUAL%20WILDLIFE%20REHABILITATION%20LOG%20TALLY.pdf), the [New York DEC Wildlife Rehabilitation Log](https://extapps.dec.ny.gov/docs/wildlife_pdf/wrlloginstruct16.pdf), and published analyses all separate these: the NY DEC form explicitly codes `D` as "died under/prior to receiving care" and `E` as "euthanized." Henger et al. 2021 (PLoS ONE) likewise separate "died under/prior to care" from "euthanized" in their analysis of 58,185 NY records. **Why does this matter?** An animal that arrives dead tells you something about mortality in the field and transport chain. An animal that dies in care under veterinary treatment tells you something about the prognosis of that admission reason. Collapsing them in the cube destroys the admission-reason × outcome correlation that is the only analytically interesting signal for research users.

**"Release-eligible long-term care" has no code.** Some species, particularly certain raptors, waterfowl, and sea turtles, spend months in rehabilitation before meeting release criteria. During that window they are neither "in_care" pending triage nor "transferred." The spec's `in_care` is designed as a residual for records that haven't resolved yet, not as a meaningful clinical category. Any rehab vet reviewing this will ask: what do you do with a pelican that's been in water conditioning for six weeks and will be released next month? It's not "transferred," not "deceased," not "euthanized" — it's appropriately "in extended pre-release conditioning." The absence of this code is fine for aggregate counts, but the public-facing narrative about release rates will be wrong if `in_care` is systematically misclassified.

### 1.3 Taxonomic class enumeration

`["bird", "mammal", "reptile", "amphibian", "marine"]` — this is a textbook mixed-level taxonomy error and any wildlife vet will flag it in the first five minutes. You are mixing taxonomic class (Aves, Mammalia, Reptilia, Amphibia) with an ecological/habitat category ("marine"). Marine is not a class; it is a biome. A marine mammal is still a mammal. A sea turtle is still a reptile. The correct solution is one of:

- **Option A (clean):** Use taxonomic class only (`bird`, `mammal`, `reptile`, `amphibian`, `fish`) and add a separate `guild` or `habitat` dimension (`marine`, `freshwater`, `terrestrial`) — which is how WRMD and most published analyses actually structure the data.
- **Option B (pragmatic):** Keep the current five categories but call the fifth `marine_mammal_or_seabird` and document explicitly that sea turtles are under `reptile` and marine mammals are under `marine` — and accept that you're building a non-standard schema.

As written, a user filtering by `class = marine` will get data that a peer reviewer cannot reconcile with any standard biological classification system. This is a credibility landmine for institutional buyers.

### 1.4 Disposition vs. outcome distinction

The spec defines both `outcomes` (`released`, `transferred`, `deceased`, `in_care`, `euthanized`) and `dispositions` (`wild_release_local`, `wild_release_relocated`, `permanent_sanctuary`, `research_donation`, `natural_death`, `humane_euthanasia`). The spec then shows outcome → disposition as a near-deterministic mapping: `released → wild_release_local (0.85)`, `deceased → natural_death (1.0)`, `euthanized → humane_euthanasia (1.0)`.

This distinction is **partially real but mostly constructed** for this framework. In actual WRMD records and state reporting forms, there is one field — "disposition" or "final outcome" — not two. The [NY DEC form](https://extapps.dec.ny.gov/docs/wildlife_pdf/wrlloginstruct16.pdf) uses a single letter code (R, T, P, I, D, E). WRMD has a single final status field. The "outcome vs. disposition" split adds analytical nuance (it lets you distinguish local vs. relocated releases, which is useful for translocation ecology), but it is not standard practice — it's a WildlifeStats design choice. That's fine, but the spec should say that explicitly rather than implying it reflects existing rehab-medicine schema. A reviewer will ask: which published dataset uses this exact two-tier structure, and where can I find the crosswalk to WRMD fields?

---

## 2. Synthetic Priors — Are They Defensible?

### 2.1 Regional species archetypes without citation

The regional species probability tables are built on educated inference, not cited data. The spec defines "Hawaii: higher seabirds, native passerines (`apapane`, `iiwi`)" — and this specific example is a credibility catastrophe waiting to happen.

`ʻIʻiwi` (*Drepanis coccinea*) was listed as **Threatened under the Endangered Species Act in 2017** ([Federal Register, 2017-20074](https://www.federalregister.gov/documents/2017/09/20/2017-20074/endangered-and-threatened-wildlife-and-plants-threatened-species-status-for-the-iiwi-drepanis)). Its range has contracted to high-elevation forest habitat on Hawaiʻi and Maui due to avian malaria from introduced mosquitoes ([FWS](https://www.fws.gov/project/iiwi-critical-habitat)). `ʻApapane` (*Himatione sanguinea*) is less dire but still an endemic honeycreeper with severely restricted range. The probability that a Hawaii rehabilitation center would be admitting these birds "in numbers" consistent with a synthetic probability weight is essentially zero. Honeycreepers at low elevation are effectively nonexistent; at high elevation, the human population density that drives rehabilitation admission is vanishingly small. Moreover, when a honeycreeper does come into contact with a rehabilitation facility, it is an event requiring **ESA Section 10 permitting** — it is not a routine intake. Any ornithologist or Hawaiian bird conservation biologist who sees `iiwi` listed alongside `passerine_songbird` as a regional species archetype for Hawaii will immediately conclude the team has never spoken to the Maui Forest Bird Recovery Project or the Peregrine Fund Hawaii program. The spec itself later adds a hedge — "taxa only, no individual species rarity calling" — which is the right instinct but still doesn't resolve the problem: `iiwi` should not appear in a synthetic probability table calibrated to rehabilitation intake frequency unless you intend to weight it at ≤0.001.

### 2.2 Seasonality amplitude is hand-waved

"Northern counties (lat ≥ 42°): peak month = June, amplitude = 2.5× off-season baseline." Where does 2.5× come from? This is the central number for the baby-season signal that the Flyway early-warning layer is proposing to detect anomalies against. If the baseline is fabricated, the anomaly detection is detecting deviations from a fiction.

Published rehabilitation data from New York state (Henger et al. 2021, PLoS ONE, n=58,185 over 2012–2014) shows orphaning at 37.3% of all admissions, trauma at 38.1%, with strong May–July seasonal peaks visible in case data. Canadian rehabilitation research (Proulx & O'Brien, 2020, *Journal of Wildlife Rehabilitation*) also documents spring-summer baby season, but the amplitude multiplier varies substantially by taxa and latitude. A 2.5× multiplier for the Northeast is plausible but is not the same as being documented. The spec needs to either cite the amplitude parameter to published seasonal intake data or explicitly state it is a design assumption — not present it as if it is calibrated.

The 2020 pandemic dip (0.92×) is asserted parenthetically as "(real centers documented this)" — no citation. This is the kind of claim that gets flagged immediately in peer review. Centers reduced operations in spring 2020, which would reduce *reported* admissions, but whether this reflects actual animal intake or reduced human reporting to wildlife centers is ambiguous. The USGS NWHC has documented wildlife mortality trends that did not necessarily follow the human-activity pattern in 2020. Presenting 0.92× as a calibrated parameter without a source is intellectually dishonest.

### 2.3 Base-rate probabilities lack grounding

`vehicle_strike` at 18% base, `orphan_displacement` at 22%, `predation` at 9% — are these calibrated against published data or invented? Comparing to Henger et al. 2021 (the most geographically comprehensive published US dataset): **trauma 38.1%, orphaning 37.3%, habitat loss 6.8%, infectious disease 3.1%, poisoning 1.4%**. If "trauma" includes vehicle strike, window strike, entanglement, predation, and other_trauma, then the WildlifeStats base rates need to be reconciled against this. At first glance, adding vehicle_strike (18) + window_strike (14) + predation (9) + entanglement (5) + other_trauma (10) = 56% trauma-class, vs. 38.1% in the NY dataset. That is a large discrepancy that is never acknowledged. Either the NY dataset is not representative (possible — NY has urban bias), or the WildlifeStats priors are inflated. A reviewer will catch this in the first pass.

---

## 3. Disease-Vector and One Health Framing

### 3.1 The One Health page promises what the cube cannot deliver

The `/one-health` page states that HPAI, leptospirosis, rabies, and West Nile virus are "visible in wildlife rehabilitation intake." This is true for real rehabilitation data. It is not true for the current synthetic cube, which has a single undifferentiated `infectious_disease` category at 6% base rate. HPAI is not separable from rabies is not separable from leptospirosis is not separable from WNV in this schema. The One Health page is therefore describing a capability the current data layer cannot support.

This is the single largest gap between the site's narrative and the actual data. A program officer at a foundation evaluating this for a One Health surveillance grant — and HPAI is currently one of the hottest funding areas in wildlife disease globally — will ask: "Show me the HPAI signal." The answer is: it doesn't exist in the current data. That conversation ends the funding discussion.

The fix is conceptually simple: add disease sub-categories to the `infectious_disease` admission reason: at minimum `hpai_suspect`, `rabies_suspect`, `wNV_suspect`, `leptospirosis`, `other_infectious`. But this requires either synthetic priors drawn from actual disease surveillance data (USGS WHISPers, APHIS HPAI detections, CDC ArboNET) or an honest acknowledgment that the One Health layer is aspirational content for a future data tier.

### 3.2 Spatial resolution and disease ecology

County FIPS as the finest geographic grain is adequate for many rehabilitation research questions (admission burden, release success by region) but insufficient for disease ecology, which is the explicit One Health use case. Mosquito-borne disease ecology (WNV, EEE, avian malaria in Hawaii) requires sub-county spatial analysis because the vector habitat — wetland edges, slow-moving water, urban heat islands — does not aggregate cleanly to county scale. The NEON network (cited in the data sources plan) is explicitly sub-county. WHISPers events are geocoded at point level (latitude/longitude). The spec never acknowledges this mismatch, implying that county-level resolution is "fine" for the disease ecology use cases the site claims to support. It is not fine for One Health peer review.

### 3.3 The `hazard.hpai_outbreak` Flyway signal lacks an operational definition

The Flyway spec proposes a `hazard.hpai_outbreak` signal with trigger logic: `"weekly post count > rolling 8-week mean × 3"` for die-off vocabulary on social media. This will fire on any viral wildlife story that drives social chatter — a single dead pelican photo going viral on TikTok, an unusual-season songbird mortality event that has nothing to do with HPAI, or the annual spring news cycle about bird flu that rehab center pages repost. The false-positive rate would be catastrophic for any researcher trying to use this as a surveillance signal.

A real HPAI early-warning signal requires: (1) species-specific vocabulary (waterfowl, raptors, corvids — not "dead bird" generically), (2) a minimum count threshold for mass die-off (single incidents are noise), (3) cross-referencing against APHIS HPAI detections in neighboring counties before firing, and (4) explicit acknowledgment that social media signals are lagging, not leading, USDA's own surveillance. The USGS WHISPers disease event database — which the data sources plan correctly identifies as a Tier 1 source — already has an early-warning function that is based on necropsy-confirmed mortality data. Flyway's social media signal should be positioned explicitly as a *complement* to WHISPers-style confirmed data, not as an early-warning system in isolation.

---

## 4. Wildlife Rehabilitation Specifics

### 4.1 "Calibrated against published wildlife rehabilitation literature" — name the papers

The methodology page states the data is "calibrated against published wildlife rehabilitation literature" and cites "studies in PLOS ONE" and "studies in the Journal of Wildlife Rehabilitation" as examples. This is not a citation. It is a gesture at a literature that exists.

Here is what that calibration would actually look like if done properly. The available published datasets for base-rate grounding:

| Source | n | Geography | Years | Key metric |
|---|---|---|---|---|
| Henger et al. 2021 (PLoS ONE) | 58,185 | New York state | 2012–2014 | Admission reasons, outcomes, taxa |
| McRuer et al. 2017 (J Wildlife Diseases) | ~10,000 | Virginia (single center) | 2000–2010 | Cat predation, outcomes |
| Tribe & Brown 2000 (J Wildl Rehab) | ~5,000 | Australia (multi-center) | — | Taxa, outcomes |
| APHIS 82-facility extrapolation (Tully et al. 2000) | ~100K extrapolated | US national | — | Admission categories |
| FWS Conservation Value review (2024) | Meta-analysis | Global | 1990s–2020s | Post-release survival |
| EWILD study (40K cases) | 140,000 | US (43 respondents) | 1995–1997 | Conditions, causes |

The 100K/year national total cited in the task brief reflects APHIS facility survey extrapolations, not a single published study. The spec's claim that "1M synthetic over 9 years means ~111K/year" is in the right ballpark compared to the FWS figure of "over half a million wild animals" annually in the US ([FWS 2024](https://www.fws.gov/sites/default/files/documents/2024-12/conservation-value-of-wildlife-rehabilitation.pdf)). Wait — that's a problem. 500,000+/year vs. 111K/year is a factor of 4–5x undercount if the FWS figure is accurate. Either the synthetic cube is underpopulated by nearly an order of magnitude relative to the real system, or the two figures are using different counting methodologies (FWS may count all animals that come in contact with a rehabilitator, including short-duration rescues; WRMD counts formal patient records). This discrepancy is never addressed in the spec and will be the first question any informed researcher asks.

The spec says nothing about which of these datasets was used to set the 22% orphan_displacement rate, the 18% vehicle_strike rate, or the 45% release rate. Without that traceability, "calibrated against published literature" is marketing language, not a methodological statement.

### 4.2 The "most comprehensive public database" claim is not honest

The data sources master plan reproduces Mike's directive verbatim: "imagine the most comprehensive public database on wildlife medicine, disease, injury, rehabilitation, One Health." The methodology page says the framework "demonstrates a method, not a real-time surveillance network," which is appropriately hedged. But the governance page and One Health page describe capabilities — disease pattern cross-reference, research-tier de-identified records, partner data tier — that don't exist yet. The live site is a demonstration of a methodology using wholly synthetic data. Presenting it to an institutional buyer as a framework that provides cross-species disease surveillance capabilities when the One Health page has no actual data is, at minimum, a significant gap in credibility management.

Wildlife medicine practitioners — veterinarians and wildlife biologists at centers like Wildlife Center of Virginia, Tufts Wildlife Clinic, or the Wildlife Rehabilitation Center of Minnesota — will push back on this framing hard. They have been collecting real intake records for 20–40 years. They know what a real rehabilitation database looks like. The synthetic data is explicitly labeled as synthetic on the methodology and data pages, and that is good. But the surrounding narrative architecture sets expectations that the current data layer cannot satisfy.

### 4.3 The McRuer 2017 problem

McRuer et al. 2017 ("Free-roaming cat interactions with wildlife admitted to a wildlife hospital," J Wildlife Diseases) is based on a **single center — Wildlife Center of Virginia — over a 10-year period (2000–2010)**. It is an excellent, well-designed facility-level study. It cannot be treated as nationally representative, and the data-sources master plan itself acknowledges this in its cat-conflict section. But the document also lists McRuer 2017 as the "rehab-data hook" for the anti-TNR ecological-impact case. A reviewer would ask: What is the cat-predation admission rate at facilities in urban California? At a Great Lakes migratory songbird flyway center? At a Florida sea turtle center? WCV in Virginia is not the US rehab population. Using it as the calibration anchor for cat-predation admission rates in a national synthetic cube is exactly the facility-level selection bias problem the spec acknowledges and then implicitly commits anyway.

---

## 5. Cat-Conflict Treatment

### 5.1 Source coverage is balanced; execution risks soft equivalence

The data sources plan does a creditable job mapping both the TNR-efficacy literature and the ecological-impact literature, with honest methodology critiques on both sides. This is better than most policy documents on the subject. The Kreisler et al. 2019 Key Largo study is correctly identified as the strongest internal-validity pro-TNR study; the geographic isolation of the site (gated peninsula, near-zero immigration pressure) is noted as the key generalizability limit.

However, the plan's proposed presentation of Loss 2013's headline numbers **without surfacing confidence intervals to users** is a known error the plan itself identifies but may not have fixed. The spec states explicitly: "Does not present Loss 2013's headline numbers without confidence intervals." But the /one-health page currently presents no cat-conflict data at all — meaning there's no way to evaluate whether the CI commitment has been honored. Loss 2013's central estimate of 1.3–4.0 billion birds killed annually is a Monte Carlo range spanning a factor of three. Presenting the median (2.4 billion) without that range is statistically irresponsible. The commitment is in the plan; the execution remains to be verified.

### 5.2 The distinction between free-roaming cat subtypes is critical

The plan correctly notes the importance of distinguishing feral colony cats, owned indoor-outdoor cats, and abandoned cats. This distinction is epidemiologically essential: owned indoor-outdoor cats have lower per-cat kill rates but are far more numerous in suburban environments; unowned colony cats are fewer but contribute more per-cat mortality (Loss 2013). The plan acknowledges this. The synthetic cube does not encode it, since there is only a single `predation` reason. This will limit any analysis that tries to use the WildlifeStats data to model the conservation-benefit of indoor-cat policies.

---

## 6. Citizen-Science Integration and Flyway Phenology

### 6.1 Bootstrapping from synthetic seasonality is scientifically indefensible as an early-warning baseline

The Flyway spec states explicitly: "bootstrapped during the synthetic-only era from the n=1M cube's seasonality model (since real Flyway signal history doesn't exist yet, the synthetic seasonality is the baseline for the first season)."

This is circular reasoning that invalidates the early-warning claim. You cannot detect anomalies against a baseline you invented. The synthetic cube's seasonality model — northern counties peak June, amplitude 2.5× — was defined by the architect with no published grounding (see §2.2 above). Using that model as the baseline for anomaly detection in the first operational year means that "early" and "late" signals will be triggered or suppressed based entirely on whatever the architect decided the normal curve should look like. The false-positive and false-negative rates are unknown and unknowable until real baseline data accumulates.

**Compare to Journey North's actual methodology.** [Journey North](https://journeynorth.org/projects) has been collecting first-of-season phenology observations for hummingbirds, monarchs, orioles, and other taxa since 1994. Its baseline is 30+ years of georeferenced first-arrival reports. Its anomaly detection is grounded in real interannual variability. A phenology researcher would not accept a synthetic seasonality curve as a substitute for even three to five years of real observation data. The appropriate response is to: (1) use Journey North's published historical data as the baseline for hummingbird and monarch phenology signals from day one, (2) use eBird's occurrence data for avian taxa, and (3) explicitly disclaim that the baby-season onset and HPAI hazard signals have no validated baseline and are in an observation-accumulation phase for the first one to three years.

### 6.2 Social media as a phenology signal source

Using public Facebook and Instagram posts from wildlife rehabilitation center Pages as a phenology signal is not how any published phenology study is designed. Journey North's methodology requires observers to submit point-located sightings with species identification — quality-controlled, standardized, and linked to real geographic coordinates. Rehab center posts are announcements, which may reference the first robin nest of the season, or may reference any of a hundred other things. LLM extraction of "baby season" signals from rehab-center posts will have high recall but very low precision — and the precision problem compounds in the baseline: if baby season signal counts include noise posts, the baseline is inflated, and real anomalies will be masked.

This doesn't mean Flyway is worthless; the oiled-bird-event and HPAI die-off hazard signals are more defensible because mass die-off events generate distinctive, high-salience post content that is less confounded by background noise. But the phenology application needs either an iNaturalist/eBird anchor (already in scope) or should be deprioritized until real baseline data exists.

---

## 7. The Institutional Buyer Test

### 7.1 If you present this at a USGS NWHC science meeting

The first reaction from NWHC scientists will not be hostile — they will appreciate that someone is trying to aggregate wildlife rehabilitation data nationally and build a One Health layer. The second reaction, within about ten minutes of reviewing the methodology page, will be: "Where's the citation for the species priors? How was the 6% infectious disease rate derived? Can you show the validation against any published rehabilitation dataset?" When you say the data is synthetic and the validation is internal consistency checks (total n within bounds, no negative counts), the room will go quiet. NWHC scientists distinguish between "calibrated against literature" (which implies a fitting procedure with published base rates as targets) and "consistent with literature" (which means it doesn't obviously contradict what we know). The spec claims the former and delivers the latter. That gap is the central credibility problem.

### 7.2 If you present to a foundation board (Pew, MacArthur, NSF Conservation Bio)

The dealbreaker question is: "When does this have real data?" The foundation community has seen many wildlife data portal projects that never get past the demonstration phase because the partnership work required to acquire real rehabilitation records is slow, institutional, and unsexy. The synthetic-data demonstration is clever framing — it shows what the platform would look like — but a sophisticated program officer will ask for a signed MOU with WRMD or a concrete partnership timeline before committing operational funds. The governance page describes the partner tier in detail, which is good. But there are no live partners. A single Letter of Intent from one real rehabilitation center, or an acknowledgment from the National Wildlife Rehabilitators Association of the project's existence, would do more for institutional credibility than the entire 1M synthetic record count.

The second question from a conservation-biology funder: "What's your data quality plan for real partner records?" The methodology page explains how synthetic records are generated but says nothing about data cleaning, standardization, and validation for real records that arrive from 2,200+ centers in varying formats. The Phase 4.5 pipeline is described in the data sources plan, but it's not visible to an institutional buyer reviewing the public site.

### 7.3 If you present to a state Game & Fish biologist asking about data contribution

A state wildlife biologist would need to see, in this order:

1. **A clear data sharing agreement template.** What does a state agency commit to when contributing data? What do they get in return? Who owns the contributed records? The governance page describes the partner tier at a high level but provides no template or term sheet.
2. **An explicit field mapping from their existing reporting format to the WildlifeStats schema.** Every state uses a different rehabilitation annual report form. Georgia's form uses different categories than New York's form, which uses different categories than California's. A state biologist will not invest staff time in contributing data unless there is a documented crosswalk.
3. **A security and privacy posture that satisfies their agency's legal counsel.** State game and fish agencies are risk-averse about data sharing. The governance page describes k-suppression and the four-tier access model, which is the right direction. It does not yet describe the technical architecture (data-at-rest encryption, access logs, breach notification procedures) that a state agency's IT security team will require.
4. **Evidence of existing partnerships.** No state biologist is going to be the first contributor to an unknown platform. One named partner center would open the door; five would make the conversation serious.

---

## Top 7 Hardening Priorities (Ranked by Impact-per-Effort)

**1. Fix the schema — split `infectious_disease` into surveillance-relevant sub-categories.**
Add at minimum: `hpai_suspect`, `rabies_suspect`, `wnv_suspect`, `lead_toxicosis`, `rodenticide_toxicosis`, `other_toxin`, `other_infectious`. This single change resolves the gap between the One Health page's claims and the data layer's actual capability. It also makes the WHISPers and APHIS HPAI cross-reference meaningful. Effort: medium (requires regenerating the cube, rewriting one section of the spec). Impact: eliminates the most important credibility gap for every disease-ecology and One Health audience.

**2. Cite the literature you claim to calibrate against.**
Add a mandatory "calibration sources" table to the methodology page listing the published datasets used to set each base-rate parameter. At minimum: Henger et al. 2021 (PLoS ONE) for admission-reason and outcome distributions; the FWS Conservation Value report (2024) for the national admissions total context; McRuer 2017 for cat-predation rates with its facility-level caveat stated explicitly. If those parameters were not derived from those papers, update the priors to match them and then cite them. This is an afternoon of work with high credibility return.

**3. Fix the taxonomic class enumeration.**
Drop `marine` as a class. Add a separate `habitat_guild` or `ecological_guild` dimension if marine versus terrestrial versus freshwater distinction is needed. This is a schema change that requires cube regeneration but is architecturally clean and eliminates a taxonomy error that would embarrass the project in front of any biologist.

**4. Separate DOA from died-in-care in the outcome enumeration.**
Rename `deceased` to `died_in_care` and add `dead_on_arrival` as a distinct outcome. This aligns the schema with every published US rehabilitation dataset and every state reporting form. Required for any researcher who wants to use WildlifeStats outcome data in a meta-analysis.

**5. Remove `apapane` and `iiwi` from synthetic probability tables or weight them at near-zero with explicit ESA-status documentation.**
The spec note "taxa only, no individual species rarity calling" is insufficient protection. Either use a generic "native_passerine" archetype for Hawaii (which is honest about the synthetic nature of the data) or document the ESA status and explain that any nonzero weight reflects the probability of incidental encounters at low-elevation, not routine clinical admissions.

**6. Disclaim the Flyway synthetic baseline explicitly on the Flyway methodology page.**
Add language: "The baby-season and phenology signal baselines in the first operational year are bootstrapped from a synthetic seasonality model. Anomaly detection during this period should be interpreted with caution; we recommend treating Year 1 as a data-collection phase, not a detection phase. Validated baselines will use three to five years of real signal observations and will incorporate Journey North and eBird historical records where available." This protects against a false-positive HPAI or baby-season alert triggering in Year 1 and destroying researcher trust before the pipeline has earned credibility.

**7. Reconcile the national admission volume discrepancy and document it.**
The 111K/year implied by the 1M synthetic cube over nine years conflicts with the FWS figure of 500,000+/year. Either this is a documentation problem (the FWS count includes contacts that don't become formal WRMD patient records) or the cube is under-scaled by a factor of four to five. Document the reconciliation explicitly on the methodology page. If the discrepancy is acknowledged, readers will trust the transparency; if they discover it themselves, they will question the entire calibration claim.

---

*This critique reflects the perspective of a wildlife disease ecologist; it is intended to identify fixable problems, not to dismiss the project. The architectural investment is real and the data sourcing plan is impressive. The credibility gaps identified above are surmountable — most are documentation problems as much as data problems — but they must be addressed before this goes in front of USGS NWHC, agency program officers, or foundation boards. The framework's long-term value depends on earning the trust of the rehabilitation and disease-ecology communities, and that trust starts with the integrity of the first dataset presented.*

---

**Key literature referenced:**
- Henger CS et al. (2021). Species, causes, and outcomes of wildlife rehabilitation in New York state. *PLoS ONE* 16(9): e0257675. https://doi.org/10.1371/journal.pone.0257675
- McRuer DL et al. (2017). Free-roaming cat interactions with wildlife admitted to a wildlife hospital. *Journal of Wildlife Diseases* 53(3): 555–565. https://abcbirds.org/wp-content/uploads/2023/01/McRuer-et-al.-2017-Free-roaming-cat-interactions-with-wildlife-admitted-to-a-wildlife-hospital.pdf
- Loss SR, Will T, Marra PP (2013). The impact of free-ranging domestic cats on wildlife of the United States. *Nature Communications* 4:1396. https://doi.org/10.1038/ncomms2380
- Doherty TS et al. (2016). Invasive predators and global biodiversity loss. *PNAS* 113(40):11261–11265. https://doi.org/10.1073/pnas.1602480113
- Kreisler RE, Cornell HN, Levy JK (2019). Decrease in population and increase in welfare of community cats in a 23-year TNR program. *Frontiers in Veterinary Science* 6:7. https://www.frontiersin.org/journals/veterinary-science/articles/10.3389/fvets.2019.00007/full
- U.S. Fish & Wildlife Service (2024). Conservation Value of Wildlife Rehabilitation. https://www.fws.gov/sites/default/files/documents/2024-12/conservation-value-of-wildlife-rehabilitation.pdf
- Federal Register (2017). Threatened Species Status for the Iʻiwi. https://www.federalregister.gov/documents/2017/09/20/2017-20074/endangered-and-threatened-wildlife-and-plants-threatened-species-status-for-the-iiwi-drepanis
- AFWA (2022). Recommendations to Wildlife Rehabilitators to Reduce Risks from HPAI. https://www.fishwildlife.org/application/files/2816/4943/1891/AFWA2022HPAIWildlifeRehabGuidance-April2022.pdf
