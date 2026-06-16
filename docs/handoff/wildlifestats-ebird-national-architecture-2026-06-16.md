# WildStats eBird national architecture note

**Date:** 2026-06-16  
**Author:** Codex  
**Status:** Durable architecture answer after the Virginia denominator pilot  
**Scope:** How the local 8 GB eBird archive relates to WildlifeStats, what the
current pilot does, and what a national rollout would require

## 1. Current reality

WildlifeStats now has a real, bounded eBird sampling-denominator pilot.

That pilot is:

- based on Mike's local archive
- aggregate-only in repo
- Virginia-only in committed output
- good enough to prove the method and the denominator policy
- not yet a national production denominator

The committed pilot output remains:

- `wildlifestats/_pipeline/sources/ebird-sampling/results/virginia_complete_checklist_effort_by_county_week_protocol.csv`
- plus the stratified derivative and compact summary

No raw eBird rows were committed.

## 2. How WildlifeStats uses the local 8 GB archive

The relevant local artifacts are:

- archive: `C:\Users\Hello\Downloads\ebd_sampling_relMay-2026.tar`
- extracted working copy:
  `C:\Users\Hello\OneDrive - Michael Oak Advisors\99_Public Folder\WildStats\ebirdSamplingMay2026`

WildlifeStats does not autonomously "reach into" a PC. The relationship is
much simpler:

1. a human operator runs the local pilot script
2. the script reads Mike's local archive or extracted working copy
3. the script emits aggregate-only derived artifacts
4. only the derived aggregate outputs and provenance notes are committed

That means the archive is a local governed input, not a repo asset and not a
live website dependency.

## 3. Is all 50-state processing required now?

No, not to validate the method.

The Virginia pilot already answers the first hard questions:

- can WildlifeStats parse the archive locally without committing raw rows?
- can it emit a useful aggregate denominator artifact?
- can it make a sane denominator-policy call without re-running the whole
  archive every time?

Those are now answered.

But there is a second question:

Can WildlifeStats make a **national production claim** off this lane yet?

Not yet.

A national public site does not mean every pipeline has to be full-country on
day one. It does mean that any eBird-derived public denominator used for
national claims eventually needs a broader national architecture than one
Virginia pilot.

## 4. Recommended rollout posture

Use a three-step ladder:

### Step 1. Keep the Virginia pilot as the canonical proof

This is already done.

Purpose:

- prove method
- prove governance posture
- prove denominator policy

### Step 2. Add a small multi-state architecture pass before "national production"

Recommended next expansion is not "run all 50 states into git."

Recommended next expansion is:

- define the national output grain
- define the off-repo artifact location
- define refresh cadence
- test a small multi-state subset or regional slice

That is the point where storage and refresh discipline matter more than one
more local pilot.

### Step 3. Move repeated or larger derived outputs out of git

If WildlifeStats wants repeated refreshes, multi-state outputs, or a full
national denominator lane, keep:

- provenance
- hashes
- compact summaries
- code

in repo, but move the heavier derived artifacts out of git.

Preferred path already named in the follow-up note:

- `C:\Users\Hello\OneDrive - Michael Oak Advisors\99_Public Folder\WildStats\artifacts\ebird-sampling\`

If that folder is broadly synced or public-facing, tighten its permissions
before treating it as the governed artifacts store.

## 5. What the data should and should not be used for right now

Safe current uses:

- denominator-method proof
- avian signal-design prototyping
- documentation of the zero-effort stratum policy
- architecture planning for a broader national lane

Not-yet-safe current uses:

- claiming WildlifeStats already has a national eBird denominator in production
- treating one Virginia pilot as if it solves all-state refresh/storage design
- normalizing a habit of storing repeated big derived outputs in git

## 6. Bottom line

The current 8 GB local archive is doing exactly one useful job:

- it is the governed local source for an aggregate-only pilot that proved the
  WildlifeStats eBird denominator method

What comes next is not "rerun everything forever."

What comes next is:

1. keep the Virginia pilot as the proof artifact
2. label it honestly as a pilot
3. design the off-repo national derived-output architecture before scaling
