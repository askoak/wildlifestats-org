"""Exa Search client for canonical-URL discovery.

Bucket 03 (Publications) is the primary consumer. The problem Exa solves:
many wildlife rehab centers publish newsletters, annual reports, and
publication archives at URLs that are NOT indexed well by general search.
Exa's neural-retrieval surface is purpose-built for "find the canonical
URL for {org}'s {artifact_type}."

USAGE PATTERN:

    from wildlifestats._pipeline._common import exa_client
    candidates = exa_client.find_canonical_url(
        org_name="Blue Ridge Wildlife Center",
        artifact_type="newsletter_archive",
        domain_hint="blueridgewildlifecenter.com",
    )
    # candidates: list[CanonicalCandidate], ranked by confidence

CONTRACT:

  1. Every query carries org context (org_name, optional domain_hint) so
     Exa's results can be filtered to the right host. Returning a newsletter
     URL from a different center is a critical error — better to return
     zero results than the wrong one.

  2. Returned URLs are then validated by fetch.fetch() before being added
     to a registry. Exa says "this is probably the newsletter archive";
     fetch confirms it returns HTTP 200 and the page contains content
     consistent with the artifact type.

  3. API budget tracked per call. Exa charges per query; bulk-pulls of
     177+ centers should batch where the API supports it.

  4. Token via creds.get_exa_token() — never module-level.

THIS MODULE IS A SCAFFOLD. Engineer fills in the API plumbing; the contract
above is non-negotiable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


ARTIFACT_TYPES = (
    "newsletter_archive",
    "annual_report_pdf",
    "annual_report_landing",
    "publications_index",
    "press_releases",
    "research_papers",
    "mission_statement",
    "board_of_directors",
    "patient_stories",
)


@dataclass
class CanonicalCandidate:
    """One ranked guess at the canonical URL for an org's artifact."""

    url: str
    title: str
    snippet: str
    confidence: float  # 0.0-1.0, Exa's similarity score
    matched_host: bool  # True iff URL host matches domain_hint
    artifact_type: str
    source_query: str


def find_canonical_url(
    org_name: str,
    artifact_type: str,
    *,
    domain_hint: Optional[str] = None,
    max_candidates: int = 5,
) -> list[CanonicalCandidate]:
    """Find candidate URLs for an org's named artifact.

    TODO[engineer]: implement against the Exa Search API at api.exa.ai.
    Use creds.get_exa_token() for auth. Recommended decomposition:

    1. Validate artifact_type is in ARTIFACT_TYPES; raise otherwise.
    2. Construct a natural-language query like:
       f"{org_name} {artifact_type.replace('_', ' ')}"
       For newsletter_archive, also try: "{org_name} newsletter past issues"
       For annual_report_pdf: "{org_name} annual report filetype:pdf"
    3. Issue 1-3 query variants and merge results, deduplicating by URL.
    4. If domain_hint provided, prefer (do not exclusively filter)
       candidates whose host matches. Mark matched_host accordingly.
    5. Return up to max_candidates, ranked by (matched_host desc,
       confidence desc).

    Callers MUST validate every candidate URL via fetch.fetch() before
    treating it as canonical. Exa is good but not perfect; a candidate
    may 404 or redirect to an unrelated page.
    """
    if artifact_type not in ARTIFACT_TYPES:
        raise ValueError(
            f"Unknown artifact_type: {artifact_type!r}. "
            f"Must be one of: {ARTIFACT_TYPES}"
        )
    raise NotImplementedError(
        "wildlifestats._pipeline._common.exa_client.find_canonical_url() "
        "is a Phase 9 scaffold."
    )


def validate_candidate(candidate: CanonicalCandidate) -> bool:
    """Validate that a CanonicalCandidate actually serves content consistent
    with its claimed artifact_type. Uses fetch.fetch() under the hood.

    TODO[engineer]: implement. For newsletter_archive, look for at least
    one date-stamped item on the page. For annual_report_pdf, verify the
    Content-Type is application/pdf or the URL ends in .pdf and the body
    starts with %PDF-. For mission_statement, verify the page contains
    keywords matching the artifact type.

    Returns True if validation passes, False otherwise. Never raises on
    a validation failure — that's a normal outcome.
    """
    raise NotImplementedError(
        "wildlifestats._pipeline._common.exa_client.validate_candidate() "
        "is a Phase 9 scaffold."
    )
