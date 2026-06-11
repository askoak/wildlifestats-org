# Zenodo deposit kit — WildlifeStats Synthetic Admissions Cube v1.1.0

**Issued:** 2026-06-11 07:53 ET
**Audience:** Mike (depositor of record) and architect/engineer for tracking
**Mike's Zenodo identity:** GitHub login via `mike@michaeloak.com`
**Purpose:** Paste-fill kit so the Zenodo "New upload" form takes ~5 minutes instead of ~30. Replaces the `10.xxxx/wildlifestats.snapshot.2026Q2` placeholder on `/methodology.html` and `/governance.html` with a real, durable DOI.

## §1 — Quick steps (the actual deposit flow)

1. Go to https://zenodo.org → top-right "New upload"
2. On the upload form, paste-fill each field below in order
3. Drag the two files from §3 into the file area
4. Click "Save" then "Publish"
5. Copy the assigned DOI (form `10.5281/zenodo.<N>`) and paste it back to architect

That's it. Zenodo issues the DOI immediately on publish.

## §2 — Form field paste kit

### Resource type
**Dataset** (radio button)

### Files
See §3 below — two files to upload.

### Basic information

**Digital Object Identifier**: leave blank — Zenodo mints one on publish.

**Publication date**: 2026-06-10 (the date the cube was generated; recorded in the meta file as `2026-06-10T19:00:00Z`)

**Title**:
```
WildlifeStats Synthetic Wildlife Rehabilitation Admissions Cube, v1.1.0
```

**Creators**:

| Family name | Given names | Affiliation | ORCID |
|---|---|---|---|
| Oak | Michael | Michael Oak Advisors | (your ORCID if you have one — otherwise leave blank) |
| WildlifeStats Consortium | (use as second creator with type "Organization") | — | — |

**Description** (paste the markdown below — Zenodo renders it):

```markdown
A deterministic synthetic dataset of one million wildlife rehabilitation
admission records distributed across all 50 U.S. states and the District of
Columbia, covering 2017–2025. The dataset is structurally calibrated to be
consistent with patterns described in published wildlife rehabilitation and
wildlife-health literature; it is not a fit to any real institution's records,
and no real center's data is incorporated.

The cube is generated from regional species archetypes, latitude-modulated
seasonality, and admission-reason base distributions documented in the
parameter provenance table at
https://wildlifestats.org/methodology.html#parameter-provenance.
Reproducibility: with a fixed master seed of 42, the generator produces
byte-identical output on every run.

**Dimensions:** year (2017–2025), month, county FIPS (3,143 counties + DC),
state postal code (51), taxonomic class, species archetype (42), admission
reason, outcome, disposition.

**Schema:** documented at
https://wildlifestats.org/methodology.html and in the source repository at
https://github.com/askoak/wildlifestats-org.

**Intended use:** methodology demonstration, schema validation, framework
testing, and as a reference layer for analytical workflows that will later
ingest real partner data. **Not** a substitute for measured rehabilitation
records. **Not** a fit to any specific institution.

**Calibration sources:** Henger et al. 2021 (PLoS ONE), McRuer et al. 2017
(Journal of Wildlife Diseases), U.S. Fish & Wildlife Service 2024
*Conservation Value of Wildlife Rehabilitation*, Loss et al. 2013 (Nature
Communications), Doherty et al. 2016 (PNAS), USGS National Wildlife Health
Center WHISPers. Full per-parameter source attribution is in the parameter
provenance table on the methodology page.

**Known limitations and explicit unfitted priors** are documented in the
parameter provenance table and on the WildlifeStats methodology page. Year-
over-year trend weights, seasonality amplitudes by latitude band, and the
regional species archetype tables are unfitted synthetic priors pending
validation against real multi-center data.

**WildlifeStats** is a national research framework for wildlife
rehabilitation, disease, injury, and One Health data. Project home:
https://wildlifestats.org. Source repository:
https://github.com/askoak/wildlifestats-org.
```

### License

**License**: **Creative Commons Attribution 4.0 International (CC-BY-4.0)**

### Keywords (paste comma-separated)

```
wildlife rehabilitation, synthetic data, wildlife disease, One Health, wildlife medicine, biodiversity informatics, reproducible research, USGS WHISPers, rehabilitation medicine, citizen science, deterministic synthetic dataset, county-level wildlife admissions, regional species archetypes, wildlife mortality, wildlife conservation
```

### Subjects / Communities

Search and add: **Open Data** community (optional but standard for openly-licensed datasets).

### Funding / Grants

Skip (none applicable; this is a Michael Oak Advisors independent research initiative).

### Related identifiers

Add the following one at a time (Zenodo lets you add multiple):

| Relation | Identifier | Resource type |
|---|---|---|
| is supplement to | https://wildlifestats.org/methodology.html | Other |
| is described by | https://wildlifestats.org/governance.html | Other |
| is documented by | https://github.com/askoak/wildlifestats-org | Software |

### Version

```
1.1.0
```

(Future quarterly snapshots get 1.2.0, 1.3.0, etc. Each gets its own deposit DOI; Zenodo also auto-creates a "concept DOI" that always resolves to the latest version.)

### Language

**English (eng)**

### Notes (optional but recommended — paste exactly)

```
This is a synthetic dataset. It is not derived from any real wildlife
rehabilitation organization's records. Researchers using this dataset must
cite both the deposit DOI and the project methodology page. Quarterly
versioned snapshots are planned; see https://wildlifestats.org/governance.html
for the snapshot policy.
```

## §3 — Files to upload

Two files, downloaded directly from the live site (no manual file prep needed):

| Source URL | Local filename to upload | Purpose |
|---|---|---|
| https://wildlifestats.netlify.app/data/cube/admissions-cube.json | `admissions-cube-v1.1.0.json` (rename on download — Zenodo shows the filename) | The cube itself (25 MB) |
| https://wildlifestats.netlify.app/data/cube/admissions-cube.meta.json | `admissions-cube-v1.1.0-meta.json` | The meta block — version, seed, generation timestamp, dimension summary |

**On macOS or Windows**, right-click each URL → Save As, then drag both files into Zenodo's upload area.

Optionally, also upload a PDF of the methodology page for archival permanence (the live URL could change someday). Skip this for the v1.1.0 deposit if it adds friction — the methodology lives on GitHub in any case and the `is described by` related identifier covers it.

## §4 — After publish

Paste the issued DOI (form `10.5281/zenodo.<N>`) into a follow-up to architect. Architect will:

1. Commit the DOI to `wildlifestats/_build/cube-doi.txt`
2. Replace `10.xxxx/wildlifestats.snapshot.2026Q2` on `/methodology.html` and `/governance.html` with the real DOI
3. Update the CSV download citation snippet template in `assets/js/data-explorer.js` to reference the real DOI
4. Update the secure-tier spec's quarterly-snapshot DOI placeholders to the same real value
5. Move this deposit kit file to `docs/handoff/closed/` once the replacements ship

## §5 — Future quarterly snapshots

When v1.2.0 ships (schema fix per Phase 4.6f) and again when real partner data layers in:

1. Log back into Zenodo
2. Open the v1.1.0 deposit
3. Click "New version" (Zenodo's UI button)
4. Replace the files, bump the version field, optionally update the description
5. Publish — Zenodo issues a new DOI and links it to the concept DOI

This is a 2-minute operation each time. The concept DOI gives researchers a
"always points to the latest" citation; the version DOIs give "this specific
snapshot, frozen" citation. Both are durable.

— Architect, `measured-fern-jasper-thrush`, 2026-06-11 07:53 ET
