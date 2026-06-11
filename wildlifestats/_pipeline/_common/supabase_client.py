"""Supabase client with §19 RLS-aware writes.

Phase 9 storage layer for buckets 02 (firm profile), 03 (publications),
06 (aggregate), 07 (regulatory), 08 (media/academic), 09 (network),
10 (events). Bucket 01 (social) records flow here too — only the
extracted signals, never raw post text. Bucket 05 (raw records) is the
§19 lane-isolated tier; see RLS contract below.

THE §19 RLS CONTRACT (Mike's clarification 2026-06-11):

The Supabase project oamqicylpytbldrnybcc is SHARED between askoak-web
(BRWC lane) and wildlifestats-org (this lane). Physical separation would
require creating a new project (which Mike's Decision C 2026-06-11 chose
NOT to do). Instead, the contract is enforced at the SCHEMA + RLS level:

  Schema prefix          Owner lane           Read access     Write access
  ─────────────────────  ───────────────────  ──────────────  ─────────────
  brwc_*                 askoak-web           brwc role       brwc role
  wildlifestats_*        wildlifestats-org    public-tier     wildlifestats role
  wildlifestats_secure_* wildlifestats-org    wildlifestats   wildlifestats role
  shared_*               either lane          authenticated   either role
                                              (read-only from public)

ANY write from this module that targets a brwc_* schema raises
CrossLaneViolation. ANY write that includes a rehab_org_id matching
BRWC's EIN (54-1641798, the Blue Ridge Wildlife Center org) in a raw-
records context raises CrossLaneViolation. Brand mentions in attributed
public-content tables are allowed (per Mike's §19 clarification —
"the rule was about raw data records only").

This module enforces the contract on the client side; the Supabase
project also enforces matching RLS policies server-side. Both gates
required.

CONTRACT:

  1. Token via creds.get_supabase_token() — never module-level. The token
     is service_role-scoped; treat it as the most sensitive credential
     in the framework.

  2. Every write specifies its target_schema explicitly. No SQL string
     concatenation; use the Supabase REST API's table parameter.

  3. Every record carries fetched_at, source_url, content_hash before
     being accepted by upsert(). Records missing the dating envelope
     raise MissingProvenance.

  4. Bucket 05 (raw records) writes are gated by the lane discipline:
       wildlifestats_secure_raw_records.brwc_*  — REJECTED (always)
       wildlifestats_secure_raw_records.<org>_  — accepted iff org's
                                                  EIN != BRWC's EIN
       brwc_*.* (any table)                     — REJECTED (always)

  5. Aggregate-tier writes (bucket 06) MUST exclude the BRWC EIN from
     any per-org breakdown unless the breakdown is published BRWC-side
     and we are linking, not republishing.

THIS MODULE IS A SCAFFOLD. Engineer wires the actual Supabase REST/PostgREST
calls and the per-bucket schema definitions.
"""

from __future__ import annotations

import json as _json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Optional

from . import creds


# Schemas owned by the WildlifeStats lane. Engineer creates these via
# `apply_migration` (Supabase MCP tool) before the bucket pipelines run.
WILDLIFESTATS_SCHEMAS = (
    "wildlifestats_bucket_01_social_signals",
    "wildlifestats_bucket_02_firm_profile",
    "wildlifestats_bucket_03_publications",
    "wildlifestats_bucket_04_help_content",
    "wildlifestats_bucket_06_aggregate",
    "wildlifestats_bucket_07_regulatory",
    "wildlifestats_bucket_08_media_academic",
    "wildlifestats_bucket_09_network",
    "wildlifestats_bucket_10_events",
    "wildlifestats_secure_bucket_05_raw_records",  # gated by per-org RLS
    "wildlifestats_secure_aggregate_drafts",  # pre-publish staging
)

BRWC_EIN = "54-1641798"  # Blue Ridge Wildlife Center — §19 protected

FORBIDDEN_SCHEMA_PREFIXES = ("brwc_", "askoak_", "moa_")


class CrossLaneViolation(RuntimeError):
    """Raised when a write targets a non-WildlifeStats schema or attempts
    to ingest BRWC's raw-record data through the WildlifeStats lane.
    Trip wire for the §19 contract."""


class MissingProvenance(RuntimeError):
    """Raised when a record lacks the dating envelope (fetched_at,
    source_url, content_hash). Phase 9 records MUST carry these."""


@dataclass
class WriteRequest:
    """One upsert intent."""

    target_schema: str
    target_table: str
    record: dict
    on_conflict: Optional[str] = None  # e.g., 'rehab_org_id,fetched_at'


def upsert(request: WriteRequest) -> dict:
    """Upsert a single record to a WildlifeStats-owned schema.

    Args:
        request: WriteRequest with target_schema + target_table + record.

    Raises:
        CrossLaneViolation: target_schema is not in WILDLIFESTATS_SCHEMAS,
            or schema name matches FORBIDDEN_SCHEMA_PREFIXES, or record
            includes a BRWC EIN in a raw-records context.
        MissingProvenance: record lacks fetched_at, source_url, or
            content_hash.

    Returns: the upserted record as Supabase returned it.

    Implementation note (Phase 9b.2): the three client-side gates below
    are the §19 trip wires; only past all three do we read the credential
    (never at module level) and issue the PostgREST upsert. Per-schema
    routing is via the Content-Profile / Accept-Profile headers, so the
    table parameter is the bare table name (no schema-qualified SQL).
    The server enforces the §19 EIN exclusion independently — a CHECK
    constraint on the bucket-05 raw_records table that no role, including
    service_role, can bypass. Both gates required.
    """
    _validate_target_schema(request.target_schema)
    _validate_provenance(request.record)
    _validate_lane_isolation(request.target_schema, request.record)

    base = creds.get_supabase_url().rstrip("/")
    token = creds.get_supabase_token()
    endpoint = f"{base}/rest/v1/{request.target_table}"
    if request.on_conflict:
        endpoint += f"?on_conflict={request.on_conflict}"

    headers = {
        "apikey": token,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        # Route the write to the owned schema (PostgREST multi-schema).
        "Content-Profile": request.target_schema,
        "Accept-Profile": request.target_schema,
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    body = _json.dumps([request.record]).encode("utf-8")
    req = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = _json.loads(resp.read().decode("utf-8") or "[]")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(
            f"Supabase upsert to {request.target_schema}.{request.target_table} "
            f"failed (HTTP {exc.code}): {detail}"
        ) from None
    return rows[0] if rows else {}


def _validate_target_schema(schema: str) -> None:
    """Raise CrossLaneViolation if schema is not a WildlifeStats schema."""
    for forbidden in FORBIDDEN_SCHEMA_PREFIXES:
        if schema.startswith(forbidden):
            raise CrossLaneViolation(
                f"Target schema {schema!r} starts with forbidden prefix "
                f"{forbidden!r}. WildlifeStats lane cannot write to "
                f"that schema. §19 contract."
            )
    if schema not in WILDLIFESTATS_SCHEMAS:
        raise CrossLaneViolation(
            f"Target schema {schema!r} is not a registered WildlifeStats "
            f"schema. Add it to WILDLIFESTATS_SCHEMAS first and create "
            f"the schema via Supabase apply_migration."
        )


def _validate_provenance(record: dict) -> None:
    """Raise MissingProvenance if dating envelope is incomplete."""
    required = ("fetched_at", "source_url", "content_hash")
    missing = [k for k in required if not record.get(k)]
    if missing:
        raise MissingProvenance(
            f"Record missing required provenance fields: {missing}. "
            f"Phase 9 records MUST carry fetched_at + source_url + "
            f"content_hash."
        )


def _validate_lane_isolation(schema: str, record: dict) -> None:
    """Raise CrossLaneViolation if a BRWC raw record is being written to
    a WildlifeStats raw-records schema."""
    if "_bucket_05_raw_records" in schema:
        ein = record.get("rehab_org_ein", "")
        if ein == BRWC_EIN:
            raise CrossLaneViolation(
                f"BRWC raw records (EIN {BRWC_EIN}) belong in the BRWC "
                f"lane (askoak/askoak-web), not the WildlifeStats lane. "
                f"§19 contract. Brand mentions in attributed public-"
                f"content schemas are allowed; raw data records are not."
            )


def list_lane_schemas() -> tuple[str, ...]:
    """Return the WildlifeStats-owned schema list. Public for callers
    that want to audit the contract from a script."""
    return WILDLIFESTATS_SCHEMAS
