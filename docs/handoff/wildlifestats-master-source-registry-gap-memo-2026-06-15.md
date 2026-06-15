# WildStats master source registry gap memo

**Date:** 2026-06-15
**Author:** Codex
**Status:** Targeted follow-up only

## Purpose

This memo names the highest-value source families that are still under-defined
after the first seeded registry pass and therefore deserve targeted research
next.

## Highest-value gaps

### 1. Federal and state law-policy source family

Why it matters:

- needed for the planned law watch page
- currently present in planning notes but not yet deeply represented in the
  older research corpus

First targets:

- Federal Register API
- Regulations.gov API
- Congress.gov API
- Open States API
- selected state wildlife bill trackers only after the federal layer is stable

### 2. Wildlife news source family

Why it matters:

- needed for a credible weekly wildlife news page
- current corpus is stronger on data and literature than on a curated news feed
  set

First targets:

- GDELT DOC API
- a curated outlet list for wildlife, conservation, veterinary, and public
  health coverage
- one clustering and dedupe rule set

### 3. State rehabber licensing and permit roster family

Why it matters:

- needed for center verification and Wildlife911 routing confidence
- current state-vet-ag contacts are strong, but many actual rehabber roster
  sources still need targeted acquisition

First targets:

- high-signal pilot states with published rehabber rosters
- a standard roster schema for public permit-holder listings

### 4. Partner-grade clinical systems family

Why it matters:

- WRMD and WILD-ONe are strategically important but operationally restricted
- current registry can name them, but a later secure-tier path needs a more
  explicit access playbook

First targets:

- WRMD metadata and public docs
- WILD-ONe request and governance path
- one secure-only source policy note

### 5. Marine stranding and marine wildlife health family

Why it matters:

- NOAA summary sources are seeded, but research-grade marine records still sit
  behind coordinator or agreement workflows

First targets:

- STSSN coordinator-grade data access path
- MMHSRP individual-record access posture
- one marine data-sharing path note

### 6. Repository and developer-tool family

Why it matters:

- the user explicitly wants websites and repositories
- current seeded registry is still heavier on datasets than on code and tooling

First targets:

- GitHub topic and repo metadata seed set
- open biodiversity or conservation software projects
- one controlled schema for repo records distinct from dataset records

## Recommendation

Do not reopen the whole registry to chase these gaps immediately. Treat them as
bounded follow-on workstreams after the first canonical registry lands and is
reviewed.
