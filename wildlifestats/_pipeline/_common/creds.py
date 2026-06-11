"""Typed credential getters for the Phase 9 ingestion framework.

Every credential is read from os.environ. The env vars are injected by
the Perplexity vault when the bash tool is invoked with the appropriate
api_credentials handle. Token values:
  - are never module-level constants
  - are never logged, printed, or returned outside this module
  - are never written to disk
  - are scoped to a single function call's local variable

USAGE FROM A PIPELINE MODULE:

    from wildlifestats._pipeline._common import creds
    token = creds.get_apify_token()
    # ... use token in a single HTTP request ...
    # token goes out of scope at function end; no leakage

USAGE FROM A BASH INVOCATION:

    bash(
        command='python wildlifestats/_pipeline/buckets/01-social/run.py',
        api_credentials=['custom-cred:api.apify.com',
                         'custom-cred:api.anthropic.com'],
    )

Each handle injects its CUSTOM_CRED_*_TOKEN and CUSTOM_CRED_*_URL env vars
for the duration of that command.

CONSENT GATES: Some credentials require one-time `approve_credential`
consent per thread. The first call to a getter in a new thread may raise
MissingCredentialError; surface that to the caller with a clear remediation
hint ("invoke approve_credential(name=..., host=...) first").

REGISTRY MATCH: The credential handles and env var names below match the
output of `pplx-tool list_credentials`. If the vault rotates a handle, this
module updates; consumers do not.
"""

from __future__ import annotations

import os


class MissingCredentialError(RuntimeError):
    """Raised when a credential is requested but not present in env.

    Includes a remediation hint pointing the caller at the vault handle
    they need to inject.
    """


def _read(env_var: str, vault_handle: str, friendly_name: str) -> str:
    """Internal: read an env var or raise with a clear remediation hint.

    Strips whitespace defensively. Does not log the value.
    """
    val = os.environ.get(env_var, "").strip()
    if not val:
        raise MissingCredentialError(
            f"{friendly_name} not in env. "
            f"Invoke bash with api_credentials=['{vault_handle}']. "
            f"On first use in a thread, you may need to call "
            f"approve_credential(name='{friendly_name}', "
            f"host='{vault_handle.split(':', 1)[1]}') first."
        )
    return val


# Bucket 01 — SOCIAL
def get_apify_token() -> str:
    """Apify API token for bucket 01 (FB, IG, X, TikTok, YouTube actors)."""
    return _read(
        "CUSTOM_CRED_API_APIFY_COM_TOKEN",
        "custom-cred:api.apify.com",
        "Apify API",
    )


# Bucket 02 — FIRM PROFILE (LLM extraction)
def get_anthropic_token() -> str:
    """Anthropic API token for structured extraction (Claude)."""
    return _read(
        "CUSTOM_CRED_API_ANTHROPIC_COM_TOKEN",
        "custom-cred:api.anthropic.com",
        "Anthropic API",
    )


def get_openai_token() -> str:
    """OpenAI API token for cheap-batch extraction fallback."""
    return _read(
        "CUSTOM_CRED_API_OPENAI_COM_TOKEN",
        "custom-cred:api.openai.com",
        "OpenAI API",
    )


# Bucket 03 — PUBLICATIONS (canonical-URL discovery + embeddings)
def get_exa_token() -> str:
    """Exa Search token for canonical-URL discovery (newsletter archives,
    annual reports, publication corpora)."""
    return _read(
        "CUSTOM_CRED_API_EXA_AI_TOKEN",
        "custom-cred:api.exa.ai",
        "Exa Search",
    )


def get_voyage_token() -> str:
    """Voyage AI token for high-quality document-corpus embeddings."""
    return _read(
        "CUSTOM_CRED_API_VOYAGEAI_COM_TOKEN",
        "custom-cred:api.voyageai.com",
        "Voyage AI",
    )


def get_perplexity_token() -> str:
    """Perplexity API token for search/embeddings backbone."""
    return _read(
        "CUSTOM_CRED_API_PERPLEXITY_AI_TOKEN",
        "custom-cred:api.perplexity.ai",
        "Perplexity API",
    )


# Buckets 05 + 06 — STORAGE
def get_supabase_token() -> str:
    """Supabase service_role key for the askoak project. The §19 RLS
    contract gates which schemas a write can touch — see supabase_client.py.
    """
    return _read(
        "CUSTOM_CRED_OAMQICYLPYTBLDRNYBCC_SUPABASE_CO_TOKEN",
        "custom-cred:oamqicylpytbldrnybcc.supabase.co",
        "Supabase service_role (oamqicylpytbldrnybcc)",
    )


def get_supabase_url() -> str:
    """Supabase project URL for the askoak project. Always
    https://oamqicylpytbldrnybcc.supabase.co."""
    return _read(
        "CUSTOM_CRED_OAMQICYLPYTBLDRNYBCC_SUPABASE_CO_URL",
        "custom-cred:oamqicylpytbldrnybcc.supabase.co",
        "Supabase service_role (oamqicylpytbldrnybcc)",
    )


# Bucket 06 — Aggregate DOI minting
def get_zenodo_token() -> str:
    """Zenodo API token for minting DOIs against aggregate-dataset releases.
    Thread-scoped credential — pre-approved from prior DOI work
    (10.5281/zenodo.20643065)."""
    return _read(
        "CUSTOM_CRED_ZENODO_ORG_TOKEN",
        "custom-cred:zenodo.org",
        "Zenodo API",
    )


# Convenience: presence check without raising. Useful for `make` targets
# that want to skip a stage when credentials aren't injected.
def is_present(env_var: str) -> bool:
    """Return True iff the named env var is set and non-empty.

    Does not return the value, does not raise. Safe to log the boolean
    result (the boolean is not a secret).
    """
    return bool(os.environ.get(env_var, "").strip())
