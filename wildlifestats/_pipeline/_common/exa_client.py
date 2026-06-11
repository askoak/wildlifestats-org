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

import json as _json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from . import creds, fetch

EXA_SEARCH_URL = "https://api.exa.ai/search"


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
    token = creds.get_exa_token()
    per_variant = max(max_candidates, 5)

    merged: dict[str, CanonicalCandidate] = {}
    for query in _query_variants(org_name, artifact_type):
        for result in _exa_search(query, token, per_variant):
            url = result.get("url")
            if not url:
                continue
            host = urlparse(url).hostname or ""
            candidate = CanonicalCandidate(
                url=url,
                title=result.get("title") or "",
                snippet=_first_highlight(result),
                confidence=float(result.get("score") or 0.0),
                matched_host=bool(domain_hint) and _host_matches(host, domain_hint),
                artifact_type=artifact_type,
                source_query=query,
            )
            prev = merged.get(url)
            if prev is None or candidate.confidence > prev.confidence:
                merged[url] = candidate

    # Rank: a host-matched candidate always outranks an off-host one (returning
    # the wrong center's URL is a critical error), then by Exa confidence.
    ranked = sorted(
        merged.values(),
        key=lambda c: (c.matched_host, c.confidence),
        reverse=True,
    )
    return ranked[:max_candidates]


def _query_variants(org_name: str, artifact_type: str) -> list[str]:
    """1-3 natural-language query variants for the artifact."""
    variants = [f"{org_name} {artifact_type.replace('_', ' ')}"]
    extra = {
        "newsletter_archive": f"{org_name} newsletter past issues archive",
        "annual_report_pdf": f"{org_name} annual report pdf",
        "annual_report_landing": f"{org_name} annual report",
        "publications_index": f"{org_name} publications library",
        "board_of_directors": f"{org_name} board of directors leadership",
        "mission_statement": f"{org_name} about mission",
    }
    if artifact_type in extra:
        variants.append(extra[artifact_type])
    return variants


def _exa_search(query: str, token: str, num_results: int) -> list[dict]:
    """One Exa /search call. Raises RuntimeError on API/network failure."""
    body = _json.dumps({
        "query": query,
        "numResults": num_results,
        "type": "auto",
        "contents": {"highlights": {"numSentences": 2, "highlightsPerUrl": 1}},
    }).encode("utf-8")
    req = urllib.request.Request(
        EXA_SEARCH_URL,
        data=body,
        headers={"x-api-key": token, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return _json.loads(resp.read().decode("utf-8") or "{}").get("results", [])
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Exa search failed (HTTP {exc.code}): {detail}") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Exa search network error: {exc.reason}") from None


def _first_highlight(result: dict) -> str:
    highlights = result.get("highlights") or []
    if highlights:
        return str(highlights[0])
    return result.get("text", "") or ""


def _host_matches(host: str, domain_hint: str) -> bool:
    """True iff host is, or is a subdomain of, the hinted domain. Tolerant of
    scheme/path/www noise in the hint."""
    hint = domain_hint.strip().lower()
    hint = re.sub(r"^https?://", "", hint).split("/")[0]
    hint = hint[4:] if hint.startswith("www.") else hint
    host = (host or "").lower()
    host = host[4:] if host.startswith("www.") else host
    return host == hint or host.endswith("." + hint)


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
    try:
        env = fetch.fetch(candidate.url)
    except fetch.FetchError:
        # Robots-disallowed, forbidden path, 4xx/5xx, or network error — all
        # normal "could not confirm" outcomes for a guessed URL.
        return False
    if env.http_status != 200:
        return False

    body = env.body or ""
    low = body.lower()
    at = candidate.artifact_type

    if at == "annual_report_pdf":
        return candidate.url.lower().endswith(".pdf") or "%PDF-" in body[:1024]
    if at == "newsletter_archive":
        has_year = bool(re.search(r"\b(19|20)\d{2}\b", body))
        return has_year and ("newsletter" in low or "issue" in low or "archive" in low)
    if at in ("annual_report_landing", "publications_index", "press_releases",
              "research_papers"):
        keywords = at.replace("_", " ").split()
        return any(k in low for k in keywords)
    # mission_statement / board_of_directors / patient_stories — keyword match.
    keywords = at.replace("_", " ").split()
    return any(k in low for k in keywords)
