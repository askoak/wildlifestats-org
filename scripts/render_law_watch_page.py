#!/usr/bin/env python3
"""Render the public /law-watch/ page from normalized local records."""

from __future__ import annotations

import html
import json
from datetime import date, datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "wildlifestats/_pipeline/law_watch/_output/law_watch_enriched.jsonl"
OUTPUT_DIR = REPO_ROOT / "law-watch"
OUTPUT_PATH = OUTPUT_DIR / "index.html"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_records() -> list[dict]:
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for line in INPUT_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("relevance_status") != "in_scope":
            continue
        if record.get("jurisdiction_level") != "federal":
            continue
        if record.get("source_id") not in {"federal_register_api", "regulations_gov_api"}:
            continue
        if not record.get("title") or not record.get("source_url"):
            continue
        key = (str(record.get("source_id")), str(record.get("source_record_id") or record.get("law_watch_id")))
        if key in seen:
            continue
        seen.add(key)
        rows.append(record)
    return rows


def parse_day(raw: str | None) -> date | None:
    if not raw:
        return None
    return date.fromisoformat(str(raw)[:10])


def parse_dt(raw: str | None) -> datetime | None:
    if not raw:
        return None
    cleaned = str(raw).replace("Z", "+00:00")
    return datetime.fromisoformat(cleaned)


def format_day(raw: str | None) -> str:
    value = parse_day(raw)
    if not value:
        return "None listed"
    return f"{value.strftime('%B')} {value.day}, {value.year}"


def format_timestamp(raw: str | None) -> str:
    value = parse_dt(raw)
    if not value:
        return "unknown"
    return f"{value.strftime('%B')} {value.day}, {value.year} at {value.strftime('%H:%M')} UTC"


def short_text(raw: str | None, limit: int = 420) -> str:
    text = " ".join((raw or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def agency_slug(name: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in name)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


TOPIC_LABELS = {
    "endangered_species": "Endangered species",
    "migratory_birds": "Migratory birds",
    "habitat": "Habitat",
    "wildlife_rehabilitation": "Wildlife rehabilitation",
    "disease_surveillance": "Disease surveillance",
    "marine_mammals": "Marine mammals",
}


def topic_label(raw: str) -> str:
    return TOPIC_LABELS.get(raw, raw.replace("_", " ").title())


def stage_bucket(record: dict) -> tuple[str, str]:
    if record.get("comment_open"):
        return ("open_for_comment", "Comment open")
    action_type = str(record.get("action_type") or "")
    status_stage = str(record.get("status_stage") or "")
    policy_stage = str(record.get("policy_stage") or "")
    if "final" in action_type or "final" in status_stage or "final" in policy_stage:
        return ("final", "Final")
    if action_type == "proposed_rule" or "proposal" in policy_stage:
        return ("proposed", "Proposed")
    if action_type == "notice" or status_stage == "notice":
        return ("notice", "Notice")
    return ("other", "Other federal action")


def action_badge(record: dict) -> str:
    action_type = str(record.get("action_type") or "")
    if action_type == "proposed_rule":
        return "Proposed rule"
    if action_type == "notice":
        return "Notice"
    if action_type == "final_rule":
        return "Final rule"
    if action_type:
        return action_type.replace("_", " ").title()
    return "Federal action"


def sort_records(records: list[dict]) -> list[dict]:
    def key(record: dict) -> tuple[int, date, int, date]:
        comment_open = bool(record.get("comment_open"))
        deadline = parse_day(record.get("comment_deadline")) or date.max
        publication = parse_day(record.get("publication_date")) or date.min
        ordinal = -publication.toordinal()
        return (0 if comment_open else 1, deadline, ordinal, publication)

    return sorted(records, key=key)


def metrics(records: list[dict]) -> dict[str, object]:
    open_comments = sum(1 for record in records if record.get("comment_open"))
    agencies = {agency for record in records for agency in (record.get("agency_names") or [])}
    this_week = 0
    today = date.today()
    week_end = date.fromordinal(today.toordinal() + 7)
    for record in records:
        deadline = parse_day(record.get("comment_deadline"))
        if deadline and today <= deadline <= week_end:
            this_week += 1
    refreshed_at = max((record.get("retrieved_at") or record.get("fetched_at") for record in records), default=None)
    return {
        "total": len(records),
        "open_comments": open_comments,
        "agencies": len(agencies),
        "deadline_this_week": this_week,
        "refreshed_at": refreshed_at,
    }


def render_page(records: list[dict]) -> str:
    stats = metrics(records)
    topic_values = sorted({topic for record in records for topic in (record.get("topic_tags") or [])}, key=topic_label)
    agency_values = sorted({agency for record in records for agency in (record.get("agency_names") or [])})

    cards: list[str] = []
    for record in records:
        stage_value, stage_label = stage_bucket(record)
        agencies = record.get("agency_names") or []
        agency_data = "|".join(agency_slug(name) for name in agencies)
        topic_data = "|".join(sorted(record.get("topic_tags") or []))
        source_value = str(record.get("source_id") or "")
        tag_items = [f"<li>{esc(topic_label(tag))}</li>" for tag in (record.get("topic_tags") or [])]
        tags_html = f'<ul class="tag-list">{"".join(tag_items)}</ul>' if tag_items else ""
        comment_deadline = record.get("comment_deadline")
        deadline_text = ""
        if comment_deadline:
            deadline_text = f" · Comment deadline {esc(format_day(comment_deadline))}"
        links = [f'<a href="{esc(record.get("source_url") or "")}" rel="noopener">Official notice</a>']
        if record.get("comment_url"):
            links.append(f'<a href="{esc(record["comment_url"])}" rel="noopener">Comment or docket page</a>')
        links.append(
            f'<a href="{esc(record.get("source_document_url") or record.get("source_url") or "")}" '
            'rel="noopener">PDF or source document</a>'
        )
        detail_bits = []
        if record.get("citation"):
            detail_bits.append(f"Citation {esc(record['citation'])}")
        if record.get("docket_id"):
            detail_bits.append(f"Docket {esc(record['docket_id'])}")
        details_html = ""
        if detail_bits:
            details_html = f'<p class="source-card__detail">{" · ".join(detail_bits)}</p>'

        cards.append(
            f"""        <li class="source-card"
          data-stage="{esc(stage_value)}"
          data-source="{esc(source_value)}"
          data-topic="{esc(topic_data)}"
          data-agency="{esc(agency_data)}"
          data-comment-open="{str(bool(record.get("comment_open"))).lower()}"
          data-publication-date="{esc(str(record.get("publication_date") or ""))}"
          data-comment-deadline="{esc(str(comment_deadline or ""))}">
          <div class="source-card__header">
            <span class="source-badge{' source-badge--open' if record.get('comment_open') else ''}">{esc(stage_label)}</span>
            <span class="source-badge{' source-badge--warning' if action_badge(record) == 'Notice' else ''}">{esc(action_badge(record))}</span>
          </div>
          <h2>{esc(record.get("title") or "")}</h2>
          <p class="source-card__meta">{esc(record.get("source_authority") or "Federal source")} · {esc(", ".join(agencies))} · Published {esc(format_day(record.get("publication_date")))}{deadline_text}</p>
          <p class="source-card__summary">{esc(short_text(record.get("short_summary") or record.get("summary")))}</p>
          {details_html}
          {tags_html}
          <p class="source-card__reason">Why it is in scope: {esc(record.get("relevance_reason") or "Wildlife-related federal source on the allowlist.")}</p>
          <div class="source-card__links">
            {' '.join(links)}
          </div>
        </li>"""
        )

    topic_options = "\n".join(
        f'              <option value="{esc(topic)}">{esc(topic_label(topic))}</option>' for topic in topic_values
    )
    agency_options = "\n".join(
        f'              <option value="{esc(agency_slug(name))}">{esc(name)}</option>' for name in agency_values
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>WildlifeStats — Law Watch</title>
  <meta name="description" content="Federal-first wildlife law watch for wildlife-related notices, proposed rules, and comment deadlines.">
  <link rel="canonical" href="https://wildlifestats.org/law-watch/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="WildlifeStats">
  <meta property="og:title" content="WildlifeStats — Law Watch">
  <meta property="og:description" content="Federal-first wildlife law watch for wildlife-related notices, proposed rules, and comment deadlines.">
  <meta property="og:url" content="https://wildlifestats.org/law-watch/">
  <meta property="og:image" content="https://wildlifestats.org/assets/img/og-default.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+Pro:wght@400;600&amp;display=swap">
  <link rel="stylesheet" href="/assets/css/tokens.css">
  <link rel="stylesheet" href="/assets/css/base.css">
  <link rel="stylesheet" href="/assets/css/site.css">
  <link rel="stylesheet" href="/assets/css/source-pages.css">
</head>
<body>
  <header class="site-header">
    <div class="container">
      <a href="/" class="brand" aria-label="WildlifeStats — home">
        <img src="/assets/img/logo.svg" alt="" width="240" height="64" class="brand__mark">
        <span class="brand__kicker">National Wildlife Rehabilitation Research Framework</span>
      </a>
      <nav class="site-nav" aria-label="Primary">
        <ul>
          <li><a href="/one-health/">One Health</a></li>
          <li><a href="/parks/">National Parks</a></li>
          <li><a href="/wildlife/">Wildlife</a></li>
          <li><a href="/wildlife911/">Wildlife911</a></li>
          <li><a href="/centers/">Centers</a></li>
          <li><a href="/data/">Data</a></li>
          <li><a href="/methodology.html">Methodology</a></li>
          <li><a href="/about.html">About</a></li>
        </ul>
      </nav>
    </div>
  </header>
  <hr class="site-divider">

  <main>
    <div class="container" data-law-watch-root>
      <p class="kicker">Federal-first policy tracker</p>
      <h1>Law Watch</h1>
      <div class="page-intro">
        <p>WildlifeStats Law Watch is a federal-first tracker for wildlife-related notices, proposed rules, and public-comment windows. It is a metadata-plus-link surface, not a legal-advice tool and not a full-text policy archive.</p>
      </div>

      <div class="page-note">
        <p><strong>Scope:</strong> federal items only for now, with links back to official government documents.</p>
        <p><strong>Current live refresh:</strong> this public build reflects the live Federal Register lane refreshed {esc(format_timestamp(stats["refreshed_at"]))}. The Regulations.gov enrichment lane exists in the schema but is not being refreshed in this environment because the required API credential is not configured here.</p>
      </div>

      <section class="metric-grid" aria-label="Summary metrics">
        <div class="metric-card"><strong>{stats["total"]}</strong><span>federal items in scope</span></div>
        <div class="metric-card"><strong>{stats["open_comments"]}</strong><span>open comment windows</span></div>
        <div class="metric-card"><strong>{stats["deadline_this_week"]}</strong><span>deadlines in the next 7 days</span></div>
        <div class="metric-card"><strong>{stats["agencies"]}</strong><span>agencies represented</span></div>
      </section>

      <section class="filter-panel" aria-label="Law Watch filters">
        <h2>Filter the tracker</h2>
        <div class="filter-grid">
          <div class="filter-field">
            <label for="law-watch-search">Search</label>
            <input id="law-watch-search" type="search" data-filter="search" placeholder="Title, summary, docket, species">
          </div>
          <div class="filter-field">
            <label for="law-watch-stage">Stage</label>
            <select id="law-watch-stage" data-filter="stage">
              <option value="all">All stages</option>
              <option value="open_for_comment">Open for comment</option>
              <option value="proposed">Proposed</option>
              <option value="final">Final</option>
              <option value="notice">Notice</option>
              <option value="other">Other federal action</option>
            </select>
          </div>
          <div class="filter-field">
            <label for="law-watch-source">Source</label>
            <select id="law-watch-source" data-filter="source">
              <option value="all">All source lanes</option>
              <option value="federal_register_api">Federal Register</option>
              <option value="regulations_gov_api">Regulations.gov</option>
            </select>
          </div>
          <div class="filter-field">
            <label for="law-watch-topic">Topic</label>
            <select id="law-watch-topic" data-filter="topic">
              <option value="all">All topics</option>
{topic_options}
            </select>
          </div>
          <div class="filter-field">
            <label for="law-watch-agency">Agency</label>
            <select id="law-watch-agency" data-filter="agency">
              <option value="all">All agencies</option>
{agency_options}
            </select>
          </div>
          <div class="filter-field">
            <label for="law-watch-timing">Timing</label>
            <select id="law-watch-timing" data-filter="timing">
              <option value="any">Any timing</option>
              <option value="comment_open">Comment open now</option>
              <option value="last_30_days">Posted in last 30 days</option>
              <option value="deadline_this_week">Deadline this week</option>
            </select>
          </div>
        </div>
        <div class="filter-actions">
          <p class="filter-status" data-visible-count>Showing {stats["total"]} of {stats["total"]} items</p>
          <button type="button" class="filter-reset" data-filter="reset">Reset filters</button>
        </div>
      </section>

      <ul class="card-grid">
{chr(10).join(cards)}
      </ul>

      <div class="empty-state" data-empty-state>
        <p>No current law-watch items match these filters.</p>
      </div>

      <p class="source-disclosure">This page is for awareness and routing only. Always verify legal status, deadline timing, and final text in the linked official government source before relying on it.</p>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <p>WildlifeStats is a research framework. Current dataset is synthetic
      (n=1,000,000) generated from regional distribution models. See
      <a href="/methodology.html">Methodology</a>.</p>
      <nav aria-label="Footer">
        <a href="/governance.html">Governance</a> ·
        <a href="/about.html">About</a> ·
        <a href="/wildlife911/">Wildlife911</a> ·
        <a href="mailto:wildlifestats@michaeloak.com">Contact</a> ·
        <span>2026</span>
      </nav>
    </div>
  </footer>
  <script src="/assets/js/site.js"></script>
  <script src="/assets/js/law-watch.js"></script>
</body>
</html>
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    records = sort_records(load_records())
    OUTPUT_PATH.write_text(render_page(records), encoding="utf-8")
    print(f"Rendered {len(records)} law-watch records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
