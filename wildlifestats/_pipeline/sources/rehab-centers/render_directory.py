#!/usr/bin/env python3
"""
Render the national rehab-center directory as static HTML pages.

Reads:  wildlifestats/_pipeline/sources/rehab-centers/centers.yaml (177 orgs)
Writes: /centers/index.html      (national directory landing + searchable table)
        /centers/<state>/index.html  (per-state directory landing — 51 pages)
        /centers/<state>/<slug>/index.html  (per-org profile — 177 pages)

Deterministic. Same registry in → byte-identical HTML out.

Strategic role: this is the FIRST national directory of wildlife rehabilitation
organizations the framework publishes. It is the demo-ready proof that
WildlifeStats covers the actual US wildlife-rehab universe, not just the
Mike-curated Flyway roster.
"""

import html
import json
import re
from pathlib import Path

import yaml


def esc(value):
    """HTML-escape any value for safe interpolation into element content or attributes.

    Critical for html-validate CI gate: prose containing bare &, <, > is
    invalid HTML even when it renders correctly in browsers. The 2026-06-11
    gate failure was caused by missing escaping on prose like "Fish & Wildlife"
    and "intake <50 animals/year". This wrapper makes escaping the default;
    callers must explicitly mark trusted HTML as such.
    """
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


REPO_ROOT = Path(__file__).resolve().parents[4]
REGISTRY_PATH = REPO_ROOT / "wildlifestats/_pipeline/sources/rehab-centers/centers.yaml"
OUT_ROOT = REPO_ROOT / "centers"

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}

SITE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="https://wildlifestats.org{canonical}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+Pro:wght@400;600&display=swap">
  <link rel="stylesheet" href="/assets/css/tokens.css">
  <link rel="stylesheet" href="/assets/css/base.css">
  <link rel="stylesheet" href="/assets/css/site.css">
  <link rel="stylesheet" href="/assets/css/centers.css">
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
          <li><a href="/centers/" class="active">Centers</a></li>
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


def page(title, description, canonical, body):
    return SITE_HEAD.format(title=title, description=description, canonical=canonical) + body + SITE_FOOT


def safe(v, default=""):
    """Return v as an HTML-escaped string, or default when v is missing.

    Escaping by default is non-negotiable per Standing Orders renderer
    discipline: every YAML-sourced value flows through here before reaching
    any HTML template. The 2026-06-11 html-validate gate failure (577 errors,
    176 files) was caused by passing un-escaped prose like 'Fish & Wildlife'
    and 'intake <50 animals/year' directly into f-string templates. Bare &,
    <, and > are invalid HTML even when browsers render them. quote=True is
    important because some safe() outputs (URLs, addresses) end up inside
    attribute values, where unescaped quotes would break the markup.
    """
    if v is None or v == "" or v == "unknown":
        return default
    return html.escape(str(v), quote=True)


def render_national_landing(centers):
    states_with_centers = sorted({c["state"] for c in centers if c.get("state")})
    state_counts = {}
    for c in centers:
        state_counts[c["state"]] = state_counts.get(c["state"], 0) + 1

    body = """
  <main>
    <div class="container">
      <p class="kicker">National Directory</p>
      <h1>US wildlife rehabilitation centers</h1>
      <p class="lead">A national directory of licensed wildlife rehabilitation organizations across the United States. Compiled from state wildlife agency rehabber directories, AnimalHelpNow, NWRA and IWRC member lists, and ProPublica's Nonprofit Explorer. Every organization listed below is a verified 501(c)(3) operating a physical facility for at least two years.</p>
"""
    body += f"""
      <section class="centers-stats">
        <div class="centers-stat"><strong>{len(centers)}</strong><span>organizations</span></div>
        <div class="centers-stat"><strong>{len(states_with_centers)}</strong><span>states + DC</span></div>
        <div class="centers-stat"><strong>{sum(1 for c in centers if safe(c.get('ein')))}</strong><span>EIN-verified</span></div>
        <div class="centers-stat"><strong>{sum(1 for c in centers if safe(c.get('wildlife_help_url')))}</strong><span>publish wildlife-help guides</span></div>
      </section>

      <section class="centers-strategic">
        <h2>How this directory is used</h2>
        <ul>
          <li><strong>Finders of injured wildlife:</strong> jump to your state below to find a licensed rehabilitator near you. For triage decisions before you call, use <a href="/wildlife911/">Wildlife911</a>.</li>
          <li><strong>Researchers:</strong> 161 organizations have verified IRS Employer Identification Numbers (EINs). These EINs power the <a href="/methodology.html">Form 990 financial ingestion pipeline</a> for sector-scale financial and compensation analysis.</li>
          <li><strong>Partner centers:</strong> see how WildlifeStats represents your organization. To request edits or to share annual report data, <a href="mailto:wildlifestats@michaeloak.com">contact us</a>.</li>
          <li><strong>State agencies and foundations:</strong> the directory is a credible map of the US wildlife rehabilitation capacity landscape, with links to state-published rehabber directories where they exist.</li>
        </ul>
      </section>
"""

    # By-state index
    body += """
      <section class="centers-state-index">
        <h2>Browse by state</h2>
        <ul class="centers-state-grid">
"""
    for st in states_with_centers:
        name = STATE_NAMES.get(st, st)
        count = state_counts[st]
        body += f'          <li><a href="/centers/{st.lower()}/"><strong>{name}</strong><span>{count} {"center" if count == 1 else "centers"}</span></a></li>\n'
    body += "        </ul>\n      </section>\n"

    # Full searchable table
    body += """
      <section class="centers-full-table">
        <h2>All organizations</h2>
        <p class="hint">Use the search box below to filter by name, city, or services.</p>
        <input type="text" id="centers-search" placeholder="Search by name, city, or services..." class="centers-search-input">
        <table class="centers-table" id="centers-table">
          <thead>
            <tr>
              <th>Organization</th>
              <th>State</th>
              <th>City</th>
              <th>Services</th>
              <th>Profile</th>
            </tr>
          </thead>
          <tbody>
"""
    for c in centers:
        slug = c.get("slug", "")
        name = safe(c.get("common_name") or c.get("legal_name"), slug)
        state = c.get("state", "")
        city = safe(c.get("city"), "—")
        services = c.get("services", {}) or {}
        svc_tags = []
        if services.get("accepts_birds"): svc_tags.append("Birds")
        if services.get("accepts_mammals"): svc_tags.append("Mammals")
        if services.get("accepts_reptiles"): svc_tags.append("Reptiles")
        if services.get("accepts_amphibians"): svc_tags.append("Amphibians")
        if services.get("accepts_marine"): svc_tags.append("Marine")
        if services.get("accepts_rabies_vector"): svc_tags.append("Rabies-vector")
        svc_str = ", ".join(svc_tags) if svc_tags else "—"
        body += f"""            <tr>
              <td>{name}</td>
              <td>{state}</td>
              <td>{city}</td>
              <td class="cell-services">{svc_str}</td>
              <td><a href="/centers/{state.lower()}/{slug}/" class="centers-link">View →</a></td>
            </tr>
"""
    body += """          </tbody>
        </table>
      </section>

      <section class="centers-methodology">
        <h2>Methodology and limitations</h2>
        <p>This directory was compiled June 11, 2026 from five parallel regional research passes drawing on:</p>
        <ul>
          <li>State wildlife agency rehabber directories (where published)</li>
          <li><a href="https://animalhelpnow.org" rel="noopener">AnimalHelpNow</a> — the leading national rehab-locator service</li>
          <li><a href="https://nwrawildlife.org" rel="noopener">National Wildlife Rehabilitators Association (NWRA)</a> member rolls</li>
          <li><a href="https://www.theiwrc.org" rel="noopener">International Wildlife Rehabilitation Council (IWRC)</a> directory</li>
          <li><a href="https://projects.propublica.org/nonprofits" rel="noopener">ProPublica Nonprofit Explorer</a> for EIN verification</li>
        </ul>
        <p><strong>Inclusion criteria:</strong> verified 501(c)(3) status, physical facility (not just a referral phone line), operating at least two years, holds state wildlife rehabilitation permit. Pet rescues that occasionally handle wildlife, individual home rehabbers without published presence, and defunct organizations are excluded.</p>
        <p><strong>Known gaps:</strong> Vermont has no qualifying standalone nonprofit center identified. West Virginia's wildlife rehabilitation infrastructure is very limited. The directory reflects the actual landscape, not a wishful one.</p>
        <p>To suggest a center we should add, or to request a correction: <a href="mailto:wildlifestats@michaeloak.com">wildlifestats@michaeloak.com</a>.</p>
      </section>
    </div>
  </main>

  <script>
    (function() {
      var input = document.getElementById('centers-search');
      var table = document.getElementById('centers-table');
      if (!input || !table) return;
      var tbody = table.querySelector('tbody');
      var rows = Array.prototype.slice.call(tbody.rows);
      input.addEventListener('input', function() {
        var q = input.value.toLowerCase().trim();
        rows.forEach(function(row) {
          var text = row.textContent.toLowerCase();
          row.style.display = (q === '' || text.indexOf(q) >= 0) ? '' : 'none';
        });
      });
    })();
  </script>
"""
    return body


def render_state_landing(state, centers):
    name = STATE_NAMES.get(state, state)
    body = f"""
  <main>
    <div class="container">
      <p class="kicker"><a href="/centers/">National Directory</a> · {name}</p>
      <h1>Wildlife rehabilitation centers in {name}</h1>
      <p class="lead">{len(centers)} verified licensed wildlife rehabilitation {"organization" if len(centers) == 1 else "organizations"} in {name}.</p>

      <section class="centers-list">
"""
    for c in sorted(centers, key=lambda x: x.get("common_name") or x.get("slug") or ""):
        slug = c.get("slug", "")
        ncn = safe(c.get("common_name") or c.get("legal_name"), slug)
        city = safe(c.get("city"), "")
        url = safe(c.get("primary_url"), "")
        mission = safe(c.get("mission_excerpt"), "")
        body += f"""        <article class="centers-card">
          <h2><a href="/centers/{state.lower()}/{slug}/">{ncn}</a></h2>
          <p class="centers-card-meta">{city}{' · ' if city and url else ''}{('<a href="' + url + '" rel="noopener">' + url.replace('https://','').replace('http://','').rstrip('/') + '</a>') if url else ''}</p>
"""
        if mission:
            body += f"          <p class=\"centers-card-mission\">{mission}</p>\n"
        body += "        </article>\n"
    body += "      </section>\n    </div>\n  </main>\n"
    return body


def render_org_profile(c):
    slug = c.get("slug", "")
    state = c.get("state", "")
    state_name = STATE_NAMES.get(state, state)
    name = safe(c.get("common_name") or c.get("legal_name"), slug)
    legal_name = safe(c.get("legal_name"), "")
    city = safe(c.get("city"), "")
    ein = safe(c.get("ein"), "")
    primary_url = safe(c.get("primary_url"), "")
    wildlife_help_url = safe(c.get("wildlife_help_url"), "")
    about_url = safe(c.get("about_url"), "")
    contact_url = safe(c.get("contact_url"), "")
    contact_email = safe(c.get("contact_email"), "")
    contact_phone = safe(c.get("contact_phone"), "")
    emergency_hotline = safe(c.get("emergency_hotline"), "")
    intake_address = safe(c.get("intake_address"), "")
    intake_hours = safe(c.get("intake_hours"), "")
    news_or_blog = safe(c.get("news_or_blog_url"), "")
    newsletter_signup = safe(c.get("newsletter_signup_url"), "")
    patient_stories = safe(c.get("patient_stories_url"), "")
    annual_reports = safe(c.get("annual_reports_url"), "")
    latest_ar = safe(c.get("most_recent_annual_report_pdf"), "")
    social = c.get("social") or {}
    services = c.get("services") or {}
    capacity = c.get("capacity") or {}
    accreditations = c.get("accreditations") or []
    leadership = c.get("leadership") or {}
    mission = safe(c.get("mission_excerpt"), "")
    notes = safe(c.get("notes"), "")
    source_urls = c.get("source_urls") or []

    body = f"""
  <main>
    <div class="container">
      <p class="kicker"><a href="/centers/">National Directory</a> · <a href="/centers/{state.lower()}/">{state_name}</a></p>
      <h1>{name}</h1>
"""
    if legal_name and legal_name != name:
        body += f'      <p class="org-legal">{legal_name}</p>\n'
    if mission:
        body += f'      <p class="lead">{mission}</p>\n'

    # Contact + intake panel
    body += '      <section class="org-contact">\n        <h2>Contact &amp; intake</h2>\n        <dl class="org-dl">\n'
    if primary_url:
        body += f'          <dt>Website</dt><dd><a href="{primary_url}" rel="noopener">{primary_url}</a></dd>\n'
    if intake_address:
        body += f'          <dt>Intake address</dt><dd>{intake_address}</dd>\n'
    if intake_hours:
        body += f'          <dt>Intake hours</dt><dd>{intake_hours}</dd>\n'
    if contact_phone:
        body += f'          <dt>Phone</dt><dd><a href="tel:{contact_phone.replace(" ", "")}">{contact_phone}</a></dd>\n'
    if emergency_hotline and emergency_hotline != contact_phone:
        body += f'          <dt>Emergency hotline</dt><dd><a href="tel:{emergency_hotline.replace(" ", "")}">{emergency_hotline}</a></dd>\n'
    if contact_email:
        body += f'          <dt>Email</dt><dd><a href="mailto:{contact_email}">{contact_email}</a></dd>\n'
    body += '        </dl>\n      </section>\n'

    # Public-facing pages
    public_links = []
    if wildlife_help_url:
        public_links.append(("Wildlife help &amp; species guides", wildlife_help_url))
    if about_url:
        public_links.append(("About", about_url))
    if contact_url and contact_url != primary_url:
        public_links.append(("Contact page", contact_url))
    if news_or_blog:
        public_links.append(("News / blog", news_or_blog))
    if patient_stories:
        public_links.append(("Patient stories", patient_stories))
    if annual_reports:
        public_links.append(("Annual reports", annual_reports))
    if latest_ar:
        public_links.append(("Most recent annual report (PDF)", latest_ar))
    if newsletter_signup:
        public_links.append(("Newsletter signup", newsletter_signup))
    if public_links:
        body += '      <section class="org-resources">\n        <h2>Public resources</h2>\n        <ul>\n'
        for label, url in public_links:
            # label is a trusted-but-may-contain-entity literal authored above (e.g.
            # "Wildlife help &amp; species guides"). Do NOT esc() it or we double-encode.
            # url is already safe()-escaped from the YAML source.
            body += f'          <li><a href="{url}" rel="noopener">{label}</a></li>\n'
        body += '        </ul>\n      </section>\n'

    # Social
    social_links = []
    for k, v in social.items():
        if v:
            social_links.append((k.title(), v))
    if social_links:
        body += '      <section class="org-social">\n        <h2>Social media</h2>\n        <ul class="org-social-list">\n'
        for label, url in social_links:
            body += f'          <li><a href="{url}" rel="noopener">{esc(label)}</a></li>\n'
        body += '        </ul>\n      </section>\n'

    # Services
    if services:
        body += '      <section class="org-services">\n        <h2>Services</h2>\n        <ul>\n'
        if services.get("accepts_birds"): body += "          <li>Accepts birds</li>\n"
        if services.get("accepts_mammals"): body += "          <li>Accepts mammals</li>\n"
        if services.get("accepts_reptiles"): body += "          <li>Accepts reptiles</li>\n"
        if services.get("accepts_amphibians"): body += "          <li>Accepts amphibians</li>\n"
        if services.get("accepts_marine"): body += "          <li>Accepts marine wildlife (marine mammals, sea turtles)</li>\n"
        if services.get("accepts_rabies_vector"): body += "          <li>Accepts rabies-vector species (fox, skunk, raccoon, bat, groundhog)</li>\n"
        if services.get("accepts_orphaned_only"): body += "          <li>Specialty: orphaned-only intake</li>\n"
        if services.get("accepts_24_7"): body += "          <li>24/7 admission</li>\n"
        if services.get("transport_offered"): body += "          <li>Transport offered</li>\n"
        if services.get("field_response"): body += "          <li>Field response available</li>\n"
        body += '        </ul>\n      </section>\n'

    # Capacity
    typical_intake_raw = capacity.get("typical_annual_intake", 0)
    try:
        typical_intake = int(typical_intake_raw) if typical_intake_raw not in (None, "", 0, "0") else 0
    except (TypeError, ValueError):
        typical_intake = 0
    if typical_intake:
        intake_year = capacity.get("intake_source_year", "")
        body += f'      <section class="org-capacity">\n        <h2>Capacity</h2>\n'
        body += f'        <p>Typical annual intake: <strong>{typical_intake:,}</strong>{f" ({esc(intake_year)})" if intake_year else ""}</p>\n'
        if capacity.get("licensed_species_count"):
            body += f'        <p>Licensed species: {esc(capacity["licensed_species_count"])}</p>\n'
        body += '      </section>\n'

    # Leadership
    if leadership.get("executive_director") or leadership.get("medical_director"):
        body += '      <section class="org-leadership">\n        <h2>Leadership</h2>\n        <ul>\n'
        if leadership.get("executive_director"):
            body += f"          <li>Executive Director: {esc(leadership['executive_director'])}</li>\n"
        if leadership.get("medical_director"):
            body += f"          <li>Medical Director: {esc(leadership['medical_director'])}</li>\n"
        body += '        </ul>\n      </section>\n'

    # Accreditations
    if accreditations:
        body += '      <section class="org-accreditations">\n        <h2>Accreditations &amp; permits</h2>\n        <ul>\n'
        for a in accreditations:
            body += f"          <li>{esc(a)}</li>\n"
        body += '        </ul>\n      </section>\n'

    # Financial section (placeholder for Phase 8b)
    if ein:
        body += f"""      <section class="org-financials">
        <h2>Financials</h2>
        <p>EIN: <code>{ein}</code></p>
        <p>Form 990 financial data for this organization will be available here once the Form 990 ingestion pipeline (Phase 8b) ships. In the meantime, the canonical source for this organization's tax filings is <a href="https://projects.propublica.org/nonprofits/organizations/{ein.replace('-','')}" rel="noopener">ProPublica Nonprofit Explorer</a>.</p>
      </section>
"""

    # Notes
    if notes:
        body += f'      <section class="org-notes">\n        <h2>Notes</h2>\n        <p>{notes}</p>\n      </section>\n'

    # Sources
    if source_urls:
        body += '      <section class="org-sources">\n        <h2>Sources</h2>\n        <ul>\n'
        for s in source_urls:
            s_esc = esc(s)
            body += f'          <li><a href="{s_esc}" rel="noopener">{s_esc}</a></li>\n'
        body += '        </ul>\n      </section>\n'

    body += '      <p class="org-back"><a href="/centers/{}/">← Back to {} centers</a></p>\n'.format(state.lower(), state_name)
    body += "    </div>\n  </main>\n"
    return body


def main():
    raw = REGISTRY_PATH.read_text(encoding="utf-8")
    centers = yaml.safe_load(raw)
    centers = [c for c in centers if isinstance(c, dict)]
    print(f"Loaded {len(centers)} centers")

    # Group by state
    by_state = {}
    for c in centers:
        st = c.get("state", "")
        if not st:
            continue
        by_state.setdefault(st, []).append(c)

    # Wipe existing /centers/
    if OUT_ROOT.exists():
        import shutil
        shutil.rmtree(OUT_ROOT)
    OUT_ROOT.mkdir(parents=True)

    # National landing
    (OUT_ROOT / "index.html").write_text(
        page(
            title="National wildlife rehabilitation center directory — WildlifeStats",
            description=f"{len(centers)} verified US wildlife rehabilitation organizations across all 50 states + DC. Searchable directory with per-organization profiles, contact info, services, and links to public resources.",
            canonical="/centers/",
            body=render_national_landing(centers),
        ),
        encoding="utf-8",
    )

    # Per-state landings + per-org profiles
    for state in sorted(by_state.keys()):
        state_orgs = by_state[state]
        st_lower = state.lower()
        st_dir = OUT_ROOT / st_lower
        st_dir.mkdir(parents=True)
        (st_dir / "index.html").write_text(
            page(
                title=f"Wildlife rehabilitation centers in {STATE_NAMES.get(state, state)} — WildlifeStats",
                description=f"{len(state_orgs)} verified licensed wildlife rehabilitation organizations in {STATE_NAMES.get(state, state)}.",
                canonical=f"/centers/{st_lower}/",
                body=render_state_landing(state, state_orgs),
            ),
            encoding="utf-8",
        )
        for c in state_orgs:
            slug = c.get("slug", "")
            if not slug:
                continue
            org_dir = st_dir / slug
            org_dir.mkdir(parents=True, exist_ok=True)
            name = safe(c.get("common_name") or c.get("legal_name"), slug)
            (org_dir / "index.html").write_text(
                page(
                    title=f"{name} — WildlifeStats",
                    description=f"Wildlife rehabilitation center profile for {name} in {safe(c.get('city'), STATE_NAMES.get(state, state))}, {state}. Contact, services, capacity, and public resources.",
                    canonical=f"/centers/{st_lower}/{slug}/",
                    body=render_org_profile(c),
                ),
                encoding="utf-8",
            )

    # Final report
    pages = list(OUT_ROOT.rglob("index.html"))
    print(f"Rendered {len(pages)} pages")


if __name__ == "__main__":
    main()
