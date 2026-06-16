#!/usr/bin/env python3
"""Render the public /funders/ page from the curated local funder registry."""

from __future__ import annotations

import html
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "wildlifestats/_pipeline/sources/sector-funders/funders.yaml"
OUTPUT_DIR = REPO_ROOT / "funders"
OUTPUT_PATH = OUTPUT_DIR / "index.html"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_funders() -> list[dict]:
    return yaml.safe_load(INPUT_PATH.read_text(encoding="utf-8")) or []


TYPE_LABELS = {
    "public_charity": "Public charity",
    "private_foundation": "Private foundation",
    "corporate_program": "Corporate program",
    "federal_program": "Federal program",
    "community_foundation": "Community foundation",
}


def type_label(raw: str) -> str:
    return TYPE_LABELS.get(raw, raw.replace("_", " ").title())


def money_label(value: int | float | None) -> str:
    if value in (None, "", 0):
        return "Not published in this registry"
    number = float(value)
    if number >= 1_000_000_000:
        return f"${number / 1_000_000_000:.1f}B"
    if number >= 1_000_000:
        return f"${number / 1_000_000:.1f}M"
    if number >= 1_000:
        return f"${number / 1_000:.0f}K"
    return f"${number:,.0f}"


def slugify(raw: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in raw)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def metrics(funders: list[dict]) -> dict[str, object]:
    known_grants = [float(funder["annual_grants_total_usd_approx"]) for funder in funders if funder.get("annual_grants_total_usd_approx")]
    focus_tags = {tag for funder in funders for tag in (funder.get("focus_areas") or [])}
    funder_types = {str(funder.get("type") or "") for funder in funders if funder.get("type")}
    return {
        "total": len(funders),
        "known_budget_count": len(known_grants),
        "known_budget_total": sum(known_grants),
        "focus_count": len(focus_tags),
        "type_count": len(funder_types),
    }


def render_page(funders: list[dict]) -> str:
    stats = metrics(funders)
    type_values = sorted({str(funder.get("type") or "") for funder in funders if funder.get("type")})
    focus_counts: dict[str, int] = {}
    for funder in funders:
        for tag in funder.get("focus_areas") or []:
            focus_counts[tag] = focus_counts.get(tag, 0) + 1
    focus_values = sorted(
        [tag for tag, count in focus_counts.items() if count >= 2],
        key=lambda tag: (tag.replace("_", " ").title(), tag),
    )

    cards: list[str] = []
    for funder in sorted(
        funders,
        key=lambda item: (
            0 if item.get("annual_grants_total_usd_approx") else 1,
            -(float(item.get("annual_grants_total_usd_approx") or 0)),
            str(item.get("common_name") or item.get("legal_name") or ""),
        ),
    ):
        common_name = funder.get("common_name") or funder.get("legal_name") or ""
        focus_tags = "".join(f"<li>{esc(tag.replace('_', ' ').title())}</li>" for tag in (funder.get("focus_areas") or []))
        focus_data = "|".join(sorted(funder.get("focus_areas") or []))
        grants_url = funder.get("grants_program_url") or funder.get("primary_url") or ""
        deadlines_url = funder.get("application_deadlines_url") or grants_url
        contact_bits = []
        if funder.get("contact_email"):
            contact_bits.append(f'Contact: <a href="mailto:{esc(funder["contact_email"])}">{esc(funder["contact_email"])}</a>')
        if funder.get("ein"):
            contact_bits.append(f'EIN: {esc(funder["ein"])}')
        contact_html = ""
        if contact_bits:
            contact_html = f'<p class="source-card__detail">{" · ".join(contact_bits)}</p>'

        cards.append(
            f"""        <li class="source-card"
          data-type="{esc(str(funder.get("type") or ""))}"
          data-focus="{esc(focus_data)}">
          <div class="source-card__header">
            <span class="source-badge">{esc(type_label(str(funder.get("type") or "")))}</span>
            <span class="source-badge">{esc(money_label(funder.get("annual_grants_total_usd_approx")))}</span>
          </div>
          <h2>{esc(common_name)}</h2>
          <p class="source-card__meta">{esc(funder.get("legal_name") or common_name)}</p>
          <p class="source-card__summary">{esc(" ".join(str(funder.get("eligibility_summary") or "").split()))}</p>
          {contact_html}
          <ul class="tag-list">{focus_tags}</ul>
          <div class="source-card__links">
            <a href="{esc(funder.get("primary_url") or "")}" rel="noopener">Organization site</a>
            <a href="{esc(grants_url)}" rel="noopener">Grant program</a>
            <a href="{esc(deadlines_url)}" rel="noopener">Deadlines or application page</a>
          </div>
        </li>"""
        )

    type_options = "\n".join(
        f'              <option value="{esc(value)}">{esc(type_label(value))}</option>' for value in type_values
    )
    focus_options = "\n".join(
        f'              <option value="{esc(value)}">{esc(value.replace("_", " ").title())}</option>' for value in focus_values
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>WildlifeStats — Funders</title>
  <meta name="description" content="Curated national funder registry for wildlife rehabilitation and adjacent conservation support.">
  <link rel="canonical" href="https://wildlifestats.org/funders/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="WildlifeStats">
  <meta property="og:title" content="WildlifeStats — Funders">
  <meta property="og:description" content="Curated national funder registry for wildlife rehabilitation and adjacent conservation support.">
  <meta property="og:url" content="https://wildlifestats.org/funders/">
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
    <div class="container" data-funders-root>
      <p class="kicker">Curated sector registry</p>
      <h1>Funders</h1>
      <div class="page-intro">
        <p>This page renders the current local WildlifeStats funder registry for wildlife rehabilitation and adjacent conservation support. It is meant to answer a basic sector question quickly: who funds this field, what do they tend to fund, and where should an operator or board start reading?</p>
      </div>

      <div class="page-note">
        <p><strong>Scope:</strong> local curated registry only for now. This is not a scraping surface and not a fundraising advice tool.</p>
        <p><strong>Use with care:</strong> grant deadlines, eligibility terms, and invitation-only posture can change. Always verify against the linked program page before acting.</p>
      </div>

      <section class="metric-grid" aria-label="Summary metrics">
        <div class="metric-card"><strong>{stats["total"]}</strong><span>funders in the current registry</span></div>
        <div class="metric-card"><strong>{stats["known_budget_count"]}</strong><span>with a published approximate annual grant total</span></div>
        <div class="metric-card"><strong>{esc(money_label(stats["known_budget_total"]))}</strong><span>combined published annual grants, where disclosed</span></div>
        <div class="metric-card"><strong>{stats["type_count"]}</strong><span>funder types represented</span></div>
      </section>

      <section class="filter-panel" aria-label="Funders filters">
        <h2>Filter the registry</h2>
        <div class="filter-grid">
          <div class="filter-field">
            <label for="funders-search">Search</label>
            <input id="funders-search" type="search" data-filter="search" placeholder="Name, focus area, eligibility">
          </div>
          <div class="filter-field">
            <label for="funders-type">Funder type</label>
            <select id="funders-type" data-filter="type">
              <option value="all">All types</option>
{type_options}
            </select>
          </div>
          <div class="filter-field">
            <label for="funders-focus">Common focus area</label>
            <select id="funders-focus" data-filter="focus">
              <option value="all">All focus areas</option>
{focus_options}
            </select>
          </div>
        </div>
        <div class="filter-actions">
          <p class="filter-status" data-visible-count>Showing {stats["total"]} of {stats["total"]} funders</p>
          <button type="button" class="filter-reset" data-filter="reset">Reset filters</button>
        </div>
      </section>

      <ul class="card-grid">
{chr(10).join(cards)}
      </ul>

      <div class="empty-state" data-empty-state>
        <p>No current funders match these filters.</p>
      </div>

      <p class="source-disclosure">Registry provenance is carried in the local YAML source file. WildlifeStats stores a restrained public subset here: name, type, focus areas, approximate disclosed scale where available, eligibility summary, and links back to the official program surface. The focus filter highlights recurring tags; search still covers the full long tail of one-off themes.</p>
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
  <script src="/assets/js/funders.js"></script>
</body>
</html>
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    funders = load_funders()
    OUTPUT_PATH.write_text(render_page(funders), encoding="utf-8")
    print(f"Rendered {len(funders)} funders to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
