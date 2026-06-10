# Public data ingestion — master source plan

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 15:45 ET
**Status:** Source of truth for the WildlifeStats public-data ingestion strategy. Drives Phase 4.5 partner pipeline expansion, the Apify social-media plan (separate, existing), and the long-tail ingestion roadmap. Synthesizes seven parallel research scans.
**Mike directive 2026-06-10 15:23 ET:** "imagine the most comprehensive public database on wildlife medicine, disease, injury, rehabilitation, One Health, specific disease vectors, citizen science projects etc."
**Mike directive 2026-06-10 15:31 ET (cat-conflict carve-out):** balanced presentation of outdoor cats / TNR — pro-TNR welfare framing AND ecological-impact framing — domestic Felis catus only; native wildcats stay in regular wildlife.

## §1 — Source landscape, in one paragraph

Seven parallel research scans mapped the universe of public-data sources WildlifeStats can credibly ingest. The space resolves to roughly 150 distinct sources across seven domains: federal/state agency data, academic and research repositories, citizen-science observation networks, rehabilitation and One Health professional networks, APIs/scrapers/literature mining, pro-TNR cat-welfare evidence, and anti-TNR ecological-impact evidence. The richest single underrepresented source is **wildlife rehabilitation intake records** — the data lives at 2,200+ rehab organizations, primarily inside WRMD (Wildlife Rehabilitation Medical Database) and a long tail of state-mandated annual reports that no one has aggregated. The data we can grab today through open APIs gives WildlifeStats a credible national footprint within 30 days; the partnerships that turn it into an authoritative database are 90-day work; the rehabilitation-intake layer that makes it unique is a 6-12 month strategic effort.

## §2 — Domain index

Seven appendix reports live in `docs/research/data-sources/`. Each is a ~7,000-8,500 word independent scan with primary-source URLs.

| Appendix | Domain | Sources cataloged |
|---|---|---|
| `01-federal-state.md` | Federal + state government data | 26 |
| `02-academic-research.md` | Academic + research repositories | 30+ |
| `03-citizen-science.md` | Citizen science + public observation | 30+ |
| `04-rehab-onehealth.md` | Wildlife rehab + One Health + disease surveillance | 30+ |
| `05-apis-scrapers-literature.md` | APIs / scrapers / literature mining / commercial | 31 |
| `06-cats-tnr-welfare.md` | Outdoor cats — TNR / welfare framing | 23 |
| `07-cats-ecological-impact.md` | Outdoor cats — ecological-impact framing | 23 |

Read appendices in full before authoring an ingestion engineer order for any specific source. This master doc is the navigation layer, not a substitute for the appendices.

## §3 — Tier 1 ingest list (open, no friction, ship in 30 days)

These sources are openly accessible, well-documented, machine-readable, and produce real signal for the WildlifeStats database. Order is by value × accessibility composite.

| # | Source | Domain | What we get | Access |
|---|---|---|---|---|
| 1 | **USGS WHISPers / NWHC** | Federal | Diagnosed wildlife mortality events, US-wide, 1975→present, public domain | CSV + ScienceBase bulk download, [WHISPers portal](https://whispers.usgs.gov) |
| 2 | **GBIF** | Academic | 3.1B occurrence records, Darwin Core, CC0/CC-BY | REST API, async bulk, no key for read |
| 3 | **iNaturalist Open Dataset (via GBIF)** | Citizen | 300M+ observations, taxa-agnostic, including roadkill/injury projects | Weekly DwC-A via GBIF; filter to CC0/CC-BY records for commercial use |
| 4 | **eBird Basic Dataset (EBD)** | Citizen | 2B+ sightings, 150M checklists, Cornell-curated | Monthly bulk download, data-use agreement (free) |
| 5 | **USDA APHIS HPAI Wild Bird Dashboard** | Federal | Live HPAI surveillance, county-level, weekday updates | Periodic table extraction (small scrape) |
| 6 | **WAHIS / WOAH** | Rehab/OneHealth | Global animal disease reports including wildlife, 2005→present | Public dashboard + export |
| 7 | **CDC ArboNET** | Federal | WNV / EEE / arboviral surveillance including dead-bird signal | CSV download |
| 8 | **CDC Rabies Surveillance** | Federal | 80-year national rabies-in-wildlife archive | Annual reports (PDF + tables) |
| 9 | **NEON pathogen + small mammal data products** | Federal | Standardized vector / pathogen / host surveillance at 81 sites, CC0 | `neonUtilities` R package |
| 10 | **EPA ECOTOX Knowledgebase** | Federal | Pesticide / contaminant toxicology, ecotoxicity | Bulk download |
| 11 | **NPS NPSpecies + IRMA** | Federal | Park-level species lists, long-term monitoring | Open REST + downloads |
| 12 | **IUCN Red List API** | Academic | Conservation status + threats for every species | Free token, no rate limit |
| 13 | **USGS Bird Banding Lab** | Federal | Band recovery → mortality + movement | ScienceBase bulk |
| 14 | **PubMed / PubMed Central + OpenAlex** | APIs/Lit | Veterinary + zoonotic disease literature corpus | Open APIs, MeSH structure |
| 15 | **GDELT + bioRxiv + ProMED** | APIs/Lit | Outbreak early-warning + preprint signal | Open APIs, free |

Engineer orders for Tier 1 sources dispatch in groups (geographic, taxonomic, or surveillance-themed bundles), not one-at-a-time. See §7 below.

## §4 — Tier 2 partnership targets (90-day pursuit)

These sources require an MOU, a research-account application, or a relationship — but the data behind them is high enough value to justify the relationship work. Architect should draft outreach templates; engineer is not blocked on these for the 30-day Tier 1 push.

| Source | What | Friction | Why pursue |
|---|---|---|---|
| **WRMD (Wildlife Rehabilitation Medical Database)** | 4.5M patient records across 2,226 orgs | Institutional research partnership | The single highest-leverage rehab-data source in existence; this is the database that turns WildlifeStats from a synthetic-data showcase into a real research platform |
| **WILD-ONe (administrative tier)** | National Wildlife Rehabilitation Network database | Administrative access | Complementary to WRMD; different sampling frame |
| **NOAA MMHSRP individual records** | Marine mammal stranding (individual-level vs. aggregate) | Email request, weeks-months | Marine mammal coverage critical for national framing |
| **NOAA STSSN individual records** | Sea turtle stranding individual records | Coordinator coordination | Same — coastal taxa |
| **State wildlife agency rehab annual reports** | Per-state legally-mandated rehab summaries | FOIA / public records, state-by-state | Pilot: NY, CA, FL, TX, WA — diverse geographies, strong data programs |
| **Movebank** | Animal tracking data, GPS / biologger | Owner approval per dataset | Movement = disease transmission corridors |
| **Wildlife Insights** | Camera trap + AI species IDs | Account + per-project rules | Mammal occurrence + presence/absence |
| **USGS NWDD partnership** | National Wildlife Disease Database — actively accepts rehab data | Formal partnership inquiry | Positions WildlifeStats as a *contributing* node, not just a consumer |
| **NWRA strategic partnership** | National Wildlife Rehabilitators Association | Direct outreach, conference engagement | Membership directory → access to the long tail of rehab orgs |
| **Christmas Bird Count** | Audubon 125-year dataset | Written permission required for database hosting | Long-baseline avian indicator |
| **COASST (UW)** | Beached-bird mortality survey, Pacific Coast | Formal research partnership | Coastal mortality methodology gold standard |

Architect deliverable in a follow-on session: draft outreach emails for top three (WRMD, USGS NWDD partnership, NWRA strategic partnership). Not in this batch — dispatching outreach drafts is a Mike-strategic move, not an engineer order.

## §5 — Tier 3 long-tail (6-12 months, opportunistic)

Sources worth ingesting but not on the critical path:

- **PDF extraction from wildlife rehab center annual reports** — Wildlife Center of Virginia, Tufts Wildlife Clinic, Raptor Center (U of MN), and the long tail of mid-size centers that publish quarterly/annual PDFs with intake counts. High effort, high yield, fully automatable with a PDF + table extraction pipeline that runs in the Phase 4.5 framework.
- **State-by-state FOIA campaigns** beyond the pilot 5. MuckRock + FOIA.gov templated request infrastructure.
- **Veterinary literature corpus** — full-text mining of Journal of Wildlife Diseases, JAVMA, Journal of Zoo and Wildlife Medicine, Frontiers in Veterinary Science. PubMed Central handles a large fraction; the rest is paywalled and needs institutional access.
- **Wikidata + Wikipedia structured data** — species pages, disease pages, range maps. Lower confidence per record but excellent for cross-linking.
- **Commercial / institutional sources** — ZIMS / Species360, VetCompass, Web of Science. Out of scope unless partner relationships develop independently.

## §6 — Cat / wildlife conflict — special handling

Mike's 15:31 ET directive: balanced presentation of outdoor cats (Felis catus). Native wildcats — bobcat, Canada lynx, mountain lion, ocelot, jaguarundi, margay, jaguar — are wildlife and live in the regular Wildlife encyclopedia, separate from any cat-conflict content.

WildlifeStats commits to **balanced source coverage**, not balanced *conclusions*. The architect's stance: the evidence base on each side has different methodological strengths and weaknesses; we present both, cite primary sources for both, and let the reader weigh them.

### §6.1 Pro-TNR / welfare framing (appendix 06)

Strongest evidence:
- Levy et al. 2003 + Spehar & Wolf 2019 UCF 28-year longitudinal — campus context, controlled, peer-reviewed
- Kreisler, Cornell & Levy 2019 (ORCAT Key Largo) — 23-year, controlled, individual medical records, strongest internal validity
- Levy, Isaza & Scott 2014 — quasi-experimental, real-world open population
- Boone et al. 2022 bioeconomic analysis
- AVMA / ICAM policy guidance

Methodological caveats noted in appendix: campus and bounded-island sites have lower immigration pressure than mainland urban contexts; UCF and Key Largo do not generalize trivially to a city neighborhood TNR colony. Authors of the supporting studies frequently acknowledge this.

### §6.2 Anti-TNR / ecological-impact framing (appendix 07)

Strongest evidence:
- Loss, Will & Marra 2013 (Nature Communications) — foundational US wildlife mortality estimate from cats
- Doherty et al. 2016 (PNAS) — global extinction attribution
- Longcore, Rich & Sullivan 2009 — peer-reviewed critique of TNR efficacy
- Castillo & Clarke 2003 + Foley et al. 2005 — countywide TNR failure documentation
- Conrad et al. 2005 — Toxoplasma gondii sea otter spillover
- CDC rabies surveillance — domestic cats lead rabies post-exposure prophylaxis among domestic species annually
- McRuer et al. 2017 — only published rehab-intake study quantifying cat-caused mortality at facility level
- US Fish & Wildlife Service, The Wildlife Society, American Bird Conservancy, Audubon position statements
- New Zealand Department of Conservation feral cat profile

Methodological caveats noted in appendix: Loss 2013 mortality estimates are modeled extrapolations with wide confidence intervals; some assumptions (cats per area, kills per cat per year) have been challenged. Rehabilitation-intake studies have facility-level selection bias.

### §6.3 How WildlifeStats presents cat content

On the public tier:

- A `/wildlife/cats/` page (within the encyclopedia) presents both framings side-by-side, with citations to primary literature on each side. NOT a "both sides have merit" mushy summary — a genuine literature review that names where each side's evidence is strong and where it's contested.
- The synthetic cube includes a `cat_predation_admission` admission reason in the `reason` enumeration. Counts on the synthetic data show the rehabilitation-intake signal in aggregate without any specific facility's records.
- WREN, when asked about TNR effectiveness, retrieves quotes from both appendix sets and presents them as: "Researchers Levy and colleagues at UF have documented sustained colony reductions over 28 years in campus contexts (citation). Researchers Longcore and colleagues at UCLA have critiqued the generalizability of those findings to mainland urban populations (citation). The American Veterinary Medical Association's policy acknowledges both the welfare arguments and the wildlife concerns (citation)."
- Native wildcats — bobcat, lynx, mountain lion, etc. — are documented in the regular wildlife encyclopedia. The encyclopedia explicitly notes the distinction at the top of `/wildlife/cats/` so readers understand we're discussing domestic cats only.

### §6.4 What WildlifeStats does NOT do

- Does not advocate for or against TNR as a management policy.
- Does not host advocacy materials from either side as authoritative WildlifeStats content (citations only, not embedded campaigns).
- Does not present Loss 2013's headline numbers without confidence intervals.
- Does not present Levy 2003 / Spehar & Wolf 2019 outcomes without the site-context caveats.
- Does not collapse "free-roaming cat" into a single category — distinguishes (with appendix support) between feral colonies, owned indoor-outdoor cats, owned strictly indoor cats, and abandoned cats, because these have different epidemiology and different management implications.

## §7 — Pipeline implications

This data-source plan changes Phase 4.5 (data pipeline) scope. Update via a follow-on engineer order:

1. The Phase 4.5 pipeline must support **source-typed ingestion** — not just partner Excel files, but federal CSV pulls, GBIF Darwin Core archives, eBird EBD bulk files, PDF table extraction, and API responses. The pipeline's stage 3 (field mapping) becomes source-template-driven: a template per source type that knows how to handle that source's quirks.
2. The pipeline gains a **source registry** — `wildlifestats/_pipeline/sources/<source-name>.json` — that declares each source's URL, access method, license, refresh cadence, and field mapping. The runner can be invoked per-source.
3. The pipeline gains a **scheduled-pull mechanism** — sources with frequent updates (APHIS HPAI dashboard, GDELT) get a GitHub Actions cron that runs the relevant slice of the pipeline daily/weekly and commits updated cube fragments. Sources with annual updates (CBC, BBS) get manual-trigger workflows.
4. The pipeline gains a **provenance layer** — every cube cell knows which source(s) contributed, with what license. This is the foundation for WREN's "How was this computed" affordance to cite the source.
5. **License enforcement at build time** — the public cube only carries CC0, CC-BY, public domain, and explicitly-permitted CC-BY-NC-with-attribution data. Anything more restrictive (CC-BY-NC commercial-prohibition, or restricted research-only data) flows to the secure tier only.

Architect will draft `wildlifestats-engineer-order-phase4.5-source-registry-expansion-2026-06-10.md` as a follow-on, dispatching after Phase 4.5a-e complete. Not in this batch — wait for the engineer to finish Phase 4 + Phase 4.5 base.

## §8 — Apify carry-over

The existing Apify plan covers social-media top-100 ingestion. It complements this plan and is not superseded. The social signal layer answers different questions (emerging public concerns, viral wildlife stories, citizen-spotted events) than the structured data sources here. Both feed into WREN at different prompt-context layers.

## §9 — What this plan is NOT

- **Not a green light to dump every source into one cube.** Each source goes through Phase 4.5's eight pipeline stages — inventory, schema inference, field mapping, normalization, validation, audit, aggregation, emission. Garbage-in garbage-out is the failure mode the pipeline exists to prevent.
- **Not a substitute for partnership work.** Tier 2 sources require relationship investment that the architect cannot delegate to an engineer order. Mike is the relationship layer.
- **Not a comprehensive global database.** Scope stays US-primary with international counterparts (WAHIS, IUCN, GBIF global) only where they add immediate value.
- **Not promising real-time anything.** Most Tier 1 sources are daily-to-monthly cadence; some (CBC, BBS) are annual. WildlifeStats is a research framework, not a surveillance system.

## §10 — Appendix index

| File | Words | Key strategic insight |
|---|---|---|
| `docs/research/data-sources/01-federal-state.md` | ~7,700 | State rehab annual reports = richest untapped source (FOIA-able) |
| `docs/research/data-sources/02-academic-research.md` | ~8,700 | USGS NWDD explicitly accepts rehabilitator data → partnership opportunity |
| `docs/research/data-sources/03-citizen-science.md` | ~7,500 | WHISPers ranks #1; iNaturalist CC-BY-NC majority needs filtering |
| `docs/research/data-sources/04-rehab-onehealth.md` | ~8,600 | WRMD 4.5M records is the prize partnership |
| `docs/research/data-sources/05-apis-scrapers-literature.md` | ~8,700 | PubMed + OpenAlex + GBIF are the foundational triplet |
| `docs/research/data-sources/06-cats-tnr-welfare.md` | ~8,400 | Kreisler Key Largo 2019 is the methodologically strongest pro-TNR study |
| `docs/research/data-sources/07-cats-ecological-impact.md` | ~7,300 | Loss 2013 + Doherty 2016 anchor the impact case; McRuer 2017 is the rehab-data hook |

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 15:45 ET
