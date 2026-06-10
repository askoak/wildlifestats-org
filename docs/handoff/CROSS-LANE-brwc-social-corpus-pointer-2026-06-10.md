# CROSS-LANE — BRWC social corpus pointer (WildlifeStats architect → BRWC architect)

**From:** WildlifeStats Architect, `measured-fern-jasper-thrush` (lane: askoak/wildlifestats-org)
**To:** BRWC Architect, `coastal-thistle-bronze-cairn` (lane: askoak/askoak-web)
**Date:** 2026-06-10 19:34 ET
**Channel:** §20 cross-lane handoff, architect-to-architect, one-way pointer. No data moves with this file.

## What

Mike attached two files in the WildlifeStats session at 19:34 ET and wrote: *"engineer was unaware of this data and the additional data in this same directory `C:\Users\Hello\OneDrive - Michael Oak Advisors\99_Public Folder\BRWC\Social Posts` which I think is all the raw BRWC socials"*

The two files Mike attached:

1. `wildlife_rehab_social_seed_top100.csv` — WildlifeStats-lane content. **No action for BRWC.** This is the 100-row roster (BRWC at rank #8). The WildlifeStats lane already has the BRWC-scrubbed 99-row version committed at `wildlifestats/_pipeline/sources/flyway-social-seed-top100.csv`. No further action.

2. `brwc-educational-replies_2026-06-08-2.csv` — **BRWC-lane content. Action for BRWC architect.**
   - 3,923 rows of comment/reply records
   - Columns: `comment_id, post_id, platform, post_url, post_posted_at_utc, comment_posted_at_utc, comment_author_handle, comment_text, comment_likes, comment_parent_comment_id, post_caption`
   - File location: Mike's local attachment + presumably mirrored in the OneDrive directory below

The directory Mike pointed at:

```
C:\Users\Hello\OneDrive - Michael Oak Advisors\99_Public Folder\BRWC\Social Posts
```

Mike's expectation: this folder holds the raw BRWC social corpus (posts, replies, educational replies, possibly attachments). BRWC engineer was unaware. **BRWC lane should ingest this on its own track.**

## Why this is in WildlifeStats's handoff folder

Per §20, cross-lane coordination happens by architect-authored pointer files in either lane's `docs/handoff/`. The BRWC architect (`coastal-thistle-bronze-cairn`) reads WildlifeStats's `docs/handoff/CROSS-LANE-*.md` files on session start. This is the canonical one-way channel; no commits to askoak-web from this seat.

## What this file is NOT

- Not a data transfer. The actual CSV file Mike attached is **not committed to this repo** and never will be (§19).
- Not an ask for WildlifeStats to do anything beyond posting this pointer.
- Not an authorization for any cross-lane code copy or schema import.

## Action requested of BRWC architect

1. Acknowledge the pointer when the BRWC session next wakes (e.g. one-line PR comment in askoak-web, or a `## Resolution` in BRWC's own handoff folder).
2. Verify the OneDrive folder contents on Mike's behalf (Mike may need to confirm a path, but the architect can ask via §16 if needed).
3. Spec the BRWC ingestion of the social corpus on BRWC's own roadmap. The Flyway social pipeline architecture in `docs/handoff/wildlifestats-flyway-spec-2026-06-10.md` is a reference for the *patterns* (extraction-only, no raw post text storage, per-post audit log) but BRWC is welcome to diverge — different audience, different storage tier, different ToS posture for the BRWC org's own content.
4. If BRWC wants to share anonymized extracted signals from its corpus back to WildlifeStats (Flyway-style aggregate signals only, no BRWC-attributable content), that's a future CROSS-LANE proposal from BRWC, not from WildlifeStats. Default: no flow back. WildlifeStats's BRWC scrub of the roster (§19) stays in effect either way.

## WildlifeStats-side note

The WildlifeStats lane's Flyway roster (`wildlifestats/_pipeline/sources/flyway-social-seed-top100.csv`, 99 orgs) is already correct and matches Mike's attached 100-row file minus the BRWC row. No update needed. The engineer's prior INBOX correctly identified the BRWC file as out-of-scope; this CROSS-LANE pointer is the resolution path for that out-of-scope content.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 19:34 ET
