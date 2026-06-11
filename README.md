# wildlifestats-org

[![Live site](https://img.shields.io/badge/live-wildlifestats.netlify.app-2A3F52)](https://wildlifestats.netlify.app)
[![License: CC-BY-4.0](https://img.shields.io/badge/data%20license-CC--BY--4.0-B96F4D)](https://creativecommons.org/licenses/by/4.0/)
<!-- DOI badge will be added below once the v1.1.0 GitHub release triggers
     Zenodo's mint webhook. Expected form:
     [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.<N>.svg)](https://doi.org/10.5281/zenodo.<N>)
-->

Source repository for **WildlifeStats** — a national research framework for
wildlife rehabilitation, disease, injury, and One Health data. Live at
[wildlifestats.netlify.app](https://wildlifestats.netlify.app) (and at
[wildlifestats.org](https://wildlifestats.org) once DNS is wired).

The framework provides a synthetic reference dataset (n = 1,000,000 admission
records), a searchable national database surface, a triage and referral
assistant (Wildlife911 Virginia is the first state edition), and a methodology
pipeline that would aggregate heterogeneous wildlife rehabilitation records
into a common schema if real partner data were contributed under partner
agreements.

## Status

Phase 1 through Phase 6 of the build plan have shipped: structural framework,
data surface, section pages, methodology + governance long-form content, SEO
baseline. Phase 4.6 hardening is in progress (architect-shipped portions live;
engineer queue remains). Phases in flight: 4.5+ source registry (10 Tier-1
sources), 4.5+f-j Flyway social/phenology pipeline, 5a-j secure tier
(researcher access, anonymized micro-data, DOI-stamped snapshots), 7a-g WREN
AI assistant + Wildlife911 LLM pill.

For the canonical phase tracker and engineer-order resolution log, browse
`docs/handoff/`.

## What lives here

Static HTML/CSS/JS + a Python data pipeline. Netlify serves the repo root
directly on every push to `main`.

```
index.html             Homepage
404.html, about.html, governance.html, methodology.html
one-health/, parks/, wildlife/, data/, ingest/, wildlife911/
                       Public section landings

data/cube/             The synthetic n=1,000,000 admissions cube
                       (admissions-cube.json + admissions-cube.meta.json)

assets/css/            Token-driven palette, base typography, site chrome,
                       Wildlife911 dispatcher styling, provenance table
assets/js/             Cube filter UI (data-explorer.js), choropleth,
                       per-section enrichments
assets/maps/           US states TopoJSON for the choropleth

wildlifestats/_build/      Cube generator + validator + species archetypes
wildlifestats/_pipeline/   Partner-data ingestion pipeline (Phase 4.5)
                           + source registry (Phase 4.5+)
                           + Flyway social/phenology pipeline (Phase 4.5+f-j)
                           + sources/flyway-social-seed-top100.csv (99 orgs,
                             BRWC-scrubbed per §19)
wildlifestats/_wren/       WREN test set + Wildlife911 corpus
  wildlife911/
    states/VA/           Canonical Virginia edition (Mike-authored)
    templates/national/  BRWC-scrubbed national template scaffold
    scripts/             render_static_va.py — generates the public
                         Wildlife911 site from the YAML deterministically

docs/handoff/          Architect/engineer coordination, engineer orders,
                       INBOX files, spec amendments, slow-pace logs
docs/research/         Five-agent critique reports (data science, AI safety,
                       wildlife research, product/UX, engineering/ops) +
                       seven public-data-source research appendices
                       + critique synthesis + Phase 4.6 hardening plan

netlify.toml           Build config + security headers + redirects
robots.txt             Allow-list with /secure/ disallow + sitemap reference
sitemap.xml            All public URLs (Phase 6 SEO baseline)
.zenodo.json           Metadata for Zenodo's GitHub-release DOI integration
.github/workflows/     CI: BRWC content guard + link check + HTML validate
                       + cube validation + pipeline dry-run
scripts/               check-no-brwc.sh — §19 content guard
```

The palette and typography are token-driven (`assets/css/tokens.css`) so a
re-brand is a single-file swap. The cube generator is deterministic (seed=42)
and reproducible per the parameter provenance table on the
[methodology page](https://wildlifestats.netlify.app/methodology.html).

## Citing this work

Each release is automatically archived to Zenodo with a Digital Object
Identifier (DOI). To cite the current release, use the DOI shown on the
Zenodo badge above (added once the first release archives). The repository
itself can be cited as:

> Oak, M. and WildlifeStats Consortium (2026). WildlifeStats: a national
> wildlife rehabilitation research framework — synthetic admissions cube
> v1.1.0. Zenodo. https://doi.org/10.5281/zenodo.<N>

A formal citation snippet is also generated inside every CSV download from
the [public data interface](https://wildlifestats.netlify.app/data/).

## Not in this repo

- Real Blue Ridge Wildlife Center patient records and any BRWC-specific
  internal content. Per Standing Orders §19, BRWC content stays in
  [askoak/askoak-web](https://github.com/askoak/askoak-web).
- The Michael Oak Advisors compensation consulting product (also in the
  askoak-web repo on a separate path).
- Real partner wildlife rehabilitation records of any kind. None exist in
  the framework yet; when partner data agreements are signed, those records
  flow through the Phase 4.5 pipeline into `secure/cube/`, never into the
  public tier (per the governance four-tier framework).

## Contact and partnership

For partnership inquiries (state wildlife agency contributions, partner
rehab organization data sharing, academic collaboration), to express interest
in a state edition of Wildlife911, or to report a content error:
[wildlifestats@michaeloak.com](mailto:wildlifestats@michaeloak.com).

## Credentials

This repo does not store credentials. See
[askoak-web's CREDENTIALS-POINTER.md](https://github.com/askoak/askoak-web/blob/main/CREDENTIALS-POINTER.md)
for the canonical credential-handling pattern across all Michael Oak Advisors
ventures (Standing Orders §18).

## CI

`.github/workflows/validate.yml` runs on every PR. Five jobs:

- **BRWC content guard** — `scripts/check-no-brwc.sh` fails if forbidden
  BRWC-identifying strings appear outside sanctioned paths (`docs/handoff/`,
  `docs/research/`, `wildlifestats/_wren/wildlife911/states/`).
- **Internal link check** — `linkinator` checks all internal links resolve.
- **HTML validation** — `html-validate` checks HTML well-formedness.
- **Cube validation** — `validate_cube.py` runs structural and statistical
  checks on the synthetic admissions cube.
- **Pipeline dry-run** — the partner ingestion pipeline runs against the
  committed samples to catch regressions in the cleaning stages.

All five must pass for §14 self-merge eligibility per the Standing Orders.

## License

- Code: MIT
- Data + documentation: CC-BY-4.0
- Wildlife911 corpus (Mike-authored): CC-BY-4.0
