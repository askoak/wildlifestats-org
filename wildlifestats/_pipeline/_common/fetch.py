"""Robots-aware, rate-limited, cached HTTP fetcher with dating envelope.

Every Phase 9 bucket pipeline uses this for any HTTP GET against a center's
website. Direct urllib/requests calls are forbidden — the trust contract
with the orgs we research is built on respect for their infrastructure.

CONTRACT:

  1. Consult robots.txt for the target host before the first fetch.
     Cache the robots decision per (host, user_agent) for 24 hours.
     If a target path is Disallow'd, return DisallowedByRobots — do not
     fetch.

  2. Default rate limit: 1 request per 2 seconds per host. Configurable
     per-host where a center's robots.txt declares Crawl-Delay.

  3. Cache responses on disk at data/_cache/{host}/{path_hash}.json
     with a freshness TTL (default 7 days). Cache envelope includes
     fetched_at, source_etag, content_hash, http_status. Subsequent
     requests within TTL return the cached envelope without hitting
     the network.

  4. Dating envelope on every response: fetched_at (ISO 8601), source_url
     (the actual URL hit, post-redirects), source_etag (where the server
     provided one). These are propagated into every downstream record so
     consumers can audit freshness.

  5. User-Agent: "WildlifeStats-Research-Bot/0.1 (https://wildlifestats.org;
     wildlifestats@michaeloak.com)". Identifies the framework and provides
     a contact for orgs that want to opt out beyond robots.txt.

  6. Never fetch from URLs at archive paths like /admin, /wp-admin, /login,
     or paths matching /api/. The framework is interested in public-facing
     content only.

THIS MODULE IS A SCAFFOLD. Engineer's Phase 9 implementation fills in the
TODOs below. The contract above is non-negotiable; the implementation
details (which cache library, which HTTP library, which robots parser)
are engineer's call.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


USER_AGENT = (
    "WildlifeStats-Research-Bot/0.1 "
    "(https://wildlifestats.org; wildlifestats@michaeloak.com)"
)

DEFAULT_RATE_LIMIT_SECONDS = 2.0
DEFAULT_CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 days

FORBIDDEN_PATH_PREFIXES = (
    "/admin",
    "/wp-admin",
    "/wp-login",
    "/login",
    "/auth",
    "/api/",
)

CACHE_ROOT = Path("data/_cache")


class FetchError(RuntimeError):
    """Base error for any fetch failure."""


class DisallowedByRobots(FetchError):
    """Raised when robots.txt disallows the requested path.

    The framework respects this absolutely. Do not work around.
    """


class ForbiddenPath(FetchError):
    """Raised when a caller requests a path matching FORBIDDEN_PATH_PREFIXES.

    Internal contract — orgs do not want their /admin probed and we don't
    want to be the framework that does it.
    """


@dataclass
class FetchEnvelope:
    """Every successful fetch returns one of these. Downstream record
    builders carry these fields into the dossier JSON envelopes."""

    source_url: str
    fetched_at: str  # ISO 8601 UTC
    http_status: int
    content_hash: str  # sha256 of body
    body: str  # decoded text
    source_etag: Optional[str] = None
    from_cache: bool = False
    cache_key: Optional[str] = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize for cache write or downstream dossier embedding.
        Does NOT include the body by default — large pages bloat dossiers."""
        return {
            "source_url": self.source_url,
            "fetched_at": self.fetched_at,
            "http_status": self.http_status,
            "content_hash": self.content_hash,
            "source_etag": self.source_etag,
            "from_cache": self.from_cache,
            "cache_key": self.cache_key,
            "notes": list(self.notes),
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cache_key(url: str) -> str:
    """Stable per-URL cache key. Includes host so cache is browsable
    by org during debugging."""
    h = urlparse(url).hostname or "unknown"
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return f"{h}/{digest}.json"


def _forbidden(url: str) -> bool:
    path = urlparse(url).path
    return any(path.startswith(p) for p in FORBIDDEN_PATH_PREFIXES)


def fetch(
    url: str,
    *,
    cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    rate_limit_seconds: float = DEFAULT_RATE_LIMIT_SECONDS,
    force_refresh: bool = False,
) -> FetchEnvelope:
    """Fetch a URL with full Phase 9 discipline.

    TODO[engineer]: implement the full contract. Recommended decomposition:

    1. `_check_forbidden(url)` — raises ForbiddenPath
    2. `_check_robots(url, user_agent=USER_AGENT)` — caches the robots.txt
       per host for 24h; raises DisallowedByRobots
    3. `_cache_lookup(url, ttl=cache_ttl_seconds)` — returns FetchEnvelope
       or None
    4. `_rate_limit_wait(host, min_interval=rate_limit_seconds)` — sleeps
       until the host's last request was at least min_interval ago
    5. `_do_fetch(url)` — actual HTTP GET with USER_AGENT, returns body
       + etag + status
    6. `_cache_write(url, envelope)` — persists envelope + body to
       CACHE_ROOT
    7. Return the envelope

    Robots-respect, rate-limit, cache, and dating are all non-negotiable.
    The implementation choice (requests vs urllib vs httpx) is yours.
    """
    if _forbidden(url):
        raise ForbiddenPath(f"Path forbidden by framework policy: {url}")

    # Scaffold raises NotImplementedError so any caller that drops in before
    # engineer fills this in fails loudly rather than silently bypassing
    # the contract.
    raise NotImplementedError(
        "wildlifestats._pipeline._common.fetch.fetch() is a Phase 9 scaffold. "
        "See the TODO[engineer] block for the implementation contract."
    )


def assert_robots_cached(url: str) -> None:
    """Raise if robots.txt has not been fetched and cached for the URL's
    host within the last 24 hours. Used by bucket pipelines that want to
    verify a host's policy is current before a batch run.

    TODO[engineer]: implement against the same cache structure used by
    fetch().
    """
    raise NotImplementedError(
        "wildlifestats._pipeline._common.fetch.assert_robots_cached() is a "
        "Phase 9 scaffold."
    )
