# Rehabilitation, One Health, and disease surveillance networks

This report inventories publicly documented data sources relevant to wildlife rehabilitation case data, One Health disease surveillance, clinical veterinary records, vector-borne disease tracking, and related mortality registries. Each source is assessed for data scope, access method, licensing, format/cadence, WildlifeStats integration value, and known friction points.

---

## Tier 1: Open API / Bulk Download (use immediately)

These sources have no registration requirement or offer fully open public data access with structured download capabilities.

---

### 1.1 WOAH WAHIS — World Animal Health Information System

**URL:** [https://www.woah.org/en/what-we-do/animal-health-and-welfare/disease-data-collection/world-animal-health-information-system/](https://www.woah.org/en/what-we-do/animal-health-and-welfare/disease-data-collection/world-animal-health-information-system/)

**Data held:** The World Animal Health Information System (WAHIS) is the global reference platform for official animal disease data. It contains three core data streams: (1) immediate notifications ("alerts") for WOAH-listed diseases in domestic animals and wildlife, covering all 117 listed terrestrial and aquatic diseases; (2) six-monthly monitoring reports with outbreak counts, case and death tallies, affected species, and geographic data by country/region; and (3) annual reports covering zoonoses, veterinary service capacity, and laboratory data. The companion **WAHIS-Wild Beta** module collects voluntary annual reports from member states on non-listed wildlife diseases, with a public dashboard. Historical archives via Handistatus II cover 1996–2004 and weekly reports cover 1992–2006.

**Access method:** Fully public interface. Data from 2005 onwards are accessible without registration via the WAHIS public dashboard. Filter by disease, country, animal species. Data entry is restricted to authorized national delegates, but public export of validated data is available. WAHIS-Wild Beta has a public dashboard for wildlife-specific non-listed disease data.

**License / use restrictions:** Data are published by an intergovernmental body for open policy and research use. No explicit CC license; standard citation to WOAH/WAHIS is required. National sovereignty considerations may affect completeness for some countries.

**Data format and update cadence:** Interactive dashboards with CSV/JSON export functionality. Immediate notifications are real-time (within days of event). Six-monthly reports update twice yearly. Annual reports: annually. WAHIS-Wild Beta updates annually.

**WildlifeStats value:** The single most authoritative source for international outbreak data affecting wildlife. Particularly valuable for: HPAI/avian influenza in wild birds, African swine fever in wild boar, rabies variant data by country, and novel zoonotic emergence. WAHIS-Wild specifically targets wildlife disease surveillance outside the mandatory list, making it directly relevant to WildlifeStats' One Health mandate. Enables cross-country comparative disease burden analysis.

**Known integration friction:** Data are country-level aggregates — no individual case records, no GPS-level coordinates for most reports. Wildlife versus domestic animal reporting is not always disaggregated cleanly before the 2009 coding change. Some member states have inconsistent reporting quality. No RESTful API documented — data must be exported via dashboard.

---

### 1.2 USDA APHIS — HPAI Wild Bird Surveillance Dashboard

**URL:** [https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/wild-birds](https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/wild-birds)

**Data held:** Detection records for Highly Pathogenic Avian Influenza (HPAI) in wild birds across the United States from January 2022 to present. Data include species, county, state, detection date (confirmatory NVSL testing date), and source (APHIS Wildlife Services or state/private facility submissions). Companion livestock dashboard covers confirmed HPAI in commercial poultry and mammals.

**Access method:** Public web page with downloadable table data. Table updated weekday by APHIS. No API, but data are in tabular format suitable for direct download. USDA APHIS also deposits H5N1 sequence read data (including from wildlife) on NCBI SRA under BioProject PRJNA1102327 on a rolling basis.

**License / use restrictions:** U.S. government open data. No explicit license restriction; standard federal data re-use norms apply. County-level geographic precision maintained; private facility/farm names are withheld for privacy.

**Data format and update cadence:** HTML table with CSV export; updated weekdays. Sequence data on NCBI SRA updated on a rolling basis as samples are processed.

**WildlifeStats value:** Directly captures the ongoing clade 2.3.4.4b H5N1 epizootic in U.S. wildlife — the most significant ongoing wildlife disease event in the country. Enables temporal and spatial mapping of HPAI spread through avian species, with species-level resolution at county scale. Cross-referenced with GISAID and NCBI SRA for genotypic data. Critical for rehabilitation facilities tracking avian patients under HPAI protocols.

**Known integration friction:** Detection date lags sample collection date; APHIS notes this discrepancy explicitly. Private facility submissions may have incomplete metadata. Pre-2022 wild bird HPAI data requires separate historical queries via WAHIS.

---

### 1.3 CDC ArboNET — National Arbovirus Surveillance System

**URL:** [https://www.cdc.gov/vector-borne-diseases/php/arbonet/index.html](https://www.cdc.gov/vector-borne-diseases/php/arbonet/index.html)

**Data held:** National surveillance data on arboviral infections (mosquito-borne and tick-borne) including: human cases, presumptive viremic blood donors, veterinary disease cases, mosquito pools, dead bird surveillance, and sentinel animal data. Covers West Nile virus (WNV), Eastern Equine Encephalitis (EEE), La Crosse, St. Louis encephalitis, Jamestown Canyon, dengue, chikungunya, Zika, Powassan, and others. Dead bird and veterinary/sentinel animal data are particularly relevant to WildlifeStats. Established in 2000 (expanded from WNV), with data updated weekly during transmission season.

**Access method:** Annual finalized datasets are publicly available via CDC's NNDSS and disease-specific pages. Provisional current-year data are updated weekly. CDC data are available via CDC WONDER and direct download from disease landing pages. Historical surveillance summary reports published in MMWR.

**License / use restrictions:** U.S. government open data. Provisional data carry a specific caution against combining with finalized years for trend analysis. Dead bird data are aggregated at state level in most public-facing reports; county-level data available in finalized annual summaries.

**Data format and update cadence:** CSV/Excel downloads available for finalized years. Weekly updates during arboviral season (approximately May–November). Annual final datasets typically released the following spring.

**WildlifeStats value:** Dead bird surveillance data are a direct wildlife-mortality signal and a key early warning metric for WNV epizootics. Veterinary/sentinel animal data provide cross-species context. EEE is a significant mortality threat to wild bird populations. Tick-borne data (Powassan) complement tick surveillance sources. Enables regional arbovirus burden mapping for One Health synthesis.

**Known integration friction:** Passive surveillance system — significantly underestimates true incidence. Dead bird submissions depend on public reporting; consistency varies by region and year. County-level dead bird data are not always published in machine-readable form. Mosquito pool data require separate queries per state health department. Species-level detail in dead bird data is limited in aggregated public releases.

---

### 1.4 CDC — Rabies Surveillance Data

**URL:** [https://www.cdc.gov/rabies/php/protecting-public-health/index.html](https://www.cdc.gov/rabies/php/protecting-public-health/index.html)

**Data held:** CDC's National Rabies Surveillance System aggregates data from 134 U.S. public health and USDA Wildlife Services laboratories, processing approximately 95,000 animal samples annually (~4,500 positive/year). Data include species, rabies virus variant, state/county, and year of detection. Annual surveillance reports are published in JAVMA and available free online. Wildlife species (bats, raccoons, skunks, foxes) account for >90% of confirmed cases. USDA National Rabies Management Program adds ~7,000 additional samples/year.

**Access method:** Annual surveillance reports published in the Journal of the American Veterinary Medical Association (JAVMA) and summarized on CDC web pages. Finalized annual data tables available for download. CDC Poxvirus and Rabies Branch maintains the national datafile compiled from state health and agriculture departments.

**License / use restrictions:** Published data are U.S. government open data. JAVMA articles may require library access for full text but data tables are often freely available. The underlying national datafile is not a public API but annual aggregated data are accessible via MMWR and JAVMA supplements.

**Data format and update cadence:** Annual surveillance reports (typically published 6–12 months after end of reporting year). State-level tables in supplementary data. Some county-level data available in rabies variant mapping reports.

**WildlifeStats value:** Essential for wildlife mortality attribution in rehabilitation intake data, regional rabies variant tracking, and One Health zoonotic exposure analysis. Enables multi-decade trend analysis (data extend back to 1938). The wildlife species breakdown and variant mapping are directly applicable to WildlifeStats' disease surveillance layer. Cross-reference with rehabilitation intake data to identify rabies exposure risk at rehab facilities.

**Known integration friction:** Annual cadence limits real-time application. State-level aggregation is standard; county-level data require contacting state labs directly. Oral rabies vaccination (ORV) program data (bait distribution zones) are maintained by USDA Wildlife Services separately.

---

### 1.5 CDC — Tick Surveillance Data and Tickborne Disease Dashboards

**URL:** [https://www.cdc.gov/ticks/data-research/facts-stats/index.html](https://www.cdc.gov/ticks/data-research/facts-stats/index.html)

**Data held:** County-level tick species occurrence data (blacklegged tick, American dog tick, lone star tick, western blacklegged tick); tickborne pathogen presence in ticks; Tickborne Disease Surveillance Data Summary (reported cases of Lyme disease, anaplasmosis, babesiosis, Rocky Mountain spotted fever, ehrlichiosis, etc.); Tick Bite Data Tracker (syndromic surveillance). Downloadable tick surveillance datasets underlie the public dashboards.

**Access method:** Public dashboards with downloadable datasets via CDC WONDER and direct CSV download links. Tick Surveillance Data Sets are published as Excel/CSV files. Tickborne disease case counts are also available via NNDSS.

**License / use restrictions:** U.S. government open data. Standard federal re-use terms.

**Data format and update cadence:** Static annual datasets (CSV/Excel) updated annually; dashboards updated as data are finalized. Geographic Distribution of Tickborne Disease Cases published at county level of residence.

**WildlifeStats value:** Tick host species overlap extensively with wildlife rehabilitation intakes (white-tailed deer, small mammals, songbirds). County-level tick distribution data enable modeling of geographic exposure risk for wildlife and wildlife handlers. Pathogen prevalence in ticks (Borrelia, Anaplasma, etc.) is directly relevant to One Health disease surveillance in WildlifeStats.

**Known integration friction:** Case data represent human disease, not wildlife infection. Wildlife-specific tick data (tick burden on wildlife hosts) are fragmented across state-level surveillance programs and academic publications.

---

### 1.6 NOAA Fisheries — Sea Turtle Stranding and Salvage Network (STSSN)

**URL:** [https://www.fisheries.noaa.gov/national/marine-life-distress/sea-turtle-stranding-and-salvage-network](https://www.fisheries.noaa.gov/national/marine-life-distress/sea-turtle-stranding-and-salvage-network)

**Data held:** Centralized database of sea turtle strandings along the U.S. Atlantic and Gulf coasts, covering 6 sea turtle species. Data fields include species, date, location, live/dead status, condition, injury type, and disposition. Summarized stranding data from the last 10 years (verified by network personnel) are available via a public Data Summary and Visualization Application. Records dating to 1998 are cataloged in NOAA's InPort metadata system.

**Access method:** Public visualization application at NOAA SEFSC; tabular reports accessible via [https://grunt.sefsc.noaa.gov/stssnrep/](https://grunt.sefsc.noaa.gov/stssnrep/). For publication-quality data, coordination with state network coordinators is expected.

**License / use restrictions:** Public data — must credit Sea Turtle Stranding and Salvage Network. Preliminary unverified data are specifically not recommended for analysis or publication. Formal data requests for research should be coordinated with NOAA/network coordinators.

**Data format and update cadence:** Web-based tabular reports; some CSV export. Data verified on a rolling basis; 10-year rolling public dataset updated periodically.

**WildlifeStats value:** Definitive U.S. source for sea turtle stranding trends, mortality events, and rehabilitation outcomes for 6 protected species. Enables detection of mass stranding events (cold stun, fibropapillomatosis, oil spill impacts). Strong linkage to rehabilitation facilities along the Atlantic and Gulf coasts. Supports One Health analyses of marine pollution and turtle health.

**Known integration friction:** Data quality is "preliminary" until verified; verification lag can be significant. Individual animal-level records are not fully public. Coordination with 20+ state coordinators is required for research-grade data. No public API.

---

### 1.7 NOAA — Marine Mammal Health and Stranding Response Program (MMHSRP) / National Stranding Database

**URL:** [https://www.fisheries.noaa.gov/national/marine-life-distress/marine-mammal-health-and-stranding-response-program](https://www.fisheries.noaa.gov/national/marine-life-distress/marine-mammal-health-and-stranding-response-program)

**Data held:** National Stranding Database containing Level A (standardized) data on stranded seals, sea lions, dolphins, porpoises, and whales collected by the U.S. Marine Mammal Stranding Network. In 2024 alone, 8,028 confirmed strandings were recorded. Also maintains the National Marine Mammal Tissue Bank for retrospective health analyses. Annual large whale entanglement reports (2017–present) document approximately 64–95 confirmed cases per year, with gear identification.

**Access method:** Stranding data are submitted by network members to the National Stranding Database, managed by NOAA. Public-facing summary reports are published annually; research access to individual-level records requires formal request to NOAA Fisheries regional offices. Annual entanglement reports are published as free PDFs.

**License / use restrictions:** Federal program data; public annual reports are openly available. Individual animal records from the National Stranding Database require a data sharing agreement with NOAA Fisheries.

**Data format and update cadence:** Annual summary reports (PDF/web); individual-level data via data sharing agreement. Entanglement reports published annually (typically ~6 months after year end).

**WildlifeStats value:** Unique national-scale dataset for cetacean and pinniped health surveillance, mortality attribution (entanglement, vessel strike, disease, pollution), and rehabilitation outcomes. Critical for Unusual Mortality Event (UME) detection. Biosurveillance role through stranding networks. Whale entanglement data document gear-wildlife interactions at species and geographic levels.

**Known integration friction:** Individual-level data require an institutional data sharing agreement (MOU-adjacent). Annual summary reports lack the granularity needed for case-level WildlifeStats integration. Tissue bank data require separate research access.

---

### 1.8 USDA NASS — Honey Bee Colonies Survey

**URL:** [https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Bee_and_Honey/](https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Bee_and_Honey/)

**Data held:** Quarterly and annual honey bee colony loss data from managed operations, including colony counts, loss rates, Colony Collapse Disorder (CCD) symptoms, health stressors (Varroa, pathogens, pesticides, nutrition), and loss percentages by state. Collected since 2009 (quarterly since 2015). USDA ARS Bee Research Labs (Beltsville and others) conduct complementary pathogen/pest surveillance.

**Access method:** Fully public via NASS Quick Stats database (https://quickstats.nass.usda.gov). Download as CSV, XML, or JSON. An API is available for programmatic access.

**License / use restrictions:** U.S. government open data. No license restrictions.

**Data format and update cadence:** CSV/JSON via Quick Stats API; quarterly report cycles. Annual reports published mid-year. Bee Informed Partnership (BIP) annual survey data (since 2007) are complementary and publicly available.

**WildlifeStats value:** Pollinator health is a One Health indicator. Managed bee colony losses signal pesticide exposure, pathogen load, and habitat quality — environmental factors that affect co-occurring wild pollinators and other wildlife. Varroa data and pathogen prevalence from managed colonies can inform wild bee/pollinator disease surveillance. The 2024–25 record 55.6% annual colony loss rate represents an urgent monitoring priority.

**Known integration friction:** Data cover managed honey bee colonies, not wild pollinators. Wild bee surveillance data are extremely fragmented and not systematically collected at a national level. The USDA Beltsville Bee Research Lab has faced closure pressure (2025), creating potential data continuity risk.

---

### 1.9 GISAID EpiFlu / EpiArbo — Influenza Sequence Database

**URL:** [https://gisaid.org](https://gisaid.org)

**Data held:** The world's largest public repository for influenza virus sequences, including all H5N1 HPAI sequences from wild birds, poultry, livestock, and spillover mammals. As of 2026, GISAID holds over 22 million genetic sequence submissions. For the ongoing U.S. H5N1 clade 2.3.4.4b outbreak, GISAID hosts sequences from wild birds, dairy cattle, cats, poultry, and wildlife sanctuary animals. USDA APHIS also deposited 239 H5N1 BioSamples directly on NCBI SRA (BioProject PRJNA1102327) for cattle, cats, chickens, skunks, raccoons, a peregrine falcon, and other wildlife.

**Access method:** Requires free registration with a GISAID Data Access Agreement. Access is non-commercial and requires commitment to acknowledge data contributors. Data can be downloaded in bulk after registration. Consensus sequences assembled from USDA's SRA data are also available via a public GitHub repository (andersen-lab/avian-influenza).

**License / use restrictions:** GISAID Database Access Agreement (non-commercial; attribution required for all contributors). Data are not CC-licensed but are functionally open for research. NCBI SRA data are fully open (no registration).

**Data format and update cadence:** FASTA sequences + metadata (TSV/JSON) via GISAID; FASTQ on SRA. Updated continuously as sequences are submitted. USDA/CDC update their submissions on a rolling basis during active outbreaks.

**WildlifeStats value:** Genomic surveillance layer for HPAI — enables phylogeographic tracing of wild bird transmission chains. GISAID data from wildlife patients at rehabilitation centers contribute to understanding spillover dynamics. Critical for WildlifeStats' One Health disease surveillance function, particularly for cross-host outbreak investigations. NCBI SRA data from wildlife species include peregrine falcon, skunk, raccoon, and others directly relevant to the rehabilitation patient population.

**Known integration friction:** Registration required (though straightforward). Attribution requirements add complexity in automated pipelines. Pre-assembled consensus sequences (GISAID) are more immediately useful than raw reads (SRA) but require bioinformatics capacity to utilize fully. Metadata quality is variable across contributing labs.

---

### 1.10 ProMED — Program for Monitoring Emerging Diseases

**URL:** [https://www.promedmail.org](https://www.promedmail.org)

**Data held:** The world's largest publicly available emerging disease outbreak reporting system, operational since 1994. ProMED covers human, animal, and plant disease outbreaks in a One Health framework. Over 31 years of archive covering >75,000 subscribers in 185 countries. Reports include wildlife disease events (avian influenza, rabies, WNV, Newcastle disease, distemper, mange, botulism events, etc.) moderated by 30 subject matter experts in 24 countries. Averages 13 posts/day, approximately 30% covering events in the United States.

**Access method:** Fully public; no registration required for browsing and searching the archive. Email subscription is free. A bulk data API is available for institutional users (ProMED Pro tier); premium institutional access includes a structured data feed used by CDC, HHS, USAID, and AI surveillance systems.

**License / use restrictions:** Free for non-commercial use. Premium/institutional data feed for commercial or AI-system integration requires subscription. Archive search is publicly available without restriction.

**Data format and update cadence:** Semi-structured text reports with geotags and links. Real-time (posts within hours of event). Structured data feed (ProMED Pro): JSON/XML.

**WildlifeStats value:** Best available informal/event-based surveillance source for novel wildlife disease events before they reach official reporting systems. WHO data show >60% of initial outbreak reports come from informal sources including ProMED. ProMED's wildlife moderators cover diseases not captured by mandatory national reporting. The 31-year historical archive enables retrospective analysis of disease emergence in wildlife populations.

**Known integration friction:** Text-based, semi-structured — requires NLP/entity extraction for systematic ingestion. A formal ProMED Pro institutional subscription is needed for structured data feeds. Some posts contain preliminary or unverified information (retraction rate ~0.01, correction rate ~0.02 historically). Primarily event-triggered rather than systematic surveillance.

---

### 1.11 HealthMap — Global Disease Outbreak Aggregation

**URL:** [http://www.healthmap.org](http://www.healthmap.org) / [https://healthmap.org](https://healthmap.org)

**Data held:** Real-time global disease outbreak intelligence aggregated from news media, health organizations, government agencies, and official surveillance systems (including ProMED, WHO, CDC). Operational since 2006 from Boston Children's Hospital/Harvard Medical School. Processes ~300 reports/day in 15 languages; covers 50+ diseases globally with geolocation and temporal tagging. Provides structured feeds to CDC, HHS, and USAID.

**Access method:** Public web visualization is free. Structured data feeds for programmatic integration are available to institutional partners (CDC has an existing partnership). API access has been available for research institutions; current availability of public API requires direct contact with the HealthMap team.

**License / use restrictions:** Free for non-commercial use; API/feed access for government and major health organizations exists via partnership agreement. Data originate from third-party sources; attribution and use restrictions vary by source.

**Data format and update cadence:** Web interface with map visualization; alert data via structured feeds (JSON/XML) for institutional users. Near-real-time (automated ingestion pipeline runs 24/7).

**WildlifeStats value:** Provides a HealthMap-style aggregation layer across multiple source types simultaneously — particularly valuable for detecting early signals of wildlife disease outbreaks before they appear in official systems. The multi-source integration approach is directly applicable to WildlifeStats' aggregation architecture. Cross-reference with ProMED and WAHIS for corroboration.

**Known integration friction:** Primarily human/public health focus; wildlife-specific filtering requires additional effort. Automated aggregation means variable data quality. Institutional data feed agreement required for structured access. Somewhat less wildlife-focused than ProMED's expert-moderated posts.

---

## Tier 2: Publication Supplements (paper-by-paper extraction)

These sources do not have open bulk-download APIs but generate significant data through published research, conference proceedings, or institutional reports that can be systematically harvested.

---

### 2.1 Wildlife Rehabilitator's MD (WRMD) — Wildlife Rehabilitation Medical Database

**URL:** [https://wrmd.org](https://wrmd.org)

**Data held:** The largest active wildlife rehabilitation patient database in the world. As of 2026: **2,226 registered organizations** across **49 countries**, with **4,525,133 patient records**. Data captured per patient include: species, life stage, sex, rescue location (GPS), rescue date, admission diagnosis, case findings, treatments, prescriptions, procedures, attachment images, disposition (release/transfer/death/euthanasia), and Federal/state band numbers. Annual reports generated automatically for regulatory compliance. Classification tagging uses standardized clinical terminology.

**Access method:** Participating rehabilitation facilities own their own data and access them via WRMD's platform. The platform is **free** and does not sell user data. Aggregate/anonymized data for research purposes requires direct institutional engagement with WRMD's administrators (Wild Neighbors Detroit Project). There is no public bulk download or API documented. Research collaborations using WRMD data have been published (e.g., the Biological Conservation study using 674,320 records from 94 centers, 2011–2019).

**License / use restrictions:** Patient records belong to the submitting organization. Aggregate data sharing for research is facilitated on a collaboration basis. WRMD explicitly does not sell or share data commercially.

**Data format and update cadence:** Proprietary cloud database; exports available to member organizations (CSV/PDF). Aggregate research extracts via institutional collaboration. Records are entered in near-real-time during patient care.

**WildlifeStats value:** The single most valuable rehabilitation-specific data source in existence. 4.5 million patient records spanning 2,226 organizations across 49 countries represents a comprehensive clinical dataset covering species, injury/illness type, treatment, and outcomes. This data is precisely the "rehabilitation medicine core" of WildlifeStats. A formal research partnership with WRMD would unlock a dataset capable of revealing continental-scale patterns in wildlife morbidity, mortality causes, rehabilitation success rates, and disease exposure.

**Known integration friction:** No public API — institutional research collaboration required. Data are proprietary to member organizations; aggregate access requires consent workflows. The 2023 Biological Conservation study demonstrates research access is achievable but requires formal collaboration with WRMD administrators. Standardization of diagnosis/treatment coding varies by user skill level.

---

### 2.2 WILD-ONe — Wildlife Incident Log / Database and Online Network

**URL:** [https://www.wildlifecenter.org/wild-one](https://www.wildlifecenter.org/wild-one) (administered by Wildlife Center of Virginia)

**Data held:** A free online database for wildlife care facility patient management, created by the Wildlife Center of Virginia. Standardized admission forms capture: species, gender, life stage, rescue/release/transfer GPS locations, rescue date, circumstances of injury, anatomical site of injury, injury categorization, disposition, and Federal band numbers. 13 standardized fields are automatically uploaded to a centralized aggregate database. Aggregate data are viewable by non-WILD-ONe account holders. As of early operation, 90+ organizations beta-tested the system with >25,000 patients; current active population is unknown but it has been superseded in market share by WRMD.

**Access method:** Participating organizations can download their own records as Excel/PDF. Aggregate data at a summary level are viewable by all users. Viewing aggregate data from non-member organizations carries modest fees. The centralized aggregate database can be queried for summary statistics on wildlife health trends.

**License / use restrictions:** Data shared to the central database are the 13 fields considered public information for state/federal permit purposes. Non-public fields (contacts, medications, procedures) are not shared without consent. Aggregate data publication requires permission from the Wildlife Center of Virginia advisory group.

**Data format and update cadence:** Web-based; Excel/PDF export for individual organizations. Centralized aggregate updates within 30 days of admission. Google Maps integration for spatial data.

**WildlifeStats value:** Represents a complementary parallel system to WRMD with an earlier standardization approach. The 13-field public data layer (including GPS rescue/release coordinates and injury categorization) is a natural WildlifeStats integration target. The Wildlife Center of Virginia's role as administrator makes it a natural MOU partner.

**Known integration friction:** WRMD has largely eclipsed WILD-ONe in active adoption; current database size and activity level require verification. Aggregate access requires coordination with Wildlife Center of Virginia. Not all users update records within the 30-day window.

---

### 2.3 Wildlife Disease Association (WDA) — Journal of Wildlife Diseases

**URL:** [https://www.wildlifedisease.org/PersonifyEbusiness/Resources/Publications](https://www.wildlifedisease.org/PersonifyEbusiness/Resources/Publications)

**Data held:** The Journal of Wildlife Diseases (JWD), published quarterly since 1965, is the premier peer-reviewed venue for wildlife disease research. Published via BioOne Complete. Content includes: outbreak investigation reports, case and epizootic reports, research papers, surveillance summaries, and book reviews. Many papers include supplementary datasets (case series, pathology records, geographic data) deposited in Dryad or supplementary files. The WDA also produces conference proceedings from its annual meeting.

**Access method:** JWD is subscription-based via BioOne Complete (institutional library access). Some articles are open access. A 2025 Nature Scientific Data article proposed a "minimum data standard for wildlife disease research" providing a formal schema for WDA-adjacent data. Data supplements from individual papers are often on Dryad or journal supplementary files.

**License / use restrictions:** BioOne subscription for full article access; some open-access articles. Supplementary data typically licensed under CC-BY or similar. WDA membership required for conference proceedings.

**Data format and update cadence:** PDF articles with Excel/CSV supplements. Quarterly journal. Annual conference proceedings.

**WildlifeStats value:** Longest-running and most authoritative primary literature source for wildlife disease in North America and globally. The JWD archive (1965–present) is a unique resource for historical disease baseline data, long-term trend analysis, and novel pathogen characterization. Individual papers frequently contain case series data with species, location, and pathology findings usable as WildlifeStats data points after literature mining.

**Known integration friction:** Paper-by-paper extraction is labor-intensive. No unified data portal. Full text requires institutional library access or BioOne subscription. Structured data extraction from PDFs requires NLP tooling.

---

### 2.4 The Raptor Center (University of Minnesota)

**URL:** [https://raptor.umn.edu](https://raptor.umn.edu)

**Data held:** The Raptor Center (TRC) admits >1,000 raptors annually and has maintained patient records for decades. Key data include: lead blood levels (measured for every Bald Eagle admitted), rodenticide exposure data, trauma injury patterns, infectious disease findings (HPAI, avian pox), treatment outcomes, and post-release survival. USFWS commissioned a 2025 report by TRC on knowledge gaps in avian rehabilitation data collection. TRC has published on microbiome changes during rehabilitation, antimicrobial resistance, and lead poisoning. TRC also collects data on car collisions, window strikes, and net entanglements as trauma causes.

**Access method:** Published research (PLoS ONE, JWD, Journal of Raptor Research). Annual reports and donor communications (publicly available PDF). The USFWS-commissioned knowledge gap report (2025) provides a policy-accessible assessment of rehabilitation data needs. Aggregate statistics in annual reports/donor communications.

**License / use restrictions:** Published papers under journal licensing; annual reports are freely available. Underlying patient records are institutional. No public API or bulk download.

**Data format and update cadence:** PDF reports and published papers. Annual report cadence. Research papers on a project basis (multi-year studies).

**WildlifeStats value:** Among the highest-volume raptor rehabilitation centers in the world, with a strong research culture. The lead poisoning dataset (271 Bald Eagles tested 2011–2021, with 26% at elevated levels) is a model longitudinal environmental contaminant record. TRC's USFWS-commissioned data-standardization work directly supports WildlifeStats' goal of integrating rehabilitation data. Strong potential for formal research collaboration.

**Known integration friction:** No systematic public data repository. Research outputs are publication-by-publication. The USFWS report emphasizes that standardization of terminology and data collection is the greatest need — meaning data integration is currently limited by definitional inconsistency across centers.

---

### 2.5 Wildlife Center of Virginia

**URL:** [https://wildlifecenter.org](https://wildlifecenter.org)

**Data held:** One of the highest-profile rehabilitation centers in the U.S., admitting thousands of patients annually. Publishes Wildlife Center Quarterly (public newsletter) and formal scientific publications on: lead poisoning in raptors (10-year Bald Eagle blood lead dataset), rodenticide exposure, avian influenza screening, WILD-ONe development (described above), and case series for various species. Lead database: 271+ Bald Eagles tested 2011–2021; 337 other raptors with blood lead data.

**Access method:** Scientific publications on the center's website and in peer-reviewed journals. Wildlife Center Quarterly available online. Lead poisoning dataset summaries are public; full datasets require direct collaboration. The center is the administrative host of WILD-ONe.

**License / use restrictions:** Publications under journal licensing. Dataset access for research via collaboration agreement.

**Data format and update cadence:** PDF newsletters, published papers, web summaries. Annual summary reports. Real-time WILD-ONe patient entry.

**WildlifeStats value:** Key source for environmental contaminant (lead, rodenticide) longitudinal data in wild raptors — a directly usable dataset for WildlifeStats toxicology layer. The center's dual role as WILD-ONe host and research publisher makes it a strategic partner for WildlifeStats integration. The publicly documented lead dataset is one of the most rigorous available for any U.S. wildlife species.

**Known integration friction:** Full dataset access requires research collaboration. The center's focus on Virginia/Mid-Atlantic region limits direct national generalizability.

---

### 2.6 Tufts Wildlife Clinic — Cummings School of Veterinary Medicine

**URL:** [https://vet.tufts.edu/tufts-wildlife-clinic](https://vet.tufts.edu/tufts-wildlife-clinic)

**Data held:** Approximately 4,000–4,400 wildlife patients treated annually (2025 was a record year at 4,428 patients). Established 1983. Data from published research include: anticoagulant rodenticide (AR) exposure in birds of prey (first AR study 2011; ongoing; 97–100% exposure rates in red-tailed hawks); lead poisoning in common loons (long-term study since late 1980s; initiated state-level lead fishing tackle bans); avian influenza screening; antimicrobial resistance in wildlife patients; tularemia and WNV sentinel surveillance. The Runstadler Lab sequences avian influenza from clinic admissions.

**Access method:** Published peer-reviewed literature (Murray et al. series on ARs; Pokras et al. on loon lead). Annual patient statistics in clinic communications. No public database.

**License / use restrictions:** Publications under journal licensing. Underlying patient records are institutional property of Tufts University.

**Data format and update cadence:** Research publications on a project basis. Annual patient count communications.

**WildlifeStats value:** Tufts is a uniquely important academic-rehab research node: the only U.S. veterinary school with a mandatory 4th-year wildlife rotation, generating continuous clinical data from a student-active environment. The rodenticide and lead poisoning longitudinal series are directly usable as environmental sentinel datasets. The AR research influenced EPA regulatory actions — demonstrating the policy value of rehabilitation-center-based surveillance. Runstadler Lab HPAI sequencing provides a genetic surveillance function.

**Known integration friction:** No public data repository. Research output is publication-dependent; data from non-published studies require IRB/institutional collaboration. New England geographic focus.

---

### 2.7 American Association of Zoo Veterinarians (AAZV)

**URL:** [https://www.aazv.org](https://www.aazv.org)

**Data held:** Annual conference proceedings (published since the 1960s); Journal of Zoo and Wildlife Medicine (JZWM, published via BioOne Complete); AAZV guidelines and care manuals. Conference proceedings contain case reports, drug formulary updates, and emerging disease alerts from zoo and wildlife veterinarians. AAZV covers both captive and free-ranging wildlife in the context of One Health.

**Access method:** Conference proceedings available to AAZV members and via institutional library access. JZWM available via BioOne subscription. AAZV membership required for conference access; some proceedings are publicly available via BioOne.

**License / use restrictions:** BioOne subscription for full journal access. Conference proceedings behind AAZV membership. Some open-access articles.

**Data format and update cadence:** PDF proceedings and journal articles. Annual conference; quarterly journal.

**WildlifeStats value:** The JZWM and AAZV proceedings are the primary secondary literature source for zoo and free-ranging wildlife medicine case data. The long publication history makes this an important historical archive for rare-species veterinary data. Cross-reference with AAWV proceedings for wild (non-captive) species data.

**Known integration friction:** Primarily captive/zoo context; free-ranging wildlife case reports are a subset. BioOne subscription required for full access. No structured data repository.

---

### 2.8 USDA APHIS — National Animal Health Reporting System (NAHRS)

**URL:** [https://www.aphis.usda.gov/livestock-poultry-disease/surveillance/nahrs](https://www.aphis.usda.gov/livestock-poultry-disease/surveillance/nahrs)

**Data held:** NAHRS is the only comprehensive U.S. reporting system for WOAH-reportable diseases. State animal health officials report monthly on confirmed NAHRS-listed diseases in livestock, avian, lagomorph, and aquaculture species. Aligns with and feeds into the U.S. WOAH reporting obligations. Data include disease name, species, state, monthly confirmed presence. Wildlife-specific coverage is limited — NAHRS is primarily a domestic animal system, but avian cases (including backyard/commercial poultry with HPAI relevance to wild bird interface) are captured.

**Access method:** Summary reports published on APHIS website. Monthly state-level summaries available for download. Not a public API; formatted reports in PDF/table format.

**License / use restrictions:** U.S. government open data.

**Data format and update cadence:** Monthly state-level disease presence tables. Annual summaries. Published on APHIS website with a ~1-month lag.

**WildlifeStats value:** Provides the domestic animal disease context essential for understanding wildlife-livestock interface events (HPAI, brucellosis, CWD, etc.). NAHRS data feed into WOAH reporting, providing a bridge between U.S. national and international surveillance. The avian disease data (including HPAI in poultry near wildlife habitat) are relevant to WildlifeStats' disease surveillance layer.

**Known integration friction:** Primarily domestic animal focus; wildlife is not directly tracked by NAHRS. Disease presence is binary (confirmed present/absent by state) without case counts or geographic sub-state precision. Wildlife-specific attribution requires cross-referencing WAHIS and APHIS HPAI dashboards.

---

## Tier 3: Membership / Professional Access

These sources are accessible but require organizational membership or credentialed professional affiliation.

---

### 3.1 National Wildlife Rehabilitators Association (NWRA)

**URL:** [https://www.nwrawildlife.org](https://www.nwrawildlife.org)

**Data held:** The Wildlife Rehabilitation Bulletin (WRB), published since the 1970s and available open-access for current issues with member access to 20+ years of archives. The NWRA Content Database contains 430+ pieces of educational content organized into searchable tracks (avian, reptile, mammal, microscopy, ethics). Topics in Wildlife Medicine publication series (Volumes 1–4 covering nutrition, infectious diseases, and orthopedics). NWRA maintains a membership directory of professional rehabilitators; annual symposium proceedings. Standards for Wildlife Rehabilitation (5th edition, co-published with IWRC).

**Access method:** WRB current issue is open-access via the journal website. Full archives require NWRA membership (~$50–$100/year). Content Database requires membership login. Publication series available for purchase (members receive 20% discount). Training records associated with the Content Database tracks (certificate of attendance on member profile).

**License / use restrictions:** Journal articles are under publisher licensing; some open-access. Member content is restricted to paid members. The minimum standards publication (co-published with IWRC) is publicly accessible as a PDF from state wildlife agencies.

**Data format and update cadence:** PDF journal articles, web-based content database. WRB is published semi-annually (2–3 issues/year). Content database is continuously updated.

**WildlifeStats value:** NWRA membership represents several thousand U.S. wildlife rehabilitators. The WRB archive is an important secondary literature source for rehabilitation case data, species-specific protocols, and historical treatment records. The member directory is a key resource for identifying potential WildlifeStats data contributors. The Standards publication defines the data collection baseline.

**Known integration friction:** Database content is educational rather than raw research data. No bulk patient data — NWRA is a professional association, not a patient registry. Full archive access requires membership. Symposium proceedings are not systematically published in a searchable format.

---

### 3.2 International Wildlife Rehabilitation Council (IWRC)

**URL:** [https://theiwrc.org](https://theiwrc.org)

**Data held:** Journal of Wildlife Rehabilitation (JWR), published since 1977, distributed to approximately 1,500 individuals and organizations in North America and globally. The JWR is the peer-reviewed primary literature source for rehabilitation case data, treatment protocols, and outcomes, bridging the field with broader wildlife science. IWRC has supported an estimated 16,000 wildlife rehabilitators with training and resources. IWRC offers courses (Foundations of Wildlife Rehabilitation and specialty modules). Membership directory and conference symposium proceedings.

**Access method:** JWR is a benefit of IWRC membership ($54 USD/year minimum for individual subscription). Some archival articles are available via IWRC's article search. IWRC course completion records are maintained in member profiles.

**License / use restrictions:** JWR articles under journal licensing; some open-access via IWRC article search. Membership required for current issue and full archives.

**Data format and update cadence:** PDF journal articles. Published three times per year.

**WildlifeStats value:** The JWR archive (since 1977) represents nearly 50 years of rehabilitation case data, treatment outcomes, and species management data. As a bridge publication between the rehabilitation field and broader wildlife science, JWR often contains standardized case series that WRMD data lacks (clinical detail, necropsy findings). IWRC's global membership (including Canada, Estonia, and other countries) provides an international dimension absent from NWRA.

**Known integration friction:** Membership required for full archive access. JWR has more modest indexing than major veterinary journals (limited PubMed presence historically). No bulk data download.

---

### 3.3 American Association of Wildlife Veterinarians (AAWV)

**URL:** [https://www.aawv.net](https://www.aawv.net)

**Data held:** Annual Wildlife & Exotic Animal Symposium proceedings (joint with AAZV); member directory of wildlife veterinarians; position statements and technical guidelines. AAWV members include veterinarians working in federal and state agencies, academic institutions, zoos, and private practice. AAWV conferences (co-held with AAZV and WDA) produce substantial case literature.

**Access method:** AAWV membership ($75–$200/year) for conference proceedings and member directory. Some conference abstracts available publicly. Joint conference proceedings with AAZV are published via AAZV website for members.

**License / use restrictions:** Member access required for most content. Conference proceedings behind AAWV/AAZV membership paywall.

**Data format and update cadence:** Annual conference proceedings (PDF). Member communications.

**WildlifeStats value:** AAWV represents the credentialed veterinary professional pipeline for wildlife disease surveillance and rehabilitation oversight. The member directory is valuable for identifying credentialed researchers and practitioners as WildlifeStats contributors. Conference proceedings contain current case reports and surveillance alerts before formal publication. AAWV members hold USDA/USFWS veterinary authority in wildlife program contexts.

**Known integration friction:** No public data repository. Conference proceedings are not systematically archivable without membership. Annual meeting proceedings have limited open-access availability.

---

### 3.4 European Wildlife Disease Association (EWDA)

**URL:** [https://ewda.org](https://ewda.org)

**Data held:** EWDA Network for Wildlife Health Surveillance in Europe, established 2009 with representatives from 25+ countries. Maintains a Google Groups discussion platform for wildlife disease surveillance sharing (186 members). Produces "diagnosis cards" and "species cards" as standardized reference sheets. Conference proceedings (biennial). Publications in Revue Scientifique et Technique, Veterinary Record, and Animals. The EWDA Network's annual reports feed into WOAH Working Group on Wildlife reporting. Collaboration with ENETWILD project (harmonized wildlife population/pathogen data in Europe). Related WILDbase initiative aims to create a common European wildlife disease surveillance database.

**Access method:** EWDA membership for conference and network participation. Google Groups platform is member-restricted. EWDA Network publications are open-access (Animals 2021 paper on "How to Start Up a National Wildlife Health Surveillance Programme"). WILDbase database (Eurosurveillance 2024) is an open-access publication.

**License / use restrictions:** Conference proceedings require membership. Most scientific publications are open-access. Google Groups network requires EWDA membership application.

**Data format and update cadence:** Conference proceedings (biennial). Peer-reviewed publications on project basis. Network meeting reports annually.

**WildlifeStats value:** Provides comparative European methodology for wildlife surveillance — highly relevant for WildlifeStats' methodological framework even though EWDA covers non-U.S. data. EWDA's ENETWILD harmonized data and WILDbase initiative represent best-practice models for multi-national data integration. EWDA publishes on diseases (ASF, avian influenza, distemper) with global wildlife relevance.

**Known integration friction:** European data only — geographic scope mismatch with WildlifeStats' national (U.S.) focus. Membership required for most content. No API or bulk data download.

---

### 3.5 TickReport / TickEncounter Resource Center

**URL (TickReport):** [https://www.tickreport.com](https://www.tickreport.com) | **TickEncounter:** [https://tickencounter.org](https://tickencounter.org)

**Data held:** TickReport (University of Massachusetts) accepts citizen-submitted tick samples for identification and pathogen testing; the passive surveillance database captures tick species, geographic location of bite/encounter, host association (human/dog/cat/wildlife), and pathogen detection results (Lyme disease Borrelia, Anaplasma, Babesia, Ehrlichia, RMSF, etc.). TickEncounter (University of Rhode Island) provides species identification and a tick encounter database with geotagged submissions. Combined, these systems represent tens of thousands of citizen-science tick reports with pathogen data.

**Access method:** TickReport public statistics page ([https://www.tickreport.com/stats](https://www.tickreport.com/stats)) provides summary data. Research access to the full database requires collaboration with UMass/URI research teams. TickEncounter summary data are publicly viewable on the website.

**License / use restrictions:** Citizen science data; summary statistics are public. Full database access requires research collaboration agreement.

**Data format and update cadence:** Web dashboards with public summary statistics. Database updated continuously with new submissions.

**WildlifeStats value:** Provides wildlife-relevant tick-borne disease surveillance data at a finer geographic scale than CDC's county-level case data. Host data (including wildlife species bites) are uniquely available here. Important for One Health tick-borne disease surveillance in WildlifeStats — allows mapping tick pathogen burden in wildlife rehabilitation patient source areas. The citizen science model is directly analogous to WildlifeStats' public reporting ambitions.

**Known integration friction:** Pathogen testing is primarily from human/pet-associated ticks. Wildlife-specific tick data are a subset of the database. Full research-grade access requires collaboration. Passive submission bias: overrepresents areas with high public awareness.

---

## Tier 4: Institutional MOU Required

These sources hold critical data but require a formal Memorandum of Understanding, data sharing agreement, or credentialed researcher status for access.

---

### 4.1 USDA National Veterinary Services Laboratories (NVSL) — Full Diagnostics Data

**URL:** [https://www.aphis.usda.gov/animal_health/lab_info_services/nvsl.shtml](https://www.aphis.usda.gov/animal_health/lab_info_services/nvsl.shtml)

**Data held:** NVSL is the reference laboratory for HPAI, chronic wasting disease (CWD), brucellosis, and other high-consequence animal diseases. Confirmatory testing for HPAI in wild birds feeds the public APHIS dashboard, but the underlying sample-level data (including full diagnostic workup, virus isolation, sequencing metadata) are held internally. NVSL also coordinates the National Animal Health Laboratory Network (NAHLN), linking state diagnostic labs.

**Access method:** Aggregate/confirmatory results enter the public APHIS dashboard and WAHIS reporting. Full diagnostic data and sample-level records require formal USDA data agreement. Federal law enforcement-related data (e.g., CWD interstate movement violations) are not public.

**License / use restrictions:** Government data; formal data use agreement required for research access to non-public records.

**WildlifeStats value:** Access to NVSL's full diagnostic data would provide the most authoritative confirmatory disease data for U.S. wildlife. Critical for validating and enriching the HPAI dashboard data with sequencing metadata. Essential for CWD surveillance integration.

**Known integration friction:** Formal USDA/APHIS data use agreement required. Inter-agency processes can take 6–18 months. CWD data particularly complex due to state/federal jurisdictional issues.

---

### 4.2 AAVLD — American Association of Veterinary Laboratory Diagnosticians (State Diagnostic Lab Network)

**URL:** [https://www.aavld.org](https://www.aavld.org)

**Data held:** AAVLD accredits and connects 60+ state veterinary diagnostic laboratories across the U.S. Member labs collectively process millions of samples annually from livestock, companion animals, and wildlife. Wildlife-specific diagnostic data held by individual state labs (e.g., California CAHFS, Wisconsin VDL, Cornell Animal Health Diagnostic Center) include: pathology findings, culture and sensitivity results, toxicology screens, CWD testing, and wildlife mortality investigations. AAVLD members participate in the NAHLN.

**Access method:** Member directory public at [https://www.aavld.org/accredited-labs](https://www.aavld.org/accredited-labs). Individual lab data access requires direct engagement with each state lab; most labs will share aggregate wildlife diagnostic data under research collaboration or public records request. No centralized AAVLD data portal.

**License / use restrictions:** State lab data are typically state government public records for aggregate summaries; individual sample records may be exempt under agricultural confidentiality statutes. Research access varies by state.

**Data format and update cadence:** Varies by lab; most maintain internal LIMS systems. Annual reports published by many state labs. Data formats are lab-specific.

**WildlifeStats value:** State diagnostic labs are the primary confirmatory testing nodes for wildlife disease events reported by rehabilitation facilities, wildlife agencies, and the public. Accessing aggregate diagnostic data from even 10–15 high-volume state labs would provide a nationally representative picture of wildlife pathogen burden. Key for toxicology (lead, rodenticides) and infectious disease (HPAI, CWD, rabies variants) spatial analysis.

**Known integration friction:** 50+ separate state entities with different data management systems, access policies, and definitions. No central aggregate portal. Some states have strong wildlife diagnostic data programs (Wisconsin, California, Minnesota) while others are limited. Requires state-by-state engagement.

---

### 4.3 VetCompass — Cross-Clinic Veterinary Surveillance Methodology

**URL:** [https://www.vetcompass.org](https://www.vetcompass.org)

**Data held:** VetCompass (Royal Veterinary College, UK / University of Sydney) aggregates clinical records from 1,800+ UK veterinary practices covering 21 million animals, with 55 million clinical documents and 181 million treatments. 100+ peer-reviewed publications from 38+ studies. Covers companion animals primarily; methodology is directly applicable to wildlife clinical data integration. VetCompass Australia is a parallel program.

**Access method:** Research access to VetCompass data requires ethics approval and a stated plan to improve animal welfare. Not open to general access — structured research collaboration with RVC. No public API.

**License / use restrictions:** Data are controlled by contributing practices and the RVC. All research projects require institutional ethics approval. Data are not for commercial use.

**Data format and update cadence:** Free-text clinical notes with LLM-assisted extraction pipeline; structured fields (weights, test results, billed treatments). Continuously updated from practice systems.

**WildlifeStats value:** VetCompass does not directly cover wildlife in the U.S., but its methodology is the most relevant model for building a WildlifeStats clinical data integration pipeline. VetCompass's approach — aggregating free-text EHR data across thousands of independent practices using standardized LLM extraction — is directly analogous to what WildlifeStats needs to do with WRMD, WILD-ONe, and state rehabilitation records. VetCompass has demonstrated this model at scale with 100+ publications.

**Known integration friction:** UK/Australia geographic scope — not directly usable as a U.S. wildlife data source. Research collaboration with RVC required for methodology access. No U.S. wildlife veterinary equivalent exists; WildlifeStats would be building this capacity from scratch using WRMD as the data foundation.

---

### 4.4 USFWS Clark R. Bavin National Fish and Wildlife Forensics Laboratory

**URL:** [https://www.fws.gov/law-enforcement/clark-r-bavin-national-fish-and-wildlife-forensics-laboratory](https://www.fws.gov/law-enforcement/clark-r-bavin-national-fish-and-wildlife-forensics-laboratory)

**Data held:** The only U.S. federal crime lab devoted to wildlife law enforcement, founded 1988 in Ashland, Oregon. Also the official crime lab for CITES and Interpol Wildlife Group. Maintains a 20,000-entry freezer database of tissue standards and a mounted specimen morphology collection. Online Feather Atlas (avian feather identification) is publicly accessible. Forensic analyses include species identification (DNA, morphology), cause-of-death determination, and toxicology. Supports 200+ Special Agents, 50 state fish & game commissions, and 150+ countries.

**Access method:** Feather Atlas is public online. Forensic data underlying law enforcement cases are not public records. Aggregate statistics on case types are available in annual reports. Research access to the tissue database or forensic methodology requires formal collaboration with USFWS Law Enforcement.

**License / use restrictions:** Law enforcement data are protected. Research collaboration with the lab is possible for non-case-related scientific work (methodology development). Annual reports summarize workload categories.

**Data format and update cadence:** Feather Atlas: web-based image database. Annual reports: PDF. Case data: not public.

**WildlifeStats value:** The forensics lab is the authoritative source for cause-of-death determination in illegally killed or poached wildlife. Aggregate data on wildlife crime patterns (shooting, poisoning, electrocution) by species and region would directly support WildlifeStats' mortality attribution layer. The tissue reference database is a critical resource for wildlife genetic monitoring. USFWS Law Enforcement collaboration would also link WildlifeStats to poaching/trafficking incident data.

**Known integration friction:** Law enforcement context means most data are protected. Aggregate statistics are available but coarse. Requires formal USFWS Law Enforcement partnership for any data beyond public reports.

---

### 4.5 NOAA — National Large Whale Entanglement Response Network / National Stranding Database (individual records)

*(See also 1.7 for aggregate/public data)*

**Data held:** Individual animal-level records in the National Stranding Database, including Level A data collection forms with detailed health assessment, pathology, and cause-of-death data. The National Marine Mammal Tissue Bank maintains samples from stranded animals for retrospective analysis. Individual entanglement case files include gear type, geographic coordinates of entanglement, injury assessment, and outcome.

**Access method:** Individual-level records require a formal data sharing agreement with NOAA Fisheries regional offices. Tissue Bank sample requests require NOAA approval.

**License / use restrictions:** Federal data; data sharing agreement required. Publication must credit NOAA and contributing network organizations.

**WildlifeStats value:** Individual-level marine mammal health records are essential for the highest-quality WildlifeStats entries for cetacean and pinniped species. Cause-of-death data, contaminant findings, and pathology reports from stranded animals represent the most detailed mortality attribution dataset for U.S. marine mammals.

**Known integration friction:** Formal NOAA data sharing agreement required, typically requiring institutional affiliation and IRB-equivalent review. Timeline for agreement execution: 3–12 months.

---

### 4.6 National Lead Poisoning Working Group (Peregrine Fund / USFWS collaborative)

**URL:** [https://wildlife.org/the-wildlife-societys-position-on-lead-in-ammunition-and-fishing-tackle/](https://wildlife.org/the-wildlife-societys-position-on-lead-in-ammunition-and-fishing-tackle/) (see also Peregrine Fund: [https://peregrinefund.org/lead-poisoning](https://peregrinefund.org/lead-poisoning))

**Data held:** The National Lead Poisoning Working Group brings together data from rehabilitation facilities, state wildlife agencies, and research labs on blood lead levels in raptors, loons, condors, and other species. The Wildlife Center of Virginia, Tufts Wildlife Clinic, the Raptor Center (UMN), and The Peregrine Fund are key data contributors. The working group synthesizes published data, unpublished facility records, and sentinel monitoring results. Published output includes the Peregrine Fund's lead ammunition conference proceedings and state-by-state regulatory tracking.

**Access method:** Working group membership for data sharing among member organizations. Published synthesis reports and conference proceedings are publicly available (Peregrine Fund). Facility-level datasets (blood lead monitoring series) accessible via direct research collaboration with individual facilities.

**License / use restrictions:** Working group data are shared under member confidentiality for unpublished records; published outputs are open-access.

**Data format and update cadence:** Published reports and conference proceedings. No centralized database with public access. Facility-level datasets updated annually.

**WildlifeStats value:** Lead poisoning is the single most consistent cause of mortality for Bald Eagles and condors in the U.S. The working group represents the most coordinated effort to aggregate this data. Integration with WildlifeStats would provide a national lead-exposure surveillance layer for raptors — arguably the most data-rich environmental contaminant dataset in wildlife rehabilitation.

**Known integration friction:** No centralized public database. Data are distributed across facility-specific records. Working group membership required for access to unpublished data. Requires collaboration with multiple institutions.

---

## Additional Sources of Note

### CDC National Rabies Management Program / Oral Rabies Vaccination Database
USDA Wildlife Services manages the oral rabies vaccination (ORV) bait distribution program, distributing 7–10 million baits annually to control raccoon, fox, and coyote rabies. ORV distribution zones, vaccination success data, and post-vaccination surveillance samples are maintained by USDA Wildlife Services. Not a public API but accessible via USDA WS program contacts or FOIA. Direct relevance: maps where wildlife have been vaccinated and monitored, informing rehabilitation intake disease risk by region.

### Bald and Golden Eagle Protection Act (BGPA) — USFWS Eagle Take Permit Records
USFWS issues and tracks take permits under BGPA for wind energy, power lines, and disturbance activities. Annual reports from general permit holders and monitoring data from specific permit holders capture eagle mortality and injury events by facility, location, and cause. These records feed into USFWS's Eagle Management Unit (EMU) take accounting. Research access is available via USFWS Law Enforcement and Office of Migratory Birds; aggregate data are published annually.

### Wisconsin DNR / State CWD Surveillance Programs
Wisconsin, Minnesota, Colorado, Wyoming, and other states maintain sophisticated CWD (Chronic Wasting Disease) prion surveillance programs covering deer, elk, and moose. Wisconsin DNR in particular maintains a publicly accessible CWD GIS layer showing positive deer by county and year. These state programs represent model wildlife disease surveillance datasets for mammalian prion disease and are directly relevant to WildlifeStats' mortality database.

### Sea Turtle Stranding and Salvage Network (STSSN) — See 1.6
Already covered in Tier 1 (open visualization tool with verification requirement for research use).

---

## Recommended Ingestion Priority Order

The following ranking balances **data value for WildlifeStats** (breadth, uniqueness, clinical depth) against **accessibility** (open data vs. MOU vs. membership barriers). Immediate-tier sources that offer structured, programmatically ingestible data rank highest.

| Priority | Source | Tier | Rationale |
|----------|--------|------|-----------|
| **1** | WRMD (Wildlife Rehabilitation MD) | 2/MOU | 4.5M patient records across 2,226 organizations; the core clinical dataset for the rehab medicine layer. Requires institutional research partnership but is the most data-rich single source. |
| **2** | USDA APHIS HPAI Wild Bird Dashboard | 1 | Live, weekday-updated, structured tabular data on the most significant active U.S. wildlife disease event. Immediately ingestible, no registration required. |
| **3** | WAHIS (WOAH) — Public Interface + WAHIS-Wild | 1 | Global official disease data from 2005; WAHIS-Wild specifically covers non-listed wildlife diseases voluntarily. Public dashboard with export. Foundational One Health layer. |
| **4** | CDC ArboNET (WNV dead bird + sentinel data) | 1 | National arboviral wildlife surveillance; dead bird data are a direct wildlife mortality signal. Public download available. |
| **5** | GISAID + NCBI SRA (H5N1 sequences) | 1 | Genomic surveillance layer for HPAI; NCBI SRA is fully open. Registration-only for GISAID. Essential for sequence-informed disease mapping. |
| **6** | CDC Rabies Surveillance (annual reports) | 1 | National wildlife rabies by species and variant; 80-year archive. Annual cadence but freely available. |
| **7** | ProMED (archive + current alerts) | 1 | Event-based surveillance with 31-year archive; wildlife-specific content; free public access. NLP extraction needed. |
| **8** | NOAA STSSN (sea turtle stranding data) | 1/2 | 10-year verified stranding data via public visualization tool; research-grade access via coordinator coordination. |
| **9** | CDC Tick Surveillance Data + TickReport | 1/3 | County-level tick distribution + pathogen prevalence; public datasets plus citizen science supplementation. |
| **10** | NOAA MMHSRP (aggregate stranding reports) | 1/4 | Aggregate annual reports freely available; individual records require MOU for research use. |
| **11** | WDA Journal of Wildlife Diseases (paper extraction) | 2 | 60-year archive; case and epizootic reports; BioOne subscription needed but library access common. |
| **12** | USDA NASS Honey Bee Colony Survey | 1 | Public Quick Stats API; quarterly colony loss data; open pollinator health indicator dataset. |
| **13** | Wildlife Center of Virginia (lead/rodenticide datasets + WILD-ONe) | 2/3 | Longitudinal raptor contaminant data; WILD-ONe administrative access; strategic partnership target. |
| **14** | AAVLD State Diagnostic Lab Network | 4 | Confirmatory diagnostic data for wildlife disease events; requires state-by-state engagement but high value for toxicology and pathogen confirmation. |
| **15** | Raptor Center (UMN) + USFWS avian rehab knowledge-gap report | 2/3 | High-volume raptor clinical data; USFWS-commissioned 2025 data standardization report directly supports WildlifeStats architecture. Research collaboration target. |

---

*Report compiled for WildlifeStats national research framework, June 2026. Sources verified via primary URL fetch and literature search. All URLs were active at time of research.*
