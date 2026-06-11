#!/usr/bin/env python3
"""
Render the Wildlife911 Virginia edition as static HTML pages.

Reads:  wildlifestats/_wren/wildlife911/states/VA/guides/wildlife_rescue_guides_va.yaml
Writes: /wildlife911/index.html
        /wildlife911/start/index.html
        /wildlife911/species/<slug>/index.html  (one per species)
        /wildlife911/state/index.html  (state directory landing)

This is a render-only script. It's deterministic — same YAML in produces
byte-identical HTML out. Run from repo root: python wildlifestats/_wren/wildlife911/scripts/render_static_va.py

The script supports the Phase 4.6h static landing requirement. When the
LLM-driven WREN pill ships in Phase 7g, the same YAML drives both the
LLM context AND this static fallback surface.

Per Phase 4.6 hardening order:
- Renders the VA YAML as-is (with Blue Ridge Wildlife Center, SW VA, and
  Wildlife Center of Virginia listed as referrals — legitimate Virginia
  rehab options per §19 + Mike's 2026-06-10 21:21 ET clarification).
- Non-VA state pages defer to AnimalHelpNow + state agency lookup.
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[4]
YAML_PATH = REPO_ROOT / "wildlifestats/_wren/wildlife911/states/VA/guides/wildlife_rescue_guides_va.yaml"
OUT_ROOT = REPO_ROOT / "wildlife911"


# ---------- HTML chrome ----------

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
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="https://wildlifestats.org/assets/img/og-default.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+Pro:wght@400;600&display=swap">
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
          <li><a href="/wildlife911/" class="active">Wildlife911</a></li>
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


def slug(s):
    return re.sub(r"[^a-z0-9-]+", "-", s.lower()).strip("-")


def safety_box():
    """The two non-negotiable safety rails, displayed prominently."""
    return """
      <aside class="w911-safety">
        <h2 class="w911-safety__title">🚨 Two situations are always emergencies</h2>
        <div class="w911-safety__row">
          <p><strong>1. Any bird that hits a window, vehicle, or building.</strong> Internal injuries and concussion are likely even when the bird flies away or appears alert. Do not advise "monitor and see." Place the bird in a ventilated box in a quiet, dark place and contact a licensed rehabilitator immediately.</p>
        </div>
        <div class="w911-safety__row">
          <p><strong>2. Any wild animal that has been in a cat's or dog's mouth.</strong> Bacterial infections from cat saliva are frequently fatal within 24-48 hours, even when no injury is visible. Referral is always required.</p>
        </div>
      </aside>
"""


def universal_calls():
    return """
      <section class="w911-calls">
        <h2>Who to call</h2>
        <ul class="w911-calls__list">
          <li><strong>Virginia DWR licensed rehabilitators</strong> — <a href="https://dwr.virginia.gov/wildlife/injured/rehabilitators/" rel="noopener">dwr.virginia.gov/wildlife/injured/rehabilitators</a></li>
          <li><strong>Animal Help Now (nationwide)</strong> — <a href="https://animalhelpnow.org" rel="noopener">animalhelpnow.org</a></li>
          <li><strong>Local animal control</strong> (especially for any rabies-vector species: fox, skunk, raccoon, bat, groundhog)</li>
        </ul>
        <p class="w911-calls__tip">Call two or three rehabilitators — availability varies. If you reach voicemail, leave a detailed message with your name, callback number, exact location, species (or description), the animal's condition, and what containment steps you have taken.</p>
      </section>
"""


def emoji_checklist(items):
    """Render the universal startup checklist as a clean list."""
    out = '<ul class="w911-checklist">\n'
    for item in items:
        # YAML uses **bold** markdown; convert to <strong>
        html = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", item)
        # Convert raw URLs in this checklist to links
        html = re.sub(r"(https?://[^\s)]+)", r'<a href="\1" rel="noopener">\1</a>', html)
        out += f"        <li>{html}</li>\n"
    out += "      </ul>\n"
    return out


# ---------- /wildlife911/index.html ----------

def render_landing(data):
    species_options = data["startup"]["script"]["menu_species_options"]
    checklist = data["startup"]["script"]["emoji_checklist"]

    body = """
  <main>
    <div class="container">
      <p class="kicker">Wildlife911 Virginia</p>
      <h1 class="w911-h1">Found a sick, injured, or orphaned wild animal?</h1>
      <p class="w911-lead">Wildlife911 is a triage and referral guide. It does not provide care, feeding, or treatment advice — those are decisions for a licensed wildlife rehabilitator. The Virginia edition below is curated to Virginia law and referral options. For other states, scroll down for the national fallback.</p>

      <div class="w911-cta-row">
        <a href="/wildlife911/start/" class="w911-cta-primary">🚨🐾 Start Wildlife 911 Virginia</a>
      </div>
"""
    body += safety_box()

    body += """
      <section class="w911-prep">
        <h2>Before you do anything else</h2>
"""
    body += emoji_checklist(checklist)
    body += "      </section>\n"

    body += universal_calls()

    # Species grid
    body += """
      <section class="w911-species-grid">
        <h2>Or jump straight to your species</h2>
        <p class="w911-species-grid__intro">Tap a species below for triage criteria specific to that animal.</p>
        <ul class="w911-species-grid__list">
"""
    for opt in species_options:
        if opt.lower().startswith("other"):
            continue
        sp_slug = MENU_LABEL_TO_SLUG.get(opt, slug(opt))
        body += f'          <li><a href="/wildlife911/species/{sp_slug}/">{opt}</a></li>\n'
    body += """        </ul>
      </section>

      <section class="w911-disclaimer">
        <h2>What Wildlife911 is — and is not</h2>
        <p><strong>Is:</strong> a triage assistant for finders of sick, injured, or orphaned wildlife. Tells you what to observe, what containment is safe, and who to call.</p>
        <p><strong>Is not:</strong> a substitute for a licensed wildlife rehabilitator. Wildlife911 never provides feeding, watering, rearing, or medical treatment guidance. Wildlife911 cannot dispatch a rehabilitator to your location.</p>
        <p>Wildlife911 Virginia is a curated extension of the original Wildlife911 CustomGPT authored by Michael Oak. Its content is calibrated to Virginia law and Virginia rehab options. <a href="/wildlife911/state/">For other states, see the state directory.</a></p>
      </section>
    </div>
  </main>
"""
    return body


# ---------- /wildlife911/start/index.html ----------

def render_dispatcher(data):
    script = data["startup"]["script"]
    intro = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", script["intro"])
    body = f"""
  <main>
    <div class="container">
      <p class="kicker">Wildlife911 Virginia · Dispatcher</p>
      <h1 class="w911-h1">🚨🐾 Wildlife 911 Virginia</h1>
      <p class="w911-intro">{intro}</p>

      <p class="w911-intro">{script["reminders_title"]}</p>
"""
    body += emoji_checklist(script["emoji_checklist"])

    body += safety_box()

    # Step 1: species
    body += """
      <section class="w911-step">
        <h2 class="w911-step__heading"><span class="w911-step__num">Step 1</span> What kind of animal have you found?</h2>
        <ul class="w911-species-grid__list">
"""
    for opt in script["menu_species_options"]:
        if opt.lower().startswith("other"):
            slug_str = "unknown"
        else:
            slug_str = MENU_LABEL_TO_SLUG.get(opt, slug(opt))
        body += f'          <li><a href="/wildlife911/species/{slug_str}/">{opt}</a></li>\n'
    body += "        </ul>\n      </section>\n"

    body += universal_calls()
    body += "    </div>\n  </main>\n"
    return body


# ---------- /wildlife911/species/<slug>/index.html ----------

# Map YAML species_guides keys to URL slugs + display order
SPECIES_KEY_TO_SLUG = {
    "bird": "bird",
    "rabbit": "rabbit",
    "squirrel": "squirrel",
    "white_tailed_deer": "deer-fawn",
    "fox": "fox",
    "raccoon": "raccoon",
    "skunk": "skunk",
    "groundhog": "groundhog",
    "bat": "bat",
    "reptiles_amphibians": "reptiles-amphibians",
    "opossum": "opossum",
}

SPECIES_DISPLAY_LABEL = {
    "bird": "Bird",
    "rabbit": "Rabbit",
    "squirrel": "Squirrel",
    "white_tailed_deer": "Deer (Fawn)",
    "fox": "Fox",
    "raccoon": "Raccoon",
    "skunk": "Skunk",
    "groundhog": "Groundhog",
    "bat": "Bat",
    "reptiles_amphibians": "Turtle / Snake / Frog (Reptiles & Amphibians)",
    "opossum": "Opossum",
}

# Menu-option label → URL slug. Used by the dispatcher and landing pages.
MENU_LABEL_TO_SLUG = {
    "Bird": "bird",
    "Rabbit": "rabbit",
    "Squirrel": "squirrel",
    "Fox": "fox",
    "Raccoon": "raccoon",
    "Skunk": "skunk",
    "Groundhog": "groundhog",
    "Bat": "bat",
    "Turtle / Snake / Frog (Reptiles & Amphibians)": "reptiles-amphibians",
    "Deer (Fawn)": "deer-fawn",
}


def render_species_block(label, block):
    """Render a single species_guides block as the body of a species page."""
    name = block.get("name", label)
    category = block.get("category", "")
    key_points = block.get("key_points", [])
    rescue = block.get("rescue_criteria", {})

    body = f"""
  <main>
    <div class="container">
      <p class="kicker">Wildlife911 Virginia · {category}</p>
      <h1 class="w911-h1">{name}</h1>
"""

    if key_points:
        body += '      <ul class="w911-keypoints">\n'
        for kp in key_points:
            body += f"        <li>{kp}</li>\n"
        body += "      </ul>\n"

    body += safety_box()

    if "injured_orphan_signs" in rescue:
        body += """
      <section class="w911-criteria">
        <h2>Signs that mean: refer immediately</h2>
        <ul>
"""
        for sign in rescue["injured_orphan_signs"]:
            body += f"          <li>{sign}</li>\n"
        body += "        </ul>\n      </section>\n"

    # Render remaining rescue_criteria keys as labeled sections
    label_map = {
        "if_injured": "If the animal is injured",
        "if_fledgling": "If it's a fledgling (feathered, hopping)",
        "if_nestling": "If it's a nestling (unfeathered)",
        "if_nest_disturbed": "If the nest was disturbed",
        "if_healthy_furred": "If it appears healthy and independent",
        "if_fallen_uninjured": "If it fell but appears uninjured",
        "if_fully_furred_mobile": "If fully furred and mobile",
        "if_orphan_suspected": "If you suspect it is orphaned",
        "if_bat_in_house": "If a bat is in the house",
        "if_human_or_pet_contact": "If a human or pet has had contact",
        "if_alone_no_visible_injury": "If alone with no visible injury",
        "if_walking_unsteady": "If walking, unsteady, or daytime activity (rabies-vector)",
    }
    for key, label_text in label_map.items():
        if key in rescue:
            body += f'      <section class="w911-rescue-step"><h2>{label_text}</h2><p>{rescue[key]}</p></section>\n'

    body += universal_calls()

    body += '      <p class="w911-back"><a href="/wildlife911/start/">← Back to dispatcher</a></p>\n'
    body += "    </div>\n  </main>\n"
    return body


# ---------- /wildlife911/state/index.html ----------

def render_state_landing():
    body = """
  <main>
    <div class="container prose">
      <p class="kicker">Wildlife911 · State directory</p>
      <h1>Wildlife911 by state</h1>
      <p>Wildlife911 is currently <strong>Virginia-complete</strong>. The Virginia edition is curated to Virginia Department of Wildlife Resources licensing, Virginia chronic wasting disease and rabies regulations, and Virginia rehab-center referral patterns.</p>

      <p>For finders of injured wildlife outside Virginia, the universal national starting point is <strong><a href="https://animalhelpnow.org" rel="noopener">Animal Help Now</a></strong>, which routes by ZIP code to nearby licensed rehabilitators and animal control. Your state wildlife agency (typically a Department of Natural Resources, Department of Fish and Wildlife, or Department of Game and Inland Fisheries) is the second institutional contact, particularly for rabies-vector species and any threatened or endangered species.</p>

      <h2>Available state editions</h2>
      <ul>
        <li><a href="/wildlife911/state/VA/"><strong>Virginia</strong></a> — full edition with species guides, dispatcher flow, and referral directory</li>
      </ul>

      <h2>State editions in development</h2>
      <p>Per-state editions are an editorial workstream, not engineering. Each state edition is authored by someone with on-the-ground knowledge of that state's wildlife law, rehab community, and species mix. State editions can be contributed by state wildlife agency staff, partner wildlife rehabilitation organizations, or delegated editors. <a href="/about.html">Contact us</a> to discuss authoring a state edition.</p>

      <h2>National fallback (any state)</h2>
"""
    body += universal_calls()
    body += safety_box()
    body += "    </div>\n  </main>\n"
    return body


def render_state_va(data):
    """A redirect-equivalent: Virginia state page is the main Wildlife911 landing."""
    body = """
  <main>
    <div class="container prose">
      <p class="kicker">Wildlife911 · State directory</p>
      <h1>Virginia</h1>
      <p>The Wildlife911 Virginia edition is the canonical Virginia triage and referral guide. <a href="/wildlife911/">Open Wildlife911 Virginia →</a></p>
    </div>
  </main>
"""
    return body


# ---------- main ----------

def main():
    raw = YAML_PATH.read_text(encoding="utf-8")
    # The YAML's first line is a bare quoted version literal that PyYAML
    # parses as a separate document. Strip leading non-mapping lines until
    # the first proper mapping key.
    lines = raw.splitlines()
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and ":" in stripped and not stripped.startswith("#") and not stripped.startswith('"'):
            start = i
            break
    cleaned = "\n".join(lines[start:])
    data = yaml.safe_load(cleaned)

    # /wildlife911/index.html
    landing = page(
        title="Wildlife911 Virginia — find help for injured wildlife",
        description="Triage and referral assistant for finders of sick, injured, or orphaned wildlife in Virginia. Static dispatcher flow with species-specific guidance and licensed rehabilitator directory.",
        canonical="/wildlife911/",
        body=render_landing(data),
    )
    (OUT_ROOT / "index.html").write_text(landing, encoding="utf-8")

    # /wildlife911/start/index.html
    dispatcher = page(
        title="🚨🐾 Start Wildlife 911 Virginia",
        description="Step through the Wildlife911 Virginia dispatcher: identify your species, get triage criteria, find a licensed rehabilitator.",
        canonical="/wildlife911/start/",
        body=render_dispatcher(data),
    )
    (OUT_ROOT / "start" / "index.html").write_text(dispatcher, encoding="utf-8")

    # /wildlife911/species/<slug>/index.html
    species_guides = data.get("species_guides", {})
    for yaml_key, block in species_guides.items():
        slug_str = SPECIES_KEY_TO_SLUG.get(yaml_key, slug(yaml_key))
        label = SPECIES_DISPLAY_LABEL.get(yaml_key, block.get("name", yaml_key))
        species_dir = OUT_ROOT / "species" / slug_str
        species_dir.mkdir(parents=True, exist_ok=True)
        sp_page = page(
            title=f"Wildlife911 Virginia — {label}",
            description=f"What to do if you find a {label.lower()} in Virginia. Triage criteria, immediate-referral signs, and licensed rehabilitator directory.",
            canonical=f"/wildlife911/species/{slug_str}/",
            body=render_species_block(label, block),
        )
        (species_dir / "index.html").write_text(sp_page, encoding="utf-8")

    # Catch-all unknown species page
    unknown_dir = OUT_ROOT / "species" / "unknown"
    unknown_dir.mkdir(parents=True, exist_ok=True)
    unknown_body = """
  <main>
    <div class="container prose">
      <p class="kicker">Wildlife911 Virginia</p>
      <h1>Not sure what species you found?</h1>
      <p>That is fine. Skip the species-specific page and use the universal triage steps below. The licensed rehabilitator you call will help identify the animal from your description over the phone.</p>
""" + safety_box() + universal_calls() + """
      <p class="w911-back"><a href="/wildlife911/start/">← Back to dispatcher</a></p>
    </div>
  </main>
"""
    (unknown_dir / "index.html").write_text(
        page(
            title="Wildlife911 Virginia — Species unknown",
            description="Universal triage steps for finders of sick, injured, or orphaned wildlife of unknown species in Virginia.",
            canonical="/wildlife911/species/unknown/",
            body=unknown_body,
        ),
        encoding="utf-8",
    )

    # /wildlife911/state/index.html
    state_landing = page(
        title="Wildlife911 — State directory",
        description="Wildlife911 is currently Virginia-complete. National fallback via Animal Help Now and state wildlife agencies.",
        canonical="/wildlife911/state/",
        body=render_state_landing(),
    )
    (OUT_ROOT / "state").mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "state" / "index.html").write_text(state_landing, encoding="utf-8")

    # /wildlife911/state/VA/index.html (canonical redirect-equivalent)
    (OUT_ROOT / "state" / "VA").mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "state" / "VA" / "index.html").write_text(
        page(
            title="Wildlife911 Virginia",
            description="Wildlife911 Virginia state edition — full triage and referral guide.",
            canonical="/wildlife911/state/VA/",
            body=render_state_va(data),
        ),
        encoding="utf-8",
    )

    # Count pages
    pages = list(OUT_ROOT.rglob("index.html"))
    print(f"Rendered {len(pages)} Wildlife911 pages from {YAML_PATH.name}:")
    for p in sorted(pages):
        print(f"  /{p.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
