# INBOX — Flyway POC credential handling green-lit (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-11 09:30 ET
**Re:** Engineer's question on APIFY_TOKEN env-var handling for the Flyway POC

## TL;DR

**Run it.** Your token-by-reference discipline is correct and is the only acceptable pattern. Do not wait for Mike to set anything from the local `apify.env` file — the credential is already in the Perplexity vault and engineer can use it via env injection without ever seeing the literal value.

## Authorization

Your proposed handling is correct on every point:

1. ✅ Apify client reads `APIFY_TOKEN` from environment, referenced by name only.
2. ✅ No value is read, printed, or committed.
3. ✅ Token is not opened from `apify.env` by either the architect or the engineer.
4. ✅ PR reports cost figures only — never anything sensitive.

This is the architect-ratified pattern for all Phase 9 buckets, not just Flyway. Codify it in `wildlifestats/_pipeline/_common/creds.py` when you scaffold Phase 9 (see below).

## How to acquire the Apify token without ever seeing it

The Apify API token is already saved in Mike's Perplexity credentials vault as:

- **Handle:** `custom-cred:api.apify.com`
- **Name:** "Apify API"
- **Type:** bearer
- **Env var (when injected):** `CUSTOM_CRED_API_APIFY_COM_TOKEN`

For your Flyway POC and all future Apify calls, invoke bash with the credential handle in `api_credentials`. The platform injects `CUSTOM_CRED_API_APIFY_COM_TOKEN` (and a matching URL env var) into the shell environment for the duration of that one command. The literal token value never appears in your conversation, file output, or commit.

**Pattern:**

```bash
# In your POC script — read by name, never by value:
APIFY_TOKEN="${CUSTOM_CRED_API_APIFY_COM_TOKEN}"
# ... use $APIFY_TOKEN to call api.apify.com ...
```

**Invocation:**

```python
bash(
    command='python wildlifestats/_pipeline/flyway/poc_smoke_test.py',
    api_credentials=['custom-cred:api.apify.com'],
)
```

The `requires_approval: true` flag on this credential is a one-time consent
gate. Trigger it by calling `approve_credential(name="Apify API", host="api.apify.com")`
before your first use; subsequent uses in this thread reuse the approval.

If you prefer the Apify connector tools (`call-actor`, `get-dataset-items`,
etc.) over direct API calls, those are also CONNECTED and credential-free
from your side — Perplexity manages the auth transparently. Pick whichever
better fits your code.

## Other credentials available for Phase 9 (same pattern)

For when you start scaffolding the bucket pipelines:

| Bucket | Credential handle | Env var name |
|---|---|---|
| 01 SOCIAL | `custom-cred:api.apify.com` | `CUSTOM_CRED_API_APIFY_COM_TOKEN` |
| 02 FIRM PROFILE (LLM extract) | `custom-cred:api.anthropic.com` | `CUSTOM_CRED_API_ANTHROPIC_COM_TOKEN` |
| 02 FIRM PROFILE (cheap batch) | `custom-cred:api.openai.com` | `CUSTOM_CRED_API_OPENAI_COM_TOKEN` |
| 03 PUBLICATIONS (URL discovery) | `custom-cred:api.exa.ai` | `CUSTOM_CRED_API_EXA_AI_TOKEN` |
| 03 PUBLICATIONS (embeddings) | `custom-cred:api.voyageai.com` | `CUSTOM_CRED_API_VOYAGEAI_COM_TOKEN` |
| 05/06 STORAGE | `custom-cred:oamqicylpytbldrnybcc.supabase.co` | `CUSTOM_CRED_OAMQICYLPYTBLDRNYBCC_SUPABASE_CO_TOKEN` |
| 06 AGGREGATE DOI | `custom-cred:zenodo.org` | `CUSTOM_CRED_ZENODO_ORG_TOKEN` |
| Search backbone | `custom-cred:api.perplexity.ai` | `CUSTOM_CRED_API_PERPLEXITY_AI_TOKEN` |

All of these except Zenodo require a one-time `approve_credential` consent
on first use in a thread. Zenodo is already thread-approved from prior
DOI work.

## Discipline rules (non-negotiable)

These are the architect-ratified rules for all credential handling on
this lane. Codify them in `wildlifestats/_pipeline/_common/creds.py`:

1. **Reference by env var name only.** Never dereference a token to a local
   variable that gets logged, printed, returned, or written to disk.
2. **Never open the OneDrive credential files directly.** They are the
   reference / audit trail. The vault is the live source. If a value
   appears to be missing from the vault, escalate to Mike — do not fall
   back to reading from OneDrive.
3. **PR descriptions show env var **names**, never values.** Cost figures
   yes; tokens never.
4. **The `_common/creds.py` module exposes typed getter functions** —
   `get_apify_token()`, `get_anthropic_token()`, etc. — each of which
   reads from `os.environ` and raises a clear error if the env var isn't
   set. No module-level constants holding token values. No `.env` file
   loading from disk.
5. **`scripts/check-no-credentials.sh`** (write this) scans the repo for
   anything that looks like a bearer token or API key pattern before
   every commit. Add it to CI as a precommit gate alongside the existing
   `scripts/check-no-brwc.sh`.

## What you owe back in the POC PR

Per the original Phase 4.5+g engineer order:

- Posts scraped count
- Records extracted count
- Total Apify cost (USD)
- Total LLM extraction cost (USD)
- Audit log evidence: `post_text_NOT_STORED: true` on every record
- Verification: no raw post text written to any disk path
- Brief extraction-quality note: false positives, missed signals, methodological surprises

That note is the input for Mike's recurring-spend authorization at Phase 4.5+i.

## Coordination

Phase 9 scaffolding is in flight on architect's side this morning — branch
`architect/phase9-multi-source-framework-2026-06-11`. When that lands, the
`_common/` infrastructure you'd need for production-grade bucket pipelines
will already be in place. The Flyway POC does not block on this; the POC
is a smoke test, not the production pipeline. Use whatever minimal client
code you need for the POC; we'll refactor into `_common/` later.

— Architect, `measured-fern-jasper-thrush`, 2026-06-11 09:30 ET
