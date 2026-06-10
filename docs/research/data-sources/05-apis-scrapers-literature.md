# APIs, scrapers, commercial repositories, and literature mining

**WildlifeStats Data Acquisition Layer — Technical Source Inventory**
*Scope: APIs, bulk download pipelines, web scraping targets, commercial repositories, literature mining, and news media. Excludes GBIF occurrence data (Agent 1), Movebank telemetry (Agent 2), and social media top-100 (Apify plan). Covers everything else that requires technical pipework to acquire.*

---

## Tier 1: Open API, no key required (use immediately)

### 1.1 ITIS — Integrated Taxonomic Information System
- **URL:** [https://www.itis.gov](https://www.itis.gov) | API: [https://www.itis.gov/web_service.html](https://www.itis.gov/web_service.html)
- **Data:** Authoritative taxonomic backbone for all seven Kingdoms of Life (Archaea, Bacteria, Protozoa, Chromista, Fungi, Plantae, Animalia). Fields include TSN (Taxonomic Serial Number), scientific name, common names, classification hierarchy, synonyms, expert-verified status, taxonomic authority, and geographic distribution.
- **Access:** REST JSON web service. Endpoint pattern: `https://www.itis.gov/ITISWebService/jsonservice/{methodName}`. Also SOAP (Basic Web Services) and JSON-P. No pagination required for single-record lookups; bulk TSN iteration is straightforward.
- **Auth:** None required. Fully open.
- **Rate limits / cost:** No documented rate limits. Free, publicly funded by 11 MOU partners including USGS, Smithsonian, and Agriculture Canada.
- **License:** Public domain / U.S. government work. Data is freely redistributable.
- **Value for WildlifeStats:** The taxonomic backbone. Every species ingested from any source should resolve to a ITIS TSN. Wildlife medicine and disease literature is full of taxonomic synonyms and spelling variants; ITIS is the authoritative resolver. Used by CDC, USGS, and EPA for species alignment.
- **Integration friction:** TSN IDs are stable but the ITIS service occasionally diverges from GBIF's backbone (which uses the Catalogue of Life). Maintain a crosswalk table between ITIS TSN and GBIF speciesKey. The SOAP endpoints are legacy and increasingly fragile; use JSON endpoints only. No batch TSN lookup — must iterate per-species.

---

### 1.2 Xeno-canto — Bird Sound Recordings
- **URL:** [https://xeno-canto.org](https://xeno-canto.org) | API: [https://xeno-canto.org/explore/api](https://xeno-canto.org/explore/api)
- **Data:** 800,000+ field recordings of birds (and some bats, grasshoppers). Each record carries: genus, species, subspecies, group, recorder, country, lat/lng, altitude, call type (song/call/alarm), sex, age stage, recording method, sonogram URLs, audio file URL, recording date/time, quality grade (A–E), background species list, and equipment metadata (mic, recorder, sample rate).
- **Access:** REST API v2. Endpoint: `https://xeno-canto.org/api/2/recordings?query={searchString}&page={n}`. Returns JSON. Paginated (page parameter). Supports complex Xeno-canto query syntax (e.g., `q:A cnt:"United States" type:call`).
- **Auth:** None. "This API can be used without restrictions."
- **Rate limits / cost:** 1 request per second. Free. Audio files are CC-licensed and directly downloadable from per-record URLs.
- **License:** Per-recording licenses (typically CC BY-NC-SA 4.0 or CC BY-NC-ND 4.0). Some recordings are CC BY. License field is in each JSON record. Commercial use requires per-recording review.
- **Value for WildlifeStats:** Primary source for vocalizations used in bioacoustic health monitoring — stress calls, injury vocalizations, disease-altered calls (West Nile, avian influenza). Pairs with Macaulay Library for multimedia and ML training data. Also captures presence/absence data with temporal and spatial resolution.
- **Integration friction:** Query syntax is idiosyncratic (documented on the search tips page, not the API page). Species name matching is exact — must pre-resolve synonyms via ITIS or Global Names before querying. The `also` field (background species) is a free-text array, not controlled vocabulary. Audio files are MP3; sonogram PNGs are convenient for ML pipelines.

---

### 1.3 Open Tree of Life — Synthetic Phylogeny
- **URL:** [https://opentreeoflife.org](https://opentreeoflife.org) | API: [https://github.com/OpenTreeOfLife/germinator/wiki/Open-Tree-of-Life-Web-APIs](https://github.com/OpenTreeOfLife/germinator/wiki/Open-Tree-of-Life-Web-APIs)
- **Data:** A continuously updated synthetic phylogenetic tree integrating 1,000+ published phylogenies covering ~2.4 million taxa. Endpoints provide: taxonomy lookup (OTT ID), phylogenetic placement, MRCA (most recent common ancestor) subtrees, full synthetic tree, and cross-references to NCBI, GBIF, ITIS, and EOL identifiers.
- **Access:** REST API v3. JSON responses. Key endpoints: `/taxonomy/taxon_info`, `/taxonomy/mrca`, `/tree_of_life/induced_subtree`, `/studies/find_studies`. No pagination on tree traversal — returns full subtree as Newick or NeXML.
- **Auth:** None.
- **Rate limits / cost:** No documented limits. Free and NSF-funded.
- **License:** Open, CC0 for the synthetic tree topology.
- **Value for WildlifeStats:** Critical for phylogenetic context in disease modeling — identifying which clades share susceptibility to specific pathogens (e.g., corvids and West Nile, mustelids and mink SARS-CoV-2). Enables taxonomic traversal queries: "all species within 3 nodes of the red fox that have confirmed rabies records."
- **Integration friction:** OTT IDs are not the same as NCBI Taxonomy IDs or GBIF taxonKeys. Crosswalk required. The synthetic tree is updated quarterly; IDs can be deprecated. Phylogenetic novelty (newly described species) has a 6–18 month lag before inclusion.

---

### 1.4 Wikidata — Structured Species and Disease Data
- **URL:** [https://www.wikidata.org](https://www.wikidata.org) | SPARQL: [https://query.wikidata.org](https://query.wikidata.org)
- **Data:** Structured linked data for ~500,000+ species (taxon items with P31=Q16521), human diseases, animal diseases, zoonoses, geographic ranges, conservation status, taxon authorities, IUCN IDs, ITIS TSNs, NCBI Taxonomy IDs, and cross-links to virtually every other knowledge graph. Property P1034 links taxa to host-pathogen relationships.
- **Access:** SPARQL endpoint at `https://query.wikidata.org/sparql`. Supports GET and POST with `query` parameter. Returns JSON, XML, CSV, TSV. Also: Wikidata REST API (`https://www.wikidata.org/w/rest.php`) for entity lookups; Action API for MediaWiki; bulk dumps via Wikimedia dumps portal.
- **Auth:** None for public queries. CORS wildcard (`*`). No account needed for read access.
- **Rate limits / cost:** SPARQL endpoint has an informal 60-second query timeout and limits on concurrent queries from a single IP. Intensive SPARQL workloads should use bulk dumps (updated weekly, available via Wikimedia Downloads). Free.
- **License:** CC0 — all Wikidata content is public domain.
- **Value for WildlifeStats:** Cross-linking hub. A single SPARQL query can return: all mammal species with known coronavirus susceptibility, their IUCN status, their range countries, and links to PubMed papers that describe them — across sources that would otherwise require dozens of API calls. Also a useful emergency bridge when a primary taxonomy source is down.
- **Integration friction:** Data quality is uneven — high for charismatic megafauna and human-relevant species, poor for invertebrates and fungi. SPARQL timeout kills complex queries; decompose into smaller traversals. Wikidata QIDs are stable but their linked external IDs (ITIS, GBIF) can become stale when primary sources update. The P1034 "vector" and P672 "host" properties are incompletely populated.

---

### 1.5 Crossref — DOI Metadata and Data Paper Supplements
- **URL:** [https://www.crossref.org](https://www.crossref.org) | API: [https://api.crossref.org](https://api.crossref.org)
- **Data:** Metadata for 150+ million scholarly works with DOIs: title, authors, journal, publication date, funder, license, abstract (where available), reference lists, citation counts (via OpenCitations link), and links to supplementary data. Covers journal articles, books, conference papers, preprints, datasets, and reports.
- **Access:** REST API. Base: `https://api.crossref.org/v1/works`. Supports field queries (e.g., `?query.bibliographic=wildlife+disease&filter=from-pub-date:2020`). JSON responses. Paginated with `rows` (max 1,000) and `offset`. OAI-PMH harvesting also available.
- **Auth:** Anonymous (public pool, 5 req/sec, 1 concurrent). Polite pool (add `mailto=` param, 10 req/sec, 3 concurrent). Metadata Plus (paid subscription): 150 req/sec, priority support, bulk snapshots.
- **Rate limits / cost:** See above. Free tiers are sufficient for most acquisition pipelines. Metadata Plus is ~$1,000–$3,000/year for production-scale use.
- **License:** CC0 for Crossref's metadata itself. Individual paper abstracts may be publisher-restricted.
- **Value for WildlifeStats:** Best tool for discovering *data papers* (papers that primarily describe and publish a dataset) — these often link to rehabilitation center data, surveillance data, and field study datasets not indexed elsewhere. Also enables citation tracking: which papers have cited a key zoonosis surveillance study, potentially revealing follow-on datasets.
- **Integration friction:** Abstract availability is inconsistent — many publishers do not deposit abstracts. The `filter=has-license:true` option is useful for identifying open-access materials. The Crossref API changed rate limit tiers in November 2025; ensure the `mailto` header is present to maintain polite pool access. Abstracts require a separate Unpaywall or OpenAlex query for full text.

---

### 1.6 bioRxiv / medRxiv — Preprint Literature
- **URL:** [https://api.biorxiv.org](https://api.biorxiv.org)
- **Data:** Preprint metadata for all bioRxiv (~250,000+ preprints) and medRxiv (~60,000+) manuscripts: title, abstract, authors, corresponding author institution, submission date, subject category, DOI, and published journal DOI (once peer-reviewed). Full-text XML available for text mining. Subject categories relevant to WildlifeStats include "Ecology," "Evolutionary Biology," "Microbiology," "Pathology," and "Zoology."
- **Access:** REST API. Endpoint: `https://api.biorxiv.org/details/{server}/{date_range}/{cursor}/{format}`. Supports date range queries, DOI lookups, category filters, and funder ROR ID filters. JSON and XML (OAI-PMH) output. Paginated at 30 records/call for metadata, 100/call for published paper crosslinks.
- **Auth:** None. Fully open.
- **Rate limits / cost:** No documented rate limits. Full corpus download takes ~1 hour via the API. Free.
- **License:** All preprints freely accessible. License per-paper (CC-BY, CC-BY-ND, etc.) is in the metadata. Text mining is explicitly permitted for non-commercial research.
- **Value for WildlifeStats:** Preprints precede publication by 6–18 months — critical for fast-moving outbreaks (SARS-CoV-2 spillover in mink, HPAI H5N1 in marine mammals). The EcoEvoRxiv server ([https://ecoevorxiv.org](https://ecoevorxiv.org)) hosts ecology and conservation-specific preprints that bioRxiv does not always index; it runs on the OSF platform with metadata available via the OSF API (`https://api.osf.io/v2/preprints/?provider=ecoevorxiv`).
- **Integration friction:** No full-text search in the API — must download abstract corpus and index locally (Elasticsearch or Solr). The `category` field uses an internal controlled vocabulary; map it to MeSH or custom WildlifeStats taxonomy. Preprints are not peer-reviewed; downstream quality scoring is needed.

---

### 1.7 GBIF — Global Biodiversity Information Facility (Occurrence)
- **URL:** [https://www.gbif.org](https://www.gbif.org) | API: [https://api.gbif.org/v1/](https://api.gbif.org/v1/)
- **Data:** 2.5+ billion occurrence records from 80,000+ datasets: museum specimens, citizen observations, automated sensor records, and experimental data. Fields follow Darwin Core: scientificName, eventDate, decimalLatitude, decimalLongitude, country, coordinateUncertaintyInMeters, basisOfRecord, taxonKey, datasetKey, license, and 200+ additional DwC terms. Also: species taxonomy lookup, dataset registry, literature that cites GBIF data.
- **Access:** REST API (JSON). Key endpoints: `/v1/occurrence/search`, `/v1/species/match`, `/v1/dataset/{uuid}`. Real-time search supports up to 100,000 records; async download API for bulk retrieval (requires registered GBIF account, result emailed as Darwin Core Archive zip). HTTP Basic Auth for downloads; most read operations are anonymous.
- **Auth:** Anonymous for search/read. GBIF account (free) required for bulk occurrence downloads.
- **Rate limits / cost:** No hard limits on read queries; rapid queries may trigger HTTP 429. For scripts running >15 minutes, use the async download API. Free. Data is CC0, CC-BY, or CC-BY-NC per dataset.
- **License:** Per-dataset (CC0/CC-BY/CC-BY-NC). GBIF download DOI provides citeable, reproducible snapshot.
- **Value for WildlifeStats:** The broadest occurrence layer for range modeling, disease vector distribution, and citizen science integration. Links to iNaturalist, eBird, museum collections, and camera trap datasets. The Darwin Core Archive download is the standard format for bulk ingestion.
- **Integration friction:** Coordinate quality is highly variable. GBIF provides geospatial issue flags (e.g., `COORDINATE_ROUNDED`, `COUNTRY_COORDINATE_MISMATCH`) — filter these before spatial analysis. Taxonomic backbone is Catalogue of Life-derived and diverges from ITIS in ~5% of cases for vertebrates. Duplicate records across datasets are common; occurrence IDs provide partial deduplication but not complete resolution.

---

### 1.8 Wikipedia — Species Pages (Template Mining)
- **URL:** [https://en.wikipedia.org](https://en.wikipedia.org) | API: [https://en.wikipedia.org/w/api.php](https://en.wikipedia.org/w/api.php)
- **Data:** Species articles contain structured infoboxes (taxoboxes) with: classification, conservation status, range maps, images, habitat descriptions, behavioral notes, and disease associations. The taxobox template is machine-parseable. Wikipedia also maintains lists of zoonoses, disease vectors, and One Health case studies.
- **Access:** MediaWiki Action API. Key endpoint: `https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles={PageTitle}&rvprop=content`. Returns raw wikitext including templates. REST API (`/api/rest_v1/`) provides cleaner JSON for page summaries. Wikidata integration via `action=wbgetentities`.
- **Auth:** None for read access.
- **Rate limits / cost:** Standard Wikimedia limits: 200 requests/second for anonymous users (rarely enforced in practice). Recommended: register a user-agent. For bulk use, download the Wikipedia XML dump (available monthly) rather than hitting the API. Free, CC BY-SA 4.0.
- **License:** CC BY-SA 4.0. Attribution required. Not CC0.
- **Value for WildlifeStats:** Rapid baseline population for species profile pages when primary databases lack prose descriptions. Wikipedia's disease association sections (e.g., rabies hosts, SARS-CoV-2 susceptibility by taxon) are often more comprehensive than any single API and updated faster during outbreak events.
- **Integration friction:** Taxobox templates are inconsistently structured — thousands of species use legacy formats, redirects, and deprecated parameters. A Wikipedia-specific parser (e.g., `mwparserfromhell` in Python) is required. Species names in Wikipedia often lag taxonomic changes by years. Do not treat Wikipedia as a primary taxonomic source; use it as a prose enrichment layer only.

---

## Tier 2: API key required but free

### 2.1 IUCN Red List — Species Assessments
- **URL:** [https://www.iucnredlist.org](https://www.iucnredlist.org) | API: [https://apiv3.iucnredlist.org/api/v3/docs](https://apiv3.iucnredlist.org/api/v3/docs)
- **Data:** Comprehensive conservation assessments for 170,000+ species: Red List category (EX/EW/CR/EN/VU/NT/LC/DD), population trend, geographic range (EOO/AOO in km²), habitat classification, threats (IUCN threat classification scheme), conservation measures, historical assessments by year, synonyms, common names, and country of occurrence. Narrative text fields: Rationale, Population, Geographic Range, Habitat, Threats, Conservation Measures, Use/Trade.
- **Access:** REST API v3. Token in URL parameter (`?token=YOUR_TOKEN`). Key endpoints: `/api/v3/species/{name}`, `/api/v3/species/narrative/{name}`, `/api/v3/threats/species/name/{name}`, `/api/v3/habitats/species/name/{name}`. Returns 10,000 records per page for full species list. JSON format.
- **Auth:** Free token via [https://apiv3.iucnredlist.org/api/v3/token](https://apiv3.iucnredlist.org/api/v3/token). Requires a brief justification. Issued within 24 hours.
- **Rate limits / cost:** No documented rate limits. Free. Token is personal — do not share.
- **License:** IUCN Red List Terms of Use. Non-commercial research and education use is permitted; commercial redistribution requires a separate agreement. Data may be cited per IUCN guidelines.
- **Value for WildlifeStats:** The single most comprehensive source for species vulnerability context — essential for interpreting wildlife disease data in a conservation framework. Threat codes (1.1 Housing, 2.1 Annual crops, 5.1.1 Hunting) provide structured cause-of-harm data that maps directly to injury/rehabilitation admission categories.
- **Integration friction:** The v3 API is actively used but a v4 is in development; monitor for deprecation. Species IDs (`taxonid`) are not stable across assessment years — use scientific name as the primary key and store both. Narrative text fields contain HTML markup that must be stripped. The API is name-based; binomial format is required (spaces, not underscores). Regional assessment support requires a separate `region_identifier` parameter.

---

### 2.2 Encyclopedia of Life (EOL) — Taxa and Trait Data
- **URL:** [https://eol.org](https://eol.org) | API: [https://eol.org/docs/what-is-eol/data-services](https://eol.org/docs/what-is-eol/data-services)
- **Data:** Multimedia species profiles aggregated from 200+ content partners: taxonomy, ecological interactions, organism attributes (body size, diet, lifespan, reproductive rate), images (CC-licensed), text descriptions, and food web relationships. Bulk downloads via Zenodo include: complete image file list, all trait data (TSV), and all taxonomic/vernacular name datasets.
- **Access:** Classic REST API (ping, pages, search, collections, data objects) — JSON, no authentication. Structured Data API uses Cypher graph query language for taxonomy, ecological interactions, and organism attributes — requires EOL account key. Reconciliation API at `https://eol.org/api/reconciliation`. Bulk data at [https://zenodo.org/communities/eol](https://zenodo.org/communities/eol).
- **Auth:** Classic API: none. Structured Data API: free EOL account + contact EOL to enable Cypher webform.
- **Rate limits / cost:** Rate limits apply (see robots.txt). Bulk downloads via Zenodo are preferred for large-scale acquisition. Free.
- **License:** Per-content-partner. Ownership rests with content partners; attribution and license details are in every record. Many are CC BY or CC BY-SA.
- **Value for WildlifeStats:** Best source for ecological trait data linked to taxa — body mass, trophic level, diet breadth, and reproductive parameters feed directly into wildlife disease transmission models. The food web JSON service provides predator-prey-competitor triads useful for vector/host network modeling.
- **Integration friction:** The experimental JSON-LD attribute service is deprecated; use Cypher API only for structured data. EOL page IDs are stable but content quality is partner-dependent and inconsistent across taxa. The Cypher API requires manual rate limit management. For large trait datasets, download the full TSV from Zenodo rather than querying the API.

---

### 2.3 PubMed / PubMed Central — Veterinary and Zoonotic Literature
- **URL:** [https://pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov) | E-utilities: [https://eutils.ncbi.nlm.nih.gov/entrez/eutils/](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/)
- **Data:** PubMed: 37+ million biomedical citations with abstracts (not full text). PubMed Central (PMC): 10+ million full-text open access articles including XML. Covers: Journal of Zoo and Wildlife Medicine, Journal of Wildlife Diseases, Veterinary Microbiology, Emerging Infectious Diseases, Zoonoses and Public Health, Vector-Borne and Zoonotic Diseases, and 10,000+ other journals. Key search fields: MeSH terms (`[MH]`), organism taxonomy (`[Organism]`), journal (`[TA]`), author (`[AU]`), filter by species, publication type.
- **Access:** Nine E-utility endpoints (ESearch, EFetch, ESummary, EPost, ELink, EInfo, EGQuery, ESpell, ECitMatch). Base URL: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`. Full-text XML from PMC via EFetch with `db=pmc`. NCBI FTP also provides bulk XML snapshots.
- **Auth:** Free NCBI API key from account settings at [https://www.ncbi.nlm.nih.gov/account/](https://www.ncbi.nlm.nih.gov/account/). Without key: 3 req/sec. With key: 10 req/sec (higher on request). Register `tool` and `email` parameters.
- **Rate limits / cost:** 3 req/sec (no key), 10 req/sec (with key). Large jobs: run between 9 PM–5 AM Eastern weekdays, or on weekends. Free.
- **License:** PubMed abstracts are freely available; full text in PMC is open access (CC-licensed). Publisher-restricted articles are abstract-only.
- **Value for WildlifeStats:** The single most important literature source. MeSH term `"Wildlife Diseases"[MH]` retrieves 50,000+ targeted papers. Combining with `"Zoonoses"[MH]`, `"Rehabilitation, Wildlife"[TW]`, or species-specific organism filters allows precision retrieval. PMC full-text XML enables NLP extraction of treatment protocols, case outcomes, pathogen characteristics, and rehabilitation statistics.
- **Integration friction:** MeSH vocabulary changes annually; track deprecated terms. PubMed does not index gray literature, conference proceedings, or most international journals published outside MEDLINE scope. Full-text XML from PMC has structural inconsistencies (especially for older articles scanned from print). The E-utilities have an undocumented history of occasional API behavior changes; test against the NCBI Developer Sandbox.

---

### 2.4 Semantic Scholar — Citation Graph and Paper Discovery
- **URL:** [https://www.semanticscholar.org](https://www.semanticscholar.org) | API: [https://api.semanticscholar.org/api-docs/](https://api.semanticscholar.org/api-docs/)
- **Data:** 200+ million academic papers with: citations, references, paper influence scores, author profiles, open-access PDF links, topic classification (including ecology and veterinary science), and a snippet search (full-text sentence extraction). Semantic Scholar Academic Graph (S2AG) provides citation velocity and "highly influential citation" flags.
- **Access:** REST API. Key endpoints: `/graph/v1/paper/search`, `/graph/v1/paper/batch`, `/graph/v1/paper/{id}/citations`. API key in `x-api-key` header. Batch endpoint handles 500 paper IDs/call. Bulk search: up to 10 million papers via paginated bulk endpoint (1,000/call). Snippet search returns sentence-level text matches.
- **Auth:** Free API key from [https://www.semanticscholar.org/product/api](https://www.semanticscholar.org/product/api). Without key: severely rate limited (100 req/5 min); key unlocks 1 req/sec default.
- **Rate limits / cost:** With API key: 1 req/sec. Batch and bulk endpoints have size limits (see Tier details above). Free. Higher rate tiers available via partnership agreement.
- **License:** Metadata is freely available. Full-text snippets are from content under various licenses (CC-BY marked in responses). The S2AG bulk dataset is available under ODC-BY.
- **Value for WildlifeStats:** Best tool for discovering gray-zone papers — rehabilitation outcome studies in wildlife medicine journals that PubMed doesn't fully index, and citation network analysis to find all papers that have built on a foundational zoonosis study. The "highly influential citation" metric identifies papers that meaningfully change a field, enabling prioritization of deep extraction.
- **Integration friction:** Coverage of non-English literature and veterinary trade journals is uneven. The `paperId` (S2 internal) and `externalIds` (DOI, PubMed, ArXiv) must both be tracked. Citation counts lag real-time publication by 2–4 weeks. The snippet search endpoint is powerful but not publicized; it can extract one-sentence descriptions of disease events from full-text papers without downloading complete PDFs.

---

### 2.5 Biodiversity Heritage Library (BHL) — Historical Literature
- **URL:** [https://www.biodiversitylibrary.org](https://www.biodiversitylibrary.org) | API: [https://www.biodiversitylibrary.org/docs/api3.html](https://www.biodiversitylibrary.org/docs/api3.html)
- **Data:** 60+ million pages of biodiversity literature digitized from natural history libraries worldwide, spanning from the 1400s to the 20th century. Full OCR text, page images, and taxonomic name extraction (linked to EOL/GBIF). Structured metadata: titles, items, parts (articles), pages, authors, subjects, and institution codes. Over 60 million species name occurrences indexed across the corpus.
- **Access:** REST API (JSON/XML). Methods: `PublicationSearch`, `PublicationSearchAdvanced`, `NameSearch`, `PageSearch`, `GetItemMetadata`, `GetPageMetadata` (including `OcrText` field for raw OCR). API key in URL parameter. Bulk dumps of name-page occurrence data available via the BHL data exports page.
- **Auth:** Free API key from [https://www.biodiversitylibrary.org/getapikey](https://www.biodiversitylibrary.org/getapikey).
- **Rate limits / cost:** Not documented. Practical limits are courteous — do not hammer. Free.
- **License:** Per-item. Most digitized materials are out of copyright; modern partner-contributed materials may carry restrictions. Rights and license fields are in every item record.
- **Value for WildlifeStats:** Historical disease and rehabilitation records predate modern digital databases by centuries. BHL contains early reports of rinderpest, distemper, and other wildlife epizootics; taxonomic treatises that establish baseline population descriptions; and veterinary textbooks pre-1923 that describe treatment approaches still in use. The OCR text layer enables full-text search for historical disease events.
- **Integration friction:** OCR quality is variable — older printed materials, particularly those in ornate or non-Latin typefaces, have high error rates. The `NameFound` field uses the Global Names Recognition system, which has its own error rate. BHL page IDs are stable but item-level metadata is inconsistent across contributing libraries. For text mining, build a local index from bulk exports rather than page-by-page API calls.

---

### 2.6 GDELT — Global News Database
- **URL:** [https://www.gdeltproject.org](https://www.gdeltproject.org) | API: [https://api.gdeltproject.org/api/v2/doc/doc](https://api.gdeltproject.org/api/v2/doc/doc)
- **Data:** Continuous monitoring and translation of news coverage in 65 languages worldwide, updated every 15 minutes. GDELT 2.0 Event Database: event-entity-tone triples from news articles. GDELT Document (DOC) API: full-text search with volume/tone timelines, article lists, image analysis. Visual Global Knowledge Graph (VGKG): deep learning image classification across global news imagery. Covers 150+ countries, 60+ years of historical data.
- **Access:** URL-based REST API. No client library required. Endpoint: `https://api.gdeltproject.org/api/v2/doc/doc?query={terms}&mode={mode}`. Modes include `artlist` (article URLs), `timelinevolinfo` (volume over time), `tonechart`, `imagecollageinfo`. JSON, CSV, RSS, HTML output. CORS wildcard — embeddable anywhere.
- **Auth:** None. Fully open. No key required.
- **Rate limits / cost:** No documented rate limits for DOC API. The GDELT 2.0 event files are also available as bulk 15-minute TSV updates via FTP. Free.
- **License:** GDELT data is released for open research use. News article content is subject to original publisher copyright; GDELT provides URLs and metadata, not article text.
- **Value for WildlifeStats:** The most critical early-warning layer for outbreak detection. A structured GDELT query for `"bird flu" OR "avian influenza" OR "HPAI" OR "highly pathogenic"` against a wildlife-specific news filter will surface regional media reports days to weeks before WAHIS or USDA official notifications. Example query already cited in GDELT documentation: `query=(wildlife+crime+OR+poaching+OR+illegal+fishing+OR+wildlife+trade)&mode=artlist&maxrecords=100&timespan=1week`. Build a daily cron job against this endpoint.
- **Integration friction:** GDELT geolocates events but accuracy is imprecise (country-level for non-Western outlets). The `tone` field is sentiment-scored but calibrated on human conflict news — wildlife disease stories are tonally neutral and may be underweighted. Article deduplication is essential; the same story appears in hundreds of syndicated outlets. Build a URL canonicalization + hash deduplication layer. GDELT does not provide full article text — must follow URLs with Newspaper3k or similar.

---

### 2.7 OpenAlex — Open Citation Graph and Scholarly Metadata
- **URL:** [https://openalex.org](https://openalex.org) | API: [https://api.openalex.org/](https://api.openalex.org/)
- **Data:** 250+ million scholarly works, 90+ million authors, 100,000+ institutions, topics, publishers, and funders. All linked in a heterogeneous directed graph (citation network). Includes open-access status, license, abstract (inverted index), cited-by count, concepts (mapped to Wikidata), and DOI/PMID/PMCID cross-references. Full database snapshots available for download.
- **Access:** REST API. Endpoint: `https://api.openalex.org/works?filter=concepts.id:{WikidataQID}`. API key (free) from account settings. Paginated with `cursor` for efficient deep retrieval. Complete quarterly snapshots in CC0 under OpenAlex bulk data.
- **Auth:** Free API key from [https://openalex.org/settings/api](https://openalex.org/settings/api). Free tier: $1/day of API credits (covers typical research use). Paid plans for production-scale or daily snapshots.
- **Rate limits / cost:** Free tier has $1/day usage credit. Snapshot (quarterly, free CC0) is preferred for bulk acquisition to avoid API cost accumulation.
- **License:** CC0 — entire dataset is public domain. This is significantly more permissive than Crossref, Semantic Scholar, or Web of Science.
- **Value for WildlifeStats:** Best freely available citation graph for tracking the diffusion of wildlife disease research — identifying which studies are most built upon, which research groups are most active in each disease area, and finding data papers that have generated datasets suitable for ingestion. Concept filtering by Wikidata QID enables precise topical filtering: `concepts.id:Q30089590` (wildlife disease) returns a targeted corpus.
- **Integration friction:** The "concepts" (topic classification) system was updated in 2024 to a new "topics" taxonomy; legacy concept IDs still work but new data uses the topics system. Abstract text is stored as an inverted index (word → position), not as raw text — must reconstruct at ingest. The quarterly snapshot is large (~500 GB uncompressed) and requires a columnar database (DuckDB or BigQuery) for efficient querying.

---

### 2.8 NewsAPI — Structured News Feed
- **URL:** [https://newsapi.org](https://newsapi.org) | API: [https://newsapi.org/docs](https://newsapi.org/docs)
- **Data:** Real-time and historical news from 150,000+ sources including AP, Reuters, BBC, regional outlets. Fields: title, description, content snippet (first 200 characters), source name, URL, author, published date. Endpoints: `/v2/top-headlines`, `/v2/everything` (full-text search across archive).
- **Access:** REST JSON API. Key in `apiKey` parameter or `X-Api-Key` header.
- **Auth:** Free developer key from [https://newsapi.org](https://newsapi.org).
- **Rate limits / cost:** Developer (free): 100 requests/day, 24-hour delay, 1 month archive. Business ($449/month): 250,000 req/month, real-time, 5-year archive. Advanced ($1,749/month): 2 million req/month. For WildlifeStats, the Business tier is the operational minimum for a live disease alert pipeline.
- **License:** NewsAPI provides metadata and truncated content. Full article retrieval requires following URLs and is subject to publisher terms.
- **Value for WildlifeStats:** Structured, easily queryable news ingestion for disease outbreak monitoring. Complements GDELT's broader but noisier coverage. Best for tracking named institutions (USDA APHIS, CDC, WHO) and specific outbreak nomenclature (H5N1, CWD, West Nile) across established media.
- **Integration friction:** The 200-character content truncation means full-text extraction still requires URL fetching. Source list coverage drops significantly for non-English and regional African/Asian outlets — GDELT is better for global coverage. Rate limits on the free tier make it development-only.

---

### 2.9 Movebank — Animal Movement Data
- **URL:** [https://www.movebank.org](https://www.movebank.org) | API: [https://github.com/movebank/movebank-api-doc](https://github.com/movebank/movebank-api-doc)
- **Data:** Animal tracking data from 3,000+ studies covering 1,000+ species. GPS telemetry, accelerometry, acoustic tags, proximity sensors. Fields follow Movebank Attribute Dictionary (which maps to Darwin Core where applicable): individual ID, species, tag ID, timestamp, GPS coordinates, altitude, ground speed, heading, mortality status flags, and study-specific attributes.
- **Access:** HTTP REST API returning CSV or JSON. Key endpoints: `https://www.movebank.org/movebank/service/direct-read?entity_type=event&study_id={id}`. Supports both CSV download (for permitted public studies) and a JavaScript/JSON service for embedding maps. API documentation on GitHub: [https://github.com/movebank/movebank-api-doc/blob/master/movebank-api.md](https://github.com/movebank/movebank-api-doc/blob/master/movebank-api.md).
- **Auth:** Free Movebank account required. Public studies download directly; restricted studies require owner permission grant. OAuth not used — HTTP Basic Auth.
- **Rate limits / cost:** No documented rate limits. Free. Data ownership remains with the original collector; access rights are set per study.
- **License:** Per-study terms of use set by data owners. Many studies have restricted redistribution even when downloadable.
- **Value for WildlifeStats:** Movement data is critical for modeling disease transmission corridors — tracking the spread of HPAI via migratory waterfowl, CWD via deer movement, or rabies via carnivore dispersal. Mortality flag fields directly intersect with rehabilitation and disease datasets. The API supports near-real-time data access for live tracking studies.
- **Integration friction:** Data ownership model means ~40% of studies are restricted; automated acquisition requires negotiating individual agreements. The Movebank Attribute Dictionary has 500+ terms but studies use inconsistent subsets. Mortality status is inconsistently coded across studies. Coordinate systems vary (WGS84 standard, but verify per study). Note: Movebank bulk telemetry is in Agent 2's scope — this source should be coordinated to avoid duplicate ingestion pipelines.

---

### 2.10 Macaulay Library (Cornell Lab) — Media Archive
- **URL:** [https://www.macaulaylibrary.org](https://www.macaulaylibrary.org)
- **Data:** World's largest scientifically archived collection of wildlife media: 50+ million digital audio, photo, and video assets. Audio: bird, mammal, amphibian, and insect vocalizations. Video: behavior, courtship, nesting. Photo: morphology, plumage, skin condition. All records have: species, date, location, recorder, catalog number (MLXXXXXXX), quality notes, and behavior tags. Accessible via eBird's data infrastructure.
- **Access:** No public REST API. Media search via [https://search.macaulaylibrary.org/catalog](https://search.macaulaylibrary.org/catalog) with CSV export of metadata (up to 10,000 records per export for logged-in users). Research requests via Cornell Lab Help Desk ticketing system. Catalog numbers in CSV enable batch media requests. Bulk requests >40,000 assets or >100 species require case-by-case review.
- **Auth:** Free Cornell Lab account for metadata export. Research requests to helpdesk for actual media files. Free for non-commercial research.
- **Rate limits / cost:** No formal API rate limit because there is no API. CSV exports: 10,000 records/query. Media file access: negotiated via helpdesk tickets. Free for research.
- **License:** Non-commercial research: free with attribution. Commercial use: licensing agreement required. Embedding: permitted for non-commercial purposes.
- **Value for WildlifeStats:** Gold-standard reference archive for bioacoustic species identification and abnormal vocalization detection. Pairs with Xeno-canto for acoustic data pipeline; Macaulay provides higher quality vetted recordings (especially for North American species) while Xeno-canto provides open API access and broader geographic coverage. Video data is unique for behavioral health indicators.
- **Integration friction:** The lack of a machine-readable API is a significant friction point. Automation requires: (1) export metadata CSVs by species/region, (2) collate catalog numbers, (3) submit helpdesk tickets. For large-scale ML training data acquisition, establish a formal research partnership with Cornell Lab. eBird API (separate, requires key) provides some overlap for presence/absence data.

---

## Tier 3: Scraping or direct request required

### 3.1 Wildlife Rehabilitation Center Websites — Intake and Outcome Data
- **URL:** Distributed. Key sources include: [Wildlife Center of Virginia](https://www.wildlifecenter.org), [International Wildlife Rehabilitation Council](https://theiwrc.org), [National Wildlife Rehabilitators Association (NWRA)](https://www.nwrawildlife.org), state-level center directories.
- **Data:** Annual or quarterly reports containing: species intake counts, injury/cause categories, release rates, disease diagnoses, mortality rates, geographic origin. Published predominantly as PDFs, some as HTML tables. The Wildlife Center of Virginia publishes a public case database. Some state agencies (e.g., California, Oregon) aggregate permitted rehab center data.
- **Access:** Web scraping (HTML tables, PDF text extraction). Tools: Scrapy or Playwright for JavaScript-rendered pages; pdfplumber or PyMuPDF for PDF extraction. No APIs exist. Requires institution-specific pipeline per center.
- **Auth:** Public reports are freely accessible. Contact for unpublished data.
- **Rate limits / cost:** No rate limits. Some PDFs are password-protected or image-scanned (requiring OCR via Tesseract or similar). Staff time cost is high.
- **License:** Reports are generally freely redistributable for research; verify per institution. Data may be aggregated but individual case records are private under state permit terms.
- **Value for WildlifeStats:** Highest-value data for the rehabilitation component of WildlifeStats that does not exist in any API. Intake data provides: leading causes of wildlife injury (vehicle strikes, window strikes, poisoning, disease), species-specific vulnerability, and temporal trends (e.g., surge in oiled birds during spills). The Wildlife Center of Virginia alone has 100,000+ case records.
- **Integration friction:** Reports use non-standardized taxonomies, cause codes, and outcome definitions. A significant normalization effort is required to map center-specific codes to a WildlifeStats common data model. Many centers publish only annual summaries (not case-level data). PDF text extraction from multi-column layouts is unreliable; table extraction via Camelot or Tabula is more reliable than raw text parsing. Prioritize centers with consistently formatted annual reports: Wildlife Center of Virginia, California Wildlife Center, PAWS Wildlife Center (WA).

---

### 3.2 AnimalDiversity Web (University of Michigan) — Species Accounts
- **URL:** [https://animaldiversity.org](https://animaldiversity.org)
- **Data:** 10,000+ species accounts authored by University of Michigan zoology students and faculty. Fields: physical description, geographic range, habitat, diet, behavior, reproduction, lifespan, economic importance, conservation status, and disease associations. Structured HTML with consistent infobox format. Well-curated for vertebrates and select invertebrates.
- **Access:** No public API. Web scraping via Scrapy or Requests+BeautifulSoup. Page structure is consistent; species pages at `https://animaldiversity.org/accounts/{SpeciesName}/`. Sitemap available.
- **Auth:** Public. [Conditions of Use](https://animaldiversity.org/about/use_conditions/) require attribution and prohibit commercial redistribution without permission.
- **Rate limits / cost:** No documented rate limits. Respect robots.txt. Free.
- **License:** University of Michigan copyright. Non-commercial educational and research use with attribution is permitted.
- **Value for WildlifeStats:** Reliable secondary synthesis for species natural history — behavioral ecology, diet, and habitat notes that provide context for disease transmission risk assessments. Particularly useful for species where IUCN narrative is sparse (invertebrates, small mammals, reptiles).
- **Integration friction:** HTML structure is consistent but not machine-readable without a custom parser. Economic importance sections occasionally contain disease/vector information that needs NLP extraction. Some accounts are outdated (pre-2010 taxonomy); cross-reference scientific names against ITIS before storing.

---

### 3.3 BugGuide / MothPhotographersGroup — Arthropod Citizen Science
- **URL:** [BugGuide](https://bugguide.net) | [Moth Photographers Group](https://mothphotographersgroup.msstate.edu)
- **Data:** BugGuide: 1.5+ million images of insects, spiders, and other arthropods from North America, with community ID-verified identifications, geographic records, host plant associations, and life stage data. Moth Photographers Group: county-level range maps and photo records for ~3,000 North American moth species. Both are highly relevant for vector identification (mosquitoes, ticks, flies, true bugs as disease vectors).
- **Access:** Web scraping. BugGuide has a loose API-like interface (`https://bugguide.net/adv_search/bgsearch.php?taxon={name}`) but no official API. HTML parsing required. Moth Photographers Group: static HTML tables, scrapeable.
- **Auth:** Public. BugGuide Terms require attribution; no commercial use without permission.
- **Rate limits / cost:** No documented rate limits. Polite crawling essential — single-threaded with delays.
- **License:** BugGuide: contributor-retained copyright on images; distribution records are community-contributed. MPG: distribution records freely available.
- **Value for WildlifeStats:** Vector databases are critical for the disease/One Health component. BugGuide's verified arthropod IDs are superior to iNaturalist for specialist taxa. Tick records (Ixodes, Dermacentor, Amblyomma) with host associations are directly actionable for Lyme disease, RMSF, and Ehrlichia range modeling.
- **Integration friction:** No bulk export. Scraping at scale requires politeness throttling and session management. Image IDs are community-verified but accuracy varies by taxonomic group — expert verification rate drops sharply below genus level. Host plant associations are valuable; host animal associations are incompletely recorded.

---

### 3.4 eMammal / Smithsonian — Camera Trap Data
- **URL:** [https://emammal.si.edu](https://emammal.si.edu)
- **Data:** Smithsonian-managed camera trap data repository with hundreds of studies and millions of images from North America and globally. Species detection events with date, time, location, detection count, and associated environmental variables. Integrated with Wildlife Insights for AI species identification.
- **Access:** No open REST API. Data access via project-level requests through the eMammal portal. Public summaries available on the explore page. Bulk data access negotiated with data owners or through Smithsonian partnership. Some datasets published to GBIF via Darwin Core Archive.
- **Auth:** Free account for browsing; data download requires project-specific permission.
- **Rate limits / cost:** Not applicable (no API). Free for research via formal request.
- **License:** Per-study terms set by contributing researchers.
- **Value for WildlifeStats:** Camera trap data provides direct wildlife presence/absence records with timestamps critical for disease range modeling. eMammal's Smithsonian institutional backing ensures data quality and long-term accessibility superior to purely crowdsourced platforms.
- **Integration friction:** No programmatic API is the critical limitation. Establish a Smithsonian data partnership for bulk access. Coordinate with Wildlife Insights (which is building the shared API layer for camera trap data across platforms) to avoid redundant pipelines.

---

### 3.5 Press Release Monitoring — PR Newswire, Business Wire, GlobeNewswire
- **URLs:** [PR Newswire](https://www.prnewswire.com) | [Business Wire](https://www.businesswire.com) | [GlobeNewswire](https://www.globenewswire.com)
- **Data:** Institutional press releases from zoos, aquariums, wildlife agencies, universities, and veterinary organizations. Outbreak declarations (HPAI detections, CWD spread, West Nile surge), study announcements, rehabilitation center opening/closing, new disease case reports. These releases often precede WAHIS, USDA APHIS, or USGS NWHC reports by 24–72 hours.
- **Access:** Web scraping (HTML parsing of search results and full release pages). PR Newswire and Business Wire have no public API. GlobeNewswire provides an RSS feed for some categories. Systematic monitoring requires: keyword-based search scraping + RSS aggregation.
- **Auth:** Public. No account required for reading releases.
- **Rate limits / cost:** No documented rate limits. Polite crawling. Free.
- **License:** Press releases are public-domain for factual content. Images may be copyrighted.
- **Value for WildlifeStats:** Unmatched for institutional early-warning. The institutional hierarchy of disclosure is: press release → news article → preprint → peer-reviewed paper → official database entry. For WildlifeStats to have the freshest data, the press release layer is essential. University news offices (e.g., UC Davis CAHFS, Tufts Cummings School) regularly announce outbreak findings before formal publication.
- **Integration friction:** No structured data — natural language processing is required to extract entities (species, pathogen, location, count). Pages are JavaScript-rendered; Playwright or Selenium required. Build entity extraction pipeline targeting: species mentions, pathogen names, geographic entities, and outcome/count statements.

---

### 3.6 FOIA Requests — Federal and State Agency Data
- **URLs:** [FOIA.gov](https://www.foia.gov) | [MuckRock](https://www.muckrock.com) | [USFWS FOIA](https://www.fws.gov/program/fws-freedom-information-act-foia)
- **Data:** Federal agency datasets not published on portals: USDA APHIS wildlife disease surveillance spreadsheets, USFWS rehabilitation permit databases, state wildlife agency injury/mortality databases, necropsy records, and enforcement actions. MuckRock tracks submitted requests and publishes received documents publicly.
- **Access:** Written FOIA requests (email or web form). No API. MuckRock provides a platform to submit, track, and publish FOIA requests and received documents. Processing time: 20 business days statutory, often 3–18 months in practice.
- **Auth:** No authentication for submitting FOIA requests (U.S. residents and organizations). MuckRock account required to use their platform.
- **Rate limits / cost:** No rate limits. First 2 hours of search time and first 100 pages of duplication are free; additional fees possible for large requests. MuckRock charges ~$20/request for filing assistance.
- **License:** Government records received via FOIA are generally public domain. Check for privacy redactions.
- **Value for WildlifeStats:** Last-resort but high-value path for data that is collected but not published. APHIS Wildlife Services kill/removal data, USFWS depredation permit databases, and state CWD surveillance data are routinely requested and received via FOIA. MuckRock's public database of already-received documents is a first-stop: search before filing.
- **Integration friction:** Long wait times make FOIA unsuitable for real-time acquisition but essential for historical baseline datasets. Received documents are predominantly PDFs requiring OCR and NLP extraction. Response quality varies widely by agency — USFWS and USGS have dedicated FOIA offices with reasonable response times; state fish and wildlife agencies vary from excellent to non-responsive.

---

### 3.7 ORCID / ResearchGate — Researcher Direct Contact
- **URLs:** [https://orcid.org](https://orcid.org) | [https://www.researchgate.net](https://www.researchgate.net)
- **Data:** ORCID: researcher identity, affiliation, works, funding, and peer review records. Public API exposes profiles with researcher-consented public data. ResearchGate: researcher profiles, paper uploads, Q&A, and dataset shares (not machine accessible via API).
- **Access:** ORCID Public API: OAuth2, free. Endpoint: `https://pub.orcid.org/v3.0/{orcid_id}/works`. ResearchGate: no API; manual contact only.
- **Auth:** ORCID: register for Public API credentials (free, OAuth2). ResearchGate: manual researcher contact.
- **Rate limits / cost:** ORCID: reasonable academic use. Free for non-commercial.
- **License:** ORCID public data is CC0 for researcher-marked public fields.
- **Value for WildlifeStats:** Enables identification of active researchers in specific disease areas for direct dataset requests and collaboration. Particularly valuable for very specific datasets (e.g., 20 years of mountain lion necropsy data from a single lab) that will never reach a public repository.
- **Integration friction:** ORCID provides researcher identity but not paper content. ResearchGate is not machine accessible and is explicitly a manual outreach tool. Response rates from cold researcher contacts are low (~15–25%); warm introductions via shared citation network are more effective.

---

## Tier 4: Commercial / institutional only

### 4.1 Web of Science — Comprehensive Literature Index
- **URL:** [https://clarivate.com/webofsciencegroup/](https://clarivate.com/webofsciencegroup/) | API: [https://clarivate.com/academia-government/scientific-and-academic-research/research-discovery-and-referencing/web-of-science/web-of-science-apis-and-xml-data/](https://clarivate.com/academia-government/scientific-and-academic-research/research-discovery-and-referencing/web-of-science/web-of-science-apis-and-xml-data/)
- **Data:** 90+ million records from 1900–present across Web of Science Core Collection, BIOSIS Previews, Zoological Record, and MEDLINE. Zoological Record is uniquely valuable — the world's oldest continuing zoological bibliographic database, covering taxonomy, behavior, ecology, and physiology from 1864 onward. Citation indices, Journal Impact Factor, InCites metrics, and normalized subject categories.
- **Access:** Suite of REST APIs (Starter, Expanded, Lite tiers). Standard XML feeds for bulk data. Ad-hoc XML datasets. Journal Citation Reports API. Requires institutional subscription for full access.
- **Auth:** Institutional subscription + API key. Non-commercial academic access available via affiliated institution.
- **Rate limits / cost:** Institutional subscription pricing (typically $10,000–$100,000+/year depending on institution size). API rate limits set per subscription tier.
- **License:** Licensed data — redistribution restricted. Usage is for internal research and reporting only.
- **Value for WildlifeStats:** The Zoological Record is the primary reason to pursue institutional WoS access — it provides 160 years of continuous zoological literature coverage with expert-curated taxonomic indexing not available in PubMed or OpenAlex. Coverage of non-MEDLINE veterinary and wildlife journals (Oryx, Biotropica, African Zoology) is superior to free alternatives.
- **Integration friction:** Requires institutional affiliation. API terms prohibit bulk redistribution of records. For WildlifeStats as a public database, any WoS-derived data must be carefully scoped to only the fields legally redistributable under the license. Recommend using WoS solely for internal metadata enrichment, not as a redistributed source layer.

---

### 4.2 Scopus / Elsevier — Biomedical and Veterinary Literature
- **URL:** [https://www.scopus.com](https://www.scopus.com) | API: [https://dev.elsevier.com](https://dev.elsevier.com)
- **Data:** 90+ million records from 25,000+ journals including most major veterinary and wildlife medicine titles. Embase (biomedical indexing, including veterinary drugs and disease records), ScienceDirect (full-text of Elsevier journals), Engineering Village, and SciVal (research metrics).
- **Access:** Elsevier Developer Portal REST APIs. Non-commercial academic access is free for most APIs (not SciVal or Embase) for researchers at subscribing institutions.
- **Auth:** API key from Elsevier Developer Portal. Full access requires institutional subscription to Scopus/ScienceDirect.
- **Rate limits / cost:** Default API quotas vary by service. Commercial use requires API license agreement.
- **License:** Licensed. Redistribution restricted. Non-commercial research use permitted for institutional subscribers.
- **Value for WildlifeStats:** Strong for veterinary pharmacology (drug treatment outcome data), Embase coverage of European and Asian wildlife disease journals, and Engineering Village for wildlife monitoring technology papers. Scopus author disambiguation is superior to OpenAlex for tracking researcher output over time.
- **Integration friction:** Same as WoS regarding redistribution restrictions. The Scopus API freely available to academic institutions provides metadata only (not full text) without ScienceDirect subscription. Embase access is restricted even for academics without a specific Embase subscription.

---

### 4.3 Wildbook / Wild Me — Individual Animal ID Platform
- **URL:** [https://wildme.org](https://wildme.org) | Instance: [https://wildbook.org](https://wildbook.org) | Docs: [https://wildbook.docs.wildme.org](https://wildbook.docs.wildme.org)
- **Data:** Photo-identification databases for specific wildlife populations: African wild dogs, whale sharks, manta rays, humpback whales, cheetahs, and 80+ other species across 70+ species-specific Wildbook deployments. Each individual animal record contains: sighting history, GPS locations, life stage, social associations (group membership), health notes, and ML annotation metadata (bounding boxes, embeddings). Open-source platform (GitHub: WildMeOrg/Wildbook), but individual deployments are institutionally operated.
- **Access:** REST API for each Wildbook deployment instance. No unified cross-species API. Individual deployment access negotiated with the operating institution. The Wildbook platform code is open source (MIT license) and self-deployable.
- **Auth:** Per-instance. Researchers retain full ownership and control. Data access is negotiated with the operating research group.
- **Rate limits / cost:** Deployment-dependent. Wild Me provides hosted instances (pricing not public). Open-source self-hosted is free.
- **License:** Per-deployment. Most deployments use restricted access for identified individuals (to prevent poaching); some publish summarized datasets.
- **Value for WildlifeStats:** Unique for individual-level longitudinal health records — tracking the same animal across multiple sightings, documenting disease progression, and linking health events to movement and social data. Most relevant for long-lived, individually identifiable species (cetaceans, large carnivores, elephants, sharks).
- **Integration friction:** No unified API across deployments. Each of 70+ instances requires a separate data agreement. The ML matching pipeline (pattern recognition, contour matching) is impressive but computationally intensive and requires GPU infrastructure to run locally. For WildlifeStats, the pragmatic path is species-specific partnerships with high-value Wildbook deployments (whale sharks, African wild dogs) rather than attempting broad coverage.

---

### 4.4 BOLD Systems — DNA Barcodes of Life
- **URL:** [https://www.boldsystems.org](https://www.boldsystems.org) | Portal API: [https://boldsystems.org/data/api/](https://boldsystems.org/data/api/)
- **Data:** 20.6 million public DNA barcode records representing 1.7 million species. Each record: specimen ID (processid), species identification, COI barcode sequence, collection location (country, province, GPS), collection date, collector institution, and identifier. Follows the Barcode Core Data Model (BCDM). Supports the iBOL BIOSCAN initiative (high-throughput metabarcoding of environmental samples).
- **Access:** BOLD5 REST API. Endpoint: `/api/query` with `scope:term` query format. Results paginated at 1,000 records/call (max 1 million per query). Larger queries require email request to support@boldsystems.org. Darwin Core TSV and JSON exports supported. Query token valid for 24 hours.
- **Auth:** No authentication for public portal API. Institutional access for private records.
- **Rate limits / cost:** 1 million record cap per query. Free for public records.
- **License:** Public records freely accessible. Data sharing follows BOLD contributor agreements.
- **Value for WildlifeStats:** DNA barcoding enables definitive species identification from environmental samples — eDNA from water/soil, fecal samples, and parasites/vectors. The BIOSCAN metabarcoding pipeline will provide unprecedented taxonomic resolution for disease vector communities. Critically useful for cases where morphological ID of parasites or vectors is ambiguous.
- **Integration friction:** The BOLD5 API (new) replaced BOLD4; some documentation and community tools still reference the old API. Query syntax uses a custom `scope:field:term` format that requires pre-validation via the `/api/query/preprocessor` endpoint. Sequences are COI-only for animals; coverage is strong for insects and vertebrates but weak for fungi and protists critical to One Health.

---

### 4.5 Maxar / Planet — Satellite-Detected Wildlife Counts
- **URL:** [https://www.maxar.com](https://www.maxar.com) | [https://www.planet.com](https://www.planet.com)
- **Data:** High-resolution satellite imagery (30cm GSD for Maxar) enabling automated detection of large-bodied wildlife from space. Applications: penguin colony counts, elephant population surveys, whale detection in coastal waters, and monitoring of aggregation sites. Machine learning models applied to imagery to count individuals. Planet provides daily global coverage at 3m GSD.
- **Access:** Commercial API with imagery tile endpoints. Machine learning wildlife detection models are typically run by the vendor or research partners, not available as a standalone API.
- **Auth:** Commercial contract required.
- **Rate limits / cost:** Commercial pricing. Maxar imagery: $15–$35/km² for standard product. Research partnerships available via Maxar's academic program. Planet provides free academic access for some research programs.
- **License:** Commercial license. Derived analysis products (counts) may be redistributable.
- **Value for WildlifeStats:** Primarily relevant for population denominator data at monitored aggregation sites — penguin colonies, rookeries, migration bottlenecks. Not actionable for individual-animal health monitoring but useful for contextualizing disease events against known population size. The marginal value for WildlifeStats is specialized; prioritize only for flagship population monitoring use cases.
- **Integration friction:** Highest integration cost of any source in this report. Requires computer vision expertise, significant cloud compute, and commercial imagery licensing. Better approached via research partnerships with groups that already have imagery analysis pipelines (e.g., Zoological Society of London, British Antarctic Survey, NCEAS).

---

### 4.6 PANGAEA — Earth and Environmental Science Data
- **URL:** [https://www.pangaea.de](https://www.pangaea.de)
- **Data:** 450,000+ published datasets in Earth and environmental sciences. Relevant for WildlifeStats: oceanographic conditions linked to marine mammal strandings, environmental contaminant data tied to wildlife poisoning events, climate variables at wildlife monitoring sites. Supports Schema.org/Dataset metadata for all records. OAI-PMH harvesting for metadata.
- **Access:** REST API for numerical and textual data. OAI-PMH at `https://ws.pangaea.de/oai/provider`. ORCID login for user account linking. SOAP and REST web services.
- **Auth:** ORCID login for upload; data access is open (read).
- **Rate limits / cost:** No documented limits. Free and open.
- **License:** CC-BY for most datasets; check per-dataset.
- **Value for WildlifeStats:** Primarily an environmental context layer — linking disease events to SST anomalies during harmful algal bloom events, or correlating contaminant levels (PCBs, PFAS) in marine mammal tissues with immune suppression and disease susceptibility. Less central than the biological data layers but valuable for One Health analyses.
- **Integration friction:** Data model is highly heterogeneous — each dataset has its own variable structure. The OAI-PMH metadata layer is the entry point; individual dataset access then requires parsing dataset-specific tabular formats. PANGAEA uses the Integrated Ocean Observing System (IOOS) and PANGAEA-specific terminology not mapped to Darwin Core.

---

## Additional Sources (Reference)

### Catalogue of Life (COL ChecklistBank)
- **URL:** [https://www.catalogueoflife.org](https://www.catalogueoflife.org) | API: [https://api.catalogueoflife.org/](https://api.catalogueoflife.org/)
- REST API (OAS3), actively developed, not yet v1.0. Free, open. Maintained jointly with GBIF. The primary species checklist behind the GBIF taxonomic backbone. Use alongside ITIS for a dual-backbone taxonomic resolution strategy.

### Global Names Architecture (GNA / GNverifier)
- **URL:** [https://globalnames.org](https://globalnames.org) | GNverifier: [https://verifier.globalnames.org](https://verifier.globalnames.org)
- REST API for name verification, parsing, fuzzy matching, and reconciliation. Free, open, no key. Essential for resolving name strings across sources — accepts OCR-degraded names, abbreviations, and authority variants. TSV and JSON output. The `gnparser` library can be embedded in ingestion pipelines.

### Symbiota / SCAN — Community Specimen Records
- **URL:** [https://symbiota.org](https://symbiota.org) | [https://scan-all-bugs.org](https://scan-all-bugs.org)
- Community-curated natural history specimen portals with Darwin Core Archive publishing. Data downloadable as DwC-A zips from individual portals. No unified API — access portal by portal. Free, open CC licensing. Best for arthropod (SCAN) and regional vascular plant co-occurrence data relevant to vector habitat modeling.

### IPT (GBIF Integrated Publishing Toolkit) — Darwin Core Publishing
- **URL:** [https://ipt.gbif.org](https://ipt.gbif.org)
- The standard tool for publishing Darwin Core Archive datasets to GBIF. Supports RSS feed endpoints for automated data ingestion. Installing IPT creates a machine-readable endpoint at `{ipt_url}/rss.do`. Essential infrastructure for WildlifeStats to both ingest and publish data.

### Mongabay / High Country News (HCN) — Environmental Journalism
- **URL:** [https://mongabay.com](https://mongabay.com) | [https://hcn.org](https://hcn.org)
- No public API. Web scraping or RSS aggregation. Mongabay's Data Studio (launched 2024) provides visualizations but not raw data API access. Both provide high-quality, fact-checked wildlife and conservation reporting that often surfaces emerging issues before scientific publication.

---

## Recommended ingestion priority order

The following 15 sources are ranked by the product of **data value for WildlifeStats** × **accessibility** (inverse of integration friction):

| Rank | Source | Justification |
|------|--------|---------------|
| **1** | **PubMed / PubMed Central** | Foundational literature layer. Free, open API, 10 req/sec with key. 37M citations + 10M full-text articles covering all veterinary and zoonotic disease domains. MeSH-structured retrieval. Start here for the literature mining pipeline. |
| **2** | **OpenAlex** | CC0 citation graph with 250M works. Quarterly bulk snapshot eliminates API costs. Best complement to PubMed for non-MEDLINE journals. Topic filtering enables precise WildlifeStats-relevant corpus extraction. |
| **3** | **GBIF Occurrence API** | 2.5B occurrence records, Darwin Core standard, free, no key for read. The baseline species distribution layer for every geographic analysis. Async download API handles large queries gracefully. |
| **4** | **IUCN Red List API** | Conservation context for every species. Free token, no rate limit. Threat classification maps directly to rehabilitation cause-of-harm taxonomy. Narrative text enables NLP extraction of disease associations. |
| **5** | **GDELT DOC API** | Real-time disease outbreak early warning. No auth, no rate limit, free. Daily cron job against wildlife disease keyword set provides days-to-weeks advance notice of HPAI/CWD/rabies events vs. official channels. |
| **6** | **ITIS Web Service** | Taxonomic backbone resolver. No auth, no rate limit, public domain. Every species from every other source should resolve through ITIS first. Prevents downstream taxonomy-induced data siloing. |
| **7** | **bioRxiv / medRxiv API** | Preprint early access for emerging research. No auth, no rate limit. Critical for fast-moving zoonotic spillover events. EcoEvoRxiv via OSF API adds ecology preprints. |
| **8** | **Xeno-canto API** | 800K+ wildlife audio recordings, open API, 1 req/sec, CC-licensed audio. Direct ingest for bioacoustic health monitoring. No auth required. |
| **9** | **Wikidata SPARQL** | Cross-linking hub for taxonomic IDs, disease associations, and geographic ranges. CC0. Weekly bulk dumps preferred for scale. Enables multi-source joins in a single query. |
| **10** | **BHL API** | 60M pages of historical biodiversity literature with OCR text. Free key, no documented rate limit. Irreplaceable for pre-1950 disease and taxonomy records. Bulk name-occurrence export for text mining. |
| **11** | **Semantic Scholar API** | Citation graph complementing OpenAlex, with snippet search enabling sentence-level extraction from full-text papers. Free key, reasonable rate limits. Best for identifying highly influential wildlife disease papers. |
| **12** | **Crossref API** | Data paper discovery and DOI metadata enrichment. Free polite pool (10 req/sec with mailto). Identifies datasets linked to wildlife disease literature. |
| **13** | **Wildlife Rehab Center PDFs** | Highest unique value for the rehabilitation domain — no other source provides intake/outcome data. High effort but high yield. Begin with Wildlife Center of Virginia (largest public case database) then expand to NWRA member directories. |
| **14** | **Open Tree of Life API** | Phylogenetic context for disease susceptibility modeling. No auth, no rate limit, CC0. Essential for clade-level disease risk queries. |
| **15** | **BOLD Systems API** | DNA barcode repository for definitive species ID from environmental samples. No auth for public records, free. Increasing relevance as eDNA surveillance methods proliferate. Prioritize for vector/parasite identification pipeline. |

---

*Report prepared for WildlifeStats national research framework. Sources verified as of June 2025. API endpoints and rate limits subject to change; verify against primary documentation before production deployment. Crossref rate limit structure updated November 2025 per [Crossref announcement](https://www.crossref.org/blog/announcing-changes-to-rest-api-rate-limits/). OpenAlex moved to paid API key model with $1/day free credit as documented at [docs.openalex.org](https://docs.openalex.org/). BOLD transitioned to BOLD5 with new API architecture at [boldsystems.org/data/api/](https://boldsystems.org/data/api/).*
