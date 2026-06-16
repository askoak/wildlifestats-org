#!/usr/bin/env python3
"""
render_static_national.py
Generate wildlife911 national directory pages — all 50 states + DC.

Wave 1 Step 4 (wildlife911 half): binds rehab-center and state-vet-ag
registries to the wildlife911 page contract for a national render.

Reads:
  wildlifestats/_pipeline/sources/rehab-centers/centers.yaml
  wildlifestats/_pipeline/sources/state-vet-ag/agencies.yaml
Writes:
  wildlifestats/_wren/wildlife911/states/{STATE}/index.html  (per-state directory page)
  wildlifestats/_wren/wildlife911/states/national/index.html (state-picker national index)

Only fields from PUBLIC_FIELDS.md in each registry directory are rendered.
No patient outcome, treatment efficacy, or clinical-advice content is included.
Every page carries a clinical-advice disclaimer (page contract requirement).
Does NOT require network access to run.

Dependencies: pyyaml (already pinned in requirements; stdlib only otherwise).
"""
import re
import sys
from html import escape
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[4]
CENTERS_YAML = REPO_ROOT / "wildlifestats/_pipeline/sources/rehab-centers/centers.yaml"
AGENCIES_YAML = REPO_ROOT / "wildlifestats/_pipeline/sources/state-vet-ag/agencies.yaml"
OUT_ROOT = REPO_ROOT / "wildlifestats/_wren/wildlife911/states"

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

# Public-safe taxa labels (per centers PUBLIC_FIELDS.md)
TAXA_LABELS = {
    "accepts_birds": "Birds",
    "accepts_mammals": "Mammals",
    "accepts_reptiles": "Reptiles",
    "accepts_amphibians": "Amphibians",
    "accepts_marine": "Marine wildlife",
    "accepts_rabies_vector": "Rabies-vector species",
}

DISCLAIMER = """\
<div class="disclaimer">
  <p><strong>Important:</strong> For clinical advice on a sick or injured animal, consult a
  licensed veterinarian or licensed wildlife rehabilitator. This page is a directory and
  contact reference only &mdash; it does not provide medical advice, treatment guidance, or
  clinical outcome predictions.</p>
</div>"""

NATIONAL_LINKS = """\
<section class="national-resources">
  <h2>National Resources</h2>
  <ul>
    <li><a href="https://animalhelpnow.org" rel="noopener noreferrer">Animal Help Now</a>
    &mdash; ZIP-code based directory of wildlife rehabilitators and animal control</li>
    <li><a href="https://www.fws.gov/program/migratory-birds" rel="noopener noreferrer">\
US Fish &amp; Wildlife Service</a>
    &mdash; national contact for migratory bird emergencies</li>
    <li><a href="https://www.nwrawildlife.org" rel="noopener noreferrer">\
National Wildlife Rehabilitators Association (NWRA)</a>
    &mdash; professional standards and member directory</li>
  </ul>
</section>"""

PAGE_FOOT = """\
<footer>
  <p>WildlifeStats is a research framework. This directory is compiled from public sources.
  Listings are not endorsements. For clinical advice, consult a licensed veterinarian or
  licensed wildlife rehabilitator.</p>
  <p><a href="/wildlifestats/_wren/wildlife911/states/national/">National directory</a>
  &middot; <a href="/about.html">About</a> &middot; &copy; 2026 WildlifeStats</p>
</footer>"""


def esc(value):
    return escape(str(value), quote=True)


def page(title, description, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
</head>
<body>
<header>
  <nav><a href="/">WildlifeStats</a> &rsaquo;
  <a href="/wildlifestats/_wren/wildlife911/states/national/">Wildlife911 National Directory</a></nav>
</header>
<main>
{body}
</main>
{PAGE_FOOT}
</body>
</html>"""


def taxa_tags(center):
    svc = center.get("services") or {}
    tags = [label for key, label in TAXA_LABELS.items() if svc.get(key)]
    return tags or ["Wildlife (contact for species list)"]


def render_center(center):
    phone = center.get("emergency_hotline") or center.get("contact_phone") or ""
    url = center.get("wildlife_help_url") or center.get("primary_url") or ""
    hours = center.get("intake_hours") or ""
    mission = center.get("mission_excerpt") or ""
    tags = taxa_tags(center)
    digits = re.sub(r"[^0-9+]", "", phone)
    phone_html = f'<p>Phone: <a href="tel:{digits}">{esc(phone)}</a></p>' if phone else ""
    hours_html = f'<p class="hours">Hours: {esc(hours)}</p>' if hours else ""
    mission_html = f'<p class="mission">{esc(mission)}</p>' if mission else ""
    url_html = (
        f'<p><a href="{esc(url)}" rel="noopener noreferrer">Wildlife intake / help page</a></p>'
        if url else ""
    )
    return (
        f'<div class="center">\n'
        f'  <h3>{esc(center["common_name"])}</h3>\n'
        f'  <p class="location">{esc(center["city"])}, {esc(center["state"])}</p>\n'
        f'  <p class="taxa">Accepts: {esc(", ".join(tags))}</p>\n'
        f"  {phone_html}\n"
        f"  {hours_html}\n"
        f"  {mission_html}\n"
        f"  {url_html}\n"
        f"</div>"
    )


def render_state_page(code, name, state_centers, agency):
    if agency:
        phone = agency.get("contact_phone") or ""
        phone_html = f"<p>Phone: {esc(phone)}</p>" if phone else ""
        prog_url = agency.get("wildlife_disease_program_url") or ""
        prog_url_html = (
            f'<p><a href="{esc(prog_url)}" rel="noopener noreferrer">'
            f"Wildlife/disease program page</a></p>"
            if prog_url and prog_url != agency.get("primary_url")
            else ""
        )
        agency_section = (
            f'<section class="state-agency">\n'
            f'  <h2>State Wildlife/Veterinary Agency</h2>\n'
            f'  <p class="agency-name">{esc(agency["agency_name"])}</p>\n'
            f"  {phone_html}\n"
            f'  <p><a href="{esc(agency["primary_url"])}" rel="noopener noreferrer">'
            f"Agency website</a></p>\n"
            f"  {prog_url_html}\n"
            f"</section>"
        )
    else:
        agency_section = ""

    if state_centers:
        center_html = "\n".join(render_center(c) for c in state_centers)
        centers_section = (
            f'<section class="centers">\n'
            f"  <h2>Licensed Wildlife Rehabilitation Centers "
            f"({len(state_centers)} listed)</h2>\n"
            f"  {center_html}\n"
            f'  <p class="note">Call two or three rehabilitators &mdash; availability varies. '
            f"If you reach voicemail, leave your name, callback number, exact location, "
            f"species, condition, and containment steps taken.</p>\n"
            f"</section>"
        )
    else:
        centers_section = (
            f'<section class="centers">\n'
            f"  <h2>Licensed Wildlife Rehabilitation Centers</h2>\n"
            f"  <p>No centers currently listed for {esc(name)} in this registry. "
            f"Contact the state agency above or use "
            f'<a href="https://animalhelpnow.org" rel="noopener noreferrer">Animal Help Now</a>'
            f" for a ZIP-code search. You can also contact "
            f'<a href="https://www.fws.gov/program/migratory-birds" rel="noopener noreferrer">'
            f"US Fish &amp; Wildlife Service</a> for migratory bird emergencies.</p>\n"
            f"</section>"
        )

    body = (
        f"<h1>Wildlife911 &mdash; {esc(name)}</h1>\n"
        f"{DISCLAIMER}\n"
        f"{agency_section}\n"
        f"{centers_section}\n"
        f"{NATIONAL_LINKS}\n"
        f'<p><a href="/wildlifestats/_wren/wildlife911/states/national/">'
        f"&larr; Back to national directory</a></p>"
    )
    return page(
        title=f"Wildlife911 — {name} Wildlife Rehabilitators & Contacts",
        description=(
            f"Find licensed wildlife rehabilitators and state agency contacts in {name}. "
            f"Directory listing with phone numbers and intake information."
        ),
        body=body,
    )


def render_national(active_centers):
    by_state = {}
    for c in active_centers:
        by_state.setdefault(c["state"], []).append(c)

    state_links = []
    for code, name in ALL_STATES:
        n = len(by_state.get(code, []))
        cnt_label = f"{n} center" if n == 1 else f"{n} centers"
        state_links.append(
            f'<li><a href="../{esc(code)}/">{esc(name)}</a>'
            f' <span class="count">({esc(cnt_label)})</span></li>'
        )

    body = (
        "<h1>Wildlife911 &mdash; National Directory</h1>\n\n"
        f"{DISCLAIMER}\n\n"
        '<section class="intro">\n'
        f"  <p>This directory lists {len(active_centers)} licensed wildlife rehabilitation "
        f"organizations across 51 US jurisdictions (all 50 states + DC), plus state "
        f"veterinary and wildlife agency contacts. Select your state to see local centers "
        f"and agency contacts.</p>\n"
        f'  <p>For an immediate ZIP-code search, use '
        f'<a href="https://animalhelpnow.org" rel="noopener noreferrer">Animal Help Now</a>.</p>\n'
        f"</section>\n\n"
        '<section class="state-picker">\n'
        "  <h2>Select a State</h2>\n"
        '  <ul class="state-list">\n'
        + "\n".join(f"    {link}" for link in state_links)
        + "\n  </ul>\n</section>\n\n"
        + NATIONAL_LINKS
        + "\n\n"
        '<section class="about">\n'
        "  <h2>About This Directory</h2>\n"
        "  <p>WildlifeStats maintains this registry as a curated, public-safe reference. "
        "Listings are compiled from publicly verifiable sources. This directory does not "
        "provide medical or clinical advice. Call two or three centers &mdash; availability "
        "varies.</p>\n"
        "</section>"
    )
    return page(
        title="Wildlife911 — National Wildlife Rehabilitator Directory",
        description=(
            "National directory of licensed wildlife rehabilitation centers and state agency "
            "contacts. Find a rehabilitator near you by state."
        ),
        body=body,
    )


def main():
    print(f"Reading centers from {CENTERS_YAML}")
    centers = yaml.safe_load(CENTERS_YAML.read_text(encoding="utf-8")) or []
    active_centers = [c for c in centers if c.get("status", "active") == "active"]
    print(f"  Loaded {len(active_centers)} active centers (of {len(centers)} total)")

    print(f"Reading agencies from {AGENCIES_YAML}")
    agencies = yaml.safe_load(AGENCIES_YAML.read_text(encoding="utf-8")) or []
    agency_by_state = {a["jurisdiction"]: a for a in agencies}
    print(f"  Loaded {len(agencies)} agencies")

    by_state = {}
    for c in active_centers:
        by_state.setdefault(c["state"], []).append(c)

    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    states_with_centers = 0
    states_without_centers = 0

    for code, name in ALL_STATES:
        state_centers = by_state.get(code, [])
        agency = agency_by_state.get(code)
        html = render_state_page(code, name, state_centers, agency)
        state_dir = OUT_ROOT / code
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "index.html").write_text(html, encoding="utf-8")
        if state_centers:
            states_with_centers += 1
        else:
            states_without_centers += 1

    national_dir = OUT_ROOT / "national"
    national_dir.mkdir(parents=True, exist_ok=True)
    (national_dir / "index.html").write_text(render_national(active_centers), encoding="utf-8")

    pages = list(OUT_ROOT.rglob("index.html"))
    print(f"\nRendered {len(pages)} pages:")
    print(f"  States with >= 1 center: {states_with_centers}")
    print(f"  States with 0 centers:   {states_without_centers}")
    print(f"  Total centers nationally: {len(active_centers)}")
    print(f"  Total agencies: {len(agencies)}")
    print(f"  National index: {OUT_ROOT / 'national' / 'index.html'}")


if __name__ == "__main__":
    main()
