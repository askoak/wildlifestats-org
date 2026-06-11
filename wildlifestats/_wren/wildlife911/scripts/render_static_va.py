#!/usr/bin/env python3
"""
Render the Wildlife911 Virginia edition as static HTML pages.

v2 (2026-06-11): substantially richer species pages that ingest:
  - the master YAML (decision-tree triage criteria)
  - the per-species .docx clinical reference content (extracted to JSON)
  - the infographics and flow-chart assets (embedded inline per species)

Renders with a warmer hotline-operator visual treatment specific to
Wildlife911, distinct from the institutional-research voice of the rest
of the site.

Reads:
  - wildlifestats/_wren/wildlife911/states/VA/guides/wildlife_rescue_guides_va.yaml
  - wildlifestats/_wren/wildlife911/states/VA/extracted/species_content.json
  - wildlifestats/_wren/wildlife911/states/VA/assets/*

Writes:
  - /wildlife911/index.html (landing + chatbot UI shell)
  - /wildlife911/start/index.html (dispatcher)
  - /wildlife911/species/<slug>/index.html (one per species, richly populated)
  - /wildlife911/state/index.html (state directory)
  - /wildlife911/state/VA/index.html
"""

import json
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
EXTRACTED_PATH = REPO_ROOT / "wildlifestats/_wren/wildlife911/states/VA/extracted/species_content.json"
ASSETS_SRC = REPO_ROOT / "wildlifestats/_wren/wildlife911/states/VA/assets"
ASSETS_DEST = REPO_ROOT / "assets/img/wildlife911"
OUT_ROOT = REPO_ROOT / "wildlife911"


# ----- HTML chrome (same nav as the rest of the site) -----

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


def slug(s):
    return re.sub(r"[^a-z0-9-]+", "-", s.lower()).strip("-")


# ----- Reusable content fragments -----

def chatbot_shell():
    """The 'Ask Wildlife911' chat UI — shipped as a visible shell even though
    the LLM backend (Phase 7g) isn't wired yet. The input is disabled with a
    clear 'coming soon' label so the chatbot identity is visibly part of
    Wildlife911 right now."""
    return """
      <section class="w911-chat" aria-label="Ask Wildlife911">
        <div class="w911-chat__avatar">🐾</div>
        <div class="w911-chat__body">
          <h2 class="w911-chat__title">Ask Wildlife911</h2>
          <p class="w911-chat__intro">A conversational AI assistant trained on the Wildlife911 Virginia knowledge base, live wildlife rehabilitation literature, and the national rehab-center directory. Describe what you've found in plain language — Wildlife911 will guide you through triage and connect you to a licensed rehabilitator near you.</p>
          <form class="w911-chat__form" onsubmit="return false;">
            <label for="w911-chat-input" class="visually-hidden">Describe what you've found</label>
            <input id="w911-chat-input" type="text" class="w911-chat__input" placeholder="Describe what you've found — for example, 'a fledgling bird hopping in my yard'" disabled>
            <button type="submit" class="w911-chat__send" disabled aria-label="Send (coming soon)">Send</button>
          </form>
          <p class="w911-chat__status">Live AI assistant coming soon (Phase 7g of the WildlifeStats build). In the meantime, use the species pages below or the dispatcher — both deliver the same triage decision tree Wildlife911 will use.</p>
        </div>
      </section>
"""


def safety_box():
    """The two non-negotiable safety rails. Visible on landing, dispatcher,
    and species pages. Warm tone but high-contrast."""
    return """
      <aside class="w911-safety" role="alert">
        <h2 class="w911-safety__title">Two situations are always emergencies</h2>
        <div class="w911-safety__row">
          <span class="w911-safety__num">1</span>
          <p><strong>Any bird that hits a window, vehicle, or building.</strong> Internal injuries and concussion are likely even when the bird flies away or appears alert. Do not advise "monitor and see." Place the bird in a ventilated cardboard box in a quiet, dark place and contact a licensed rehabilitator immediately.</p>
        </div>
        <div class="w911-safety__row">
          <span class="w911-safety__num">2</span>
          <p><strong>Any wild animal that has been in a cat's or dog's mouth.</strong> Bacterial infections from pet saliva are frequently fatal within 24 to 48 hours, even when no injury is visible. Referral is always required.</p>
        </div>
      </aside>
"""


def universal_calls():
    return """
      <section class="w911-calls" aria-label="Who to call">
        <h2>Who to call</h2>
        <div class="w911-calls__grid">
          <div class="w911-calls__card">
            <h3>Virginia DWR licensed rehabilitators</h3>
            <p>The official Virginia Department of Wildlife Resources directory of permitted wildlife rehabilitators.</p>
            <p><a href="https://dwr.virginia.gov/wildlife/injured/rehabilitators/" rel="noopener" class="w911-link">dwr.virginia.gov/wildlife/injured/rehabilitators</a></p>
          </div>
          <div class="w911-calls__card">
            <h3>Animal Help Now (nationwide)</h3>
            <p>ZIP-code-based directory of wildlife rehabilitators and animal control nationwide.</p>
            <p><a href="https://animalhelpnow.org" rel="noopener" class="w911-link">animalhelpnow.org</a></p>
          </div>
          <div class="w911-calls__card">
            <h3>Local animal control</h3>
            <p>For rabies-vector species (fox, skunk, raccoon, bat, groundhog), and for any animal in your home, contact local animal control first.</p>
          </div>
        </div>
        <p class="w911-calls__tip">Call two or three rehabilitators — availability varies. If you reach voicemail, leave a detailed message with your name and callback number, exact location, species (or description), the animal's condition, and what containment steps you have taken.</p>
      </section>
"""


def render_paragraphs_with_bold(paragraphs):
    """Render a list of paragraph strings as HTML <p> tags, converting
    **bold** markdown to <strong> and inline URLs to links."""
    out = []
    for p in paragraphs:
        html = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", p)
        html = re.sub(r"(https?://[^\s)]+)", r'<a href="\1" rel="noopener" class="w911-link">\1</a>', html)
        out.append(f"        <p>{html}</p>")
    return "\n".join(out)


def render_section(heading, paragraphs):
    """Render a docx-extracted section."""
    if not paragraphs:
        return ""
    return f"""
      <section class="w911-clinical-section">
        <h2>{heading}</h2>
{render_paragraphs_with_bold(paragraphs)}
      </section>
"""


# ----- Per-species infographic mapping -----
# Each species page embeds the relevant infographics and flow charts.

SPECIES_ASSETS = {
    "bird": [
        ("baby_bird_flow_chart.jpg", "Decision flow chart for found baby birds — nestling, fledgling, injured, or healthy. Used by Wildlife911 Virginia triage."),
    ],
    "rabbit": [
        ("baby_bunny_flow_charts.jpg", "Decision flow chart for found baby rabbits. Mother rabbits visit nests only twice daily at dawn and dusk, so 'alone' rarely means 'orphaned.'"),
        ("baby-rabbit-infographic.png.webp", "Reference infographic — baby cottontail rabbit development stages and when to intervene."),
    ],
    "squirrel": [
        ("squirrel_flow_chart.jpg", "Decision flow chart for found baby squirrels. Squirrel mothers will often retrieve fallen babies if given time and a warm container at the base of the tree."),
        ("baby-squirrel-infographic.png.webp", "Reference infographic — baby squirrel development stages and reunification protocol."),
    ],
    "deer-fawn": [
        ("fawn-infographic.jpg.webp", "Reference infographic — white-tailed deer fawn behavior. Does leave fawns alone for hours; lone fawns are almost never orphans."),
    ],
}


# ----- Per-species docx mapping -----
# Maps slug → list of docx keys to ingest for that species. Some species
# (rabies vectors) draw from multiple docs.

SPECIES_DOCX = {
    "bird": ["bird"],
    "rabbit": ["rabbit"],
    "squirrel": ["squirrel"],
    "deer-fawn": ["deer"],
    "fox": ["fox", "rabies_fox_skunk_raccoon_bat"],
    "raccoon": ["raccoon", "rabies_fox_skunk_raccoon_bat"],
    "skunk": ["skunk", "rabies_fox_skunk_raccoon_bat"],
    "bat": ["bats", "rabies_fox_skunk_raccoon_bat"],
    "groundhog": ["groundhog"],
    "reptiles-amphibians": ["reptiles_and_amphibians"],
    "opossum": ["opossum"],
}


# YAML → URL-slug mapping for species_guides
YAML_KEY_TO_SLUG = {
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

# Display labels
SPECIES_LABEL = {
    "bird": "Bird",
    "rabbit": "Rabbit (Cottontail)",
    "squirrel": "Squirrel",
    "deer-fawn": "Deer (Fawn)",
    "fox": "Fox",
    "raccoon": "Raccoon",
    "skunk": "Skunk",
    "groundhog": "Groundhog",
    "bat": "Bat",
    "reptiles-amphibians": "Reptiles & Amphibians",
    "opossum": "Opossum",
}

# Hotline-operator-friendly one-liner per species
SPECIES_TAGLINE = {
    "bird": "Window strikes are emergencies. Fledglings on the ground are usually fine. Cat-caught birds always need help.",
    "rabbit": "Mothers visit only at dawn and dusk. A baby alone in a nest is almost never orphaned.",
    "squirrel": "Fallen babies can often be reunited with mom. Warm them up and give her time to retrieve them.",
    "deer-fawn": "Does leave fawns alone for hours. A lone fawn is almost never an orphan — leave it.",
    "fox": "Rabies-vector species. Do not handle. Call animal control or a licensed rehabber first.",
    "raccoon": "Rabies-vector species. Do not handle. Look for mom before assuming orphan.",
    "skunk": "Rabies-vector species. Daytime activity or unsteadiness needs immediate animal control.",
    "groundhog": "Rabies-vector species in Virginia. Day-active is normal; staggering is not.",
    "bat": "Rabies-vector species. Any bat in living space requires animal control and rabies-exposure evaluation.",
    "reptiles-amphibians": "Do not relocate. Help across the road in the direction it was heading. Reptiles travel known territories.",
    "opossum": "Marsupials. Young that are still attached to mother are not orphans. Check pouch on roadkill mothers.",
}


# ----- Species page renderer (the big one) -----

def render_species_page(species_slug, yaml_data, extracted_data):
    """Render a richly-populated species page."""
    label = SPECIES_LABEL.get(species_slug, species_slug.title())
    tagline = SPECIES_TAGLINE.get(species_slug, "")

    # Find the YAML species block (if mapped)
    yaml_block = None
    for yk, ys in YAML_KEY_TO_SLUG.items():
        if ys == species_slug:
            yaml_block = yaml_data.get("species_guides", {}).get(yk, {})
            break
    yaml_block = yaml_block or {}

    # Find docx blocks
    docx_keys = SPECIES_DOCX.get(species_slug, [])

    # Get infographics
    assets = SPECIES_ASSETS.get(species_slug, [])

    # Begin rendering
    body = f"""
  <main>
    <div class="container">
      <p class="kicker"><a href="/wildlife911/" class="w911-link-soft">Wildlife911 Virginia</a> · Species</p>
      <h1 class="w911-h1">{label}</h1>
      <p class="w911-tagline">{tagline}</p>
"""

    # Safety box always at top
    body += safety_box()

    # Embed infographic(s) prominently right after safety box
    if assets:
        body += '      <section class="w911-infographics" aria-label="Reference infographics">\n'
        for asset_file, caption in assets:
            body += f"""        <figure class="w911-infographic">
          <img src="/assets/img/wildlife911/{asset_file}" alt="{caption}" loading="lazy">
          <figcaption>{caption}</figcaption>
        </figure>
"""
        body += '      </section>\n'

    # YAML structured rescue criteria — the actionable triage block
    rescue = yaml_block.get("rescue_criteria", {})
    if rescue:
        body += '      <section class="w911-triage">\n'
        body += '        <h2>Immediate triage — what to look for</h2>\n'

        # Refer-immediately signs
        if "injured_orphan_signs" in rescue:
            body += '        <div class="w911-triage__refer">\n'
            body += '          <h3>Signs that mean: refer immediately</h3>\n          <ul>\n'
            for sign in rescue["injured_orphan_signs"]:
                body += f"            <li>{sign}</li>\n"
            body += '          </ul>\n        </div>\n'

        # Conditional rescue scenarios
        scenario_labels = {
            "if_injured": "If the animal is injured",
            "if_fledgling": "If it is a fledgling (feathered, hopping)",
            "if_nestling": "If it is a nestling (no feathers, eyes closed)",
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
        for key, label_text in scenario_labels.items():
            if key in rescue:
                body += f"""        <div class="w911-triage__scenario">
          <h4>{label_text}</h4>
          <p>{rescue[key]}</p>
        </div>
"""
        body += '      </section>\n'

    # YAML key points
    if yaml_block.get("key_points"):
        body += '      <section class="w911-keypoints-section">\n'
        body += '        <h2>Key points</h2>\n        <ul class="w911-keypoints">\n'
        for kp in yaml_block["key_points"]:
            body += f"          <li>{kp}</li>\n"
        body += '        </ul>\n      </section>\n'

    # Full docx clinical content (progressive disclosure — visible by default,
    # readers can skim past)
    if docx_keys:
        body += """
      <section class="w911-clinical">
        <h2 class="w911-clinical__heading">Detailed reference</h2>
        <p class="w911-clinical__intro">The clinical and behavioral reference below is the full Wildlife911 Virginia guidance for this species. It is written for finders, volunteers, and educators who want to understand the reasoning behind the triage decisions above.</p>
"""
        for docx_key in docx_keys:
            doc = extracted_data.get(docx_key)
            if not doc:
                continue
            # Render each section's content
            for section in doc["sections"]:
                heading = section["heading"]
                paragraphs = section["body"]
                if not paragraphs:
                    continue
                # Skip the first "Overview" if it's just the document title
                if heading == "Overview" and len(paragraphs) <= 2 and "Guide" in (paragraphs[0] if paragraphs else ""):
                    # Treat as intro: use as a sub-title only
                    continue
                body += render_section(heading, paragraphs)
        body += "      </section>\n"

    # Chatbot shell at bottom (less prominent than landing-page placement)
    body += chatbot_shell()

    # Universal calls
    body += universal_calls()

    body += """      <p class="w911-back"><a href="/wildlife911/start/" class="w911-link">← Back to dispatcher</a></p>
    </div>
  </main>
"""
    return body


# ----- Landing page -----

def render_landing(yaml_data):
    script = yaml_data["startup"]["script"]
    species_menu = [s for s in script["menu_species_options"] if not s.lower().startswith("other")]

    body = """
  <main>
    <div class="container">
      <p class="kicker">Wildlife911 Virginia</p>
      <h1 class="w911-h1">Found a sick, injured, or orphaned wild animal?</h1>
      <p class="w911-lead">Wildlife911 is your calm, evidence-based first step. It will help you decide whether the animal actually needs rescue (many don't), how to safely contain it if it does, and which licensed rehabilitator to contact. It will never tell you to feed it, water it, or treat it yourself — those are decisions for a professional.</p>
      <div class="w911-cta-row">
        <a href="/wildlife911/start/" class="w911-cta-primary">🚨🐾 Start Wildlife 911 Virginia</a>
      </div>
"""

    body += safety_box()
    body += chatbot_shell()

    # Species grid as the main path
    body += """
      <section class="w911-species-grid" aria-label="Species selector">
        <h2>Jump to your species</h2>
        <p class="w911-species-grid__intro">Tap a species below for triage criteria, flow charts, and detailed clinical reference.</p>
        <ul class="w911-species-grid__list">
"""
    menu_to_slug = {
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
    for opt in species_menu:
        sp_slug = menu_to_slug.get(opt, slug(opt))
        tagline = SPECIES_TAGLINE.get(sp_slug, "")
        body += f"""          <li>
            <a href="/wildlife911/species/{sp_slug}/">
              <strong>{opt}</strong>
              <span class="w911-species-grid__tagline">{tagline}</span>
            </a>
          </li>
"""
    body += "        </ul>\n      </section>\n"

    body += universal_calls()

    body += """
      <section class="w911-disclaimer">
        <h2>What Wildlife911 is — and is not</h2>
        <p><strong>Is:</strong> a triage assistant for finders of sick, injured, or orphaned wildlife. Built around the principle that most situations look more urgent than they are — and that when an animal does need help, the right answer is a licensed wildlife rehabilitator, not a layperson.</p>
        <p><strong>Is not:</strong> a substitute for a licensed wildlife rehabilitator. Wildlife911 never provides feeding, watering, rearing, or medical treatment guidance.</p>
        <p>Wildlife911 Virginia is curated to Virginia law, Virginia rabies regulations, Virginia chronic wasting disease counties, and the active Virginia wildlife rehabilitation community (Blue Ridge Wildlife Center, Wildlife Center of Virginia, Southwest Virginia Wildlife Center, and others). <a href="/wildlife911/state/" class="w911-link">For other states, see the state directory.</a></p>
      </section>
    </div>
  </main>
"""
    return body


def render_dispatcher(yaml_data):
    script = yaml_data["startup"]["script"]
    intro = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", script["intro"])

    body = f"""
  <main>
    <div class="container">
      <p class="kicker"><a href="/wildlife911/" class="w911-link-soft">Wildlife911 Virginia</a> · Dispatcher</p>
      <h1 class="w911-h1">🚨🐾 Wildlife 911 Virginia</h1>
      <p class="w911-lead">{intro}</p>

      <h2 class="w911-step-heading">Before you go further</h2>
"""
    # Emoji checklist from YAML
    body += '      <ul class="w911-checklist">\n'
    for item in script["emoji_checklist"]:
        html = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", item)
        html = re.sub(r"(https?://[^\s)]+)", r'<a href="\1" rel="noopener" class="w911-link">\1</a>', html)
        body += f"        <li>{html}</li>\n"
    body += "      </ul>\n"

    body += safety_box()

    # Step 1: species
    body += """
      <section class="w911-step">
        <h2 class="w911-step-heading"><span class="w911-step-num">Step 1</span> What kind of animal have you found?</h2>
        <ul class="w911-species-grid__list">
"""
    menu_to_slug = {
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
    for opt in script["menu_species_options"]:
        if opt.lower().startswith("other"):
            sp_slug = "unknown"
        else:
            sp_slug = menu_to_slug.get(opt, slug(opt))
        tagline = SPECIES_TAGLINE.get(sp_slug, "")
        body += f"""          <li>
            <a href="/wildlife911/species/{sp_slug}/">
              <strong>{opt}</strong>
              <span class="w911-species-grid__tagline">{tagline}</span>
            </a>
          </li>
"""
    body += "        </ul>\n      </section>\n"

    body += chatbot_shell()
    body += universal_calls()

    body += "    </div>\n  </main>\n"
    return body


def render_state_landing():
    body = """
  <main>
    <div class="container prose">
      <p class="kicker">Wildlife911 · State directory</p>
      <h1>Wildlife911 by state</h1>
      <p>Wildlife911 is currently <strong>Virginia-complete</strong>. The Virginia edition is curated to Virginia Department of Wildlife Resources licensing, Virginia chronic wasting disease and rabies regulations, and the active Virginia wildlife rehabilitation community.</p>
      <p>For finders of injured wildlife outside Virginia, the universal national starting point is <strong><a href="https://animalhelpnow.org" rel="noopener" class="w911-link">Animal Help Now</a></strong>, which routes by ZIP code to nearby licensed rehabilitators and animal control. Your state wildlife agency is the second institutional contact, particularly for rabies-vector species and any threatened or endangered species.</p>

      <h2>Available state editions</h2>
      <ul>
        <li><a href="/wildlife911/state/VA/" class="w911-link"><strong>Virginia</strong></a> — full edition with species guides, dispatcher flow, infographics, and referral directory</li>
      </ul>

      <h2>State editions in development</h2>
      <p>Per-state editions are an editorial workstream, not engineering. Each state edition is authored by someone with on-the-ground knowledge of that state's wildlife law, rehab community, and species mix. State editions can be contributed by state wildlife agency staff, partner wildlife rehabilitation organizations, or delegated editors. <a href="/about.html" class="w911-link">Contact us</a> to discuss authoring a state edition.</p>

      <h2>National fallback (any state)</h2>
"""
    body += universal_calls()
    body += safety_box()
    body += "    </div>\n  </main>\n"
    return body


def render_state_va():
    body = """
  <main>
    <div class="container prose">
      <p class="kicker">Wildlife911 · State directory</p>
      <h1>Virginia</h1>
      <p>The Wildlife911 Virginia edition is the canonical Virginia triage and referral guide.</p>
      <p><a href="/wildlife911/" class="w911-cta-primary">Open Wildlife911 Virginia →</a></p>
    </div>
  </main>
"""
    return body


# ----- main -----

def main():
    # Load YAML (handle the leading version literal)
    raw = YAML_PATH.read_text(encoding="utf-8")
    lines = raw.splitlines()
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and ":" in stripped and not stripped.startswith("#") and not stripped.startswith('"'):
            start = i
            break
    yaml_data = yaml.safe_load("\n".join(lines[start:]))

    # Load extracted docx content
    extracted_data = json.loads(EXTRACTED_PATH.read_text(encoding="utf-8"))

    # Sync assets from VA edition to /assets/img/wildlife911/
    ASSETS_DEST.mkdir(parents=True, exist_ok=True)
    for asset in ASSETS_SRC.iterdir():
        if asset.is_file():
            dest = ASSETS_DEST / asset.name
            dest.write_bytes(asset.read_bytes())
    print(f"Synced {len(list(ASSETS_SRC.iterdir()))} assets to {ASSETS_DEST}")

    # Wipe existing rendered pages
    if OUT_ROOT.exists():
        import shutil
        shutil.rmtree(OUT_ROOT)
    OUT_ROOT.mkdir(parents=True)

    # /wildlife911/index.html
    (OUT_ROOT / "index.html").write_text(
        page(
            title="Wildlife911 Virginia — find help for injured wildlife",
            description="Calm, evidence-based triage for finders of sick, injured, or orphaned wildlife. Virginia edition: species guides, infographics, flow charts, and the Virginia licensed rehabilitator directory.",
            canonical="/wildlife911/",
            body=render_landing(yaml_data),
        ),
        encoding="utf-8",
    )

    # /wildlife911/start/index.html
    (OUT_ROOT / "start").mkdir(parents=True)
    (OUT_ROOT / "start" / "index.html").write_text(
        page(
            title="🚨🐾 Start Wildlife 911 Virginia",
            description="Step through the Wildlife911 Virginia dispatcher: identify your species, get triage criteria, find a licensed rehabilitator.",
            canonical="/wildlife911/start/",
            body=render_dispatcher(yaml_data),
        ),
        encoding="utf-8",
    )

    # /wildlife911/species/<slug>/index.html — one per species
    (OUT_ROOT / "species").mkdir(parents=True)
    species_count = 0
    for yaml_key, sp_slug in YAML_KEY_TO_SLUG.items():
        sp_dir = OUT_ROOT / "species" / sp_slug
        sp_dir.mkdir(parents=True, exist_ok=True)
        label = SPECIES_LABEL.get(sp_slug, sp_slug)
        sp_page = page(
            title=f"Wildlife911 Virginia — {label}",
            description=f"What to do if you find a {label.lower()} in Virginia. Triage criteria, decision flow charts, full clinical reference, and licensed rehabilitator directory.",
            canonical=f"/wildlife911/species/{sp_slug}/",
            body=render_species_page(sp_slug, yaml_data, extracted_data),
        )
        (sp_dir / "index.html").write_text(sp_page, encoding="utf-8")
        species_count += 1

    # Unknown species page
    unknown_dir = OUT_ROOT / "species" / "unknown"
    unknown_dir.mkdir(parents=True, exist_ok=True)
    unknown_body = """
  <main>
    <div class="container prose">
      <p class="kicker"><a href="/wildlife911/" class="w911-link-soft">Wildlife911 Virginia</a> · Species unknown</p>
      <h1 class="w911-h1">Not sure what species you found?</h1>
      <p class="w911-lead">That's fine. The licensed rehabilitator you call will help identify the animal from your description. Use the universal steps below.</p>
""" + safety_box() + chatbot_shell() + universal_calls() + """
      <p class="w911-back"><a href="/wildlife911/start/" class="w911-link">← Back to dispatcher</a></p>
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

    # State directory + Virginia state page
    (OUT_ROOT / "state").mkdir(parents=True)
    (OUT_ROOT / "state" / "index.html").write_text(
        page(
            title="Wildlife911 — State directory",
            description="Wildlife911 is currently Virginia-complete. National fallback via Animal Help Now and state wildlife agencies.",
            canonical="/wildlife911/state/",
            body=render_state_landing(),
        ),
        encoding="utf-8",
    )

    (OUT_ROOT / "state" / "VA").mkdir(parents=True)
    (OUT_ROOT / "state" / "VA" / "index.html").write_text(
        page(
            title="Wildlife911 Virginia",
            description="Wildlife911 Virginia state edition — full triage and referral guide.",
            canonical="/wildlife911/state/VA/",
            body=render_state_va(),
        ),
        encoding="utf-8",
    )

    # Count
    pages = list(OUT_ROOT.rglob("index.html"))
    print(f"\nRendered {len(pages)} Wildlife911 pages:")
    for p in sorted(pages):
        print(f"  /{p.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
