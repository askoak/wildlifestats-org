#!/usr/bin/env python3
"""Render public Wildlife911 state-directory routes from the source registries.

Writes:
  wildlife911/state/index.html
  wildlife911/state/<STATE>/index.html

Uses only public-safe fields documented in:
  wildlifestats/_pipeline/sources/rehab-centers/PUBLIC_FIELDS.md
  wildlifestats/_pipeline/sources/state-vet-ag/PUBLIC_FIELDS.md
"""

from __future__ import annotations

import html
import re
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]
CENTERS_YAML = REPO_ROOT / "wildlifestats/_pipeline/sources/rehab-centers/centers.yaml"
AGENCIES_YAML = REPO_ROOT / "wildlifestats/_pipeline/sources/state-vet-ag/agencies.yaml"
OUT_ROOT = REPO_ROOT / "wildlife911/state"

ALL_STATES = [
    ("AK", "Alaska"), ("AL", "Alabama"), ("AR", "Arkansas"), ("AZ", "Arizona"),
    ("CA", "California"), ("CO", "Colorado"), ("CT", "Connecticut"), ("DC", "District of Columbia"),
    ("DE", "Delaware"), ("FL", "Florida"), ("GA", "Georgia"), ("HI", "Hawaii"),
    ("IA", "Iowa"), ("ID", "Idaho"), ("IL", "Illinois"), ("IN", "Indiana"),
    ("KS", "Kansas"), ("KY", "Kentucky"), ("LA", "Louisiana"), ("MA", "Massachusetts"),
    ("MD", "Maryland"), ("ME", "Maine"), ("MI", "Michigan"), ("MN", "Minnesota"),
    ("MO", "Missouri"), ("MS", "Mississippi"), ("MT", "Montana"), ("NC", "North Carolina"),
    ("ND", "North Dakota"), ("NE", "Nebraska"), ("NH", "New Hampshire"), ("NJ", "New Jersey"),
    ("NM", "New Mexico"), ("NV", "Nevada"), ("NY", "New York"), ("OH", "Ohio"),
    ("OK", "Oklahoma"), ("OR", "Oregon"), ("PA", "Pennsylvania"), ("RI", "Rhode Island"),
    ("SC", "South Carolina"), ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"),
    ("UT", "Utah"), ("VA", "Virginia"), ("VT", "Vermont"), ("WA", "Washington"),
    ("WI", "Wisconsin"), ("WV", "West Virginia"), ("WY", "Wyoming"),
]

TAXA_LABELS = {
    "accepts_birds": "Birds",
    "accepts_mammals": "Mammals",
    "accepts_reptiles": "Reptiles",
    "accepts_amphibians": "Amphibians",
    "accepts_marine": "Marine wildlife",
    "accepts_rabies_vector": "Rabies-vector species",
}

SITE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="https://wildlifestats.org{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="WildlifeStats">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="https://wildlifestats.org{canonical}">
  <meta property="og:image" content="https://wildlifestats.org/assets/img/og-default.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+Pro:wght@400;600&amp;display=swap">
  <link rel="stylesheet" href="/assets/css/tokens.css">
  <link rel="stylesheet" href="/assets/css/base.css">
  <link rel="stylesheet" href="/assets/css/site.css">
  <link rel="stylesheet" href="/assets/css/wildlife911.css">
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
"""

SITE_FOOT = """  <footer class="site-footer">
    <div class="container">
      <p>WildlifeStats is a research framework. Current dataset is synthetic
      (n=1,000,000) generated from regional distribution models. See
      <a href="/methodology.html">Methodology</a>.</p>
      <nav aria-label="Footer">
        <a href="/governance.html">Governance</a> ·
        <a href="/about.html">About</a> ·
        <a href="/wildlife911/">Wildlife911</a> ·
        <a href="/centers/">Centers</a> ·
        <a href="mailto:wildlifestats@michaeloak.com">Contact</a> ·
        <span>2026</span>
      </nav>
    </div>
  </footer>
  <script src="/assets/js/site.js"></script>
</body>
</html>
"""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def safe_phone_href(raw: str) -> str:
    digits = re.sub(r"[^0-9+]", "", raw)
    return digits or raw


def load_data() -> tuple[list[dict], dict[str, dict]]:
    centers = yaml.safe_load(CENTERS_YAML.read_text(encoding="utf-8")) or []
    agencies = yaml.safe_load(AGENCIES_YAML.read_text(encoding="utf-8")) or []
    active_centers = [center for center in centers if center.get("status") == "active"]
    agency_by_state = {agency["jurisdiction"]: agency for agency in agencies if agency.get("jurisdiction")}
    return active_centers, agency_by_state


def page(*, title: str, description: str, canonical: str, body: str) -> str:
    return SITE_HEAD.format(
        title=esc(title),
        description=esc(description),
        canonical=canonical,
    ) + body + SITE_FOOT


def taxa_tags(center: dict) -> list[str]:
    services = center.get("services") or {}
    labels = [label for key, label in TAXA_LABELS.items() if services.get(key)]
    return labels or ["Wildlife intake"]


def render_center_card(center: dict) -> str:
    name = esc(center.get("common_name") or "")
    city = esc(center.get("city") or "")
    state = esc(center.get("state") or "")
    hotline = center.get("emergency_hotline") or center.get("contact_phone") or ""
    hotline_html = ""
    if hotline:
        hotline_html = (
            f'<p><strong>Phone:</strong> <a href="tel:{esc(safe_phone_href(hotline))}" '
            f'class="w911-link">{esc(hotline)}</a></p>'
        )
    help_url = center.get("wildlife_help_url") or center.get("primary_url") or ""
    help_html = ""
    if help_url:
        help_html = (
            f'<p><a href="{esc(help_url)}" rel="noopener" class="w911-link">'
            "Wildlife intake or help page</a></p>"
        )
    hours = center.get("intake_hours") or ""
    hours_html = f"<p><strong>Hours:</strong> {esc(hours)}</p>" if hours else ""
    mission = center.get("mission_excerpt") or ""
    mission_html = f'<p class="w911-center-card__mission">{esc(mission)}</p>' if mission else ""
    tags = "".join(f"<li>{esc(label)}</li>" for label in taxa_tags(center))
    return f"""          <article class="w911-center-card">
            <h2>{name}</h2>
            <p class="w911-center-card__meta">{city}, {state}</p>
            <ul class="w911-tag-list">{tags}</ul>
            {hotline_html}
            {hours_html}
            {mission_html}
            {help_html}
          </article>
"""


def render_agency_card(agency: dict | None, state_name: str) -> str:
    if not agency:
        return f"""        <div class="w911-directory-card">
          <h2>State wildlife or veterinary agency</h2>
          <p>WildlifeStats does not currently have a public agency record loaded for {esc(state_name)}. Use
          <a href="https://animalhelpnow.org" rel="noopener" class="w911-link">Animal Help Now</a> for
          a ZIP-code search and contact your state wildlife agency directly.</p>
        </div>
"""

    agency_url = esc(agency.get("primary_url") or "")
    phone = agency.get("contact_phone") or ""
    phone_html = ""
    if phone:
        phone_html = (
            f'<p><strong>Phone:</strong> <a href="tel:{esc(safe_phone_href(phone))}" '
            f'class="w911-link">{esc(phone)}</a></p>'
        )
    disease_url = agency.get("wildlife_disease_program_url")
    disease_html = ""
    if disease_url and disease_url != agency.get("primary_url"):
        disease_html = (
            f'<p><a href="{esc(disease_url)}" rel="noopener" class="w911-link">'
            "Wildlife or disease program page</a></p>"
        )
    return f"""        <div class="w911-directory-card">
          <h2>State wildlife or veterinary agency</h2>
          <p><strong>{esc(agency.get("agency_name") or state_name)}</strong></p>
          {phone_html}
          <p><a href="{agency_url}" rel="noopener" class="w911-link">Official agency website</a></p>
          {disease_html}
        </div>
"""


def render_national_cards() -> str:
    return """      <div class="w911-directory-grid">
        <div class="w911-directory-card">
          <h2>Need Virginia-specific guidance?</h2>
          <p>Virginia remains the deepest authored Wildlife911 edition, with species pages,
          triage flow charts, and Virginia-specific law and referral notes.</p>
          <p><a href="/wildlife911/" class="w911-link">Open Wildlife911 Virginia</a></p>
        </div>
        <div class="w911-directory-card">
          <h2>Need the fastest national fallback?</h2>
          <p>Animal Help Now remains the fastest ZIP-code lookup for licensed wildlife
          rehabilitators and animal control coverage across the country.</p>
          <p><a href="https://animalhelpnow.org" rel="noopener" class="w911-link">Open Animal Help Now</a></p>
        </div>
        <div class="w911-directory-card">
          <h2>Need a state agency contact?</h2>
          <p>Every state page in this directory includes the stable state wildlife or veterinary
          agency contact carried in the public registry.</p>
          <p><a href="/centers/" class="w911-link">See the national center directory</a></p>
        </div>
      </div>
"""


def render_state_index(active_centers: list[dict]) -> str:
    counts: dict[str, int] = {}
    for center in active_centers:
        state_code = center.get("state")
        if state_code:
            counts[state_code] = counts.get(state_code, 0) + 1

    cards = []
    for code, name in ALL_STATES:
        count = counts.get(code, 0)
        label = "center" if count == 1 else "centers"
        cards.append(
            f"""        <li>
          <a href="/wildlife911/state/{esc(code)}/">
            <strong>{esc(name)}</strong>
            <span>{count} {label}</span>
          </a>
        </li>"""
        )

    body = f"""  <main>
    <div class="container">
      <p class="kicker">Wildlife911 · National directory</p>
      <h1 class="w911-h1">Wildlife help by state</h1>
      <p class="w911-lead">Wildlife911 now publishes a national state-directory layer: {len(active_centers)} active wildlife rehabilitation organizations across all 50 states and the District of Columbia, paired with public state-agency contacts. This is a referral directory, not clinical advice. Virginia remains the deepest authored edition.</p>
      <div class="w911-cta-row">
        <a href="/wildlife911/" class="w911-cta-primary">Open Wildlife911 Virginia</a>
        <a href="https://animalhelpnow.org" rel="noopener" class="w911-cta-secondary">National ZIP-code lookup</a>
      </div>
{render_national_cards()}
      <section class="w911-state-directory" aria-label="State directory">
        <h2>Browse by state</h2>
        <p class="w911-intro">Choose your state for public rehab-center listings and the stable state wildlife or veterinary agency contact carried in the WildlifeStats registry.</p>
        <ul class="w911-state-grid">
{chr(10).join(cards)}
        </ul>
      </section>

      <aside class="w911-safety" role="alert">
        <h2 class="w911-safety__title">Two situations are always emergencies</h2>
        <div class="w911-safety__row">
          <span class="w911-safety__num">1</span>
          <p><strong>Any bird that hits a window, vehicle, or building.</strong> Internal injuries and concussion are likely even when the bird appears alert. Box the bird in a quiet, dark place and contact a licensed rehabilitator immediately.</p>
        </div>
        <div class="w911-safety__row">
          <span class="w911-safety__num">2</span>
          <p><strong>Any wild animal that has been in a cat's or dog's mouth.</strong> Pet-saliva infections can be fatal within 24 to 48 hours even when no wound is visible. Referral is always required.</p>
        </div>
      </aside>
    </div>
  </main>
"""
    return page(
        title="Wildlife911 — State directory",
        description="Browse Wildlife911 rehab-center and state-agency directory pages for all 50 states and the District of Columbia.",
        canonical="/wildlife911/state/",
        body=body,
    )


def render_state_page(code: str, state_name: str, centers: list[dict], agency: dict | None) -> str:
    centers_html = ""
    if centers:
        centers_html = "".join(render_center_card(center) for center in centers)
    else:
        centers_html = f"""          <div class="w911-directory-card">
            <h2>No center currently listed</h2>
            <p>WildlifeStats does not currently have an active wildlife-rehabilitation center record
            loaded for {esc(state_name)}. Use <a href="https://animalhelpnow.org" rel="noopener"
            class="w911-link">Animal Help Now</a> and contact the state agency below.</p>
          </div>
"""

    virginia_note = ""
    if code == "VA":
        virginia_note = """      <div class="w911-directory-card w911-directory-card--feature">
        <h2>Virginia has a deeper authored edition</h2>
        <p>The Virginia route includes Wildlife911 species guidance, dispatcher content, and Virginia-specific law and referral notes in addition to the directory data below.</p>
        <p><a href="/wildlife911/" class="w911-link">Open the full Virginia edition</a></p>
      </div>
"""

    body = f"""  <main>
    <div class="container">
      <p class="kicker">Wildlife911 · {esc(state_name)}</p>
      <h1 class="w911-h1">Wildlife911 {esc(state_name)}</h1>
      <p class="w911-lead">Use this page to find licensed wildlife rehabilitation contacts in {esc(state_name)} and the stable state wildlife or veterinary agency reference. This page does not give treatment instructions or replace a licensed rehabilitator.</p>
      <div class="w911-cta-row">
        <a href="/wildlife911/state/" class="w911-cta-secondary">Back to all states</a>
        <a href="https://animalhelpnow.org" rel="noopener" class="w911-cta-primary">Animal Help Now</a>
      </div>
{virginia_note}
      <div class="w911-directory-grid">
{render_agency_card(agency, state_name)}
        <div class="w911-directory-card">
          <h2>Before you call</h2>
          <p>For rabies-vector species, bats in a living space, or any wild animal inside a home, contact local animal control first. For most other situations, call two or three rehabilitators because availability varies.</p>
          <p>Leave your name and callback number, exact location, species or description, the animal's condition, and any containment steps already taken.</p>
        </div>
      </div>

      <section class="w911-center-section" aria-label="Wildlife rehabilitators">
        <h2>Licensed wildlife rehabilitators</h2>
        <p class="w911-intro">{len(centers)} active center{"s" if len(centers) != 1 else ""} currently listed in the public-safe registry for {esc(state_name)}.</p>
        <div class="w911-center-grid">
{centers_html}
        </div>
      </section>

      <section class="w911-calls" aria-label="National resources">
        <h2>National resources</h2>
        <div class="w911-calls__grid">
          <div class="w911-calls__card">
            <h3>Animal Help Now</h3>
            <p>ZIP-code-based national directory of wildlife rehabilitators and animal control.</p>
            <p><a href="https://animalhelpnow.org" rel="noopener" class="w911-link">animalhelpnow.org</a></p>
          </div>
          <div class="w911-calls__card">
            <h3>US Fish &amp; Wildlife Service</h3>
            <p>Federal contact point for migratory bird questions and selected protected-species issues.</p>
            <p><a href="https://www.fws.gov/program/migratory-birds" rel="noopener" class="w911-link">fws.gov/program/migratory-birds</a></p>
          </div>
          <div class="w911-calls__card">
            <h3>National Wildlife Rehabilitators Association</h3>
            <p>Professional association and standards body for wildlife rehabilitation.</p>
            <p><a href="https://www.nwrawildlife.org" rel="noopener" class="w911-link">nwrawildlife.org</a></p>
          </div>
        </div>
      </section>
    </div>
  </main>
"""
    return page(
        title=f"Wildlife911 — {state_name}",
        description=f"Wildlife911 directory page for {state_name}: public rehab-center listings and state-agency wildlife contacts.",
        canonical=f"/wildlife911/state/{code}/",
        body=body,
    )


def main() -> None:
    active_centers, agency_by_state = load_data()
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "index.html").write_text(render_state_index(active_centers), encoding="utf-8")

    grouped: dict[str, list[dict]] = {code: [] for code, _ in ALL_STATES}
    for center in active_centers:
        state_code = center.get("state")
        if state_code in grouped:
            grouped[state_code].append(center)

    for code, name in ALL_STATES:
        state_dir = OUT_ROOT / code
        state_dir.mkdir(parents=True, exist_ok=True)
        centers = sorted(grouped.get(code, []), key=lambda center: (center.get("city") or "", center.get("common_name") or ""))
        html_text = render_state_page(code, name, centers, agency_by_state.get(code))
        (state_dir / "index.html").write_text(html_text, encoding="utf-8")

    print(f"Rendered Wildlife911 public state routes to {OUT_ROOT}")


if __name__ == "__main__":
    main()
