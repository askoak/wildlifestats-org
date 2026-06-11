# Critique #4 — Product, UX, Demo Readiness
## WildlifeStats (wildlifestats.netlify.app) — Adversarial Product Review
**Reviewer:** Senior Product Strategist / UX Research perspective  
**Date:** 2026-06-11  
**Site reviewed:** https://wildlifestats.netlify.app  
**Docs reviewed:** Master plan, LANE handoff, Secure tier spec, WREN spec, Wildlife911 amendment

---

## Executive summary before the details

The current build is a respectable structural skeleton with genuine design restraint. The typography (serif heading / sans-serif nav), the cream background, the muted clay accent color — these signal institutional seriousness. The synthetic-data disclaimers are better than most academic demo sites manage. The methodology page is actually excellent prose.

But "demo-ready for institutional buyers" is a different standard than "structurally sound." By that standard, the site has five critical failures right now and several more that will ambush you in a Pew meeting if unaddressed. The critique below names each one without softening.

---

## 1. The "PhD researcher to 80-year-old volunteer" promise

### What the site currently delivers

The homepage opens with: *"WildlifeStats is a national research framework for wildlife rehabilitation data."* That sentence is pitched to the researcher half of the audience. The 80-year-old volunteer who just found a stunned bird outside a window has no idea why she's on this page, and the navigation — **One Health · National Parks · Wildlife · Data · Methodology · About** — offers her no obvious entry point for her actual problem.

Walk through each surface:

**Homepage — PhD: 7/10, Grandma: 2/10.**  
The copy is earnest and clear about what the site *is not* ("not a triage-replacement for any specific rehab center"). But the positive case for what a non-researcher does here is never made. There is no "find help for an injured animal" entry point anywhere on the current live site. The Wildlife911 pill — the single feature most relevant to the volunteer audience — is not yet deployed. A volunteer landing here has nowhere to go.

**One Health — PhD: 6/10, Grandma: 4/10.**  
The prose is accurate. Linking to USDA APHIS, CDC Leptospirosis, CDC Rabies, and USGS NWHC is the right citation discipline. But the page ends abruptly. There are no data visualizations connected to the narrative, no "what does this look like in the dataset" moment. It is disease-ecology background text with four hyperlinks. A researcher would call this a stub; a volunteer would absorb it as background reading and wonder what to do next.

**National Parks — PhD: 6/10, Grandma: 5/10.**  
This is the most navigable interactive surface on the site. The park search list works; you can click Acadia or Arches and get data. The search-by-name interaction is reasonable for any audience. **However**: the disclaimer "county centroids within roughly fifty miles" appears only in the Methodology page's "Known limitations" section — not on the parks page itself. A researcher who screenshots a park profile and cites it without reading methodology is getting illustrative synthetic data without that label front-and-center.

**Wildlife — PhD: 5/10, Grandma: 3/10.**  
Landing here shows: "Choose a class, then a species archetype." No further instruction, no example, and a "Loading the dataset…" message that just hangs if JavaScript doesn't resolve the cube before the screenshot is taken. "Species archetype" is unexplained jargon on this page. A volunteer who found a bird and clicked "Wildlife" hoping for identification or help is stranded. A researcher using this as a species-distribution lookup will find the archetype-level granularity (raptors, not Red-tailed Hawk) too coarse for most work.

**Data (/data) — PhD: 7/10, Grandma: 1/10.**  
The disclaimer block is solid: "Synthetic dataset, n=1,000,000 records distributed across all 50 states and the District of Columbia. Generated from regional distribution models calibrated against published wildlife rehabilitation literature. See Methodology." And the footer caption: "Dataset version 1.1.0. Synthetic wildlife rehabilitation admission records, n=1,000,000. Not derived from any real center's data." This is honest and visible.

But the cube filter UI is a research instrument, not a general-audience tool. The filter categories — year, month, county, species, class, admission reason, outcome, disposition — have no labels, no tooltips, no default state explanations for someone who doesn't already know what "admission reason" or "disposition" means in the rehab context. "Grandma-usable" requires explanatory labels. "Researcher-credible" requires at minimum a data dictionary linked from the filter pane. Neither exists. The summary/map/CSV that updates on filter change is conceptually correct but completely invisible until the cube loads (which, in the screenshot, it hasn't — just "Loading the dataset…"). For a demo, a cube that loads slowly or incompletely is a demo-killer.

**Methodology — PhD: 9/10, Grandma: 4/10.**  
This is the best page on the site. The generation algorithm walk-through (state allocation → county allocation → region/species → time → reason/outcome/disposition) is clear, reproducible, and honest about limitations. The calibration-sources section names PLOS ONE, Journal of Wildlife Rehabilitation, USGS NWHC appropriately. The `seed=42` reproducibility commitment is exactly what a researcher needs.

Why does it score 4/10 for grandma? Because she will never click this page. The Methodology link is in the nav, not in the paths grandma follows. And even if she lands here, the generation algorithm is five paragraphs of technical prose before the "Known limitations" section tells her "this data cannot reveal anything that was not built into the model."

**Governance — PhD: 8/10, Grandma: 6/10.**  
The four-tier framework (Public → Partner → Research → Surveillance) is clearly explained. The k-suppression policy is present. The "why synthetic" rationale — "using synthetic data for the public tier is a privacy decision, not a shortcut" — is excellent framing for an institutional audience. A Pew program officer will appreciate this page. The citation guidance is appropriate for academic use.

**About — PhD: 3/10, Grandma: 3/10.**  
Exactly two sentences: "WildlifeStats is an independent research framework. It is not affiliated with any specific wildlife rehabilitation center, government agency, or academic institution." This is the thinnest page on the site and a wasted opportunity. Who built this? Why does it exist? What is the theory of change? What problem does it solve that USGS NWHC or WHISPers does not? A buyer who lands here looking for institutional credibility finds nothing.

### Progressive disclosure — aspiration, not implementation

The WREN spec calls for a beautiful three-tier model: **plain answer → show the data → how was this computed**. This is not implemented anywhere in the current live site. There is no WREN assistant. There is no expandable data affordance under any piece of content. The Methodology page links are the closest thing to "how was this computed," but they require navigation, not inline reveal.

The progressive disclosure architecture is the single most important UX promise in the entire plan. Until it ships, the PhD/grandma promise is entirely aspirational.

---

## 2. Voice consistency

The site plans for three voices. Right now only one is deployed, but it's worth flagging the collision course:

**Voice 1: National-research register (current).** The homepage and methodology pages strike this tone well. "The framework demonstrates a method, not a real-time surveillance network." "The generator and every input table are committed to the public repository so that the method is auditable, not asserted." This is Pew Research Center / Brookings prose. Appropriate.

**Voice 2: Wildlife911 hotline-operator (planned).** The Wildlife911 amendment spec describes this as "calm, factual, professional, reassuring, safety-first, never alarmist." The golden rules ("never provide feeding, watering, rearing, or medical treatment instructions") are necessarily directive. This is a different register — shorter sentences, imperative mood, explicit action steps.

**Voice 3: WREN's answer voice (planned).** The WREN spec calls for two-to-four sentence declarative plain-language answers, no jargon, no tables, citing the dataset by name. A conversational data assistant.

**The collision:** Currently there is no voice conflict because Voices 2 and 3 don't exist yet. But when they ship together — a researcher reading "The generator draws each of the 1,000,000 records through a fixed sequence of conditional steps" on the methodology page, then asking WREN a question and getting a two-sentence conversational reply, then stumbling into a Wildlife911 flow that says "Any bird caught by a cat must be referred immediately" — the tonal whiplash will be jarring.

**The bigger problem now:** The homepage does not clearly explain what WildlifeStats *is* versus what BRWC is versus what Wildlife911 is. If a Pew program officer has never heard of any of these:
- WildlifeStats: the research framework site they're on. OK, clear.
- BRWC / Blue Ridge Wildlife Center: never mentioned anywhere on the live site. ✓ (deliberate, per lane discipline)
- Wildlife911: mentioned in the WREN spec as "currently deployed as a CustomGPT on BRWC's homepage," but on the live WildlifeStats site there is **no mention of Wildlife911 anywhere**. It doesn't exist yet in the UX.

The omission of Wildlife911 from the current nav and homepage means the "volunteer audience NOW" promise cited in the task brief is simply unfulfilled on the live site. The institutional buyer seeing this demo today sees nothing for the volunteer use case.

---

## 3. Synthetic data honesty

This is the site's most serious reputation risk. The current implementation handles it partially well and partially dangerously.

**What's working:** Every occurrence of the data — homepage, /data, governance, methodology, footer — carries an explicit "synthetic" label. The /data page's disclaimer ("Not derived from any real center's data") is above the fold. The methodology page's first sentence, in bold, says "synthetic." The footer sitewide says "Current dataset is synthetic (n=1,000,000) generated from regional distribution models."

**What's not working:** Once a user has filtered the cube to a specific combination — say, Virginia, 2024, bird, window strike — they get a number. A count. That count has all the visual authority of a real figure: a map choropleth, a table row, a downloadable CSV. The filter interaction produces output that *feels* like research data. There is no persistent inline badge on the output saying SYNTHETIC. The disclaimer text is above the filter UI; once a user scrolls into the results, the reminder is out of view.

**The tweet scenario:** A researcher at a state wildlife agency filters to "Loudoun County, VA, 2024, window strikes: n=14." Screenshots the table. Pastes it into a slide for a board meeting. Tweets it. The screenshot shows a clean data table with no synthetic label in the frame. When a wildlife professional with real Loudoun County data calls this out ("we took in 3 window-strike birds last year, not 14"), the damage is to WildlifeStats' credibility as a research framework — exactly the audience it most needs to convince.

**Mitigation required:** Every rendered cell in the cube output, every chart, and every CSV row must carry an inline "Synthetic" watermark or label — not just in the header prose, but in the data output itself. The CSV download header should contain `# SYNTHETIC DATASET: not derived from real centers` as row 1. The choropleth map should have a map title that says "Synthetic data — WildlifeStats Framework v1.1.0." This is not done.

---

## 4. Demo flow

### The 30-minute Pew program officer walkthrough

You have 30 minutes. Here is the realistic demo script using the current live site:

1. **Minutes 0–3: Homepage.** Open wildlifestats.netlify.app. Read the homepage copy together. Point to the key disclaimers ("The framework demonstrates a method, not a real-time surveillance network"). This establishes honesty upfront. The buyer will appreciate the explicit "what this isn't" list. *Risk: the homepage is text-heavy and has no visual lead — no hero map, no data chart, no mission image. It looks like the intro section of a report, not the front page of a tool. You're already managing first-impression deficit.*

2. **Minutes 3–7: Methodology.** Navigate to Methodology. Walk through the generation algorithm and calibration sources. Emphasize: "The generator is committed to the public repo. Any figure we show can be reproduced byte-for-byte by any reviewer." Name-drop PLOS ONE and USGS NWHC as calibration anchors. *This is the strongest page on the site and the best place to establish researcher credibility early.*

3. **Minutes 7–12: Governance.** Navigate to Governance. Show the four-tier framework. Emphasize the partner tier ("a contributing center retains ownership of its records") — this is the pitch for why real rehabilitation centers would participate. The k-suppression policy is your privacy due-diligence moment. The CC-BY 4.0 license is your open-data commitment. *Risk: the governance page has no examples of what a partner relationship looks like, no sample data-sharing agreement outline, no named advisory board. It's a policy document with no institutional faces. A program officer asking "who has already signed on?" will get silence.*

4. **Minutes 12–18: Data.** Navigate to /data. Let the cube load. Filter to a topic relevant to the buyer's portfolio — if Pew has an environmental health grant focus, filter to One Health admission reasons (disease categories). Show the choropleth. Demonstrate the CSV download. *Risk: this is the highest-probability demo-killer (see below). If the cube loads slowly, or if the choropleth renders blank, or if the filters behave unexpectedly, you lose the technical credibility the first 12 minutes built. Have a pre-loaded screenshot as backup.*

5. **Minutes 18–22: National Parks lens.** Navigate to /parks/. Search "Shenandoah." Show the species breakdown. This is a legible, relatable moment — Shenandoah is recognizable, the park-specific view is concrete. *This is currently the most functional interactive surface on the site and the safest demo moment.*

6. **Minutes 22–26: One Health.** Navigate to /one-health/. Connect the HPAI narrative to current news (H5N1 dairy cattle spillover). Reference the USDA APHIS and USGS NWHC links. Position WildlifeStats as a surveillance-ready framework that will surface these signals early through Flyway. *Risk: there is no data visualization connected to this narrative. You're telling the buyer to imagine the charts that don't exist.*

7. **Minutes 26–30: Roadmap pitch.** Return to the homepage. Describe the partner tier, the secure research access tier, and WREN. Show the Flyway methodology page briefly. End with the vision: "When any wildlife center contributes their records, they get national comparative context in this same interface, under their own secure login, with WREN answering their questions." *Risk: this is a future-state pitch with nothing live. You're asking the buyer to fund an aspiration, which is legitimate for a foundation pitch but requires you to have a compelling "why us, why now" that the current About page completely fails to provide.*

### The single most-likely demo-killer

**The /data cube not loading or rendering incompletely during the live demo.** The screenshot taken during this review shows "Loading the dataset…" still displayed below the stats panel, with no filter controls visible. If JavaScript is slow, or if the cube JSON (which is the full 8MB payload) hasn't transferred before the demo participant is watching, the most important page on the site shows a spinner. That's the demo. Over.

Secondary demo-killer: the About page. If the program officer opens it mid-meeting expecting institutional backstory — founding team, advisory board, fiscal sponsor, publication history, theory of change — they find two sentences of negative-space definition. This is not a technical failure but a credibility crater.

### Dead clicks on the current live site

- `/secure/` — blocked by robots.txt, returns disallow error; in a live browser it would redirect or require auth that doesn't exist yet
- `/wildlife/` — shows "Loading the dataset…" and may stall if the JS cube query doesn't resolve (the screenshot confirms this)
- `/wildlife911/` — does not exist (planned for Phase 7g)
- `/wren/` — does not exist (planned for Phase 7)
- Governance's "partner onboarding" CTA — the page says "Centers interested in the partner model can follow the project as the partner tier is built out." There is no signup form, no email address, no link. Partner interest evaporates.

---

## 5. Secure tier presentation

The secure tier is genuinely well-architected in the spec. Three tiers, ORCID integration, DOI-stamped downloads, k=5 vs k=10 suppression levels, Netlify Identity — this is serious national-research infrastructure thinking. The problem is that none of it exists in the live UX today, and `/secure/` returns a disallow from robots.txt or a redirect rather than even a "coming soon" landing page that could be demo-shown.

**In a demo, here's the credible preview:** Navigate to the Governance page. The four-tier framework table is there. Read it aloud. Then say: "The secure tier ships in phases — 5a is Netlify Identity with member and researcher roles; 5b adds deeper aggregate views; 5d unlocks anonymized individual records for credentialed researchers. The spec is fully written. We're showing you the architecture today and inviting you to be an early research-tier member." Then show the governance page's "Why the dataset is synthetic" section — this directly explains the privacy logic that makes real partner data safe to contribute.

**What's missing for this to work:** A "Request early research access" button or email on the Governance page. The buyer needs a next step. Right now there is no next step.

**Wildlife911 visibility:** The Wildlife911 pill is the site's most practically useful feature for the volunteer audience, and it is completely absent from the live UX. There is no `/wildlife911/` page. The nav has no Wildlife entry point that leads to triage guidance. The volunteer user — arguably the most emotionally compelling part of the pitch ("from a PhD biostats researcher to an 80-year-old volunteer at a wildlife hospital") — has nothing on the current site. In a demo to a foundation interested in public-benefit science communication, this is a gap. The Wildlife911 spec is ready; the deployment is blocked on Phase 7g. For demo purposes, even a static `/wildlife911/` landing page that says "Wildlife911 is coming — here's what it will do" with a screenshot of the Virginia guidance structure would be stronger than silence.

---

## 6. Comparison to credible sites

### WHISPers (whispers.usgs.gov)

WHISPers is a U.S. federal government system for wildlife mortality and morbidity event reporting. Its UI is filter-heavy, somewhat dated, and clearly government-portal in visual register. On the day of this review it returned a "Query failed due to web service error" error on the homepage — an instructive reminder that even federal surveillance systems have reliability problems.

**Where WildlifeStats is stronger:**
- Typography and visual design. WildlifeStats' cream-and-slate palette, Playfair-style serif headings, and clean whitespace are markedly more polished than WHISPers' dense, utilitarian Angular UI.
- Synthetic-data honesty. WHISPers serves real surveillance data with minimal caveating on-screen; WildlifeStats is exhaustive about what it is and isn't.
- Methodology transparency. WildlifeStats publishes a public seed and reproducibility command. WHISPers publishes metadata but not algorithm source.

**Where WildlifeStats is weaker:**
- Real data. WHISPers has actual events, actual species, actual mortality counts. WildlifeStats has a model. In a side-by-side, no program officer confuses the two.
- Query depth. WHISPers supports complex multi-filter searches including event type, species order/genus, diagnosis, and date range. WildlifeStats' cube is less dimensionally rich at the species level (archetype not species).
- Institutional imprimatur. USGS is a federal agency. WildlifeStats is explicitly unaffiliated with any institution. That independence is also a liability.

### eBird (Cornell Lab of Ornithology)

eBird is the gold-standard citizen-science data platform. It handles the researcher-to-casual-birder range successfully because it has two distinct modes: the science/data portal and the consumer birding app. They share data but not interfaces.

**Where WildlifeStats is stronger:**
- The synthetic data transparency is actually better than eBird's default experience, where observation quality variability is real but largely invisible to casual users.

**Where WildlifeStats is weaker:**
- eBird has 100M+ real observations, a community of half a million users, and 20 years of demonstrated scientific output. WildlifeStats has 1M synthetic records and zero published research built on it yet.
- eBird's "Explore" section has choropleth maps, species distribution maps, bar charts, abundance graphs — a visual feast. WildlifeStats' visualization layer is a single choropleth that may not load during your demo.
- eBird has clear institutional branding (Cornell Lab), faculty names, peer-reviewed papers. WildlifeStats' About page has two sentences.

### Animal Help Now

Animal Help Now is a field-use mobile app — the "wildlife 911" for people who find injured animals. Its design is functional and mobile-first, oriented entirely around one action: "I found an injured animal, who do I call."

**Where WildlifeStats is stronger:**
- Research depth. AHN is a directory, not a data framework.
- National rehabilitation data context.

**Where WildlifeStats is weaker:**
- AHN does the one thing the volunteer actually needs right now: phone numbers for nearby rehabbers. WildlifeStats currently does none of this.
- AHN has a working mobile app on iOS and Android. WildlifeStats is a desktop-first static site.

### Visual design verdict

WildlifeStats is **not** a Notion-template site. The typography is distinctive, the color palette is intentional and subdued, the layout is clean. It reads as "thoughtful independent research organization," which is exactly the right register. 

The critical problem is that it reads as *empty thoughtful independent research organization*. The pages that exist look good. Most of the sections a buyer wants to see either show a loading spinner (Wildlife), a single paragraph of prose without data visualization (One Health), or two sentences (About). Design credibility is undermined by content vacancy.

---

## 7. Mobile experience

The site was not tested at a true 375px viewport in this review (screenshot tooling uses desktop resolution), but the content structure gives strong signals:

**What will work on mobile:** The text-heavy pages (Methodology, Governance, About, One Health) will render readably on mobile — they are HTML text with minimal layout complexity.

**What will break on mobile:**
- The nav bar. Six horizontal links (One Health, National Parks, Wildlife, Data, Methodology, About) at desktop will collapse. If the hamburger menu is not implemented, these links overflow or stack badly. This was not tested live but is a known failure mode for this nav structure.
- The /data cube. An 8MB JSON payload filtered in-browser with a choropleth map is a performance disaster on a mobile data connection. The map may not render at an acceptable size or speed.
- The /parks/ search-and-list. This is the best candidate for mobile usability — a text search and a scrollable list. Likely acceptable.

**For the volunteer use case**, mobile is where they'll be: outside, in their yard, with a bird in a box. The volunteer audience arrives on mobile, and the current site delivers them nothing useful on any viewport.

---

## 8. Accessibility

From visual inspection and content review:

**Positive signals:**
- The WREN spec explicitly calls for WCAG 2.1 AA compliance in Phase 7e ("accessibility audit").
- The spec mentions `aria-expanded` states for progressive-disclosure affordances.
- Text-based content pages (Methodology, Governance) will have reasonable heading hierarchy if the HTML is well-structured.

**Concerns:**
- The `/data` page loads its filter controls and choropleth via JavaScript. If these elements are not implemented with ARIA labels and keyboard navigation, the primary interactive surface is inaccessible to screen reader users.
- Color choices: the muted clay accent (`#B96F4D` per the lane handoff) on cream background must be tested for WCAG AA contrast (4.5:1 for normal text). Muted warm tones against cream are a common contrast failure.
- The parks list and wildlife class selector — both interactive — are JavaScript-rendered. Tab order and focus management for these components have not been verified.
- No `skip to main content` link is visible in the screenshot nav, though it may be implemented off-screen.
- The footer attribution text ("WildlifeStats is a research framework. Current dataset is synthetic (n=1,000,000) generated from regional distribution models. See Methodology.") is in a smaller typeface — likely fails 4.5:1 contrast at that size.

The accessibility picture is "no gross failures yet, but the interactive surfaces haven't been tested." For an 80-year-old volunteer, accessibility is not an edge case.

---

## 9. Conversion / call-to-action

This is the section that most clearly reveals the gap between institutional-research ambition and functional demo-readiness.

**Current CTAs on the live site: zero.**

There is no:
- "Request research access" button
- "Partner with us" contact form or email address
- "Sign up for updates" subscription
- "Cite this work" one-click citation copy
- "Download the dataset" prominent action
- "Get help with an injured animal" entry point

The Governance page says "Centers interested in the partner model can follow the project as the partner tier is built out." That is not a CTA. That is a deferral.

The About page says "The current public site is in active development; section pages note their build status individually." That is a disclaimer, not a value proposition.

**The institutional-restraint vs. institutional-paralysis question:** Brookings and Pew do not plaster "Donate" buttons over their research pages — true. But they do have clear mission statements, editorial leadership biographies, institutional email addresses, and annual reports. They have found-ability: there is a person or organization responsible for the work, and you can contact them. WildlifeStats has none of this.

**What a convinced Pew program officer does after the meeting:** They open the site to find the contact information for the project lead. They look at About. They find two sentences. They look at the footer. They find a copyright year and two links (Governance, About). There is no email address, no name, no organization, no way to initiate a formal partnership inquiry. The conversion fails at the moment of highest intent.

**Minimum viable CTA for demo readiness:** A single "Contact the WildlifeStats project" email link, surfaced on the About and Governance pages. Everything else can wait.

---

## The synthesis problem no individual section names

Reading across all nine sections, a single structural problem explains most of the weaknesses: **WildlifeStats is currently built for the reader who already understands what it is.** Every page assumes the visitor arrived with context — that they know what a "national wildlife rehabilitation research framework" is, that they understand the distinction between a methodology demonstration and a surveillance system, that they know what admission reason and disposition mean in a rehabilitation intake context.

The doctoral researcher who has read three rehabilitation epidemiology papers before landing here will feel at home. The program officer who followed a link in an email will need to spend 10 minutes reading before they understand what they're looking at. The volunteer who found a bird will leave within 30 seconds.

This is a fixable framing problem, not a fundamental architecture problem. The building blocks are good. The institutional voice is right. The methodology is honest. The issue is the absence of a guided path for anyone who isn't already persuaded.

---

## Top 7 Hardening Priorities (ranked by impact per effort)

**1. Synthetic data watermark on all output cells (impact: critical / effort: low)**  
Every rendered data value in the cube — every table cell, every choropleth color, every chart axis value — must carry an inline "Synthetic" label or badge. The current approach of disclaiming in the header prose is insufficient once a user screenshots results. Add a persistent "SYNTHETIC DATA" banner above the filter results area and embed a `# SYNTHETIC — WildlifeStats v1.1.0` comment as the first row of every CSV download. This is a one-engineer-day fix that prevents the most dangerous reputational failure mode.

**2. Cube load performance and failure state (impact: critical / effort: medium)**  
The 8MB cube JSON loading in-browser produces a "Loading the dataset…" state that has no timeout, no progress indicator, and no failure message. For a live demo, this is unacceptable. Implement: a loading progress bar, a timeout with fallback message ("Dataset unavailable — try refreshing"), and a pre-rendered static table showing the top-10 state totals as a default view that renders before the full cube loads. The demo must never show a blank data page.

**3. About page rewrite with contact path (impact: high / effort: low)**  
Replace the current two-sentence About page with: project mission (2-3 sentences), theory of change (1 paragraph), who is responsible (name or organization), and a contact email. This is the single most-requested page in any institutional due-diligence process. Estimated effort: 2 hours of writing, 30 minutes of engineering. The missing contact path is the conversion-killer after a successful demo.

**4. Wildlife911 static landing page at /wildlife911/ (impact: high / effort: low)**  
The Wildlife911 pill is not yet deployed, but a static landing page that explains what it will do, shows the Virginia guidance structure, and links to Animal Help Now as the current interim resource costs one engineering day. This fulfills the "volunteer audience NOW" promise in the demo pitch and makes the PhD-to-grandma range credible to a buyer rather than theoretical.

**5. Partner onboarding CTA on Governance page (impact: high / effort: low)**  
The Governance page's partner section ends with a deferral ("follow the project as the partner tier is built out"). Add a single sentence with a specific action: "To express interest in the partner tier, contact [email]." This turns the Governance page from a policy document into a live pipeline for the relationships the entire business model depends on.

**6. One Health page data visualization connection (impact: medium / effort: medium)**  
The One Health page is prose with four external links. At minimum, add one embedded data chart — seasonal admission counts for disease-related admission reasons (HPAI-relevant waterfowl intake by month, or West Nile corvid/raptor admissions by year) — to connect the narrative to the actual synthetic dataset. This makes the One Health page a data demonstration rather than a reading list, and gives the demo a visual moment in this section.

**7. Mobile nav and responsive filter UI audit (impact: medium / effort: medium)**  
Test the six-item nav at 375px and implement a hamburger menu if it doesn't exist. Test the /data filter UI at 375px — if it's unusable on mobile, add a "For the best experience, use a desktop browser" notice rather than leaving the mobile user staring at a broken layout. The volunteer audience uses mobile. If Wildlife911 ships as a static page (priority #4), it must be fully mobile-usable. An accessibility audit of color contrast at key text sizes (body, footer, accent links) should accompany this work.

---

*Prepared for Mike (WildlifeStats principal). Direct and adversarial per brief. All observations derived from the live site at wildlifestats.netlify.app, screenshots taken 2026-06-11, and full review of all spec documents cited in the task brief.*
