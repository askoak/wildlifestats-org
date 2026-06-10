# Federal and State Wildlife Data Sources

*Compiled for WildlifeStats — a national research framework for wildlife medicine, disease, rehabilitation, One Health, disease vectors, and citizen science. Scope: United States federal and state government sources; major international counterparts noted where directly relevant.*

---

## Tier 1: Open API / Bulk Download (Use Immediately)

These sources offer machine-readable access with no institutional gatekeeping. Priority for first-pass ingestion.

---

### 1. USGS WHISPers — Wildlife Health Information Sharing Partnership Event Reporting System

**URL:** [https://whispers.usgs.gov](https://whispers.usgs.gov) | Data catalog: [https://www.usgs.gov/centers/nwhc/data](https://www.usgs.gov/centers/nwhc/data)

**What data they hold:**  
WHISPers is the most directly relevant federal database for WildlifeStats. It is a web-based repository of current and historic wildlife **mortality (death) and morbidity (illness) events** reported by state and federal partners nationwide. Key fields include:
- Event type (mortality, morbidity, or both)
- Species affected (common and scientific name, taxonomic class)
- Geographic location (county, state, latitude/longitude)
- Number of animals affected, found dead, sick
- Diagnostic conclusions and suspected/confirmed etiologies
- Land ownership type
- Lab submissions flagged to USGS NWHC diagnostic services

The NWHC Laboratory Information Management System (LIMS) holds **diagnostic case-level data** — individual specimens submitted for necropsy, histopathology, and toxicology — which feeds into WHISPers at the event level. A public-domain dataset of NWHC diagnostic case data is published on USGS ScienceBase (DOI: [https://doi.org/10.5066/P9B0A3IM](https://doi.org/10.5066/P9B0A3IM)).

**Access method:**  
- Web UI with search, filter, and CSV/spreadsheet export — open to public, no login required for browse
- Data download via built-in export tool (CSV)
- A user guide is available at [https://www.usgs.gov/media/files/whispers-user-guide-viewing-searching-saving-whispers-data](https://www.usgs.gov/media/files/whispers-user-guide-viewing-searching-saving-whispers-data)
- Contact: whispers@usgs.gov for bulk data requests or API questions

**License / Use restrictions:**  
Public domain (USA.gov Public Domain Label 1.0) for the underlying NWHC dataset on ScienceBase. WHISPers event data is openly accessible.

**Data format and update cadence:**  
CSV export from web UI; underlying dataset on ScienceBase in tabular format. Updated continuously as partners report new events; diagnostic case dataset on ScienceBase has periodic releases.

**Value for WildlifeStats:**  
- **Disease surveillance**: Primary national register for multi-animal wildlife mortality events — avian influenza, lead toxicosis, West Nile virus, CWD, botulism, canine distemper, Tyzzer's disease, parasitic infections
- **Rehabilitation case loads**: Morbidity events link directly to rehabilitation intake scenarios (oiled birds, lead-poisoned raptors, disease-driven die-offs)
- **One Health**: Events tagged with human-relevance flags; NWHC is the lead federal wildlife diagnostic center
- **Regional analysis**: County-level geocoding enables state and flyway-scale mapping
- **Species patterns**: Taxonomically diverse; spans all vertebrate classes

**Known integration friction:**  
- The WHISPers front-end is a JavaScript-heavy SPA (single-page application) that loads as "Loading..." — programmatic bulk extraction requires the CSV export tool or the ScienceBase dataset rather than the live UI
- No documented public REST API for WHISPers as of 2025; contact whispers@usgs.gov for data pipeline arrangements
- Partner-reported data: completeness varies by state and season; some events are reported weeks or months after occurrence
- Some diagnostic conclusions are provisional; field "confirmed" vs. "suspect" etiology must be filtered carefully

---

### 2. USGS Bird Banding Laboratory (BBL) / North American Bird Banding Program

**URL:** [https://www.usgs.gov/labs/bird-banding-laboratory](https://www.usgs.gov/labs/bird-banding-laboratory) | ScienceBase data: [https://www.sciencebase.gov/catalog/](https://www.sciencebase.gov/catalog/)

**What data they hold:**  
The BBL (established 1920) maintains the North American Bird Banding Program (NABBP) dataset:
- Individual banding records: species, band number, age, sex, date, location (lat/lon), bander
- Encounter/recovery records: subsequent location of banded individuals (dead recoveries, live recaptures, resightings)
- Electronic records from 1960 to present; pre-1960 data available for encountered birds
- Encounter data from 1913

**Access method:**  
- Full dataset published annually on ScienceBase — bulk download, no authentication required
- Bander Portal web tool for targeted data requests by species/geography/time period: [https://www.pwrc.usgs.gov/BBL/Bander_Portal/](https://www.pwrc.usgs.gov/BBL/Bander_Portal/)
- Account registration required for the Bander Portal (free, non-banders can register)

**License / Use restrictions:**  
Public domain via USGS ScienceBase. Bulk download available to all.

**Data format and update cadence:**  
CSV/tabular; annual ScienceBase release (updated each year with most recent banding season).

**Value for WildlifeStats:**  
- **Species patterns**: Population-level movement and survival data for >700 North American bird species
- **Disease / rehabilitation**: Banding age-class and condition data; mortality encounter records provide cause-of-death when recorded
- **Migratory bird context**: Essential for linking disease events to flyway corridors

**Known integration friction:**  
- The full ScienceBase dataset is large (hundreds of millions of records since 1960)
- Some coordinate precision is intentionally degraded for rare/sensitive species
- Encounter reason codes (dead recovery, live recapture) require careful schema parsing

---

### 3. USFWS ECOSphere / ECOS REST API — Endangered Species Data

**URL:** [https://ecos.fws.gov/ecp/services](https://ecos.fws.gov/ecp/services) | Data Explorer: [https://ecos.fws.gov/ecp/](https://ecos.fws.gov/ecp/)

**What data they hold:**  
The Environmental Conservation Online System (ECOS) is the FWS authoritative registry for:
- All ESA-listed species (threatened, endangered, proposed, candidate) with listing status, taxonomy, and Federal Register citations
- Critical habitat boundary polygons and lines (GIS shapefiles and ArcGIS services)
- Recovery plans and documents by species
- Petition history for listing decisions
- IPaC Location API: T&E species lists, migratory bird species, and wetland sensitivity data by geographic extent

**Access method:**  
- REST API with JSON, XML, CSV, HTML output — fully open, no key required
- ECOS Data Explorer: [https://ecos.fws.gov/ecp/report/adhocDocumentation?catalogId=species&reportId=species](https://ecos.fws.gov/ecp/report/adhocDocumentation?catalogId=species&reportId=species)
- Critical habitat shapefiles: direct bulk download
- IPaC Location API: REST endpoint returning species lists by bounding box
- ServCat (FWS data catalog): [https://ecos.fws.gov/ServCat/](https://ecos.fws.gov/ServCat/)

**License / Use restrictions:**  
Public domain. FWS data; freely reusable.

**Data format and update cadence:**  
REST API returns JSON/XML/CSV. Critical habitat GIS data updated weekly via LiveSync. ESA listing data updated as listings occur.

**Value for WildlifeStats:**  
- **Species patterns**: Definitive registry of protected species; enables regulatory-context tagging of all WildlifeStats records
- **Regional analysis**: Critical habitat polygons enable spatial overlay with rehabilitation intake locations
- **One Health**: ESA-listed species appearing in rehabilitation or disease surveillance records gain immediate regulatory context

**Known integration friction:**  
- ECOS schema has evolved over years; legacy endpoints occasionally return inconsistent taxonomy
- Critical habitat polygons can be geometrically complex; some species have hundreds of parcels
- IPaC API documented primarily for project-based use; rate limits not publicly stated

---

### 4. GBIF-US / BISON — Biodiversity Information Serving Our Nation

**URL:** [https://www.gbif.us](https://www.gbif.us) | Global GBIF API: [https://techdocs.gbif.org/en/data-use/api-downloads](https://techdocs.gbif.org/en/data-use/api-downloads)

**What data they hold:**  
BISON (now transitioned to GBIF-US, managed by USGS Science Analytics and Synthesis) aggregates US species occurrence data:
- 800+ million US species occurrence records from federal agencies, state agencies, museums, universities, and citizen science platforms
- Data from USFWS, USGS, NPS NPSpecies, herbaria, natural history collections, eBird, iNaturalist
- Darwin Core standard fields: taxon, date, lat/lon, basis of record, data provider, dataset DOI
- GBIF global dataset: 3.1+ billion occurrence records across all countries

**Access method:**  
- GBIF REST API with free account: [https://api.gbif.org/v1/](https://api.gbif.org/v1/) — asynchronous bulk download (SIMPLE_CSV, Darwin Core Archive, Species List formats)
- R package `rgbif`; Python package `pygbif`
- Free account registration at gbif.org; no institutional affiliation required
- Downloads require citation with DOI assigned at time of download

**License / Use restrictions:**  
Open access. Individual dataset licenses vary (CC0, CC-BY, CC-BY-NC); GBIF tracks and exposes per-record license. WildlifeStats should filter on CC0 and CC-BY records for most permissive reuse.

**Data format and update cadence:**  
Darwin Core Archive (DwC-A) or SIMPLE_CSV. GBIF index updated daily from providers; full re-indexing periodically. US data via gbif.us updated as providers push changes.

**Value for WildlifeStats:**  
- **Species patterns**: Broadest available occurrence backbone for cross-referencing rehabilitation species against known ranges
- **Citizen science**: iNaturalist research-grade observations, eBird (EOD), museum collections all flow through GBIF
- **Regional analysis**: Entire US covered; enables multi-decade trend analysis

**Known integration friction:**  
- Large downloads (wildlife-relevant taxa US-only can still exceed tens of millions of records)
- Darwin Core fields are inconsistently populated across providers; lat/lon precision varies enormously
- Asynchronous download: query → wait (minutes to hours) → email notification → download
- Duplicate records common across providers; GBIF deduplication is imperfect
- iNaturalist records in GBIF (EOD) lack effort/sampling metadata present in EBD

---

### 5. EPA ECOTOX Knowledgebase

**URL:** [https://cfpub.epa.gov/ecotox/](https://cfpub.epa.gov/ecotox/)

**What data they hold:**  
ECOTOX is EPA's publicly available ecotoxicology database:
- 1.1+ million test records from 54,000+ peer-reviewed references
- Nearly 14,000 aquatic and terrestrial species
- 13,000+ chemicals (pesticides, metals, pharmaceuticals, industrial chemicals)
- Three integrated sub-databases: AQUIRE (aquatic), TERRETOX (terrestrial wildlife), PHYTOTOX (plants)
- Fields: chemical CAS number, species, test endpoint (LC50, NOEC, etc.), effect type, life stage, exposure route, concentration, reference

**Access method:**  
- Open web search at [https://cfpub.epa.gov/ecotox/](https://cfpub.epa.gov/ecotox/) — no account required
- Bulk data download available (full database export)
- Filter by species, chemical, effect, endpoint (19 parameters, 100+ output fields)
- Updated quarterly

**License / Use restrictions:**  
Public domain; EPA-generated database. Free for unrestricted use.

**Data format and update cadence:**  
CSV export; full database bulk download. Quarterly updates.

**Value for WildlifeStats:**  
- **Pesticide exposure**: Direct link between rehabilitation intake causes (rodenticide toxicosis, organophosphate poisoning, lead) and toxicological thresholds
- **One Health**: Chemical stressors documented in wildlife translate to ecological risk and human exposure context
- **Disease vectors**: Ecotoxicology of pesticide effects on vector-competent species (mosquitoes, ticks)

**Known integration friction:**  
- Literature-derived; not surveillance data — reflects experimental findings, not field exposure events
- Species taxonomy uses its own coding system; requires mapping to common wildlife taxonomy standards (ITIS, GBIF backbone)

---

### 6. CDC NORS — National Outbreak Reporting System

**URL:** [https://www.cdc.gov/nors/](https://www.cdc.gov/nors/) | Data download: [https://data.cdc.gov](https://data.cdc.gov)

**What data they hold:**  
NORS collects reports of all US foodborne, waterborne, and enteric disease outbreaks, including:
- **Animal contact outbreaks (ACOSS)**: All outbreaks of enteric illness spread to humans from contact with animals or their environments — including wildlife contact events
- Waterborne disease outbreaks (since 1971)
- Foodborne disease outbreaks (since 1970s)
- Pathogen: Campylobacter, Cryptosporidium, E. coli, Giardia, Salmonella, Norovirus, and hundreds more
- Outbreak setting, number ill, laboratory confirmation, exposure vehicle
- BEAM Dashboard: interactive visualization tool

**Access method:**  
- Open download at data.cdc.gov: [https://data.cdc.gov](https://data.cdc.gov) — CSV download, no account required
- BEAM Dashboard interactive tool for visualization
- Data are finalized 12–18 months after reporting year end

**License / Use restrictions:**  
Public domain (CDC data). Freely downloadable.

**Data format and update cadence:**  
CSV via data.cdc.gov. Annual finalized release; provisional data available.

**Value for WildlifeStats:**  
- **One Health**: Animal contact transmission pathways documented with pathogen, setting, and host-animal type
- **Disease surveillance**: Wildlife-to-human spillover events; especially relevant for avian/reptile contact outbreaks
- **Rehabilitation use case**: Contact with wildlife during rehabilitation represents an occupational exposure pathway — NORS data provides epidemiological context

**Known integration friction:**  
- Animal species implicated is often poorly classified ("bird," "reptile," "wild animal") — requires secondary lookup to link to specific taxa
- Voluntary reporting; significant underreporting by states
- Finalized data lag of 12–18 months from event

---

### 7. NSF NEON — National Ecological Observatory Network Pathogen Data

**URL:** [https://www.neonscience.org](https://www.neonscience.org) | Data Portal: [https://data.neonscience.org](https://data.neonscience.org)

**What data they hold:**  
NEON operates 81 terrestrial and aquatic field sites across 20 eco-climatic domains. Wildlife-medicine-relevant data products include:
- **Tick-borne pathogen status (DP1.10092.001)**: Presence/absence of Borrelia burgdorferi, Anaplasma phagocytophilum, Babesia microti, Ehrlichia, Francisella tularensis, Rickettsia, Borrelia miyamotoi — tested on individual nymphal ticks from six key species
- **Mosquito-borne pathogen status (DP1.10041.001)**: Alphavirus, bunyavirus, flavivirus screening pools; West Nile virus, EEE, others
- **Rodent-borne pathogen status (DP1.10064.001)**: Small mammal blood/ear tissue for tick-borne pathogens and (2014–2019) hantavirus seropositivity
- **Tick abundance/diversity (DP1.10093.001)**: Species, sex, life stage counts by site and date
- **Small mammal trapping (DP1.10072.001)**: Individual-level capture data for Peromyscus and other reservoirs
- Physical specimens archived at NEON Biorepository (ASU) and US National Tick Collection

**Access method:**  
- Open data portal: [https://data.neonscience.org](https://data.neonscience.org) — all data freely downloadable, no login
- R package `neonUtilities`; Python API wrapper
- Data products in tabular CSV format with comprehensive metadata

**License / Use restrictions:**  
CC0 (public domain). NSF-funded; open science mandate.

**Data format and update cadence:**  
CSV with EML metadata; provisional data available near-real-time, finalized data released on rolling basis. Tick pathogen testing has external lab processing lag of ~6 months.

**Value for WildlifeStats:**  
- **Disease vectors**: Highest-quality standardized continental-scale tick and mosquito pathogen surveillance data in existence — directly informs WildlifeStats One Health and vector-borne disease modules
- **Rodent reservoirs**: Peromyscus-focused pathogen data links rodent ecology to Lyme disease, tick-borne pathogen, and hantavirus risk
- **Species patterns**: Long-term time series from fixed sites across all major US biomes

**Known integration friction:**  
- Sites are fixed (81 locations); not a nationwide systematic survey — significant geographic gaps in coverage
- Pathogen testing is on subsets of collected specimens; not all ticks or mosquitoes are tested
- NEON Biorepository portal experienced availability issues (noted June 2026)
- Requires NEON product IDs and understanding of data stacking utilities to use efficiently

---

## Tier 2: Public but Friction-y (FOIA, Manual Request, State-by-State)

These sources hold extremely valuable data but require non-trivial effort to access: manual data requests, state-by-state variation, lengthy fulfillment timelines, or substantial data wrangling.

---

### 8. USDA APHIS — National Wildlife Disease Program (NWDP) & HPAI Wild Bird Surveillance

**URL:** [https://www.aphis.usda.gov/national-wildlife-programs/nwdp](https://www.aphis.usda.gov/national-wildlife-programs/nwdp) | HPAI wild birds: [https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/wild-birds](https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/wild-birds)

**What data they hold:**  
The NWDP coordinates wildlife disease surveillance across APHIS Wildlife Services field operations:
- **HPAI Wild Bird Surveillance Dashboard**: All confirmed HPAI (H5N1) detections in wild birds since January 2022 — county-level, species, detection date, map and table. Includes samples from APHIS Wildlife Services and state agency morbidity/mortality submissions. Updated continuously; downloadable table on the HPAI detections page.
- **Wild Bird Avian Influenza Surveillance Dashboard**: Broader AI surveillance including negative tests and flyway-level summaries: [https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/wild-bird-surveillance-dashboard](https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/wild-bird-surveillance-dashboard)
- Feral swine disease surveillance (classical swine fever, African swine fever preparedness, pseudorabies)
- Chronic wasting disease (CWD) in cervids — coordination role; data primarily at state level
- Rabies field surveillance: APHIS biologists test ~7,000 animals annually as part of the National Rabies Management Program (NRMP)

**Access method:**  
- HPAI wild bird detection table: publicly downloadable from the detections page (HTML table, exportable)
- Program Data Reports (PDRs): annual reports published at [https://www.aphis.usda.gov/wildlife-services/publications/pdr](https://www.aphis.usda.gov/wildlife-services/publications/pdr) — reports from 1996 to present; pre-2013 archived versions available by emailing APHISWeb@usda.gov
- NWDP contact for surveillance data requests: julianna.b.lenoch@usda.gov, sarah.n.bevins@usda.gov
- FOIA for unpublished surveillance data: [https://www.aphis.usda.gov/freedom-information-act](https://www.aphis.usda.gov/freedom-information-act)

**License / Use restrictions:**  
USDA public data; freely reusable. HPAI detection table is openly published. PDRs are public documents.

**Data format and update cadence:**  
- HPAI table: HTML/CSV-equivalent, updated weekdays
- PDRs: annual PDF/HTML reports, published ~6 months post-fiscal year end
- Underlying surveillance data: not available in machine-readable bulk format without direct request

**Value for WildlifeStats:**  
- **Disease surveillance**: HPAI detections are the most pressing current wildlife disease surveillance dataset in the US — over 10,000 wild bird detections since 2022 (H5N1 clade 2.3.4.4b)
- **One Health**: HPAI spillover to mammals (bears, foxes, sea lions) documented in this dataset
- **Regional analysis**: County-level data enables state and flyway-level analysis

**Known integration friction:**  
- HPAI table is HTML-embedded; no direct API or stable CSV download URL — requires periodic table extraction
- PDRs are PDF/HTML narrative reports, not machine-readable databases; structured data must be extracted manually from tables
- Raw sample-level surveillance data (negative tests, specific geographic coordinates) requires direct researcher contact or FOIA
- Privacy policy redacts private landowner location details

---

### 9. USDA APHIS Wildlife Services — Program Data Reports (PDR)

**URL:** [https://www.aphis.usda.gov/wildlife-services/publications/pdr](https://www.aphis.usda.gov/wildlife-services/publications/pdr)

**What data they hold:**  
Annual PDRs since 1996 document all wildlife damage management activities by WS field operations:
- Animals encountered, dispersed, and lethally removed — by species, state, and removal method
- Management action types: trapping, shooting, exclusion, chemical deterrents, oral bait vaccines (rabies)
- Funding sources: federal appropriations vs. cooperator funds, by state
- Program areas: airport wildlife hazards, livestock protection, disease management, T&E species protection, urban wildlife conflicts
- Human health and safety incidents
- In FY2021: 26.6 million animals encountered; ~1.76 million lethally removed; 6.6% lethal rate

**Access method:**  
- Annual reports publicly available at [https://www.aphis.usda.gov/wildlife-services/publications/pdr](https://www.aphis.usda.gov/wildlife-services/publications/pdr) — 2014 to present online; 1996–2013 by email request
- Reports are HTML/PDF with embedded data tables — no bulk machine-readable download
- State-by-state breakdowns require aggregating multiple report sections

**License / Use restrictions:**  
Public domain USDA documents; freely reusable.

**Data format and update cadence:**  
HTML and PDF tables; annual release, ~6 months post-fiscal year. FY runs October–September.

**Value for WildlifeStats:**  
- **Rehabilitation interface**: Animals captured but released (dispersed) include injured/ill wildlife that may enter rehabilitation pipelines
- **Disease management**: Oral rabies vaccination (ORV) bait distribution quantities by state — direct disease management proxy
- **Species patterns**: Species-level removal and encounter data spans all 50 states; 26 years of time series

**Known integration friction:**  
- Data locked in HTML tables and PDFs — requires table parsing (e.g., pdfplumber, tabula-py)
- Terminology for management actions is not standardized across years; schema shifts require manual reconciliation
- PDR data represents WS-direct activities only; does not capture data from state wildlife agencies operating independently

---

### 10. NOAA Fisheries — National Marine Mammal Stranding Database / Health MAP

**URL:** [https://www.fisheries.noaa.gov/national/marine-life-distress/national-stranding-database-public-access](https://www.fisheries.noaa.gov/national/marine-life-distress/national-stranding-database-public-access) | Health MAP: [https://www.fisheries.noaa.gov/national/marine-life-distress/marine-mammal-health-monitoring-and-analysis-platform-health-map](https://www.fisheries.noaa.gov/national/marine-life-distress/marine-mammal-health-monitoring-and-analysis-platform-health-map)

**What data they hold:**  
The National Marine Mammal Stranding Database (current system, to be replaced by Health MAP in 2026+) records **every stranded marine mammal responded to** by the 120+ authorized members of the National Marine Mammal Stranding Response Network:
- Species, approximate age class, sex
- Date and location of stranding (state/county; lat/lon where available)
- Condition at initial observation (alive/dead, condition code 1–5)
- Final determination (cause of mortality/stranding where known)
- Human interaction flags: fishery entanglement, vessel strike, gunshot
- Level A standard form fields (morphometrics, disposition) for all cases

**Forthcoming Health MAP (2026+):** Mandated by the Marine Mammal Research and Response Act (MMRRA, 2022 NDAA), Health MAP will replace the current database with a richer schema including histopathology, toxicology, microbiology, virology, parasitology, and live animal rehabilitation admission/release data. A public web portal will be required by law.

**Access method (current):**  
- **Restricted to active stranding network members** for full database query access
- Public researchers: email data request to MMHSRP.NationalDB@noaa.gov or regional stranding coordinators; fulfillment takes **weeks to months**
- Three public example CSV datasets for teaching/analysis (2022 vintage): West Coast California Sea Lions 2017–2018; East Coast Bottlenose Dolphins 2017–2019; Large Whales 2005–2015
- Sea Turtle Stranding and Salvage Network (STSSN): summary reports available for 1980–present via web interface: [https://www.fisheries.noaa.gov/inport/item/27318](https://www.fisheries.noaa.gov/inport/item/27318)

**License / Use restrictions:**  
Government data; publicly available upon request. PII (boat names, respondent contact info) redacted from public releases.

**Data format and update cadence:**  
Excel/CSV provided for data requests. Updated continuously by network members.

**Value for WildlifeStats:**  
- **Rehabilitation case loads**: Richest national dataset on marine mammal rehabilitation intake, treatment, and disposition — central to WildlifeStats marine mammal module
- **Disease surveillance**: Unusual mortality events (UMEs), morbillivirus, HAB toxins, infectious disease, human interaction injuries
- **One Health**: Zoonotic disease in marine mammals (leptospirosis, brucellosis, influenza A)
- **Species patterns**: All US cetacean and pinniped strandings since 1972

**Known integration friction:**  
- Access currently restricted; requires network membership or manual data request
- Long fulfillment times for custom queries (weeks–months)
- Health MAP transition in progress (2026) may create data continuity gaps and schema changes
- STSSN sea turtle data has separate access procedures through the Southeast Fisheries Science Center

---

### 11. CDC ArboNET — National Arbovirus Surveillance System

**URL:** [https://www.cdc.gov/vector-borne-diseases/php/arbonet/index.html](https://www.cdc.gov/vector-borne-diseases/php/arbonet/index.html)

**What data they hold:**  
ArboNET is the national arbovirus surveillance system managed by CDC and state/territorial health departments:
- Human arboviral disease cases: West Nile virus, Eastern and Western Equine Encephalitis, St. Louis Encephalitis, La Crosse, Dengue, Zika, others
- **Non-human surveillance streams highly relevant to WildlifeStats**:
  - Dead bird surveillance data (sentinel species, primarily corvids for WNV)
  - Sentinel animal serology (horses, chickens, other sentinel flocks)
  - Mosquito pool testing results by species and location
  - Presumptive viremic blood donor (PVD) detections
- Veterinary (equine) case reports
- Weekly reporting from 54 jurisdictions (50 states + DC + 5 territories)

**Access method:**  
- Disease maps interactive viewer: [https://wwwn.cdc.gov/arbonet/Maps/ADB_Diseases_Map/index.html](https://wwwn.cdc.gov/arbonet/Maps/ADB_Diseases_Map/index.html)
- Annual summary reports published in MMWR
- Historical data files for nationally notifiable arboviral diseases available through NNDSS/WONDER: [https://wonder.cdc.gov/nndss/](https://wonder.cdc.gov/nndss/)
- **Raw ArboNET data (dead bird, mosquito pool, sentinel animal streams)**: not available as bulk public download; access via direct CDC request or state health department

**License / Use restrictions:**  
CDC government data; publicly available summaries. Raw surveillance data access requires CDC/state coordination.

**Data format and update cadence:**  
Annual MMWR reports; NNDSS tabular data on CDC WONDER/data.cdc.gov. Weekly provisional updates.

**Value for WildlifeStats:**  
- **Disease vectors**: Definitive national dataset for vector-borne disease; dead bird and mosquito pool data directly relevant to wildlife surveillance
- **One Health**: Human WNV cases linked temporally and geographically to wildlife die-offs (crow mortality) that WildlifeStats would monitor
- **Regional analysis**: County-level data for most disease types

**Known integration friction:**  
- Non-human ArboNET streams (dead birds, mosquito pools) are not in the public bulk download — requires state health department contact or CDC request
- Human case data (NNDSS) is the most accessible stream but is less directly wildlife-relevant
- Dead bird data was rich during 1999–2010 WNV emergence but surveillance intensity has declined in many states
- State-by-state variation in what is reported to ArboNET vs. held at state level

---

### 12. CDC National Rabies Surveillance System

**URL:** [https://www.cdc.gov/rabies/php/protecting-public-health/index.html](https://www.cdc.gov/rabies/php/protecting-public-health/index.html)

**What data they hold:**  
CDC's National Rabies Surveillance System processes data from 130+ state public health laboratories that test ~95,000 animals annually:
- ~3,500–4,500 positive animal cases per year; >90% wildlife
- Reservoir species breakdown: bats (35%), raccoons (29%), skunks (17%), foxes (8%)
- Rabies virus variant typing: identifies which animal reservoir variant (raccoon rabies, skunk Mephitid, bat variants, etc.)
- Geographic distribution of variants (strain mapping)
- USDA NRMP oral rabies vaccination (ORV) program data merged into CDC national datafile
- Human exposure statistics, PEP usage

**Access method:**  
- Annual report "Rabies Surveillance in the United States" published in JAVMA and MMWR — publicly accessible
- Summary data tables in annual report (year, state, species, count)
- Raw case-level data: maintained by CDC, not in public bulk download — requires direct contact with CDC Poxvirus and Rabies Branch (rabies@cdc.gov)
- Historical reports available via CDC publications archive

**License / Use restrictions:**  
CDC data; annual reports are public domain. Case-level data requires data use agreement.

**Data format and update cadence:**  
Annual report PDF with data tables; typically published ~1 year after reporting period.

**Value for WildlifeStats:**  
- **Disease surveillance**: Foundational national dataset for the single most consistently monitored wildlife disease program in the US
- **One Health**: Direct wildlife-to-human transmission risk; variant typing links specific wildlife reservoirs to human exposure risk
- **Rehabilitation case loads**: Rabies exposure risk from rehabilitation intake of bat, raccoon, skunk, fox species — requires variant context

**Known integration friction:**  
- Annual cadence; no near-real-time data
- Raw case-level data not publicly available in bulk — requires researcher-direct contact
- Variant typing data richest in MMWR/JAVMA annual reports; not machine-readable

---

### 13. NPS IRMA Portal — NPSpecies, Data Store, Aquarius

**URL:** [https://irma.nps.gov/Portal/](https://irma.nps.gov/Portal/) | NPSpecies: [https://irma.nps.gov/NPSpecies/](https://irma.nps.gov/NPSpecies/) | Data Store: [https://irma.nps.gov/DataStore/](https://irma.nps.gov/DataStore/)

**What data they hold:**  
IRMA (Integrated Resource Management Applications) is the NPS data hub serving 400+ park units:
- **NPSpecies**: Species occurrence lists for 300+ parks — species presence/absence, occurrence status, nativity, management concern; REST web services for programmatic access
- **Data Store**: Tens of thousands of reports, datasets, and geospatial files — natural resource condition assessments, biodiversity inventories, water quality monitoring, vegetation maps
- **Aquarius Web Data Portal**: Continuous water quality and quantity data from NPS monitoring locations
- **Visitor Use Statistics**: Annual visitation counts by park (1904–present)
- **Research Permit and Reporting System (RPRS)**: Study results from all permitted research in NPS units — potentially containing unpublished wildlife health and rehabilitation data

**Access method:**  
- NPSpecies: open public access; species lists downloadable; REST API available
- Data Store: open public search and download at irma.nps.gov/DataStore/
- REST/web services for NPSpecies and other applications (contact irma@nps.gov)
- NPSpecies data also published to GBIF/BISON via ipt.gbif.us
- RPRS study results: some public, some restricted to researchers

**License / Use restrictions:**  
Public domain with NPS disclaimer. NPSpecies certified species lists: CC0 (per GBIF publication).

**Data format and update cadence:**  
CSV/Excel for species lists; various formats in Data Store (PDF, shapefiles, CSVs). NPSpecies updated as parks submit new surveys; no fixed cadence.

**Value for WildlifeStats:**  
- **Species patterns**: Park-level species lists for 300+ protected areas; essential for understanding what species are present in national park rehabilitation catchment areas
- **Regional analysis**: Long-term monitoring data from NPS Inventory & Monitoring Networks
- **Disease**: Park-specific wildlife health studies in Data Store; I&M network data on mammal populations

**Known integration friction:**  
- NPSpecies data quality is highly variable — some lists are "certified" (reviewed), others are informal; status flags require careful filtering
- Data Store has inconsistent metadata; finding relevant wildlife health datasets requires keyword search with manual review
- REST API for NPSpecies is functional but poorly documented externally
- RPRS research reports may contain key wildlife health data but are not systematically indexed by disease or species condition

---

### 14. State Wildlife Rehabilitation Annual Reports — State DNR / Fish & Wildlife Agencies

**No single URL** — state-by-state. Key examples:
- New York: NYSDEC — [https://dec.ny.gov/permits/permits-licenses-registrations/wildlife-hunting-fishing-trapping-licenses/wildlife-rehabilitation-permit](https://dec.ny.gov/permits/permits-licenses-registrations/wildlife-hunting-fishing-trapping-licenses/wildlife-rehabilitation-permit)
- California: CDFW — [https://nrm.dfg.ca.gov](https://nrm.dfg.ca.gov) (Data Portal; Wildlife Rehabilitation Annual Report form: DFW 486)
- National template: USFWS Form 3-202-4 (annual report for federal rehabilitation permittees)

**What data they hold:**  
This is the **single richest untapped public-records source** for wildlife rehabilitation case loads in the United States. Requirements vary by state, but the majority of the ~50 states that license wildlife rehabilitators require annual submission of:
- Species-level intake records (common/scientific name, number of animals)
- Intake reason / presenting distress code (injury, orphan, disease, oiled, chemical exposure)
- Outcome by species: released, transferred, died in care, euthanized, DOA, remains in care
- Approximate age class and sex (where recorded)
- Geographic area of recovery (often county-level)
- In New York (since 1985): individual case-level Wildlife Rehabilitator Log (WRL) forms submitted annually for **all licensed rehabilitators** — effectively a **complete census** of wildlife rehabilitation in the state; 2012–2014 dataset alone contained 58,185 cases from 441–458 rehabilitators annually
- California CDFW: DFW 486 form requires species-by-species outcome table, with integration with the Wildlife Rehabilitation Medical Database (WRMD)

**Access method:**  
- Data held by state wildlife agencies; not typically available as downloadable open data
- **Public records / FOIA requests**: State equivalents of FOIA (e.g., NY FOIL, CA PRA, TX PIA) apply to agency-held records from permitted rehabilitators. Annual summary data and aggregated species tables are generally producible without privacy concerns
- Some states may provide data directly upon researcher request with a data use agreement
- USFWS 3-202-4 federal form data held by FWS MBMO (Migratory Bird Management Office) — accessible via FWS FOIA: [https://www.fws.gov/program/fws-freedom-information-act-foia](https://www.fws.gov/program/fws-freedom-information-act-foia)
- Wildlife Rehabilitation Medical Database (WRMD — [https://www.wrmd.org](https://www.wrmd.org)) is a private SaaS platform used by many rehabilitators; some states accept WRMD exports as the annual report — this creates a potential single-source ingestion pathway through WRMD partnerships

**License / Use restrictions:**  
State public records; raw annual reports are government documents. Aggregated, non-PII data generally available under state open records law. Individual rehabilitator contact info may be withheld.

**Data format and update cadence:**  
Paper forms and/or WRMD digital exports; PDF or paper submissions scanned and held by state agency. Annual cadence (report due January 31 or December 1, depending on state).

**Value for WildlifeStats:**  
- **Rehabilitation case loads**: The most granular, species-resolved, outcome-coded rehabilitation dataset available nationally — far exceeds any existing aggregated federal source
- **Disease surveillance**: Intake reason codes and mortality rates by species serve as leading indicators for disease events (e.g., WNV in corvids, HPAI in raptors, distemper in raccoons)
- **Regional analysis**: State-level data enables geographic mapping of rehabilitation demand, seasonal patterns, and species-specific trends
- **One Health**: Rehabilitator occupational exposure events may be captured in state records; zoonotic risk documentation

**Known integration friction:**  
- **No national aggregation exists** — WildlifeStats would need to run 50 separate FOIA campaigns
- Data quality and format vary enormously by state; some states have detailed electronic records, others have paper forms scanned to PDF
- Fulfillment timelines for public records requests vary (10–60 business days; varies by state workload)
- Some states may redact rehabilitator-level identifiers, producing species-only aggregate tables
- Not all states have mandatory annual reporting; ~10–15 states have minimal or informal requirements
- WRMD partnership (if achievable) would provide the richest structured data but requires negotiation with a private company

---

### 15. USDA Forest Service — Forest Inventory and Analysis (FIA) + Wildlife Monitoring

**URL:** FIA: [https://www.fia.fs.usda.gov/](https://www.fia.fs.usda.gov/) | Geodata: [https://data.fs.usda.gov/geodata/edw/datasets.php](https://data.fs.usda.gov/geodata/edw/datasets.php) | NWRC: [https://www.aphis.usda.gov/national-wildlife-programs/nwrc](https://www.aphis.usda.gov/national-wildlife-programs/nwrc)

**What data they hold:**  
**FIA (Forest Service):**
- Forest inventory plots covering all 50 states (~125,000 forested plots sampled on rolling 5–10 year cycles)
- Tree species, canopy cover, forest type, understory vegetation
- Wildlife habitat indices derived from forest structure
- Does **not** directly contain wildlife occurrence data but is the definitive habitat characterization layer for forested ecosystems

**NWRC (APHIS National Wildlife Research Center):**
- Research publications on wildlife disease ecology (feral swine, CWD, bovine TB, avian influenza, SARS-CoV-2 in wildlife, rabies)
- Disease detection and surveillance tool development data
- Digital collections and archive at [https://nwrcarchive.libraryhost.com](https://nwrcarchive.libraryhost.com)

**Access method:**  
- FIA data: open download via FIA DataMart and EVALIDator tool
- USFS national geospatial datasets: open download at data.fs.usda.gov
- NWRC publications: open access via APHIS publications page; research data on USDA Ag Data Commons

**License / Use restrictions:**  
Public domain USDA data; freely reusable.

**Data format and update cadence:**  
FIA: CSV/database via DataMart; annual rolling panel updates. NWRC: publications; associated data in Ag Data Commons.

**Value for WildlifeStats:**  
- **Regional analysis**: FIA forest structure data is an essential covariate for habitat-linked disease models (CWD in deer, tick-borne disease in wooded landscapes)
- **Species patterns**: Forest type and disturbance history inform species distribution models for forest-dependent wildlife

**Known integration friction:**  
- FIA does not contain wildlife data directly — value is as a spatial covariate/habitat layer
- NWRC research data is not aggregated in a single searchable repository; requires paper-by-paper data retrieval

---

## Tier 3: Researcher-Direct Request (Requires Institutional Contact)

These sources hold significant data but gate access behind network membership, institutional affiliation, or formal data-sharing agreements.

---

### 16. NOAA STSSN — Sea Turtle Stranding and Salvage Network

**URL:** [https://www.fisheries.noaa.gov/national/marine-life-distress/sea-turtle-stranding-and-salvage-network](https://www.fisheries.noaa.gov/national/marine-life-distress/sea-turtle-stranding-and-salvage-network) | InPort: [https://www.fisheries.noaa.gov/inport/item/27318](https://www.fisheries.noaa.gov/inport/item/27318)

**What data they hold:**  
The STSSN (est. 1980) maintains stranding records for all five sea turtle species in US waters:
- Species (loggerhead, Kemp's ridley, green, leatherback, hawksbill)
- Date, location, condition (alive, dead, cold-stunned)
- Human interaction flags (boat strike, fishery gear entanglement, debris ingestion)
- Rehabilitation outcome
- Records from 1980 to present; summary reports queryable via web interface

**Access method:**  
- Public summary reports (1980–present) via NOAA InPort/Southeast Fisheries Science Center
- Interactive sea turtle stranding visualization tool (NOAA)
- **Full case-level data**: contact Southeast Fisheries Science Center; similar institutional request process to marine mammal stranding database
- The STSSN application (seaturtlestranding.com) is a reporting tool for authorized network members

**License / Use restrictions:**  
Government data; publicly available in summary form; case-level data requires formal request.

**Value for WildlifeStats:**  
- **Rehabilitation case loads**: Sea turtle rehabilitation is a significant component of coastal wildlife medicine; STSSN data captures all cold-stun events, fibropapillomatosis cases, entanglement injuries
- **One Health / pollution**: Fibropapillomatosis linked to eutrophication and environmental contaminants; anthropogenic impact proxy

**Known integration friction:**  
- Institutional request required for full case-level access; summary-only data is coarser
- STSSN and the marine mammal stranding database have different regional coordinators and request pathways

---

### 17. USFWS — Migratory Bird Data (HIP / Breeding Bird Survey / Band Recovery)

**URL:** HIP harvest: [https://www.fws.gov/library/collections/migratory-bird-hunting-activity-and-harvest-reports](https://www.fws.gov/library/collections/migratory-bird-hunting-activity-and-harvest-reports) | Breeding Bird Survey: [https://www.usgs.gov/centers/eesc/science/north-american-breeding-bird-survey](https://www.usgs.gov/centers/eesc/science/north-american-breeding-bird-survey)

**What data they hold:**  
- **Harvest Information Program (HIP)**: Annual migratory bird harvest estimates by species, state, and flyway; hunter activity surveys since 1999; published reports and underlying estimates available
- **North American Breeding Bird Survey (BBS)**: USGS/CWS cooperative survey; >4,000 annual roadside survey routes; relative abundance data for all detected bird species; open data at [https://www.usgs.gov/data/north-american-breeding-bird-survey-dataset](https://www.usgs.gov/data/north-american-breeding-bird-survey-dataset)
- **Band recovery data**: BBL ScienceBase annual release (see Tier 1 entry above)

**Access method:**  
- HIP harvest reports: open PDF/HTML at FWS library
- BBS data: open download from USGS ScienceBase
- IPaC migratory bird lists: REST API (see ECOS entry)

**License / Use restrictions:**  
Public domain USGS/USFWS data.

**Value for WildlifeStats:**  
- **Species patterns**: Definitive population trend data for all hunted migratory species; BBS provides abundance trends for all birds
- **Regional analysis**: Flyway-level analysis; temporal trends for disease risk modeling

---

### 18. CDC NNDSS — National Notifiable Diseases Surveillance System (Wildlife-Adjacent Zoonoses)

**URL:** [https://www.cdc.gov/nndss/](https://www.cdc.gov/nndss/) | Data: [https://data.cdc.gov](https://data.cdc.gov)

**What data they hold:**  
NNDSS collects case reports of all nationally notifiable conditions from 50 states + DC + territories. Wildlife-relevant notifiable diseases include:
- Rabies (human and animal)
- West Nile virus neuroinvasive disease
- Eastern/Western/Venezuelan Equine Encephalitis
- Plague (Yersinia pestis)
- Tularemia
- Hantavirus pulmonary syndrome
- Brucellosis
- Lyme disease
- Spotted fever Rickettsiosis (including RMSF)
- Anaplasmosis, Ehrlichiosis
- Leptospirosis

**Access method:**  
- Weekly provisional tables: data.cdc.gov (CSV download)
- Annual finalized tables: CDC WONDER ([https://wonder.cdc.gov/nndss/](https://wonder.cdc.gov/nndss/)) and CDC Stacks
- Historical data from 1912 to present (reporting intensity varies by era)

**License / Use restrictions:**  
CDC public domain data. Freely downloadable.

**Data format and update cadence:**  
CSV via data.cdc.gov; weekly provisional, annual finalized.

**Value for WildlifeStats:**  
- **One Health**: Human cases of wildlife-reservoir zoonoses serve as epidemiological confirmation of wildlife transmission events
- **Disease surveillance**: NNDSS Lyme/tick-borne disease cases provide the human-side correlate to NEON tick pathogen data and state wildlife surveillance

**Known integration friction:**  
- NNDSS is human-only data — no direct wildlife records
- County-level data suppressed for many low-count states (privacy protection)
- Voluntary reporting; geographic completeness varies
- Animal rabies data (distinct from human rabies) is in a separate CDC database

---

### 19. NOAA Fisheries — Bycatch DROP / Fisheries Observer Programs

**URL:** [https://www.fisheries.noaa.gov/national/fisheries-observers/bycatch-data-reporting-observer-programs-database](https://www.fisheries.noaa.gov/national/fisheries-observers/bycatch-data-reporting-observer-programs-database) | FOSS: [https://foss.nmfs.noaa.gov/](https://foss.nmfs.noaa.gov/)

**What data they hold:**  
- **Fisheries observer programs**: Professionally trained biologists on commercial vessels documenting catch composition, bycatch species/quantity, condition of protected species at release, gear type, location, date
- **Bycatch DROP (in development 2025)**: Centralized database of bycatch estimates from observer programs across all NMFS regions — marine mammals, sea turtles, seabirds
- **FOSS (Fisheries One Stop Shop)**: Commercial and recreational landings data by species, state, year (2009–present); guest login access; CSV export

**Access method:**  
- FOSS: guest login; CSV export of summarized landings data
- Bycatch DROP: in active development; GitHub repository for uploaded regional data files: not yet public portal
- Raw observer data: restricted to NOAA regional offices; requires formal data request through NMFS regional science centers
- NOAA InPort metadata catalog for all NMFS datasets: [https://www.fisheries.noaa.gov/inport/](https://www.fisheries.noaa.gov/inport/)

**Value for WildlifeStats:**  
- **Rehabilitation case loads**: Sea turtle, marine mammal, and seabird bycatch injuries require rehabilitation; observer data captures injury type and condition
- **Disease surveillance**: Observer data on anomalous animal conditions at sea feeds into unusual mortality event detection

**Known integration friction:**  
- Observer data is confidential at vessel level; only aggregated estimates released
- Bycatch DROP not yet fully public as of 2025/2026
- FOSS does not contain marine mammal/sea turtle/seabird data directly

---

## Tier 4: Restricted / Partner-Only

These sources hold significant wildlife health data but require formal partnership, institutional affiliation, or are operationally internal to agencies.

---

### 20. USFWS IPaC — Information for Planning and Consultation

**URL:** [https://ipac.ecosphere.fws.gov](https://ipac.ecosphere.fws.gov)

**What data they hold:**  
IPaC is primarily a regulatory consultation tool for project proponents, but provides:
- ESA-listed species lists by location (bounding box)
- Migratory bird species lists by location
- Wetland and critical habitat overlays
- Location-based T&E species with biologically sensitive location data that may not be in ECOS public download

**Access method:**  
- Web tool: open public access for project-based queries
- IPaC Location API: REST endpoint for programmatic access (documented, open)
- Species lists with biologically sensitive data may be restricted for certain species (e.g., Northern Long-eared Bat prior to listing adjustment)

**Value for WildlifeStats:**  
- **Species patterns**: Location-based species lists for regulatory context; complements ECOS for ESA coverage

**Known integration friction:**  
- Sensitive species locations not returned in API (intentional); publicly available locations only

---

### 21. USDA NWRC Wildlife Disease Research Data

**URL:** [https://www.aphis.usda.gov/national-wildlife-programs/nwrc/research-areas/wildlife-disease](https://www.aphis.usda.gov/national-wildlife-programs/nwrc/research-areas/wildlife-disease)

**What data they hold:**  
NWRC researchers generate primary data on wildlife disease ecology at the wildlife-agriculture interface:
- Feral swine disease surveys (pseudorabies, brucellosis, ASF preparedness, swine influenza)
- CWD transmission studies and cervid disease ecology
- Bovine TB at wildlife-livestock interface (deer, elk, badgers)
- Avian influenza strain characterization and host range studies
- SARS-CoV-2 wildlife spillback studies
- Volatile organic compound biomarker tools for CWD/bTB detection

**Access method:**  
- Data associated with publications deposited on USDA Ag Data Commons ([https://data.nal.usda.gov/](https://data.nal.usda.gov/)) — open access
- Unpublished surveillance data: requires direct researcher contact (jeff.root@usda.gov for wildlife disease)
- NWRC archives (historical data): appointment required (Fort Collins, CO); email NWRC.Library@usda.gov

**Value for WildlifeStats:**  
- **Disease surveillance**: High-quality experimental and field surveillance data on the most critical US wildlife diseases at the agriculture interface
- **One Health**: NWRC work directly addresses zoonotic spillover

**Known integration friction:**  
- Most data requires co-author or co-investigator relationship to access prior to publication
- Archive access requires in-person visit or formal request

---

### 22. State Fish and Wildlife Agency Open Data Portals (Selected Major Sources)

**No single URL** — state-by-state, but major examples:

| State | Portal | Key Wildlife Data |
|---|---|---|
| California | [wildlife.ca.gov](https://wildlife.ca.gov) / [nrm.dfg.ca.gov](https://nrm.dfg.ca.gov) / BIOS | CNDDB (rare species), CWHR habitat models, GIS clearinghouse, CDFW open data |
| Texas | [tpwd.texas.gov/gis](https://tpwd.texas.gov/gis) | TXNDD rare species, GIS open data, wildlife management areas |
| New York | dec.ny.gov | NYSDEC wildlife unit data; rehabilitation annual reports (1985–present) |
| Idaho | [idfg.idaho.gov/data](https://idfg.idaho.gov/data) | Idaho FWIS (Fish and Wildlife Information System); GIS data portal |
| Florida | myfwc.com | FWC wildlife data; sea turtle nesting, manatee, panther telemetry |

**What data they hold:**  
State agency data portfolios typically include:
- Species occurrence and population monitoring data (game and non-game)
- Natural Heritage Program / Natural Diversity Database occurrence records for rare, threatened, and endangered species
- Hunting and harvest data (license sales, check stations, hunter surveys)
- Wildlife disease surveillance (CWD, HPAI, dove inclusion body hepatitis, etc.) — often more detailed than federal summaries for intrastate data
- Rehabilitation permit holder databases and annual reports
- Waterbird colony surveys, breeding bird atlases
- Camera trap / telemetry data from research programs (often unpublished in bulk)

**Access method:**  
- Ranges from full open data portals (California BIOS, Idaho FWIS) to FOIA-only
- State open records laws (FOIA equivalents) apply to all agency-held public records
- Natural Heritage Programs: most have researcher data-sharing agreements; contact state NHP
- Disease surveillance data: often held informally in internal databases; public records request usually required

**Value for WildlifeStats:**  
- **Rehabilitation case loads**: State-held annual rehabilitation reports (see entry #14)
- **Disease surveillance**: State CWD surveillance data often exceeds USDA/federal summaries in geographic granularity
- **Regional analysis**: Species occurrence and harvest data fill gaps between federal monitoring programs

**Known integration friction:**  
- 50 different data systems, formats, update cadences, and access policies
- No national standard for state wildlife data interoperability
- FOIA/PRA fulfillment quality varies enormously by state
- Some NHP occurrence data is intentionally obscured for rare species (sensitive location data)

---

### 23. EPA EnviroAtlas

**URL:** [https://www.epa.gov/enviroatlas](https://www.epa.gov/enviroatlas) | Interactive map: [https://enviroatlas.epa.gov/enviroatlas/interactivemap/](https://enviroatlas.epa.gov/enviroatlas/interactivemap/) | Data download: [https://www.epa.gov/enviroatlas/forms/enviroatlas-data-download](https://www.epa.gov/enviroatlas/forms/enviroatlas-data-download)

**What data they hold:**  
EnviroAtlas provides 500+ national data layers linking ecosystem services, stressors, and human health:
- Pesticide use by crop and county
- Impaired waters (303d)
- Air toxic emissions and concentrations
- National Air Toxics Assessment (NATA)
- Land cover, imperviousness
- Species diversity and habitat connectivity indices
- Water quality and nutrient pollution
- Green infrastructure and urban ecosystem services

**Access method:**  
- Open download (post-form submission, which can be skipped): national and community-level CSV and GeoTIFF
- Interactive map with REST service endpoints
- All 500+ layers listed in downloadable spreadsheet catalog

**License / Use restrictions:**  
EPA data; freely downloadable. Survey form optional.

**Data format and update cadence:**  
GeoTIFF, CSV, REST services. Update cadence varies by data layer; many are based on decadal or periodic national surveys.

**Value for WildlifeStats:**  
- **Pesticide exposure**: Pesticide use density as a covariate for rehabilitation intake causes (raptor rodenticide exposure, insecticide impacts)
- **One Health**: Environmental pollution context for disease events
- **Regional analysis**: Spatial covariate layer for habitat quality and anthropogenic stress

---

## Additional High-Value Sources for WildlifeStats Consideration

### 24. eBird (Cornell Lab of Ornithology)
**URL:** [https://science.ebird.org/en/use-ebird-data](https://science.ebird.org/en/use-ebird-data)  
**Data:** 1+ billion bird observations globally; 500+ million US records. eBird Basic Dataset (EBD): all raw observations with effort data; updated monthly.  
**Access:** Free download after account registration and data request (typically approved within 7 days). R package `auk`. API for real-time queries.  
**License:** Non-commercial use; requires CC-BY attribution. Commercial use requires written permission.  
**Value:** Species-level occurrence backbone for all US birds at high spatial/temporal resolution; essential for contextualizing rehabilitation intake patterns and disease event timing against population abundance.  
**Friction:** Non-commercial license restricts direct WildlifeStats commercial deployment; EBD files are large (multi-GB compressed); requires data agreement process.

### 25. iNaturalist (GBIF/Open Data)
**URL:** [https://www.inaturalist.org](https://www.inaturalist.org) | API docs: [https://api.inaturalist.org/v1/docs/](https://api.inaturalist.org/v1/docs/)  
**Data:** 270+ million research-grade observations globally; strong US wildlife representation including mammals, reptiles, amphibians, birds, invertebrates. Observation metadata: taxon, date, lat/lon, quality grade, photos.  
**Access:** REST API (open, free key); CSV export via web UI (10,000 record limit per request); full dataset via GBIF (EOD, annual release, CC-BY).  
**License:** CC0 for observation metadata; photos retain photographer rights.  
**Value:** Citizen science occurrence records for wildlife species with photographic evidence; research-grade observations can confirm species presence at rehabilitation intake locations.  
**Friction:** API page limit (10,000 records); large downloads best routed through GBIF; EOD lacks sampling effort metadata needed for rigorous analysis.

### 26. USGS ScienceBase
**URL:** [https://www.sciencebase.gov/catalog/](https://www.sciencebase.gov/catalog/)  
**Data:** Trusted USGS digital repository hosting hundreds of wildlife-related datasets including BBL banding data, amphibian monitoring, chronic wasting disease distribution maps, bat hibernacula surveys, telemetry datasets.  
**Access:** Open API ([https://www.usgs.gov/sciencebase-instructions-and-documentation/api-and-web-services](https://www.usgs.gov/sciencebase-instructions-and-documentation/api-and-web-services)); REST JSON/XML; free account optional.  
**License:** Varies by dataset; most USGS data is public domain.  
**Value:** Central repository for USGS wildlife data products; one-stop for datasets associated with USGS publications; BBL, CWD distribution, amphibian monitoring all housed here.  
**Friction:** Heterogeneous schema across datasets; requires keyword search with manual review; no single unified wildlife health data model.

---

## Recommended Ingestion Priority Order

Ranked by **value × accessibility** for WildlifeStats's first ingestion pass — prioritizing sources that are (a) directly relevant to wildlife medicine, rehabilitation, disease surveillance, or One Health, AND (b) accessible without institutional gatekeeping.

| Rank | Source | Tier | Primary Use Case | Access Effort |
|------|--------|------|-----------------|---------------|
| 1 | **USGS WHISPers / NWHC Diagnostic Case Data** | 1 | Disease surveillance, mortality events | Low — CSV export + ScienceBase bulk download |
| 2 | **GBIF-US (via GBIF API + rgbif/pygbif)** | 1 | Species occurrence backbone for all taxa | Low — free API, async download |
| 3 | **NEON Pathogen Data Products (DP1.10092, DP1.10041, DP1.10064)** | 1 | Vector-borne disease, rodent reservoirs | Low — open data portal |
| 4 | **EPA ECOTOX Knowledgebase** | 1 | Pesticide/contaminant toxicology | Low — bulk download |
| 5 | **CDC NORS (data.cdc.gov)** | 1 | Animal-contact disease outbreaks, One Health | Low — CSV download |
| 6 | **USFWS ECOS REST API + Critical Habitat** | 1 | ESA species context, regulatory overlay | Low — open REST API |
| 7 | **USDA APHIS HPAI Wild Bird Detection Table** | 2 | Active HPAI surveillance, current outbreak data | Medium — periodic table extraction |
| 8 | **USDA APHIS Wildlife Services PDRs (1996–present)** | 2 | Wildlife encounter/removal, disease management proxy | Medium — PDF/HTML table parsing |
| 9 | **NPS NPSpecies + IRMA Data Store** | 2 | Park-level species lists, long-term monitoring data | Low-Medium — open download + REST |
| 10 | **CDC ArboNET summary data (NNDSS/WONDER)** | 2 | WNV, EEE, arboviral disease trends | Medium — WONDER query interface |
| 11 | **CDC NNDSS zoonotic disease tables (data.cdc.gov)** | 2 | Human-side One Health correlate for wildlife zoonoses | Low — CSV download |
| 12 | **USGS BBL / North American Bird Banding Program** | 1 | Bird population context, band recovery mortality data | Low — ScienceBase bulk download |
| 13 | **State Rehabilitation Annual Reports (NY, CA, TX, FL as pilot)** | 2–3 | Rehabilitation case loads — richest available data | High — FOIA campaigns per state |
| 14 | **NOAA Marine Mammal Stranding Database (data request)** | 3 | Marine mammal rehabilitation, stranding trends | High — email request, weeks–months |
| 15 | **eBird Basic Dataset (Cornell EBD)** | 2 | Avian occurrence backbone with effort data | Medium — data request form; 7-day approval |

### Strategic Notes for WildlifeStats Ingestion

**Immediate actions (Days 1–30):**
1. Download NWHC LIMS diagnostic case dataset from ScienceBase (DOI: 10.5066/P9B0A3IM) — this is the highest-value single-table dataset for wildlife disease
2. Register for GBIF account and initiate bulk US wildlife occurrence download (filter: Animalia, country=US, hasCoordinate=TRUE)
3. Download NEON tick/mosquito/rodent pathogen data products via neonUtilities R package
4. Pull ECOS REST API for full ESA species list with listing status and taxonomy
5. Download EPA ECOTOX full database export

**Short-term actions (Days 30–90):**
6. Establish data extraction pipeline for APHIS HPAI wild bird detection table (weekly pull)
7. Parse APHIS Wildlife Services PDRs (2014–present) into structured database using table extraction tools
8. Submit GBIF-filtered download for eBird Observational Dataset (EOD)
9. Initiate FOIA/state public records requests to NY, CA, FL, TX, WA state wildlife agencies for rehabilitation annual reports (pilot states representing diverse geographies and strong data programs)

**Medium-term (90+ days):**
10. Submit NOAA MMHSRP data request (MMHSRP.NationalDB@noaa.gov) for multi-region marine mammal stranding data
11. Establish WRMD partnership discussions (Wildlife Rehabilitation Medical Database) for direct rehabilitation case data pipeline
12. Contact CDC rabies branch (rabies@cdc.gov) for annual species-level tabular data

**International counterparts (directly relevant):**
- **WOAH (World Organisation for Animal Health) WAHIS**: Global animal disease reporting including wildlife; US reports feed into this system. Relevant for international context on zoonoses that have US wildlife reservoir relevance. Public data access at wahis.woah.org.
- **GBIF global node**: The same GBIF API covers international occurrence data — essential for migratory species distribution context and for comparing US wildlife disease patterns to Canadian and Mexican counterparts.

---

*Report compiled June 2026. URLs verified against primary agency sources. Data availability subject to change as agencies update portals, complete database transitions (NOAA Health MAP), and modify access policies.*
