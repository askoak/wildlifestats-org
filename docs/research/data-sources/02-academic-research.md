# Academic and Research Data Repositories

> **Scope:** University-hosted, society-hosted, journal-mandated, and consortium repositories relevant to the WildlifeStats national framework for wildlife medicine, disease surveillance, rehabilitation, One Health, disease vectors, and citizen science. Coverage includes biodiversity occurrence repositories, trait databases, disease registries, movement ecology archives, media collections, preprint servers, and journal-mandated data archives.

---

## Tier 1: Open API / Bulk Download (Use Immediately)

These repositories provide fully open programmatic access with no registration barrier. WildlifeStats can ingest from these sources today.

---

### 1.1 GBIF — Global Biodiversity Information Facility

- **URL:** [https://www.gbif.org](https://www.gbif.org)
- **What data they hold:** GBIF is the world's most comprehensive aggregator of biodiversity occurrence data. As of 2025, GBIF serves over [3.1 billion species occurrence records](https://www.gbif.se/news/2025/international-day-for-biodiversity-open-access-to-data-is-key-to-future-conservation/) from 113,854 datasets published by 2,476 institutions worldwide, with data being shared at a rate of 13.6 records per second in 2024. Content includes specimen records from natural history collections, observation data from field surveys, citizen science observations (including all research-grade iNaturalist records), satellite tracking points, literature-extracted records, and environmental DNA detections. The registry also indexes datasets, organizations, and networks. GBIF explicitly supports mapping of wild host, vector, and reservoir species involved in disease transmission cycles — a direct fit for One Health applications.
- **Access method:** Fully open REST API at `https://api.gbif.org/v1/`. Four logical sections: Registry, Species, Occurrence, and Maps. Real-time paged search via occurrence endpoint; asynchronous download API for large bulk exports (requires free GBIF account only for downloads, not for API queries). Parquet bulk dumps available on cloud. R package `rgbif` and Python `pygbif` provide convenience wrappers. No authentication required for read queries.
- **License / use restrictions:** GBIF requires datasets to be published under one of three Creative Commons licenses: [CC0 (public domain), CC-BY (attribution), or CC-BY-NC (non-commercial)](https://www.gbif.org/developer/summary). The majority of records are CC0 or CC-BY. Each downloaded dataset package includes machine-readable license metadata per record. Citation of the GBIF download DOI is required for publications.
- **Data format and update cadence:** RESTful JSON API; bulk downloads in Darwin Core Archive (DwC-A) ZIP format (CSV + EML metadata); Parquet cloud dumps refreshed monthly. The index is updated daily as publishers push new data; full snapshots are cut periodically.
- **Specific value for WildlifeStats:** Distribution and occurrence data for every wildlife taxon globally — the backbone for species range mapping, disease vector distribution (mosquitoes, ticks, rodents), host-pathogen co-occurrence analysis, and multi-year population trend detection. Can filter by taxon, country, coordinate precision, basis of record, date range, and dataset. Critical for linking rehabilitation cases to wild population distribution.
- **Known integration friction:** ~30% of records lack precise coordinates or have known geospatial issues (centroid assignments, country-level only). Taxonomic backbone uses Catalogue of Life; name matching is necessary before joining with other databases. Large downloads (>100k records) require a GBIF account and async download job management. CC-BY-NC records must be excluded from any commercial downstream uses.

---

### 1.2 iDigBio — Integrated Digitized Biocollections

- **URL:** [https://www.idigbio.org](https://www.idigbio.org) | API: [https://search.idigbio.org/v2/](https://search.idigbio.org/v2/)
- **What data they hold:** iDigBio is the NSF-funded US national aggregator of natural history specimen data from museums and universities. The portal aggregates millions of neontological and paleontological specimen records from US institutions, formatted according to Darwin Core and Audubon Core standards. Records include voucher specimens with associated locality data, collection dates, preparation type, and associated media (label images, specimen photographs). Strong coverage across all vertebrate groups, invertebrates, plants, and fungi.
- **Access method:** Fully open REST API (no authentication required for queries). R package `ridigbio` provides direct access, returning `data.frame` objects. The iDigBio portal at [https://portal.idigbio.org](https://portal.idigbio.org) uses the same API. Bulk download via API or portal CSV export. The API supports Darwin Core field filtering, full-text search, and faceted queries.
- **License / use restrictions:** Specimen records are provided open access; individual institutions retain their own license terms, but iDigBio encourages CC0 or CC-BY. Check per-dataset licenses before redistribution.
- **Data format and update cadence:** Darwin Core (DwC) and Audubon Core; JSON via API; CSV exports from portal. Updated as contributing institutions push new digitization batches — continuous but institution-dependent.
- **Specific value for WildlifeStats:** Voucher specimens provide verified, curator-quality location and morphological data for wildlife species. Critical for building baseline distribution maps before disease overlays. Media records (images, labels) add documentation value. Covers historical specimens dating back centuries — essential for detecting long-term range shifts relevant to disease emergence.
- **Known integration friction:** US-centric; European and global collections are better served by GBIF. Duplicate records with GBIF (iDigBio is a GBIF publisher). Some records lack georeferenced coordinates or have legacy taxonomy. Bulk downloads can be large; field normalization required.

---

### 1.3 OBIS — Ocean Biodiversity Information System

- **URL:** [https://obis.org](https://obis.org) | API: [https://api.obis.org](https://api.obis.org)
- **What data they hold:** OBIS is the IOC-UNESCO global repository for marine biodiversity data. It holds [over 100 million records](https://manual.obis.org/access.html) of marine organisms, including marine mammals (cetaceans, pinnipeds, sirenians), seabirds, marine turtles, sharks, rays, fish, and invertebrates. Records include occurrence observations, museum specimens, trawl surveys, acoustic detections, and tagging data. OBIS also includes eDNA and DNA-derived records. Relevant to One Health for marine zoonotic pathogens, harmful algal bloom impacts on wildlife, and marine mammal stranding events that may co-locate with disease vectors.
- **Access method:** Open REST API at `https://api.obis.org/`. R package `robis` for programmatic access. Full data exports available in GeoParquet or TSV format. The OBIS Mapper provides filtered CSV downloads with all 225 DwC fields plus OBIS QC pipeline fields. No account required for access or download.
- **License / use restrictions:** Per-dataset licenses; full export packages include a license manifest for underlying datasets. Users must cite datasets according to their individual licenses. Most datasets are CC0 or CC-BY.
- **Data format and update cadence:** Darwin Core (occurrence, event, eMoF extensions); GeoParquet and TSV for bulk exports; CSV via Mapper; Source DwC-Archive per dataset. OBIS QC pipeline adds 68 standardized fields to all records in full exports. Updated continuously as OBIS nodes push new data.
- **Specific value for WildlifeStats:** Essential for marine wildlife health, aquatic zoonoses, and coastal wildlife rehabilitation contexts. Marine mammals are sentinels of ocean health; their stranding data, disease records, and population trends intersect directly with the One Health mandate. OBIS data bridges freshwater-marine continuum for amphibians, migratory waterfowl, and sea turtles.
- **Known integration friction:** Marine-only scope; taxonomic authority is WoRMS (World Register of Marine Species) requiring AphiaID-based lookups rather than GBIF backbone. Some datasets are contributed at low spatial precision. Overlaps with GBIF for taxa published to both systems.

---

### 1.4 GBIF-mediated iNaturalist Open Dataset

- **URL:** [https://registry.opendata.aws/inaturalist-open-data/](https://registry.opendata.aws/inaturalist-open-data/) | [https://github.com/inaturalist/inaturalist-open-data](https://github.com/inaturalist/inaturalist-open-data)
- **What data they hold:** The iNaturalist Open Dataset is one of the [world's largest public datasets of photos of living organisms, containing over 70 million photos](https://github.com/inaturalist/inaturalist-open-data) tied to geo-referenced species observations. Covers all kingdoms; strong coverage for vertebrates, insects, plants, and fungi across all continents. All research-grade iNaturalist observations are also indexed in GBIF; this separate AWS dataset provides direct bulk access to photo metadata and observation CSV exports.
- **Access method:** AWS S3 public bucket (`s3://inaturalist-open-data/`) — no authentication required. Four tab-separated CSV files: `observations.csv.gz`, `observers.csv.gz`, `photos.csv.gz`, `taxa.csv.gz`. Snapshots regenerated monthly. REST API also available at `https://api.inaturalist.org/v1/` (max 10,000 records per parameterized call; suitable for targeted queries rather than bulk retrieval).
- **License / use restrictions:** Observation metadata is CC0. Individual photos carry varied Creative Commons licenses (CC0, CC-BY, CC-BY-NC, etc.) as set by each observer. License fields are included in the photo CSV. Non-commercial use restrictions apply to CC-BY-NC images.
- **Data format and update cadence:** Gzipped tab-separated CSV; JPEG images via S3. Monthly snapshot cadence for bulk data; API is real-time.
- **Specific value for WildlifeStats:** Citizen science observations at massive scale — directly relevant to rehabilitation intake verification (range confirmation), wildlife encounter reporting, and One Health trend detection (unusual sightings, mortality reports, disease symptoms captured in photos). Computer vision labels already applied to photos by iNaturalist's AI model can assist automated intake classification.
- **Known integration friction:** Substantial observer bias (urban areas, charismatic species, accessible habitats). Research-grade only represents ~30–40% of total observations; the remainder are "needs ID" quality. Photo licenses vary per image requiring per-record license checks before downstream reuse. Temporal resolution is high but spatial precision varies.

---

### 1.5 VertNet

- **URL:** [https://vertnet.org](https://vertnet.org)
- **What data they hold:** VertNet consolidates four legacy vertebrate specimen networks: MaNIS (Mammal Networked Information System — mammals), ORNIS (Ornithological Information System — birds), HerpNET (amphibians and reptiles), and FishNet 2 (fishes). Together, [these networks collectively mobilize over 80 million vertebrate records spanning a large number of institutions and museums](https://ropensci.org/blog/2014/03/17/spocc/), representing natural history collection specimens with georeferenced locality data, preparation types, and institutional provenance. VertNet serves as a cloud-based, Darwin Core–compliant data store with annotation and quality assessment infrastructure.
- **Access method:** Open REST API; R package `rvertnet` provides direct access. Cloud-hosted; no server installation required by users. Bulk download available. ORNIS note: [VertNet is now transitioning datasets from DiGIR to IPT](https://sites.google.com/site/ornisnet/home); all MaNIS, FishNet, HerpNET, and ORNIS datasets now use IPT-based publishing.
- **License / use restrictions:** CC0 or CC-BY per contributing institution. Darwin Core standard; attribution required per dataset.
- **Data format and update cadence:** Darwin Core; JSON via API; CSV bulk download. Contributor-mediated update cadence — updates published by institutions as data is improved.
- **Specific value for WildlifeStats:** Best single source for vertebrate specimen records with full natural history metadata — taxonomy, morphology, locality, sex, age, preparation type. Provides systematic coverage needed for rehabilitation species baselines, range verification, and historical comparison against modern disease data. Covers all four major vertebrate groups.
- **Known integration friction:** Substantial overlap with iDigBio and GBIF (VertNet is a GBIF publisher). Historical records often lack precise coordinates (require georeferencing). Networks originated in the early 2000s; some metadata fields are legacy and require normalization. MaNIS/HerpNET/ORNIS are now legacy names; data now flows through VertNet's IPT infrastructure.

---

### 1.6 Dryad Digital Repository

- **URL:** [https://datadryad.org](https://datadryad.org)
- **What data they hold:** Dryad is an open research data publisher hosting [over 65,000 data publications from over 300,000 researchers in connection with over 100,000 international institutions and over 2,000 academic journals](https://datadryad.org/stash/about). Content is primarily paper-supplement datasets from ecology, evolutionary biology, conservation biology, and related fields. Includes tabular data, genomic sequences, multimedia, code, and compressed archives. Ecology and wildlife datasets are among the most common content types, covering population ecology, disease ecology, species interactions, epidemiological data, and behavior studies.
- **Access method:** Open download — no account required to access or download published datasets. REST API available (v2). All datasets have DOIs. Dryad integrates with Zenodo for concurrent software and supplemental deposition, and with Frictionless Data for tabular quality validation.
- **License / use restrictions:** [All data files must be licensed under Creative Commons Zero (CC0)](https://datadryad.org/stash/faq) — public domain dedication. Software and supplemental files hosted via Zenodo may carry alternative open licenses. This makes Dryad one of the most permissive repositories for downstream integration.
- **Data format and update cadence:** Preferred formats: CSV, TSV, ODF for tabular data; XML/JSON for structured text; standard image, audio, and video formats. Individual file size limit 10 GB; 2 TB per publication. Datasets are published asynchronously as papers are accepted; no fixed cadence.
- **Specific value for WildlifeStats:** The richest source of paper-linked ecological datasets — disease ecology studies, population health assessments, pathogen prevalence surveys, and rehabilitation outcome studies all deposit supplemental data here. Query by keyword, species, or journal. Enables meta-analysis pipelines for wildlife disease and rehabilitation data.
- **Known integration friction:** No controlled vocabulary for disease or health topics — requires full-text search and manual curation to identify relevant datasets. Datasets are highly heterogeneous in structure, requiring per-dataset schema inspection. No versioning transparency (updates create new DOIs).

---

### 1.7 DataONE — Data Observation Network for Earth

- **URL:** [https://www.dataone.org](https://www.dataone.org) | Search: [https://search.dataone.org](https://search.dataone.org)
- **What data they hold:** DataONE is a federated network of distributed data repositories providing a single point of discovery for Earth observational and ecological data. Member repositories include the [Knowledge Network for Biocomplexity (KNB)](https://knb.ecoinformatics.org/) — 28,869 public datasets; the Arctic Data Center; ORNL DAAC (NASA Oak Ridge — ecology, biogeochemistry, remote sensing); Smithsonian Data Research Repository; TERN (Terrestrial Ecosystem Research Network, Australia); LTER-EU; and numerous others. Data types include ecological time series, biogeochemical measurements, species occurrence, land cover, and climate-linked datasets.
- **Access method:** [Single point of discovery via MetaCat interface at search.dataone.org](https://www.dataone.org/about/). R client (`dataone` package) for programmatic access. KNB individually accessible at `https://knb.ecoinformatics.org/`. ORNL DAAC provides OGC web services (WCS/WMS/WFS) via the [Spatial Data Access Tool (SDAT)](https://daac.ornl.gov/SERVICES/guides/SDAT.html) for spatial subsetting and reformatting. No authentication required for open datasets; some datasets are registration-gated.
- **License / use restrictions:** KNB uses CC0 and CC licenses. Individual member nodes set their own policies; ORNL DAAC data is generally open with attribution. License metadata included per dataset.
- **Data format and update cadence:** EML (Ecological Metadata Language) standard across all nodes; data in CSV, NetCDF, HDF5, GeoTIFF, and other formats depending on node and data type. Continuously updated as member nodes publish new datasets.
- **Specific value for WildlifeStats:** ORNL DAAC holds long-term ecological monitoring datasets directly relevant to species population dynamics, land cover changes affecting wildlife habitat, and climate-linked disease risk. KNB hosts many ecology and conservation datasets not found elsewhere. The federation model means a single DataONE query can surface datasets from dozens of specialized repositories simultaneously.
- **Known integration friction:** Federated architecture means data format and metadata quality vary widely across nodes. Metadata is in EML — requires EML parsing for automated ingestion. Some member nodes require registration. Search relevance for wildlife disease topics requires careful query construction.

---

### 1.8 USDA Ag Data Commons

- **URL:** [https://data.nal.usda.gov](https://data.nal.usda.gov)
- **What data they hold:** The Ag Data Commons is the USDA's FAIR-data catalog and repository for publicly funded agricultural and environmental research data. Content includes tabular data, genomic sequences, multimedia, databases, and associated software from USDA-funded projects. Wildlife-relevant content includes zoonotic disease ecology datasets (tick-borne diseases, avian influenza, CWD, brucellosis), livestock-wildlife interface studies, invasive species data, and habitat monitoring data produced by USDA APHIS, USFS, and ARS programs.
- **Access method:** Open download — no account required to access or download published data. Account required only for data submission. Search interface at [https://data.nal.usda.gov](https://data.nal.usda.gov). CKAN-based platform with API.
- **License / use restrictions:** US Federal government data in public domain (USG Open Data Policy). Many datasets carry public domain or CC-BY designations.
- **Data format and update cadence:** Tabular (CSV, XLSX), genomic sequences, multimedia. Published as papers or reports are completed; no fixed cadence.
- **Specific value for WildlifeStats:** Direct connection to federally funded zoonotic disease research at the livestock-wildlife interface — critical for One Health and disease surveillance components. CWD prion data, HPAI surveillance, brucellosis in bison/elk, and tick-borne pathogen ecology are all well-represented. APHIS National Wildlife Disease Program datasets are deposited here.
- **Known integration friction:** Discovery requires keyword search; no wildlife-specific taxonomy browse. Dataset quality and metadata completeness vary by submitting agency. Some APHIS datasets are access-controlled pending FOIA review.

---

### 1.9 IUCN Red List

- **URL:** [https://www.iucnredlist.org](https://www.iucnredlist.org) | API: [https://apiv3.iucnredlist.org/api/v3/docs](https://apiv3.iucnredlist.org/api/v3/docs)
- **What data they hold:** The IUCN Red List is the world's authoritative source for conservation status assessments of all described species. It provides for each assessed taxon: Red List category (EX, EW, CR, EN, VU, NT, LC, DD), population trend, geographic range, habitat associations, threats (coded by IUCN threat classification), conservation measures, narrative descriptions (range, population, ecology, threats), trade and use data, historical assessment series, synonyms, and links to spatial range polygons. Covers ~162,000+ assessed species as of 2025.
- **Access method:** Free API token obtainable by registering at [https://apiv3.iucnredlist.org](https://apiv3.iucnredlist.org). Token-authenticated REST API returning JSON. Endpoints for species list (10,000 records/page), species info, narrative fields, threats, habitats, conservation measures, synonyms, country occurrence, and historical assessments. Bulk spatial data (range polygons as shapefiles) downloadable from the website after free registration.
- **License / use restrictions:** Use governed by [IUCN Red List Terms of Use](https://apiv3.iucnredlist.org/api/v3/docs) — not open license (not CC). Data may be used for non-commercial research and conservation with attribution. Redistribution in compiled databases requires IUCN permission. The API is free but token-gated; bulk use must be declared.
- **Data format and update cadence:** JSON via API; SHP/geodatabase for spatial polygons. The Red List is updated 3–4 times per year with new assessments added in each version.
- **Specific value for WildlifeStats:** Core reference for every species in the rehabilitation database — threat context, population trend, conservation status, and geographic range. Threat codes directly map to disease, persecution, habitat loss, and trade drivers. Historical assessments enable trend tracking. Essential for triage prioritization: critically endangered species in rehabilitation warrant escalated reporting.
- **Known integration friction:** Not open-licensed — redistribution terms must be reviewed for WildlifeStats's public-facing outputs. API is v3 (legacy); v4 is in development. IDs can change between versions; use taxon names as primary keys. Spatial polygons are large files requiring GIS processing.

---

### 1.10 Biodiversity Heritage Library (BHL)

- **URL:** [https://www.biodiversitylibrary.org](https://www.biodiversitylibrary.org) | API: [https://www.biodiversitylibrary.org/docs/api3.html](https://www.biodiversitylibrary.org/docs/api3.html)
- **What data they hold:** BHL is the world's largest open-access digital library for biodiversity literature, providing access to [hundreds of thousands of volumes comprising over 60 million pages from the 15th–21st centuries](https://about.biodiversitylibrary.org/). Content spans taxonomic monographs, natural history journals, expedition reports, field guides, and early disease literature. BHL also provides [over 300,000 free nature images via Flickr](https://about.biodiversitylibrary.org/) and a Biodiversity Literature Repository (BLR) on Zenodo containing extracted data from publications.
- **Access method:** [Free API providing access to metadata, full-text search, item downloads, and occurrence data extracted from the literature](https://about.biodiversitylibrary.org/). Source data files available for harvesting. Creative Commons-licensed materials available for direct download. No account required for API queries.
- **License / use restrictions:** Public domain content freely usable. In-copyright materials are shared under Creative Commons licenses with rights holder permission. API use is free with attribution.
- **Data format and update cadence:** PDF pages, JPEG images, OCR full text, metadata XML/JSON. Continuously updated as partners digitize new material.
- **Specific value for WildlifeStats:** Historical disease and pathology literature predating modern databases — critical for understanding historical baselines of wildlife disease, pre-epizootic species descriptions, and taxonomic history. BHL-extracted occurrence data feeds the Biodiversity Literature Repository on Zenodo, providing millions of additional occurrence records. Useful for historical range data for species now in rehabilitation care.
- **Known integration friction:** OCR quality varies for older texts — full-text search is imprecise for older material. Occurrence extraction is automated and carries errors. Content is primarily text, not structured data — NLP pipeline required to extract health/disease mentions.

---

### 1.11 AnAge — Database of Animal Ageing and Longevity

- **URL:** [https://genomics.senescence.info/species/](https://genomics.senescence.info/species/)
- **What data they hold:** AnAge is a [curated database of ageing and life history in animals, including extensive longevity records](https://genomics.senescence.info/species/). Covers maximum lifespan, body mass, metabolic rate, reproductive parameters, and associated literature for thousands of animal species. Published in Science, Nature Reviews Genetics, and other high-impact journals. Designed for comparative biology but directly useful for zoos, field biologists, and conservation studies.
- **Access method:** Free download of zipped tab-delimited dataset (latest stable build). Web-based search and taxonomy browser. No account required.
- **License / use restrictions:** Freely available under [HAGR (Human Ageing Genomic Resources) license](https://genomics.senescence.info/species/) — open for research with attribution.
- **Data format and update cadence:** Tab-delimited flat file; CSV. Updated periodically with new build releases.
- **Specific value for WildlifeStats:** Longevity and life history data are essential for rehabilitation triage (age estimation, expected lifespan, reproductive status assessment) and for modeling population recovery rates post-disease event. Maximum lifespan and body mass data inform allometric dosing in wildlife medicine.
- **Known integration friction:** Contains raw data only, not individual observations. Some modeled values (not directly measured). Limited to species with published life history data — taxonomic coverage biased toward vertebrates and model organisms.

---

### 1.12 EltonTraits 1.0 — Species-Level Foraging Attributes

- **URL:** [https://figshare.com/collections/EltonTraits_1_0/3306933/1](https://figshare.com/collections/EltonTraits_1_0/3306933/1) (via Figshare)
- **What data they hold:** [EltonTraits 1.0 is a species-level dataset of foraging attributes for the world's birds and mammals](https://opentraits.org/datasets/elton-traits.html), compiled by Walter Jetz et al. (2014, Ecology). Includes diet composition (% vertebrates, invertebrates, plants, etc.), foraging stratum (ground, canopy, aerial, etc.), nocturnality, and body mass for ~10,000 bird species and ~5,400 mammal species.
- **Access method:** Direct download from Figshare — no account required. Files available at `https://figshare.com/ndownloader/files/5631081` (birds) and `5631084` (mammals). Also available via the `traitdata` R package.
- **License / use restrictions:** [CC-BY 4.0](https://opentraits.org/datasets/elton-traits.html) — attribution required.
- **Data format and update cadence:** CSV. Static release (v1.0, 2014); no scheduled updates but v2 is anticipated.
- **Specific value for WildlifeStats:** Diet and foraging trait data inform disease risk modeling (generalist foragers vs. specialists, dietary exposure pathways to toxins and pathogens). Nocturnality and foraging stratum data help parameterize vector exposure risk. Essential for One Health exposure modeling linking food web position to disease spillover probability.
- **Known integration friction:** Fixed 2014 release; taxonomic names may diverge from current authorities. Birds and mammals only — no reptiles, amphibians, or fish. Body mass values are medians; individual variation not captured.

---

### 1.13 PanTHERIA — Mammal Life History Database

- **URL:** [https://doi.org/10.6084/m9.figshare.c.3301274.v1](https://doi.org/10.6084/m9.figshare.c.3301274.v1) | ESA Ecological Archives: [https://esapubs.org/archive/ecol/E090/184/](https://esapubs.org/archive/ecol/E090/184/)
- **What data they hold:** PanTHERIA is a [species-level dataset compiled for analysis of life history, ecology, and geography of all known extant and recently extinct mammals](https://opentraits.org/datasets/pan-theria.html) (Jones et al. 2009, Ecology 90:2648). Covers ~5,416 mammal species with 80+ variables including body mass, litter size, gestation length, weaning age, longevity, home range, diet breadth, geographic range, climate space, human footprint overlap, and population density.
- **Access method:** Free download via Figshare and ESA Ecological Archives. Available via `traitdata` R package (`data("pantheria")`). No account required.
- **License / use restrictions:** [CC-BY](https://opentraits.org/datasets/pan-theria.html) — attribution required.
- **Data format and update cadence:** CSV / tab-delimited. Static 2009 release; widely used as the standard mammal trait reference.
- **Specific value for WildlifeStats:** Fundamental reference for mammal rehabilitation context — reproductive biology, body mass norms, range data, and ecological niche data for all wild mammal species. Many variables (litter size, weaning age, home range) are directly relevant to rehabilitation protocols and return-to-wild assessments.
- **Known integration friction:** 2009 data — some values modeled from literature averages, not directly measured. Some missing values for data-poor species. Taxonomic names use Wilson & Reeder 2005 — requires synonym mapping to current taxonomy.

---

### 1.14 PREDICTS — Projecting Responses of Ecological Diversity in Changing Terrestrial Systems

- **URL:** [https://data.nhm.ac.uk/dataset/release-of-data-added-to-the-predicts-database-november-2022](https://data.nhm.ac.uk/dataset/release-of-data-added-to-the-predicts-database-november-2022)
- **What data they hold:** PREDICTS is a Natural History Museum (London) global biodiversity database containing [1,040,752 records from local biodiversity surveys](https://data.nhm.ac.uk/dataset/release-of-data-added-to-the-predicts-database-november-2022) across terrestrial ecosystems worldwide. It compiles data from published papers on how local biodiversity responds to human pressures. Data are at the site and species level, including abundance, occurrence, and species richness metrics alongside land-use type (primary forest, secondary vegetation, cropland, pasture, urban). Two major releases: 2016 (CC BY-NC 4.0) and 2022 (CC-NC).
- **Access method:** Freely accessible via NHM Data Portal. R package `predictsr` provides direct access: `predicts <- GetPredictsData()` — [the NHM API has no rate limits](https://biodiversity-futures-lab.github.io/predictsr/). The package retrieves both 2016 and 2022 data as a data frame. Also available via CRAN (`install.packages("predictsr")`).
- **License / use restrictions:** Both releases licensed under [CC BY-NC](https://biodiversity-futures-lab.github.io/predictsr/) — non-commercial use only. Attribution required. Commercial applications require separate licensing from NHM.
- **Data format and update cadence:** Zipped CSV (database extract). Static releases; 2016 and 2022 versions available.
- **Specific value for WildlifeStats:** Quantitative data on how biodiversity responds to land-use change — directly relevant to modeling wildlife disease emergence as habitats degrade. PREDICTS data can identify which species lose/gain abundance under human land use pressure, informing rehabilitation hotspot predictions.
- **Known integration friction:** NC license restricts commercial use — must be verified for WildlifeStats's public-facing components. Data are site-level summaries, not individual specimen records. Human-footprint variables may require recoding for disease ecology applications.

---

### 1.15 Movebank — Animal Tracking Repository (Max Planck)

- **URL:** [https://www.movebank.org](https://www.movebank.org)
- **What data they hold:** Movebank is an online platform managed by the Max Planck Institute of Animal Behavior hosting the world's largest archive of animal movement data. As of March 2026, Movebank holds [10.4 billion animal locations, 8.6 billion other animal-borne sensor measurements, across 9,833 studies covering 1,643 taxa](https://www.movebank.org/cms/movebank-content/about-movebank). Data includes GPS, Argos, GLS, accelerometer, heart rate, temperature, and other bio-logging sensor data. The Movebank Data Repository provides DOI-citable published datasets. The Env-DATA System links tracking data to hundreds of environmental variables.
- **Access method:** Publicly shared studies are accessible via Movebank REST API, MoveApps platform, and direct download. Published studies in the Movebank Data Repository are fully open. R package `move` and Python tools interface with the API. Data can be converted to Darwin Core and published to GBIF/OBIS via `movepub`.
- **License / use restrictions:** Data owners retain ownership; [publicly shared data uses CC-BY](https://www.movebank.org/cms/movebank-content/about-movebank). The Movebank Data Repository requires CC licensing and DOI assignment. Some studies have owner-approval access (Tier 2 access).
- **Data format and update cadence:** Movebank proprietary format (CSV-based) and the standardized Movebank Vocabulary (`http://vocab.nerc.ac.uk/collection/MVB`); Darwin Core export available. Near real-time for live-feed studies.
- **Specific value for WildlifeStats:** Animal tracking data reveals migratory corridors, range use, and habitat selection — critical for modeling disease transmission routes, identifying wildlife-livestock interface zones, and informing release site selection for rehabilitated animals. Accelerometer data can detect behavioral anomalies associated with disease. Studies of HPAI-affected birds, CWD-affected deer, and disease-vector species are directly searchable.
- **Known integration friction:** Many studies require owner approval even if data are nominally public. Study-level rather than species-level organization requires cross-study aggregation. Very large datasets require efficient parallelized download strategies. License varies per study; automated license checking needed.

---

## Tier 2: Account-Gated but Free

These repositories require registration or a free API token but impose no financial cost. Access can be set up within hours.

---

### 2.1 IUCN Red List API (Registration)

See Section 1.9 above — the IUCN API is free but requires an account registration to obtain a token. Included here as a reminder that the account step must be completed before automated ingestion.

---

### 2.2 WHISPers — Wildlife Health Information Sharing Partnership Event Reporting System (USGS NWHC)

- **URL:** [https://whispers.usgs.gov](https://whispers.usgs.gov) | [https://www.usgs.gov/tools/wildlife-health-information-sharing-partnership-event-reporting-system-whispers](https://www.usgs.gov/tools/wildlife-health-information-sharing-partnership-event-reporting-system-whispers)
- **What data they hold:** WHISPers is the [USGS NWHC's partner-driven, web-based repository for sharing basic information about historic and ongoing wildlife mortality (death) and/or morbidity (illness) events](https://www.usgs.gov/tools/wildlife-health-information-sharing-partnership-event-reporting-system-whispers). The USGS NWHC Data Portal associated with WHISPers holds 127+ scientific datasets including: diagnostic case-level data (carcass and tissue submissions, test results, cause of death) from January 2000 to present; specific disease studies covering white-nose syndrome, CWD prions, snake fungal disease, chytrid fungus, tick microbiome/mycobiome, SARS-CoV-2/Mpox spillback risk, and coral disease. WHISPers event data is licensed under [USG public domain](https://data.usgs.gov/datacatalog/data/USGS:581deaed-18e7-45b1-8935-1ea7342ba7e5).
- **Access method:** Event data accessible at [https://whispers.usgs.gov](https://whispers.usgs.gov) — public access; no account required for browsing. API access for structured download requires contacting whispers@usgs.gov. USGS NWHC scientific datasets available at [https://www.usgs.gov/centers/nwhc/data](https://www.usgs.gov/centers/nwhc/data). Some datasets deposited in USGS ScienceBase.
- **License / use restrictions:** US Federal public domain — fully open, no restrictions.
- **Data format and update cadence:** CSV, chromatogram files, Excel, qPCR result tables. Event reporting is ongoing; datasets published as studies conclude.
- **Specific value for WildlifeStats:** The most directly relevant US wildlife disease surveillance repository. Mortality and morbidity events across all taxa, with diagnostic confirmation, provide the gold-standard ground truth for disease surveillance. CWD, white-nose syndrome, HPAI, snake fungal disease, and emerging zoonoses all represented. Direct pipeline from USGS NWHC diagnostic laboratory to the WildlifeStats disease surveillance module.
- **Known integration friction:** WHISPers API access requires direct USGS contact; no self-service bulk download. Event data schema is event-centric (not specimen-centric) requiring transformation. Scientific datasets are heterogeneous — each requires individual schema review. Coverage biased toward federally studied diseases.

---

### 2.3 Wildlife Insights — Camera Trap Data Platform

- **URL:** [https://www.wildlifeinsights.org](https://www.wildlifeinsights.org)
- **What data they hold:** Wildlife Insights is a Google-backed, WWF, WCS, NPS, and Smithsonian-partnered platform hosting [millions of camera trap photos and associated species identification data from protected areas and wildlife monitoring projects worldwide](https://www.wildlifeinsights.org/about). Photos are annotated by a deep learning model (Google Vision AI) trained on wildlife species. Data includes project metadata, deployment information (camera location, terrain, season), individual image metadata, and AI-generated or human-validated species identifications. Data from projects around the world is accumulated continuously.
- **Access method:** Free account registration at [https://app.wildlifeinsights.org/join](https://app.wildlifeinsights.org/join) + account approval form. Data upload, explore, and download tools available after approval. Bulk data download available for publicly shared projects.
- **License / use restrictions:** License varies by data contributor project settings. Platform terms require attribution. AI-labeled data may have uncertainty scores requiring threshold filtering.
- **Data format and update cadence:** JSON metadata; JPEG images; CSV species identification exports. Continuously growing — new data uploaded daily.
- **Specific value for WildlifeStats:** Camera trap data provides presence/absence, relative abundance indices, and behavior documentation for wildlife across protected areas. Species detection frequencies can serve as population health proxies. AI-labeled images enable rapid species occurrence mapping. Particularly valuable for nocturnal and cryptic species rarely captured in rehabilitation data.
- **Known integration friction:** Account approval adds a delay step. Image data is large-scale (storage-intensive). AI classification confidence varies by species and habitat; validation pipeline required. Data sharing is project-owner dependent — not all data is publicly accessible.

---

### 2.4 Macaulay Library — Cornell Lab of Ornithology

- **URL:** [https://www.macaulaylibrary.org](https://www.macaulaylibrary.org)
- **What data they hold:** The [Macaulay Library is the world's premier scientific archive of natural history audio, video, and photographs](https://www.macaulaylibrary.org/about/), with holdings spanning birds, amphibians, fishes, and mammals. The collection preserves recordings of each species' behavior and natural history. Contains tens of millions of media records, primarily contributed via eBird/Macaulay Library upload tool. Accessible through the eBird API.
- **Access method:** Web browser access is open; research, educational, and commercial access available for audio and video recordings. eBird API (free account required) provides programmatic access to associated observation and media metadata.
- **License / use restrictions:** Individual media licenses vary by contributor; many are CC-BY or CC-BY-NC. Commercial use requires separate licensing inquiry. Audio and video for research use freely accessible.
- **Data format and update cadence:** JPEG (images), MP3/WAV (audio), MP4 (video). Continuously updated via citizen science contributions and formal expedition deposits.
- **Specific value for WildlifeStats:** Behavioral audio-visual documentation supports species identification training for rehabilitation staff, behavioral health baselines for captive wildlife, and vocalization-based population monitoring. Sick or injured animals may display abnormal vocalizations documentable in this archive. Amphibian and mammal sound archives support non-bird wildlife rehabilitation programs.
- **Known integration friction:** Media-heavy database — storage and processing demands are high. API is primarily designed for eBird occurrence data, not media retrieval at scale. Per-media license checking required before any redistribution.

---

### 2.5 Encyclopedia of Life (EOL)

- **URL:** [https://eol.org](https://eol.org)
- **What data they hold:** EOL aggregates biodiversity knowledge from partner institutions including BHL, BOLD, Catalogue of Life, and GBIF into species-level pages. Content includes [text descriptions, photos, range maps, taxonomic data, ecological information, conservation status, behavioral data, and trait databases](https://eol.org/docs/what-is-eol). EOL v3 (launched 2018) uses a knowledge graph structure linking organisms to traits, environments, and interactions. TraitBank within EOL holds millions of trait records across taxa.
- **Access method:** Open web access; data services in commonly used formats; TraitBank CSV download. An API is available for programmatic access to species pages. Freely accessible; account required for content contributions.
- **License / use restrictions:** Provider-dependent; EOL works with rights holders for CC licensing. TraitBank data is CC0.
- **Data format and update cadence:** JSON/XML via API; CSV for TraitBank. Updated as partner organizations push new content.
- **Specific value for WildlifeStats:** Rich species reference pages combining taxonomy, ecology, distribution, and conservation data — useful for building species profile pages in WildlifeStats. TraitBank provides structured trait data (diet, habitat, body size) usable for triage and care protocol lookups.
- **Known integration friction:** Data quality varies by taxon and provider — some pages are student-written without expert review. API has rate limits; bulk data best obtained via periodic TraitBank CSV export. Some data is from aggregated sources and may duplicate records from GBIF and BHL.

---

### 2.6 WAHIS / WAHIS-Wild — WOAH World Animal Health Information System

- **URL:** [https://wahis.woah.org](https://wahis.woah.org)
- **What data they hold:** WAHIS is the [global animal health reference database of WOAH (World Organisation for Animal Health), holding validated animal health information from 2005 onwards](https://wahis.woah.org/) reported by Veterinary Services from Member and non-Member Countries on terrestrial and aquatic Listed diseases in domestic animals and wildlife, as well as emerging diseases and zoonoses. WAHIS-Wild specifically covers non-listed wildlife diseases reported voluntarily. Archive of weekly animal health reports from 1992–2006 also available. Covers 50+ wildlife diseases.
- **Access method:** Public dashboard accessible without account; interactive mapping tools and dashboards for data consultation and extraction. Authorized users (WOAH delegates) access a separate restricted space for reporting. [WAHIS portal provides access to real-time alert notices and historical data from 2005 onwards](https://www.woah.org/en/what-we-do/animal-health-and-welfare/disease-data-collection/world-animal-health-information-system/).
- **License / use restrictions:** WOAH data available for research and public health purposes with attribution to WOAH. Specific terms on WOAH website.
- **Data format and update cadence:** Web dashboards; download tools via portal interface. Real-time alert system for emerging disease events; six-monthly updates for monitoring data; annual reports.
- **Specific value for WildlifeStats:** Global disease outbreak intelligence at the wildlife-livestock interface — real-time alerts for WOAH-listed diseases (HPAI, FMD, rabies, anthrax, brucellosis) relevant to wildlife rehabilitation biosafety and One Health surveillance. Historical outbreak data enables retrospective analysis of geographic and temporal disease patterns.
- **Known integration friction:** Not a structured API-first platform — bulk data extraction requires dashboard interaction rather than programmatic access. WAHIS-Wild data is voluntary and may have reporting gaps. Primarily covers domestic animal diseases with wildlife as secondary; wildlife-specific data requires WAHIS-Wild Beta interface.

---

### 2.7 NEON — National Ecological Observatory Network

- **URL:** [https://www.neonscience.org/data](https://www.neonscience.org/data) | Portal: [https://data.neonscience.org](https://data.neonscience.org)
- **What data they hold:** NEON is a [continental-scale ecological observation facility operated by Battelle under NSF funding](https://www.nsf.gov/focus-areas/infrastructure/national-ecological-observatory-network), providing free and open data on the drivers of and responses to ecological change across 81 sites in the US. Wildlife-relevant data products include: small mammal trapping (species, abundance, body condition, ectoparasite loads), bird point count surveys, aquatic macroinvertebrate sampling, plant phenology, tick and pathogen surveillance, mosquito and pathogen surveillance (WNV, WEE, EEE in mosquito pools), soil microbiome, and climate/hydrology variables.
- **Access method:** All data are free and publicly available through the NEON Data Portal. R package `neonUtilities` enables programmatic download; API available at `data.neonscience.org`. No account required.
- **License / use restrictions:** All data CC0 (public domain). NEON data are free for any use without restriction.
- **Data format and update cadence:** CSV; HDF5 for some sensor data; standardized data product formats with QC flags documented per product. Standardized sampling protocols; seasonal and annual updates depending on data product.
- **Specific value for WildlifeStats:** Unique value for disease vector surveillance — NEON's tick and mosquito monitoring data with pathogen testing (Lyme, WNV, etc.) provides standardized, multi-year, continental-scale vector data directly feeding the disease vector component of WildlifeStats. Small mammal trapping provides host population data with ectoparasite loads — the host-vector-pathogen trifecta for Lyme and hantavirus modeling. Standardized sampling makes cross-site comparisons reliable.
- **Known integration friction:** 81 fixed sites — not comprehensive geographic coverage; sites selected to represent major US ecoregions but many areas are uncovered. Data latency: field data typically released 60–180 days after collection. HDF5 format for some continuous sensor data requires specialized parsing. Data product documentation is extensive but complex for new users.

---

## Tier 3: Researcher Application Required

These repositories require a formal application, institutional affiliation, or data use agreement before access is granted.

---

### 3.1 ESA Ecological Archives / Ecological Data Registry

- **URL:** [https://esapubs.org/archive/](https://esapubs.org/archive/) | [https://esa.org/publications/data-policy/](https://esa.org/publications/data-policy/)
- **What data they hold:** Ecological Archives is the ESA's supplemental data repository for the ESA journal family (Ecology, Ecological Applications, Ecological Monographs, Ecosphere, Ecosystem Health and Sustainability). It publishes appendices, supplements, and peer-reviewed data papers. Archives through end of 2015 are being transitioned to Figshare; newer content uses Wiley Online, Figshare, and Dryad. Data include long-term ecological datasets, species traits, food webs, population dynamics, and disease ecology studies.
- **Access method:** Open access via [https://esapubs.org/archive/](https://esapubs.org/archive/). Data upload is restricted to registered journal authors; download is open. ESA data policy requires authors to [deposit data in Dryad, Figshare, or other approved repositories](https://esa.org/publications/data-policy/) at time of publication.
- **License / use restrictions:** CC licenses applied; [re3data lists CC as the database license](https://www.re3data.org/repository/r3d100010064). Specific dataset terms depend on the submitting author.
- **Data format and update cadence:** Mixed formats — CSV, R data files, SAS files, GIS layers, images — per individual archive entry. Updated as papers are published.
- **Specific value for WildlifeStats:** ESA journals are the primary publication venue for wildlife ecology, population dynamics, disease ecology, and habitat studies in North America. Ecological Archives (now transitioning to Dryad/Figshare) holds the supplemental datasets from decades of these papers — including many foundational wildlife disease ecology datasets not available elsewhere.
- **Known integration friction:** Archive platform is in transition (pre-2016 content on legacy system; newer content dispersed across Figshare/Dryad/Wiley). No unified API — requires journal-by-journal search or Figshare community search. Data heterogeneity is high.

---

### 3.2 Dryad (Researcher Application for Submission Only)

Note: Dryad is already listed in Tier 1 for data access. Submission requires institutional or journal partnership, but all published data is freely downloadable by anyone.

---

### 3.3 bioRxiv / EcoEvoRxiv — Preprint Servers

- **URLs:** [https://www.biorxiv.org](https://www.biorxiv.org) | [https://ecoevorxiv.org](https://ecoevorxiv.org)
- **What data they hold:** bioRxiv (Cold Spring Harbor Laboratory) is the leading biology preprint server covering ecology, evolutionary biology, epidemiology, microbiology, and related fields. [EcoEvoRxiv](https://sortee.org/blog/2019/01/14/2019_ecoevorxiv_launched/) is a community-driven preprint server for ecologists and evolutionary biologists integrated with the Open Science Framework (OSF), focused on the ecology/evolution community and the Transparency in Ecology and Evolution (TEE) movement. Both host preprints before peer review, including papers with associated data deposited in linked repositories. EcoEvoRxiv hosts papers on topics directly relevant to WildlifeStats including avian influenza modeling, telemetry, and wildlife behavior.
- **Access method:** Fully open — no account required to read or download preprints. bioRxiv API available at `https://api.biorxiv.org/` for metadata and content retrieval. EcoEvoRxiv accessible via OSF API.
- **License / use restrictions:** Most preprints CC-BY or CC0. Individual licenses set by authors. Preprints are not peer-reviewed — quality control required before treating as authoritative.
- **Data format and update cadence:** PDF full text; metadata JSON via API. Posted as submitted; no fixed cadence.
- **Specific value for WildlifeStats:** Early access to wildlife disease, rehabilitation, and ecology research 6–18 months before journal publication. Monitoring bioRxiv/EcoEvoRxiv provides horizon-scanning capability — identify emerging disease threats (new pathogens, new geographic ranges) from preprints before formal peer-reviewed confirmation. Also captures linked datasets posted to Dryad/Zenodo/OSF before paper publication.
- **Known integration friction:** Preprints are not peer-reviewed — findings may be revised or retracted. Version management (preprint vs. published) requires tracking. API coverage is complete for metadata but full-text parsing requires PDF processing. Some authors do not post preprints even when permitted.

---

### 3.4 University Library Data Repositories

Several major research universities with strong wildlife and veterinary programs host institutional data repositories relevant to WildlifeStats:

- **Cornell eCommons** ([https://ecommons.cornell.edu](https://ecommons.cornell.edu)): Cornell University Library's [open-access digital repository](https://www.re3data.org/repository/r3d100012322) for Cornell-related research content, including datasets from Cornell Lab of Ornithology, College of Veterinary Medicine, and wildlife ecology programs. Accepts educational and research content; deposit restricted to Cornell community but download is open. CC and varied licenses.

- **University of Minnesota Data Repository (DRUM)** ([https://conservancy.umn.edu/](https://conservancy.umn.edu/)): University of Minnesota's institutional repository, hosting data from the College of Veterinary Medicine, wildlife ecology, and conservation biology programs. Open download; deposit requires institutional affiliation. CC licenses.

- **UC Santa Barbara (NCEAS)** — The National Center for Ecological Analysis and Synthesis hosts data products from synthesis projects at [https://www.nceas.ucsb.edu/](https://www.nceas.ucsb.edu/) and the KNB repository. Many wildlife disease and ecological synthesis datasets available.

- **Zenodo (CERN/OpenAIRE)** ([https://zenodo.org](https://zenodo.org)): Not university-specific but serves as the generalist repository for EU-funded research and many ecology groups worldwide. Open upload and download; CC0/CC-BY encouraged. Zenodo's Biodiversity Literature Repository community hosts data extracted from biodiversity publications. The ecology community at Zenodo contains thousands of relevant datasets.

- **Figshare for Institutions** ([https://figshare.com](https://figshare.com)): Hosts ESA Ecological Archives legacy data, journal supplemental data, and institutional repositories for many US universities. Open download for most content; CC-BY or CC0.

**Integration value:** University repositories fill the gap for datasets tied to specific research programs (e.g., wildlife rehabilitation outcomes, clinical pathology data from veterinary teaching hospitals) that are not deposited in subject-specific repositories. Key search pattern: search by university + "wildlife" + "dataset" in Zenodo, Figshare, and institutional repository portals. Cornell, UC Davis, UF, and UMN are particularly productive for wildlife health data.

---

### 3.5 PLOS Data Policy — Journal-Mandated Sharing

- **URL:** [https://journals.plos.org/plosone/s/data-availability](https://journals.plos.org/plosone/s/data-availability)
- **What data they hold:** PLOS journals (PLOS ONE, PLOS Biology, PLOS Pathogens, PLOS Neglected Tropical Diseases) require all authors to [make underlying data fully available without restriction at time of publication](https://pmc.ncbi.nlm.nih.gov/articles/PMC3934816/), subject to ethical constraints. Data is deposited in Dryad, Figshare, Zenodo, GenBank, or as Supporting Information. PLOS Pathogens and PLOS NTDs are particularly relevant for wildlife zoonoses.
- **Access method:** Data accessed through linked repository (Dryad, etc.) or Supporting Information attached to published articles. Fully open — no account required.
- **License / use restrictions:** PLOS policy recommends CC-BY or less restrictive licenses for data; licenses not more restrictive than CC-BY required for repository deposits.
- **Specific value for WildlifeStats:** Any PLOS paper on wildlife disease, host-pathogen dynamics, or conservation biology published since 2014 has linked data. PLOS ONE alone publishes hundreds of wildlife ecology papers annually. Systematic monitoring of new PLOS publications can feed a continuous pipeline of new datasets into WildlifeStats.
- **Known integration friction:** Data is distributed across multiple repositories — requires following DOI links per paper. No unified API for "all PLOS wildlife data." Data Availability Statements vary in completeness; "data available on request" statements still appear in older papers.

---

### 3.6 Wildlife Society Bulletin — Open Access with CC-BY

- **URL:** [https://wildlife.org/wildlife-society-bulletin/](https://wildlife.org/wildlife-society-bulletin/)
- **What data they hold:** The Wildlife Society Bulletin is the [Wildlife Society's open access journal for wildlife practitioners](https://wildlife.org/wildlife-society-bulletin/), publishing peer-reviewed research on management and conservation strategies with management and conservation applications. All articles are published under [CC-BY Creative Commons License](https://wildlife.org/wp-content/uploads/2025/12/TWS_Journal_Submission-Guidelines_Oct2023.pdf). Supporting Information (spreadsheets of raw data, code, in-depth tables) is included with manuscripts. Directly focused on practical wildlife management, rehabilitation, and disease management outcomes in the US.
- **Access method:** Fully open access — no subscription required. Articles and supporting data downloadable without account. Published via Wiley.
- **License / use restrictions:** CC-BY — all content freely reusable with attribution.
- **Specific value for WildlifeStats:** The most practitioner-relevant journal for rehabilitation, management, and disease data. Published studies on population health, disease prevalence, rehabilitation outcomes, and management interventions are directly applicable to WildlifeStats's operational database.
- **Known integration friction:** Supporting information files lack a standardized format — CSV, Excel, PDF mixed. No data-specific API; metadata extraction requires web scraping or Wiley API access.

---

## Tier 4: Institutional Partnership Only

These repositories require formal institutional membership, MOUs, or researcher application with institutional backing.

---

### 4.1 ZIMS / Species360

- **URL:** [https://species360.org](https://species360.org) | Insights: [https://species360.org/species360-insights/](https://species360.org/species360-insights/)
- **What data they hold:** ZIMS (Zoological Information Management System) is [the world's leading zoological recordkeeping system](https://species360.org/zims/), used by zoos, aquariums, and wildlife facilities in 100+ countries. ZIMS holds lifetime medical and husbandry records for animals in human care: biological information, parentage, transfers, breeding history, population data, veterinary records (ZIMS for Medical — diagnoses, procedures, pathology, anesthesia protocols, blood reference intervals), and studbook data. As of current data, ZIMS covers [over 13 million individual animals](https://species360.org/species360-insights/). [Species360 Insights provides subscription-based access to aggregated global wildlife data](https://species360.org/species360-insights/) including current holdings, IUCN status summaries, birth/death records, and diagnostic reference intervals.
- **Access method:** ZIMS is a member-only platform — access requires institutional membership in Species360 (annual fee based on institution size). LearnZIMS provides educational licensing for universities. Species360 Insights offers subscription-based research access to aggregated data. The Conservation Science Alliance enables collaborative research projects.
- **License / use restrictions:** Institutional data is proprietary to contributing member institutions. Aggregated Insights data available under Species360 research data use agreements. Custom data sharing agreements required for research access.
- **Data format and update cadence:** Web-based platform; data exportable in CSV/Excel for members. Daily updates as member institutions enter data.
- **Specific value for WildlifeStats:** The most complete database of wildlife in human care worldwide — longevity records, disease history, reproductive outcomes, anesthesia protocols, and blood reference intervals for virtually every managed wildlife species. ZIMS for Medical data is the gold standard for wildlife clinical reference data. Directly relevant to rehabilitation medicine protocols, species longevity benchmarks, and outcomes research. Partnership with Species360 would provide WildlifeStats with an unmatched clinical reference layer.
- **Known integration friction:** Requires formal institutional membership and fee payment. Data is not openly licensed — MOU required for research access to aggregated data. Privacy of individual animal records is protected; only aggregate statistics are accessible externally. Integration requires Species360 API access negotiation.

---

### 4.2 WildHealthNet — WCS One Health Wildlife Health Surveillance

- **URL:** [https://oneworldonehealth.wcs.org/Initiatives/WildHealthNet.aspx](https://oneworldonehealth.wcs.org/Initiatives/WildHealthNet.aspx)
- **What data they hold:** WildHealthNet is a [Wildlife Conservation Society One Health initiative to develop national wildlife health surveillance systems](https://oneworldonehealth.wcs.org/Initiatives/WildHealthNet.aspx). It connects rangers, hunters, and animal rescue centers with scientists and decision-makers to detect and share information about wildlife health and mortality events globally. Focus on early warning for disease threats at wildlife-livestock-human interfaces. Currently operational in select countries; data is shared among network participants.
- **Access method:** Partner-based network — access requires formal partnership with WCS One Health program. Not a public database; data shared among wildlife health surveillance system participants.
- **License / use restrictions:** Network-level data sharing agreement required. WCS retains coordination role.
- **Specific value for WildlifeStats:** Direct alignment with the One Health and disease surveillance mission. WildHealthNet's event-based reporting model (mortality events, unusual presentations) could feed real-time disease alerts into WildlifeStats. Partnership would enable bidirectional data flows — rehabilitation intake data could inform WildHealthNet alerts.
- **Known integration friction:** Requires formal WCS partnership. Network is developing — geographic coverage is incomplete. Data schema may not be fully standardized across participating countries. Engagement requires project-level MOU.

---

### 4.3 USGS National Wildlife Disease Database (NWDD)

- **URL:** [https://www.usgs.gov/centers/nwhc/science/national-wildlife-disease-database-partner-us-protect-wildlife-agriculture-pet](https://www.usgs.gov/centers/nwhc/science/national-wildlife-disease-database-partner-us-protect-wildlife-agriculture-pet)
- **What data they hold:** The NWDD applies [advanced analytics to integrated data from government agencies, wildlife rehabilitators, and open sources](https://www.usgs.gov/centers/nwhc/science/national-wildlife-disease-database-partner-us-protect-wildlife-agriculture-pet) to identify unusual disease events, assess impacts, and map disease occurrences nationwide. It integrates WHISPers event data with USDA, APHIS, state wildlife agency, and partner-submitted data into a unified surveillance platform. Explicitly designed to serve "natural resource managers, agricultural communities, veterinary professionals, and human health practitioners."
- **Access method:** Partner-driven; USGS actively invites partners (including wildlife rehabilitators) to contribute data. Access to integrated analytical outputs requires partnership agreement. WHISPers component has public access (see Tier 2).
- **License / use restrictions:** Partnership agreement required; USG public domain for federal data components.
- **Specific value for WildlifeStats:** NWDD explicitly targets the same stakeholders as WildlifeStats and accepts wildlife rehabilitator data. A formal partnership would: (1) give WildlifeStats access to multi-agency integrated disease surveillance, and (2) position WildlifeStats as a contributing partner, strengthening both databases. This is the highest-priority Tier 4 relationship to establish.
- **Known integration friction:** Requires USGS partnership application. Data integration standards need alignment. Federal data governance requirements apply to contributed data.

---

### 4.4 PREDICTS (Note on License)

Already described in Tier 1 (Section 1.14). The CC-NC license means commercial applications require a separate institutional agreement with the Natural History Museum London. Non-commercial research access is open.

---

## Additional Notable Sources

### A. Zenodo Ecology Community and Biodiversity Literature Repository

- **URL:** [https://zenodo.org/communities/ecology/](https://zenodo.org/communities/ecology/) | BLR: [https://zenodo.org/communities/biosyslit/](https://zenodo.org/communities/biosyslit/)
- Zenodo is CERN/OpenAIRE's generalist open repository. The ecology community and BLR collectively host thousands of wildlife ecology and disease datasets, NLP-extracted biodiversity records from literature, and supplemental files from EU-funded research. All CC0/CC-BY. Fully open REST API. Essential companion to Dryad for discovering ecology datasets not linked to specific journals.

### B. Nature Scientific Data

- **URL:** [https://www.nature.com/sdata/](https://www.nature.com/sdata/)
- Nature's data descriptor journal requires all described datasets to be deposited in community-recognized open repositories. Wildlife-relevant datasets described in Scientific Data span genomics, ecology, movement tracking, and disease surveillance. Articles are open access; linked data is in Figshare, Zenodo, Dryad, or GBIF. Systematic monitoring of new Scientific Data publications provides a continuous pipeline of curated, described datasets.

### C. Animal Diversity Web (ADW)

- **URL:** [https://animaldiversity.org](https://animaldiversity.org)
- ADW is a [large searchable encyclopedia of animal natural history, distribution, classification, and conservation biology](https://animaldiversity.org/about/) hosted by the University of Michigan Museum of Zoology. Species accounts are authored by students and reviewed by instructors. Contains skull imagery, QT VR movies, and sound recordings. Less authoritative than PanTHERIA or IUCN for quantitative trait data but useful for narrative species profiles and educational content in WildlifeStats's public-facing portal.

### D. BioProject / NCBI GenBank (INSDC)

- **URL:** [https://www.ncbi.nlm.nih.gov/bioproject/](https://www.ncbi.nlm.nih.gov/bioproject/)
- GenBank/INSDC holds all publicly submitted nucleotide sequences, including wildlife pathogen sequences (HPAI H5N1, WNS fungus, CWD prion gene sequences). BioProject organizes related genomic datasets. For wildlife disease genomics, GenBank is the primary archive. Open API; CC0.

---

## Recommended Ingestion Priority Order

Ranked by combined value for WildlifeStats (wildlife medicine, disease surveillance, One Health, rehabilitation, species patterns) × accessibility (open API or bulk download available immediately).

| Rank | Source | Primary Value | Tier | Key Data Type |
|------|--------|--------------|------|---------------|
| 1 | **GBIF** | Global species occurrence backbone — vector/host distribution, population trends | 1 | Occurrence records (3.1B+) |
| 2 | **WHISPers / USGS NWHC** | Wildlife disease events, diagnostic data, mortality surveillance | 2 | Disease events, pathology cases |
| 3 | **IUCN Red List** | Conservation status, threats, range maps for every wildlife species | 2 (token) | Status + threats per taxon |
| 4 | **Movebank** | Animal tracking, movement corridors, disease transmission routes | 2 (owner approval) | GPS/bio-logger time series |
| 5 | **WAHIS / WAHIS-Wild** | Global livestock-wildlife disease alerts, historical outbreak intelligence | 2 | Disease event notifications |
| 6 | **NEON** | Standardized tick/mosquito vector + pathogen surveillance; small mammal host data | 2 | Vector-host-pathogen datasets |
| 7 | **iNaturalist Open Dataset** | Citizen science occurrence + media at massive scale | 1 | Observations + photos |
| 8 | **Dryad** | Paper-linked ecological datasets — disease ecology, rehabilitation outcomes | 1 | Mixed research datasets |
| 9 | **iDigBio** | US museum specimen data — species baselines, historical distribution | 1 | Specimens (Darwin Core) |
| 10 | **OBIS** | Marine wildlife (mammals, turtles, seabirds), aquatic zoonoses | 1 | Marine occurrence (100M+) |
| 11 | **DataONE / KNB / ORNL DAAC** | Long-term ecological monitoring, synthesis datasets | 1 | Time-series ecology data |
| 12 | **USDA Ag Data Commons** | Livestock-wildlife interface zoonoses, USDA disease research datasets | 1 | USDA research datasets |
| 13 | **PanTHERIA + EltonTraits + AnAge** | Mammal/bird life history and trait references for all rehab species | 1 | Trait/life history tables |
| 14 | **VertNet (MaNIS/HerpNET/ORNIS)** | Vertebrate specimen records, all four major wildlife groups | 1 | Specimens (Darwin Core) |
| 15 | **Wildlife Insights** | Camera trap AI-species identifications, population presence/absence | 2 | Camera trap + species IDs |

**Immediate next steps for WildlifeStats ingestion:**
1. Register GBIF account and configure async download pipeline (DwC-A → normalization → WildlifeStats species layer)
2. Contact whispers@usgs.gov for WHISPers API access and NWDD partnership inquiry
3. Request IUCN API token and configure species status lookup service
4. Deploy `rgbif`, `ridigbio`, `robis`, `rvertnet`, and `neonUtilities` R packages in ETL pipeline
5. Configure Dryad metadata harvester (keyword: "wildlife disease", "rehabilitation", "One Health")
6. Initiate Species360 partnership discussion for ZIMS clinical reference data (Tier 4 highest priority)
7. Formalize USGS NWDD partnership to position WildlifeStats as a contributing rehabilitation data node

---

*Report prepared for WildlifeStats national research framework. Sources cited throughout; all URLs verified at time of research. Data access terms and record counts subject to change; verify directly with each repository before production ingestion.*
