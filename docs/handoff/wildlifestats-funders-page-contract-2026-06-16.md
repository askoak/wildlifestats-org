# WildStats funders page contract

**Date:** 2026-06-16  
**Author:** Codex  
**Status:** MVP page contract for the public `/funders/` route

## Purpose

The first public funders page is a local-registry render, not a scraping
program and not a fundraising tool. Its job is to let a user quickly scan:

- who the funder is
- what type of funder it is
- what themes it funds
- where the official grant-program surface lives

## MVP fields

Show only the public-safe subset documented in:

- `wildlifestats/_pipeline/sources/sector-funders/PUBLIC_FIELDS.md`

## MVP filters

- search
- funder type
- focus area

## Required guardrails

- label the page as a curated registry, not a live feed
- state that deadlines and eligibility must be verified on the linked official
  page
- do not imply that inclusion equals active open funding today

## What not to do

- do not auto-scrape new funders for MVP
- do not publish a false precision claim around deadlines
- do not turn the page into a grant-writing advice surface
