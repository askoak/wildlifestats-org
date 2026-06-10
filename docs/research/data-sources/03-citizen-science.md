# Citizen Science and Public Observation Networks

**WildlifeStats Data Source Assessment — Module 03**
*Scope: Structured citizen-science platforms with independent data systems. Social-media top-100 scraping handled separately via Apify.*

---

## Quick-Reference Summary Table

| Source | Tier | Records (approx.) | API | Bulk DL | License | Disease/Health Signal |
|---|---|---|---|---|---|---|
| iNaturalist (GBIF DwC-A) | 1 | 300M+ obs | Yes | Yes (17 GB) | CC0/BY/BY-NC mix | Medium |
| eBird EBD | 1 | 2B+ sightings | Yes | Yes (200 GB+) | Custom open | Low direct |
| USGS BBS | 1 | 1966–present, 700+ spp | No | Yes (CSV) | Public domain | Low |
| NEON | 1 | 81 sites, 2012–present | Yes | Yes | CC0 | Medium (small mammal pathogens) |
| WHISPers | 1 | All US mortality events | Yes (partial) | Yes (annual CSVs) | Public domain | **HIGH** |
| USGS Bee Lab Database | 1 | Large collections | Via GBIF | Via GBIF | Public domain | Low |
| Bumble Bee Watch (GBIF) | 1 | Large verified obs | Via GBIF | DwC-A (CC BY 4.0) | CC BY 4.0 | Medium |
| Globe Observer Mosquito | 1 | 2017–2020+ | API | CSV | Open (NASA) | **HIGH** (disease vector) |
| CROS (CA Roadkill) | 1 | Largest US roadkill DB | Partial | Contact | Not stated | Medium (mortality) |
| Snapshot USA | 1 | 1M+ captures, 50 states | Via Wildlife Insights | Dryad | Open (CC) | Medium |
| Wildlife Insights | 1 | Millions of images global | Yes | Yes (CC0/BY/BY-NC) | CC0/BY/BY-NC | Medium |
| Project FeederWatch | 2 | 1.8M+ checklists, 1988– | No | CSV (free, 380MB–1.3GB) | Open (free) | Low |
| NestWatch | 2 | Nest-level records | No | CSV/ZIP (CC BY-NC 4.0) | CC BY-NC 4.0 | Low |
| eBird Status & Trends | 2 | 2,900+ spp globally | R pkg / API | GeoTIFF/GeoPackage | Non-commercial free | Low |
| Christmas Bird Count | 2 | 1900–present | No | Portal download | Non-commercial only | Low |
| NABat | 2 | Bat acoustics, US/CAN | Via portal | ZIP (request-based) | Varies by project | Medium |
| BatAMP | 2 | Bat acoustic obs | Via portal | Spreadsheet upload/share | Not stated | Medium |
| HerpMapper | 3 | Reptile/amphibian obs | No public API | Partners only | Restricted | Medium (roadkill, DOR) |
| COASST | 3 | Beached birds, 1999– | No | Research partnership | Restricted | **HIGH** (mortality/disease) |
| Snapshot Wisconsin | 3 | Camera trap, statewide | Dashboard only | Contact DNR | Not stated | Medium |
| Bumble Bee Watch (direct) | 3 | Bumble bee sightings | No | Request-based | Restricted (direct) | Low |
| TickEncounter/TickSpotters | 3 | Tick encounter reports | No | Contact URI | Not stated | **HIGH** (vector-borne) |
| Adventure Scientists | 3 | Wildlife connectivity, roadkill, pollinators | No | Request-based | Not stated | Medium |
| North American Bird Banding | 4 | 75M+ banded, 1913– | No | Researcher request | Govt. permit / request | Low direct |
| Earthwatch | 4 | Field research datasets | No | Project-specific request | Open per project | Medium |
| Whale Alert | 4 | Marine mammal sightings | Via email request | Contact | Not stated | Medium (vessel strike/stranding) |

---

## Tier 1: Open API / Bulk Download (Use Immediately)

### 1.1 iNaturalist
**URL:** [https://www.inaturalist.org](https://www.inaturalist.org) | GBIF dataset: [https://www.gbif.org/dataset/50c9509d-22c7-4a22-a47d-8c48425ef4a7](https://www.gbif.org/dataset/50c9509d-22c7-4a22-a47d-8c48425ef4a7)

**What they hold:** Taxa-agnostic citizen observations covering all kingdoms of life — animals, plants, fungi, and more. As of March 2026, iNaturalist has [surpassed 300 million verifiable observations](https://www.inaturalist.org/blog/126478-inaturalist-at-300-million-observations), from nearly 4 million observers globally. Approximately 102,000 observers across six continents contributed 3.3 million observations in just four days during the 2025 City Nature Challenge. Records include species ID (community-verified), GPS coordinates, date/time, observer notes, photos, and quality grade. The "Research Grade" designation is applied when two-thirds of community ID suggestions agree on the species and the observation passes iNaturalist's Data Quality Assessment. Over 7,000 scientific publications have used iNaturalist data.

**Access method:**
- **GBIF DarwinCore Archive:** All Research Grade observations under CC0, CC BY, or CC BY-NC license, distributed as a zip archive of CSV files. Size: ~17 GB as of January 2025, [updated weekly](https://www.inaturalist.org/pages/developers). This is the recommended bulk ingestion path.
- **REST API:** Up to 100 requests/minute (recommended ≤60). Suitable for targeted queries, not bulk extraction. Authenticated via OAuth2.
- **Export Tool:** Direct CSV exports from the iNaturalist website for defined observation sets.
- **Range Map Dataset:** Range maps for 100,000+ taxa, updated monthly.

**License:** Mixed. CC0, CC BY 4.0, and CC BY-NC 4.0 are all present in the GBIF archive. The CC BY-NC fraction (the largest) prohibits commercial use. For WildlifeStats — a public database framework — this is generally acceptable, but any commercial data products built on iNaturalist data require careful license filtering to CC0/CC-BY-only records.

**Data format and update cadence:** DwC-A (ZIP of CSVs). GBIF archive updated weekly. Taxonomy DwC-A updated monthly.

**Value for WildlifeStats:**
- Broadest taxonomic scope of any citizen science platform — the most likely single source for incidental wildlife observations including injury and mortality.
- Roadkill and injury observations can be recovered via the iNaturalist annotation/field system (e.g., "Global Roadkill Observations" project, state roadkill projects, "Dead Birds," "Dead Mammals" projects).
- Disease indicators captured incidentally: abnormal behavior, lesions, unusual mortality events reported by observers.
- City Nature Challenge events produce annual concentrated biodiversity snapshots from urban/periurban areas relevant to One Health.
- Provides species composition baseline for essentially every region of North America.

**Known integration friction:**
- CC BY-NC license on the majority of records limits commercial reuse.
- Precise locations of sensitive species are obscured to 0.2-degree grid (~22 km).
- No standardized disease/mortality annotation — these must be extracted via free-text observation notes, tags, and project membership.
- Research Grade quality requires community consensus; freshly submitted observations are unverified.

---

### 1.2 eBird (Cornell Lab of Ornithology)
**URL:** [https://ebird.org](https://ebird.org) | Data: [https://science.ebird.org/en/use-ebird-data/download-ebird-data-products](https://science.ebird.org/en/use-ebird-data/download-ebird-data-products)

**What they hold:** The world's largest avian observation database. As of August 2025, [eBird surpassed 2 billion bird sightings](https://news.cornell.edu/stories/2025/08/lab-ornithology-hits-2-billion-bird-sightings-3-million-recordings) from over 1 million users worldwide across more than 150 million checklists. Data covers all bird species globally with species ID, count, GPS location, date/time, observer effort (distance, duration, method), and habitat covariates assignable post-hoc.

**Access method (three tiers):**
1. **eBird Basic Dataset (EBD):** Full raw observations plus checklist metadata. Account + brief data request form (approved within 7 days). Tab-delimited text, ~200 GB+ uncompressed. [Updated monthly on the 15th](https://science.ebird.org/en/use-ebird-data/download-ebird-data-products). R package `auk` provides efficient filtering before loading.
2. **eBird Observational Dataset (EOD):** Basic occurrence data (species, date, location only — no effort metadata). Available via [GBIF](https://www.gbif.org/dataset/4fa7b334-ce0d-4e88-aaae-2e0c138d049e). Updated annually.
3. **eBird Status and Trends Data Products:** Modeled abundance, range, and trend estimates for 2,900+ species globally. Access request form at [https://ebird.org/st/request](https://ebird.org/st/request). Immediate approval for non-commercial use. R package `ebirdst`; GeoTIFF and GeoPackage formats. [Commercial use not permitted](https://science.ebird.org/en/status-and-trends/faq).
4. **Public API:** JSON, key-based (free). Real-time recent observations, hotspot data, species lists by region.

**License:** EBD is open-access with a custom eBird license that permits research and conservation use. Commercial use requires written permission from Cornell. Status and Trends explicitly prohibits commercial use. EOD on GBIF has similar open terms.

**Data format and update cadence:** EBD — tab-delimited text (.txt.gz), monthly. EOD — DwC-A via GBIF, annual. Status and Trends — GeoTIFF, GeoPackage, annual.

**Value for WildlifeStats:**
- Definitive source for avian species composition and abundance trends across North America.
- Checklist-based effort data enables detection of absence, supporting disease surveillance inference (e.g., sudden population drop in a previously common species).
- Mortality/injury not systematically captured — eBird is a live-bird sighting system.
- Status and Trends data provides baseline species range maps for all 2,900+ species, enabling regional species composition intelligence and context for wildlife health events.
- Important complement to WHISPers for understanding baseline avian population context when large mortality events are reported.

**Known integration friction:**
- EBD size (~200 GB) requires infrastructure for ingestion; standard relational DB approaches need pre-filtering with `auk`.
- No mortality/disease annotation in the standard schema.
- Sensitive species locations obscured.
- Status and Trends commercial restriction limits certain monetization paths.

---

### 1.3 USGS North American Breeding Bird Survey (BBS)
**URL:** [https://www.pwrc.usgs.gov/bbs/](https://www.pwrc.usgs.gov/bbs/) | Data: [https://doi.org/10.5066/P136CRBV](https://doi.org/10.5066/P136CRBV)

**What they hold:** The BBS is a long-term roadside survey of North American breeding bird populations running continuously [since 1966](https://www.sciencebase.gov/catalog/item/52b1dfa8e4b0d9b325230cd9). Covers 700+ North American bird species via standardized point counts along 3,000+ survey routes across the US and Canada. Each annual release includes all preceding data plus corrections; the 1966–2023 dataset was released in 2024.

**Access method:** Fully public download via USGS ScienceBase ([https://doi.org/10.5066/P136CRBV](https://doi.org/10.5066/P136CRBV)). No account required. The `retriever` tool can install BBS data as CSV (`retriever install csv BBS`). USGS-analyzed results also available on the BBS website.

**License:** US Public Domain ([http://www.usa.gov/publicdomain/label/1.0/](http://www.usa.gov/publicdomain/label/1.0/)). No restrictions.

**Data format and update cadence:** Multiple CSV files per release. Annual release (data collected summer, released following calendar year). Stop-level GPS coordinates available for many routes.

**Value for WildlifeStats:**
- Gold-standard long-term population trend data for avian species composition across North America.
- 58-year time series enables detection of long-term population collapses potentially attributable to disease (e.g., House Finch conjunctivitis, West Nile Virus impacts on corvids and raptors).
- Regional species composition baselines for every major habitat type.
- Used by state and federal wildlife agencies for management decisions.

**Known integration friction:**
- Roadside survey methodology introduces spatial bias — not representative of remote or non-roadside habitats.
- Annual cadence limits real-time utility.
- No direct mortality/disease annotation.

---

### 1.4 NEON (National Ecological Observatory Network)
**URL:** [https://www.neonscience.org](https://www.neonscience.org) | Data Portal: [https://data.neonscience.org](https://data.neonscience.org)

**What they hold:** NSF-funded network of 81 field sites across 20 eco-climatic domains across the US (including Alaska, Hawaii, Puerto Rico). NEON is quasi-citizen science — data is collected by NEON technicians and researchers using standardized protocols, not the general public — but all data are fully open. Wildlife-relevant data products include: small mammal box trapping ([DP1.10072.001](https://data.neonscience.org/data-products/DP1.10072.001)) with individual IDs, reproductive condition, and pathogen samples; tick collections (DP1.10093.001); bird point counts (DP1.10003.001); herpetofauna pitfall traps; amphibian/reptile abundance; invertebrate pitfall traps; ground beetle pitfalls; plant diversity; and aquatic macroinvertebrates. Small mammal data includes blood, ear, hair, whisker, fecal, and voucher samples collected for pathogen testing — a direct One Health signal. Data span June 2012 to present.

**Access method:** Fully open via the [NEON Data Portal](https://data.neonscience.org). API available. R package `neonUtilities` and Python package `neonutilities` for programmatic access. No account required for most products. Annual RELEASE versions with DOIs.

**License:** [CC0 1.0](https://www.neonscience.org/data-samples/guidelines-policies/publishing-research-outputs) for most data products. Completely unrestricted.

**Data format and update cadence:** CSV tables within zipped download packages, with PDF/HTML/Markdown documentation. Latency 45 days for most observational products. Annual RELEASE versions archive finalized data.

**Value for WildlifeStats:**
- Best structured data for pathogen-host interactions in small mammals: NEON's small mammal trapping protocol explicitly includes pathogen sample collection bouts (3-night bouts), yielding blood and tissue samples.
- Tick abundance and phenology data by eco-climatic domain — critical for vector surveillance.
- Long-term standardized wildlife population data at 81 sites enabling trend detection.
- CC0 license = zero friction for any use case including commercial.

**Known integration friction:**
- Not citizen science; primary value is as a scientific complement/calibration layer.
- Spatial coverage limited to 81 sites — not nationally comprehensive.
- Small mammal pathogen results are in associated publications, not always in the primary data download.

---

### 1.5 WHISPers (Wildlife Health Information Sharing Partnership — Event Reporting System)
**URL:** [https://whispers.usgs.gov](https://whispers.usgs.gov) | USGS Data Catalog: [https://data.usgs.gov/datacatalog/data/USGS:581deaed-18e7-45b1-8935-1ea7342ba7e5](https://data.usgs.gov/datacatalog/data/USGS:581deaed-18e7-45b1-8935-1ea7342ba7e5)

**What they hold:** WHISPers is a partner-driven, web-based repository of wildlife mortality (death) and morbidity (illness) events reported by partners nationwide — primarily wildlife veterinarians, state wildlife agencies, USGS National Wildlife Health Center (NWHC), and other professionals. Events are recorded at the geographic and temporal level (not individual animal level), with diagnosis, species affected, number affected/dead, cause of death when known, and submitting agency. Annual avian morbidity/mortality datasets are released publicly on USGS data catalog ([example: 2023 avian data](https://catalog-old.data.gov/dataset/avian-morbidity-and-mortality-data-reported-to-the-wildlife-health-information-sharing-31--66b98)) with CSV/XML download.

**Access method:** Public web interface at whispers.usgs.gov with event search and map. Annual structured data releases on data.usgs.gov as CSV/XML. Public domain — US government work. WHISPers also serves as a portal for requesting diagnostic/epidemiologic services from NWHC.

**License:** US Public Domain. No restrictions on use.

**Data format and update cadence:** Web-based searchable archive. Annual CSV/XML data releases on USGS data catalog. The data are opportunistically collected and do not represent all mortality events in North America.

**Value for WildlifeStats:**
- **Single highest-priority source for wildlife disease surveillance.** Covers diagnosed mortality/morbidity events for all vertebrate taxa.
- Direct One Health signal: includes zoonotic diseases, avian influenza, Newcastle disease, rabies, West Nile Virus, chronic wasting disease, and emerging pathogens.
- Provides event-level data including diagnosis, geographic location, number affected, and reporting agency — enabling direct integration into disease surveillance dashboards.
- Rehabilitation triggers: large mortality events documented in WHISPers are primary signals for wildlife rehabilitation centers.
- Also accessible as annual USGS data releases with DOIs for reproducible research.

**Known integration friction:**
- Data is partner-submitted and opportunistic — significant under-reporting, especially in areas without active NWHC partnerships.
- Event-level (not individual animal-level) data; no individual animal tracking.
- Web interface requires JavaScript (initial fetch showed "Loading..." — full data requires browser rendering or direct API call).
- Annual releases lag real-time events.

---

### 1.6 USGS Bee Lab Database
**URL:** [https://www.usgs.gov/centers/eesc/bee-database](https://www.usgs.gov/centers/eesc/bee-database)

**What they hold:** The USGS Native Bee Inventory and Monitoring Lab (BIML) maintains a database of all collection activity by BIML staff plus collaborators — systematically collected native bee specimens from across North America. Data are submitted to GBIF and accessible via that pathway. Covers species identification, collection location, date, collector, and associated plant hosts.

**Access method:** Data are public domain and available via GBIF ([USGS BIML on GBIF](https://www.gbif.org/publisher/2f6cbeb0-3e30-11dd-b1b7-b8a03c50a862)) and the Global Native Bee Monitoring Network. Direct download from GBIF as DwC-A.

**License:** Public domain (US government work).

**Data format and update cadence:** DwC-A via GBIF; CSV tables. Cadence tied to GBIF publishing schedule.

**Value for WildlifeStats:**
- Pollinator health baseline; useful for detecting native bee population decline that may indicate pesticide use, habitat loss, or pathogen spread.
- One Health context: pollinator decline is a sentinel for broader ecosystem health relevant to food security.
- Small but high-quality verified scientific dataset.

---

### 1.7 Bumble Bee Watch (GBIF / Xerces Society)
**URL:** [https://www.bumblebeewatch.org](https://www.bumblebeewatch.org) | GBIF: [https://doi.org/10.15468/t4rau8](https://doi.org/10.15468/t4rau8)

**What they hold:** North American bumble bee (genus *Bombus*) sightings submitted by citizen scientists and verified against expert identifications. Collaborative project of the Xerces Society, Wildlife Preservation Canada, York University, the Montreal Insectarium, and other partners. Focuses on tracking species of conservation concern.

**Access method:**
- **Public/verified records:** Available as a DwC-A on GBIF ([CC BY 4.0 license](https://ipt.gbif.us/resource?r=xerces-bumblebeewatch)), published by USGS. Freely downloadable.
- **Sensitive/private records:** Require a written data request to Bumble Bee Watch. Raw data redistribution on the internet requires specific written approval. Data request processing fees may apply ($75/hour) though often waived for academic use.

**License:** CC BY 4.0 for public GBIF dataset. Internal sensitive data has more restrictive terms.

**Data format and update cadence:** DwC-A (GBIF), CSV. Updated with each GBIF publish cycle. [Current version: 1.11 (2024)](https://ipt.gbif.us/resource?r=xerces-bumblebeewatch).

**Value for WildlifeStats:**
- Sentinel pollinator species with strong conservation concern implications.
- Species range contraction data relevant to One Health and ecosystem function.
- Declining bumble bee populations are linked to disease (*Nosema bombi*, *Crithidia bombi*) and pesticide exposure.

**Known integration friction:**
- Sensitive/private data (precise GPS for rare species) requires formal request and may be restricted.
- Small taxonomic scope (bumble bees only).

---

### 1.8 GLOBE Observer — Mosquito Habitat Mapper
**URL:** [https://observer.globe.gov](https://observer.globe.gov) | Data: [https://observer.globe.gov/get-data/mosquito-habitat-data](https://observer.globe.gov/get-data/mosquito-habitat-data)

**What they hold:** NASA/GLOBE Program citizen science platform. The Mosquito Habitat Mapper module collects georeferenced observations of mosquito habitats and larvae reported by students and citizen scientists globally. The [2017–2020 dataset](https://observer.globe.gov/get-data/mosquito-habitat-data) covers Africa, Asia and Pacific, and Latin America/Caribbean. An "Adopt a Pixel" 3km nested framework dataset was also released (2020). Includes habitat type, larvae presence/absence, species identification where possible, and GPS location.

**Access method:** Direct CSV download, no account required. [Freely available for research, publications, and commercial applications](https://observer.globe.gov/get-data/mosquito-habitat-data). NASA data acknowledgment required for publications.

**License:** Open — freely available for use in research, publications, and commercial applications. Only requirement is a publication acknowledgment crediting the GLOBE Program.

**Data format and update cadence:** CSV files (zipped). 2017–2020 dataset is a static historical release; real-time observations accessible via GLOBE API.

**Value for WildlifeStats:**
- **Critical One Health / disease vector data.** Mosquito habitat mapping directly supports surveillance for West Nile Virus, Eastern Equine Encephalitis, and other arboviruses that affect both humans and wildlife.
- GPS-georeferenced, global scope.
- Commercial use permitted — highest flexibility.
- Complements CDC tick surveillance data for a comprehensive vector layer.

---

### 1.9 California Roadkill Observation System (CROS)
**URL:** [https://www.wildlifecrossing.net/california/](https://www.wildlifecrossing.net/california/)

**What they hold:** The largest single roadkill reporting system in the US. Data come from citizen scientists as well as California Highway Patrol officers. Records include species, GPS location, date/time, photos, road context, and decay state. Spatial accuracy published at ~13 meters; species ID accuracy >97%. Data are used by Caltrans, CDFW, academic researchers, and NGOs. A parallel California Roadkill DNA Biobank enables tissue collection from roadkill (volunteer enrollment via [RoadkillDNA@wildlife.ca.gov](mailto:RoadkillDNA@wildlife.ca.gov)).

**Access method:** Web portal with search and map. Formal data downloads require contact with the Road Ecology Center at UC Davis ([roadecology.ucdavis.edu](https://roadecology.ucdavis.edu/research/projects/cros)). Data actively used by state agencies but direct CSV download not prominently advertised. The companion ROaDS (Roadkill Observation and Data System) tool, developed with the National Park Service, can be deployed by partner organizations via the Center for Large Landscape Conservation.

**License:** Not formally stated. Used by public agencies; de facto open for research purposes with attribution.

**Data format and update cadence:** Web-based system. Data underlying published studies available in supporting information of papers. Continuous/real-time submission.

**Value for WildlifeStats:**
- **Highest-quality roadkill mortality database in North America** — directly captures injury/death patterns for all vertebrate taxa.
- Species-level roadkill hotspot data enables prevention, rehabilitation resource planning, and population-level mortality estimates.
- California-only geographic scope is a significant limitation, but the methodology is the model for national expansion.
- DNA Biobank is an extraordinary add-on for genomic research.

**Known integration friction:**
- California-only scope.
- No published open API; data access by contact.
- ROaDS tool data must be requested project-by-project from Center for Large Landscape Conservation partners.

---

### 1.10 Snapshot USA / Wildlife Insights
**URL:** Snapshot USA: [https://www.snapshot-usa.org](https://www.snapshot-usa.org) | Wildlife Insights: [https://www.wildlifeinsights.org](https://www.wildlifeinsights.org) | Dryad: [https://doi.org/10.5061/dryad.k0p2ngfhn](https://doi.org/10.5061/dryad.k0p2ngfhn)

**What they hold:** Snapshot USA is a Smithsonian Institution / NC Museum of Natural Sciences coordinated camera trap survey covering [all 50 US states](https://nationalzoo.si.edu/conservation-ecology-center/snapshot-usa). Annual September–October deployments. Since 2019, the project has gathered data from 200+ collaborating institutions with over 1 million mammal captures from ~16 million raw images (2024 season alone: ~6 million images from 186 camera arrays). Data are uploaded to Wildlife Insights, AI-identified, verified, then published as open-access data papers on Dryad. Multi-year standardized dataset (2019–2023) is available.

Wildlife Insights is the broader platform: a Google-developed camera trap data management system that accepts images from anyone, applies AI species ID, and shares data under user-selected Creative Commons licenses (CC0, CC BY, CC BY-NC). Projects can be embargoed for up to 48 months.

**Access method:**
- **Snapshot USA data:** Openly shared via Dryad and Wildlife Insights Explore page. Free Wildlife Insights account required to download from WI ([https://app.wildlifeinsights.org/explore](https://app.wildlifeinsights.org/explore)).
- **Wildlife Insights broader data:** API available. Free account. CC license varies by project.

**License:** Snapshot USA publications are open access; most data CC BY or CC0. Wildlife Insights allows project owners to choose CC0, CC BY 4.0, or CC BY-NC 4.0 for images and metadata. Sensitive species coordinates are fuzzed to ~11 km.

**Data format and update cadence:** CSV (deployment metadata, species detections), JPEG images. Snapshot USA annual publications (multi-year releases). Wildlife Insights continuous.

**Value for WildlifeStats:**
- Standardized national mammal abundance monitoring — the only fully standardized camera trap survey covering all 50 states.
- Detects population trends for species not well-covered by other surveys (bobcat, fisher, opossum, raccoon, skunk — species relevant to rabies, distemper, and other wildlife diseases).
- Camera trap imagery captures behavior, body condition, and unusual mortality contexts.
- Snapshot Wisconsin (Wisconsin DNR) is the state-level analogue — year-round, statewide camera network managed through [Zooniverse](https://www.zooniverse.org/projects/zooniverse/snapshot-wisconsin) with public classification platform.

---

## Tier 2: Account-Gated but Free

### 2.1 Project FeederWatch (Cornell Lab / Birds Canada)
**URL:** [https://feederwatch.org](https://feederwatch.org) | Data: [https://feederwatch.org/explore/raw-dataset-requests/](https://feederwatch.org/explore/raw-dataset-requests/)

**What they hold:** Standardized counts of birds visiting backyard feeders across North America, November through April. Data run [continuously from 1988](https://feederwatch.org/explore/raw-dataset-requests/), constituting one of the longest-running citizen science bird datasets. Over 1.8 million checklists. Standardized two-day count periods with effort data (hours observed). Covers 200+ feeder bird species. Site description files include habitat and feeder type metadata.

**Access method:** Freely downloadable CSV files organized by 5-year periods (1988–1995, 1996–2000, etc.) directly from the FeederWatch website. No account required for download, though researchers are invited to consult with Cornell staff. Files range from 380 MB to 1.3 GB per period.

**License:** Freely available. No explicit Creative Commons license stated, but Cornell and Birds Canada explicitly commit to free access for students, journalists, researchers, and the public. Personal information of participants is withheld.

**Data format and update cadence:** CSV. [Updated annually on or about June 1](https://feederwatch.org/explore/raw-dataset-requests/). Last update: June 2024.

**Value for WildlifeStats:**
- Long-term feeder bird population trends — sensitive indicators of local population health.
- Complements BBS (breeding season) with winter season data.
- House Finch disease (conjunctivitis from *Mycoplasma gallisepticum*) was first detected and tracked via FeederWatch data.
- Provides geographic reach into suburban/urban environments for One Health relevance.

---

### 2.2 Project NestWatch (Cornell Lab)
**URL:** [https://nestwatch.org](https://nestwatch.org) | Data: [https://nestwatch.org/explore-data/nestwatch-open-dataset-downloads/](https://nestwatch.org/explore-data/nestwatch-open-dataset-downloads/)

**What they hold:** Nest monitoring records for North American bird species — nesting attempts, clutch size, hatching success, fledgling count, nest fate. Data run from 2000 to present (older historical data also incorporated). Available from the Mendeley Data archive.

**Access method:** Direct CSV download (no account required beyond visiting the Mendeley page). ZIP archives. [Updated January 2026](https://nestwatch.org/explore-data/nestwatch-open-dataset-downloads/). Sensitive species precise coordinates withheld; available to qualified scientists on request.

**License:** [CC BY-NC 4.0](https://nestwatch.org/explore-data/nestwatch-open-dataset-downloads/). Non-commercial use only.

**Data format and update cadence:** CSV/ZIP. Updated annually.

**Value for WildlifeStats:**
- Breeding success metrics provide population health indicators.
- Nest failure data (predation, abandonment, infertility) can signal environmental stressors.
- Not directly a mortality/disease source, but declining nest success in a region is an indirect wildlife health signal.

**Known integration friction:**
- CC BY-NC license restricts commercial use.
- Not suitable as a primary disease surveillance source.

---

### 2.3 eBird Status and Trends Data Products
**URL:** [https://ebird.github.io/ebirdst/](https://ebird.github.io/ebirdst/) | Access form: [https://ebird.org/st/request](https://ebird.org/st/request)

**What they hold:** Machine learning–derived weekly species distribution models — abundance, range, habitat associations, and trends for 2,900+ species globally. Derived from 63.7 million eBird checklists from 32 million unique locations (2009–2023). Products include 52-week relative abundance rasters, seasonal range maps, habitat variable associations, and trend estimates with uncertainty.

**Access method:** Free access request form (immediate approval for non-commercial use). R package `ebirdst` for download. GeoTIFF and GeoPackage formats also available directly from the Status and Trends website for most-used products. API available for programmatic access outside R.

**License:** Non-commercial use free. Commercial use requires written permission from Cornell Lab. No resale or incorporation into commercial products.

**Data format and update cadence:** GeoTIFF (abundance), GeoPackage (trends/ranges). Annual updates; [2023 status + 2022 trends](https://ebird.github.io/ebirdst/) is current release.

**Value for WildlifeStats:**
- Provides baseline species abundance and range context for interpreting mortality/disease events.
- Trend data can flag species undergoing rapid decline.
- State-level summaries include stewardship maps and population percentage per state — useful for prioritizing surveillance effort.

---

### 2.4 Christmas Bird Count (CBC) — National Audubon Society
**URL:** [https://www.audubon.org/community-science/christmas-bird-count](https://www.audubon.org/community-science/christmas-bird-count) | Data portal: [https://www.christmasbirdcount.org](https://www.christmasbirdcount.org)

**What they hold:** The world's longest-running citizen science wildlife survey, running annually since [1900](https://www.audubon.org/content/policy-regarding-use-christmas-bird-count-data). Each count circle (15-mile diameter) is surveyed on a single day between December 14 and January 5 each year. Over 2,500 count circles across the Western Hemisphere. Data include species counts, observer effort, and geographic location by count circle.

**Access method:** Public online raw data portal and trend viewer at [https://www.christmasbirdcount.org](https://www.christmasbirdcount.org). Canadian data also via Birds Canada's NatureCounts platform.

**License:** Audubon retains intellectual property rights. Non-commercial use for academic research, education, conservation, and government assessments is permitted. Commercial use requires written permission (cbcadmin@audubon.org). Data may not be shared with third parties or placed in permanent databases/apps without written permission. Anti-automated-access provisions prohibit bots/scrapers.

**Data format and update cadence:** CSV/tabular via web portal. Annual.

**Value for WildlifeStats:**
- 125-year winter bird population trend record — unmatched temporal depth for detecting long-term avian population changes.
- Trend viewer provides population trend analyses for hundreds of species.
- Directly complements BBS (breeding season) and FeederWatch (winter feeder counts).
- Not a direct mortality/disease source, but population collapse signals (e.g., corvid declines after West Nile) are detectable.

**Known integration friction:**
- Restrictive data use terms: no third-party sharing, no permanent databases without written permission.
- Anti-automation provision explicitly prohibits bots — must use manual download.
- Commercial use requires permission.
- **This is a significant integration friction for WildlifeStats if it operates as a hosted public database — requires written permission from Audubon before ingestion.**

---

### 2.5 North American Bat Monitoring Program (NABat)
**URL:** [https://www.nabatmonitoring.org](https://www.nabatmonitoring.org) | Data: [https://www.nabatmonitoring.org/get-data](https://www.nabatmonitoring.org/get-data)

**What they hold:** NABat is a USGS-coordinated continental bat monitoring program using standardized acoustic monitoring protocols. Covers stationary acoustic detectors, mobile transects, and colony counts at hibernacula and roost sites. Designed to detect Pd (white-nose syndrome) impacts and other bat population changes. Data from hundreds of partners across the US and Canada are aggregated.

**Access method:** Registered NABat Partner Portal users (free account) can submit third-party data requests. Filter by species, temporal scope, and geographic extent. Data approved by project leads are compiled as ZIP files with metadata.json. Some projects auto-approve; others require project lead authorization. Data request results are public and viewable in the Request Archive.

**License:** Varies by project; NABat itself does not state a uniform license.

**Data format and update cadence:** ZIP archives with metadata.json. Continuous data submission by partners; request compilation as-needed.

**Value for WildlifeStats:**
- **Critical for white-nose syndrome (Pseudogymnoascus destructans) surveillance** — one of the most catastrophic wildlife diseases in North American history, having killed millions of bats.
- Bat populations are key disease reservoir hosts (rabies); monitoring trends is directly relevant to One Health.
- Acoustic data captures species presence/activity, enabling seasonal and geographic trend detection.

**Known integration friction:**
- Account registration required; some projects require individual project lead approval.
- Data sharing inconsistent across projects.
- Acoustic data interpretation requires specialized software (SonoBat, Kaleidoscope, etc.) — not standard CSV tables.

---

### 2.6 BatAMP (Bat Acoustic Monitoring Portal)
**URL:** [https://batamp.databasin.org](https://batamp.databasin.org)

**What they hold:** An open-access web-based portal for archiving and visualizing bat echolocation monitoring datasets from any acoustic detector or species ID process. Users upload spreadsheets of acoustic monitoring results. The portal enables aggregated visualization of bat species activity patterns, occurrence maps, and temporal animations across North America.

**Access method:** Web-based portal. Users contribute and explore data. BatAMP-compatible spreadsheet format required; SonoBat provides a BatAMP-friendly export. Currently hosted via the Data Basin platform.

**License:** Not formally stated on the portal.

**Data format and update cadence:** Spreadsheet uploads (CSV-compatible); visualization tools. Contributed continuously.

**Value for WildlifeStats:**
- Complements NABat with longer historical baseline; some datasets predate NABat.
- Geographic coverage extends across migration corridors.
- Bat species activity data relevant to rabies reservoir surveillance.

---

## Tier 3: License-Restricted or Access-Gated

### 3.1 HerpMapper
**URL:** [https://www.herpmapper.org](https://www.herpmapper.org)

**What they hold:** Global reptile and amphibian (herpetofauna) observation platform. Records include species ID, photographs, GPS location, date, and habitat notes. Designed for herpetologists and citizen scientists to document herp occurrences. Roadkill/dead-on-road (DOR) recording is explicitly supported. App-based field data collection (iOS/Android) works offline with GPS.

**Access method:** Public users and HerpMapper account holders see only basic record info; exact locality data is restricted. HerpMapper Partners (research institutions, conservation organizations) can apply for full data access including precise GPS coordinates. Public data via API is limited. No public bulk download.

**License:** Not formally stated. Data shared with Partners for research and conservation. Redistribution restrictions apply.

**Data format and update cadence:** Web + app platform. Continuous.

**Value for WildlifeStats:**
- Captures reptile and amphibian mortality (DOR records) and live sightings for taxa poorly covered by other platforms.
- Critical for tracking chytrid fungus (Batrachochytrium dendrobatidis, Bd) and ranavirus impacts on amphibian populations.
- Roadkill data for herps fills a major gap in mortality tracking not addressed by eBird or iNaturalist at comparable quality.
- Complements iNaturalist herpetofauna observations.

**Known integration friction:**
- Exact locality data restricted to Partners — requires formal partnership agreement.
- No public API for bulk data.
- Limited record counts not publicly disclosed.

---

### 3.2 COASST (Coastal Observation and Seabird Survey Team)
**URL:** [https://coasst.org](https://coasst.org)

**What they hold:** Standardized monthly surveys of beached birds along the Pacific Coast of the US (Alaska through northern California) and Great Lakes. Running since [1999](https://coasst.org/about/publications/). Volunteers survey assigned beach segments and record all beached birds found (species, age, sex, condition, cause of death when determinable, associated tags/bands). COASST data have been used in reports and publications by resource management agencies on oil spills, harmful algal bloom mortality, and climate-driven population shifts.

**Access method:** No public bulk download or API. Data are shared through research partnerships with COASST staff at the University of Washington. Researchers contact COASST directly. Data use for management reports by resource agencies is an established pathway.

**License:** Not formally stated. Research partnership terms apply.

**Data format and update cadence:** Survey-level data (per beach, per month). Continuous; 25+ years of baseline data.

**Value for WildlifeStats:**
- **High-value mortality and disease surveillance for coastal/marine birds.** COASST is the primary long-term beached bird dataset for the Pacific Coast.
- Detects mortality spikes attributable to: oil spills, harmful algal blooms (domoic acid), unusual mortality events, avian influenza.
- Provides baseline mortality rates enabling detection of anomalous mortality events.
- Data have been used in oil spill litigation and regulatory proceedings.

**Known integration friction:**
- No open access — requires research partnership with COASST/UW.
- Pacific Coast geographic scope only (though Great Lakes coverage exists).

---

### 3.3 TickEncounter Resource Center / TickSpotters
**URL:** [https://web.uri.edu/tickencounter/](https://web.uri.edu/tickencounter/)

**What they hold:** University of Rhode Island program collecting citizen-submitted tick photographs and encounter details from across North America. The TickSpotters program provides expert tick ID and risk assessment to submitters in exchange for their encounter data (tick species, life stage, attachment duration, geographic location, host species). This crowd-sourced data supports tick population trend monitoring and tickborne disease risk mapping. Published research using TickEncounter data includes [spatial and temporal patterns of tick exposure in the US](https://www.sciencedirect.com/science/article/pii/S1877959X23000420).

**Access method:** No public data portal. Data accessible through research collaboration with URI's Center for Vector-Borne Disease. Published analyses available in peer-reviewed literature.

**License:** Not formally stated. Academic institution controls data.

**Data format and update cadence:** Photo-based submissions with metadata (JPG + questionnaire responses). Continuous.

**Value for WildlifeStats:**
- **Critical One Health data.** Tick species and life stage distributions, tick attachment on humans and pets, and geographic risk patterns are directly relevant to wildlife disease ecology (Lyme disease, Rocky Mountain spotted fever, etc.).
- Human encounter data is a proxy for tick abundance and distribution in residential/periurban landscapes — where wildlife–human interface is highest.
- Complements CDC Tick Surveillance datasets (county-level establishment data for *Ixodes scapularis*, *I. pacificus*, and pathogens) which are available publicly from [CDC](https://www.cdc.gov/ticks/data-research/facts-stats/tick-surveillance-data-sets.html).

---

### 3.4 Snapshot Wisconsin
**URL:** [https://dnr.wisconsin.gov/topic/research/projects/snapshot](https://dnr.wisconsin.gov/topic/research/projects/snapshot)

**What they hold:** Year-round statewide camera trap network managed by the Wisconsin DNR. Volunteers host trail cameras on their properties. Images are crowdsourced-classified on [Zooniverse](https://www.zooniverse.org/projects/zooniverse/snapshot-wisconsin). Species included: beaver, bobcat, coyote, fisher, fox, opossum, otter, raccoon, skunk, white-tailed deer, wolves, and others — the only monitoring for many of these species in Wisconsin.

**Access method:** Web data dashboard for visualization. Scientific publications available. Direct data access requires contact with Wisconsin DNR. Not openly downloadable at present.

**License:** Not formally stated. State agency program.

**Data format and update cadence:** Camera trap images + Zooniverse classifications. Continuous.

**Value for WildlifeStats:**
- Year-round continuous camera trap data for rabies vector species (raccoon, fox, skunk, opossum) and other wildlife disease hosts.
- Population trend data for fur-bearing species managed by the state.
- Complements Snapshot USA with year-round (not just September–October) coverage.

---

### 3.5 Bumble Bee Watch (Direct Data Access)
**URL:** [https://www.bumblebeewatch.org](https://www.bumblebeewatch.org)

*See also Tier 1.7 for the public GBIF dataset.*

**What they hold (sensitive/private records):** Location-precise bumble bee observations for rare and vulnerable species that are masked in public GBIF outputs. These records have precise GPS coordinates useful for conservation planning.

**Access method:** Written proposal required for sensitive data. Processing fees may apply ($75/hour, $500/day). Distribution restrictions: raw data not publicly redistributable; derived maps/tables generally acceptable.

**License:** Restricted — use-specific approval, no redistribution of raw data without permission.

**Value for WildlifeStats:** Only if precise rare bumble bee locations are needed for regional conservation planning — otherwise the public GBIF dataset (Tier 1.7) is sufficient.

---

### 3.6 Adventure Scientists — Wildlife Connectivity and Roadkill Datasets
**URL:** [https://www.adventurescientists.org](https://www.adventurescientists.org) | Datasets: [https://www.adventurescientists.org/access-datasets.html](https://www.adventurescientists.org/access-datasets.html)

**What they hold:** Adventure Scientists engages outdoor athletes (hikers, cyclists, climbers) to collect scientific data in remote environments. Relevant datasets include:
- **Global Wildlife Connectivity (2013–2021):** Surveys of roadways worldwide documenting wildlife collisions — species, photos, locations, speed limits, and deceased/living wildlife along roadways.
- **Montana Wildlife Connectivity (2019–2020):** Focused roadkill data on 50-mile cycling segments — small animals (amphibians, birds) and large mammals (ungulates, carnivores), road infrastructure, and fencing.
- **Pollinators dataset:** Large-scale backcountry butterfly and host plant data from remote areas.

**Access method:** Request-based via website "Request a Dataset" button. Approval process.

**License:** Not formally stated on the website.

**Data format and update cadence:** Not specified. Field survey data; project-specific.

**Value for WildlifeStats:**
- Roadkill data from remote roadways and backcountry areas not covered by CROS or iNaturalist roadkill projects.
- Fills a geographic gap for wildlife mortality data in wilderness and federal land contexts.
- Pollinator data from backcountry areas complements Bumble Bee Watch and USGS Bee Lab data.

---

### 3.7 Globe at Night / Loss of the Night
**URL:** [https://globeatnight.org](https://globeatnight.org) | Data: [Kaggle mirror (2006–2025)](https://www.kaggle.com/datasets/bwandowando/globe-at-night-2006-to-2024)

**What they hold:** Globe at Night is a citizen science program measuring light pollution via naked-eye limiting magnitude observations and Sky Quality Meter readings. Loss of the Night is a companion app for smartphone-based sky brightness measurement. Data cover global light pollution measurements since 2006, with hundreds of thousands of observations.

**Access method:** Globe at Night data are publicly viewable at globeatnight.org/maps. CSV data available via direct download (see Kaggle mirror). Original data portal at [globeatnight.org](https://globeatnight.org).

**License:** Public/open — consistent with NOIRLab/NSF stewardship.

**Value for WildlifeStats:**
- Adjacent (not direct wildlife health data) but relevant to One Health: light pollution disrupts circadian rhythms, migration patterns, and predator-prey dynamics for a wide range of wildlife taxa.
- Useful as an environmental covariate for modeling wildlife behavior, nesting disruption, and foraging changes.

---

## Tier 4: Researcher / Institutional Access Required

### 4.1 North American Bird Banding Program (USGS Bird Banding Laboratory)
**URL:** [https://www.usgs.gov/labs/bird-banding-laboratory](https://www.usgs.gov/labs/bird-banding-laboratory) | Band recovery reporting: [https://www.reportband.gov](https://www.reportband.gov)

**What they hold:** The Bird Banding Laboratory (BBL), established 1920, administers the North American Bird Banding Program in collaboration with the Canadian Wildlife Service. It holds over 75 million banding records and encounter data for migratory birds. Individual banding data available electronically from 1960; encounter data from 1913. Records include band number, species, age, sex, banding location, banding date, condition at banding, and all subsequent recoveries/recaptures with location and condition (alive, injured, dead, cause of death where known).

**Access method:** Banding and encounter data are available for research purposes via a formal data request process. Individual banding requires a federal Bird Banding and Marking Permit under the Migratory Bird Treaty Act. Longevity records are publicly viewable. Public band reporting via [reportband.gov](https://www.reportband.gov) for anyone who finds a banded bird.

**License:** US government data; effectively public domain once approved for release.

**Data format and update cadence:** Electronic records from 1960 (banding) and 1913 (encounters). Format upon request; database queries by USGS staff.

**Value for WildlifeStats:**
- Band recovery data includes cause of death/injury for millions of individual birds — one of the largest multi-species wildlife mortality records in existence.
- Encounter data captures birds reported as "found dead" or "found injured" by members of the public — direct rehabilitation-relevant signal.
- Long-term individual tracking enables survival rate and mortality cause analysis across species.

**Known integration friction:**
- Formal research request required; not self-service.
- Federal permit required for active banding participation.
- Large data volumes; custom query by USGS staff.

---

### 4.2 Earthwatch Institute Projects
**URL:** [https://earthwatch.org.uk](https://earthwatch.org.uk) | Datasets: Project-specific, published in scientific journals with supporting data

**What they hold:** Earthwatch funds and deploys paid volunteer researchers on expeditions to collect field data in support of scientific projects. Data topics include wildlife population surveys, disease ecology, animal behavior, and ecosystem health. Earthwatch policy states: ["project data and metadata are made publicly available and, where possible, results are published in open access format"](https://earthwatch.org.uk/citizen-science/). Data are published through peer-reviewed journals with supporting information or deposited in repositories.

**Access method:** Contact project scientists; data published in scientific literature with supporting files. No central Earthwatch data portal for all projects.

**License:** Open access per project; varies.

**Value for WildlifeStats:**
- Unique field research data from biodiversity-rich regions.
- Disease ecology projects (e.g., malaria vectors, wildlife reservoirs).
- Quality is high — data are collected by trained volunteers under scientific supervision.

---

### 4.3 Whale Alert / Marine Mammal Stranding Citizen Science
**URL:** [https://www.fisheries.noaa.gov/resource/tool-app/whale-alert](https://www.fisheries.noaa.gov/resource/tool-app/whale-alert) | IFAW: [https://www.ifaw.org/international/campaigns/whale-alert](https://www.ifaw.org/international/campaigns/whale-alert)

**What they hold:** Whale Alert collects citizen-reported whale sightings (live, dead, distressed) from boaters, whale watchers, mariners, and the general public. Launched 2012 by NOAA Stellwagen sanctuary and IFAW. Covers US Atlantic, Pacific, and now European waters. Sightings include species, number of animals, condition (live/dead/distressed), GPS location, date/time, and photos. Feeds into the NOAA Right Whale Sighting Advisory System. Also integrates acoustic detections from NOAA buoys and gliders.

**Access method:** App is free. Scientific data access requires contact: [info@whalealert.org](mailto:info@whalealert.org). Not a self-service open data portal.

**Related platforms:** HappyWhale ([https://happywhale.com](https://happywhale.com)) provides photo-ID matching for humpback and other whale species from citizen-submitted photos. Marine Mammal Center stranding network integrates rescue and health data.

**License:** Not formally stated for bulk data access.

**Value for WildlifeStats:**
- Reports of dead and distressed whales are directly relevant to rehabilitation triggers and cause-of-death analysis (vessel strike, entanglement, disease).
- North Atlantic right whale data are among the most critically important cetacean conservation datasets.
- Complements marine mammal stranding network data (NOAA Marine Mammal Health and Stranding Response Program).

---

### 4.4 State-Level Rabies Submission and Wildlife Mortality Portals
**Examples:** Maryland ([health.maryland.gov](https://health.maryland.gov/laboratories/pages/rabies-animal-dfa.aspx)), Pennsylvania, North Carolina, and all other states.

**What they hold:** Each state health department operates a rabies testing laboratory accepting specimens for rabies diagnosis from animals that have potentially exposed humans, pets, or livestock. Data include species, geographic origin, test result, and date. Some states also have wildlife mortality hotlines (e.g., CDFW in California).

**Access method:** Not public databases — specimen submission portals for health professionals and animal control agencies. Summary data published by CDC (annual rabies surveillance reports). CDC Tick Surveillance Data provide county-level tick establishment data publicly.

**License:** Public health data; available via CDC annual reports and state health agency data releases.

**Value for WildlifeStats:**
- Critical One Health surveillance layer: rabies testing results by species and county.
- Data on wildlife species submitted for rabies testing (raccoon, fox, skunk, bat, groundhog) reflect wildlife population health and human-wildlife contact rates.
- Integration pathway: CDC compiles national data; state-level data requires state-by-state relationships.

---

### 4.5 COASST (Additional Detail)
*See Tier 3.2 for full entry. Elevated frictions apply: full data sharing requires formal University of Washington research partnership.*

---

## Additional Sources Noted

### iNaturalist Roadkill Network
Multiple iNaturalist community projects specifically track roadkill observations: [Global Roadkill Observations](https://www.inaturalist.org/projects/14609), state-level projects (Roadkills of Oregon, Roadkills of Texas, etc.), "Dead Birds," "Dead Mammals." These are accessible via the standard iNaturalist API and GBIF DwC-A with field filters — no separate ingestion needed beyond the main iNaturalist pipeline.

### City Nature Challenge / BioBlitzes
The City Nature Challenge is an annual four-day global BioBlitz run on the iNaturalist platform, producing [3.3 million observations from 102,000+ observers across six continents in 2025](https://www.inaturalist.org/blog/123031-impact-highlights-from-2025). All CNC data are ingested via the standard iNaturalist pipeline. No separate data source required.

### Lost Ladybug Project / BeeSpotter
Both are regional citizen science projects for native ladybug and bee species respectively. Lost Ladybug Project (Cornell) data feed into iNaturalist and GBIF. BeeSpotter (University of Illinois) focuses on bumble bees and honey bees in Illinois; data available through the project website. Both have limited geographic scope and are superseded for WildlifeStats purposes by iNaturalist and Bumble Bee Watch.

### ROaDS (Roadkill Observation and Data System)
Developed by the National Park Service, Western Transportation Institute, and Center for Large Landscape Conservation for federal lands and partner organizations. Not a public data portal — organizations must apply to deploy the tool. Partner data can be accessed via the Center for Large Landscape Conservation ([largelandscapes.org](https://largelandscapes.org/news/roads-app/)).

### EpiCollect5
Open-source mobile and web data collection platform used by many wildlife disease and ecology projects. Not a data source itself, but many wildlife health citizen science projects (emerging pandemic threat surveillance, etc.) run on EpiCollect5. Data export in CSV/JSON; project-specific access.

---

## Recommended Ingestion Priority Order

The following ranking weighs **data value to WildlifeStats** (disease/mortality signal, rehabilitatation relevance, One Health content, geographic scope, taxonomic breadth) against **accessibility** (licensing, bulk download availability, API support, no legal barriers to public database hosting).

| Rank | Source | Rationale |
|---|---|---|
| 1 | **WHISPers** | Highest direct wildlife disease and mortality signal; public domain; API + annual CSV releases. The only systematically diagnosed wildlife health event database in the US. |
| 2 | **iNaturalist (GBIF DwC-A)** | Broadest taxonomic scope; 300M+ records; weekly DwC-A updates; roadkill/mortality projects extractable via filter. CC BY-NC restriction manageable for public database. |
| 3 | **eBird EBD** | 2B+ sightings, 150M checklists; monthly bulk download; essential avian species composition and abundance baseline. |
| 4 | **NEON** | CC0; standardized wildlife + pathogen sample data; 81 sites; best structured One Health signal for small mammal disease vectors. |
| 5 | **USGS BBS** | Public domain; 58-year bird population time series; CSV; essential for long-term avian health trend context. |
| 6 | **GLOBE Observer / Mosquito Habitat Mapper** | Open, commercial-use permitted; direct disease vector data; NASA backing; globally georeferenced mosquito habitat observations. |
| 7 | **Snapshot USA / Wildlife Insights** | All-50-state standardized mammal camera trap data; CC licensing; annual open-access publications on Dryad; covers rabies-relevant species. |
| 8 | **Project FeederWatch** | Free CSV download; 37-year dataset; feeder bird health indicators; precedent for disease tracking (House Finch conjunctivitis). |
| 9 | **USGS Bee Lab (via GBIF)** | Public domain; native bee baseline; accessible via GBIF DwC-A pipeline already established for iNaturalist. |
| 10 | **Bumble Bee Watch (GBIF, CC BY 4.0)** | DwC-A via GBIF; CC BY 4.0; verified pollinator health data; USGS-published. |
| 11 | **NABat** | Free account; bat population + white-nose syndrome surveillance; critical disease reservoir data. Registration friction manageable. |
| 12 | **CROS (California Roadkill)** | Highest-quality roadkill dataset in North America; requires contact for data access but well-established research use. |
| 13 | **NestWatch** | CC BY-NC; free download via Mendeley; breeding success as long-term health indicator. |
| 14 | **Christmas Bird Count** | 125-year dataset; restrictive terms require written Audubon permission for database hosting — secure this early. |
| 15 | **COASST** | High-value coastal bird mortality baseline; Pacific Coast scope; requires formal UW research partnership — pursue concurrently with WHISPers integration. |

**Near-term partnership targets (Tiers 3–4 worth pursuing):** COASST (UW), TickEncounter (URI), NABat full partnerships, HerpMapper (research partner status), and North American Bird Banding Lab (research data request).

---

*Report compiled for WildlifeStats. Primary sources: [eBird Science](https://science.ebird.org/en/use-ebird-data/download-ebird-data-products), [iNaturalist Developers](https://www.inaturalist.org/pages/developers), [GBIF iNaturalist dataset](https://www.gbif.org/dataset/50c9509d-22c7-4a22-a47d-8c48425ef4a7), [USGS BBS ScienceBase](https://doi.org/10.5066/P136CRBV), [WHISPers USGS](https://data.usgs.gov/datacatalog/data/USGS:581deaed-18e7-45b1-8935-1ea7342ba7e5), [NEON Science](https://www.neonscience.org/data-samples/guidelines-policies/publishing-research-outputs), [Project FeederWatch Data](https://feederwatch.org/explore/raw-dataset-requests/), [NestWatch Downloads](https://nestwatch.org/explore-data/nestwatch-open-dataset-downloads/), [CBC Data Terms of Use](https://www.audubon.org/content/policy-regarding-use-christmas-bird-count-data), [NABat Get Data](https://www.nabatmonitoring.org/get-data), [Bumble Bee Watch GBIF](https://ipt.gbif.us/resource?r=xerces-bumblebeewatch), [Wildlife Insights Terms](https://wildlifeinsights.org/terms-use-summary), [GLOBE Observer Data](https://observer.globe.gov/get-data/mosquito-habitat-data), [Snapshot USA Smithsonian](https://nationalzoo.si.edu/conservation-ecology-center/snapshot-usa), [CROS Road Ecology](https://roadecology.ucdavis.edu/research/projects/cros), [eBird Status and Trends](https://ebird.github.io/ebirdst/), [Adventure Scientists Datasets](https://www.adventurescientists.org/access-datasets.html), [iNaturalist 300M observations](https://www.inaturalist.org/blog/126478-inaturalist-at-300-million-observations), [eBird 2 billion sightings](https://news.cornell.edu/stories/2025/08/lab-ornithology-hits-2-billion-bird-sightings-3-million-recordings), [WhaleAlert IFAW](https://www.ifaw.org/international/campaigns/whale-alert), [CDC Tick Surveillance](https://www.cdc.gov/ticks/data-research/facts-stats/tick-surveillance-data-sets.html), [USGS Bee Lab](https://www.usgs.gov/centers/eesc/bee-database).*
