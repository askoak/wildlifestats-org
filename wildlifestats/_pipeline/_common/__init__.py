"""Shared infrastructure for the WildlifeStats multi-source ingestion framework.

Every Phase 9 bucket pipeline imports from here. The discipline rules below
are non-negotiable and apply to every module in this package.

DISCIPLINE RULES (codified from 2026-06-11 09:30 ET credential INBOX):

1. Reference credentials by env var name only. Never dereference a token to
   a local variable that gets logged, printed, returned to the caller, or
   written to disk. Token values exist only inside HTTP request headers
   during a single API call.

2. Never open OneDrive credential files directly. They are the reference
   and audit trail. The Perplexity vault is the live source. If a value
   appears missing from the vault, escalate — do not fall back to disk.

3. Every fetcher MUST honor robots.txt and rate-limit politely. The
   ingestion framework is built on the trust of the orgs being researched;
   that trust is non-renewable.

4. Every extracted record MUST carry a dating envelope (`fetched_at` ISO
   8601, `source_url`, `source_etag` where available). Stale content is
   visible to the consumer; the framework never pretends to a freshness
   it cannot prove.

5. Renderers and dossier writers MUST cite source URLs inline. No
   black-box conclusions. Mike's published principle: "transparent
   reasoning preferred over black-box conclusions."

6. The §19 raw-data separation is enforced at the storage layer
   (supabase_client.py) and audited at the file-content layer
   (scripts/check-no-brwc.sh). Both gates run on every commit.

7. Pipeline isolation: Phase 9 lives at wildlifestats/_pipeline/. It
   does NOT import, copy, or fork code from askoak/moa-pipeline,
   askoak/brwc-*, or any other lane. Architectural patterns may be
   informed by them; code does not cross lanes.
"""

__version__ = "0.1.0"
