# Outdoor cats — ecological impact and anti-TNR framing data sources

**Scope:** *Felis catus* as invasive species and predator; TNR ineffectiveness at population scale; disease spillover to wildlife and humans; wildlife mortality quantification; wildlife rehabilitation intake burden. Native wildcats (bobcat, lynx, cougar, ocelot, jaguarundi, margay, jaguar) are explicitly out of scope.

**Purpose:** Literature-review mapping of the ecological-impact evidence base, with honest methodology notes, for balanced ingestion by WildlifeStats. This is not advocacy; it documents one side of a contested scientific and policy debate.

**Companion file:** `08-cats-TNR-humane.md` (companion agent covering TNR-efficacy and community-cat framing).

---

## Tier 1: Peer-reviewed primary research

### 1.1 Loss, Will & Marra (2013) — *Nature Communications*

- **Full citation:** Loss SR, Will T, Marra PP. "The impact of free-ranging domestic cats on wildlife of the United States." *Nature Communications* 4:1396 (2013). DOI: [10.1038/ncomms2380](https://doi.org/10.1038/ncomms2380)
- **PubMed:** [PMID 23360987](https://pubmed.ncbi.nlm.nih.gov/23360987/)
- **ABC-hosted PDF (open access):** [abcbirds.org/wp-content/uploads/2015/09/Loss_et_al._2013-Impacts_Outdoor_Cats.pdf](https://abcbirds.org/wp-content/uploads/2015/09/Loss_et_al._2013-Impacts_Outdoor_Cats.pdf)
- **Scope:** Systematic review and quantitative estimate of annual bird and mammal mortality caused by free-ranging domestic cats in the contiguous United States. Distinguishes owned cats from unowned (feral/stray/colony) cats.
- **Access:** Open access via Nature Publishing Group; PDF also hosted by ABC.
- **License:** CC-BY at time of publication; supplementary data available in paper.
- **Data format:** Synthesized meta-analysis with Monte Carlo uncertainty intervals; no raw primary dataset released separately.
- **Update cadence:** Single publication; no update series. Superseded in some estimates by Loss & Marra 2015 review.
- **Key claims supported:**
  - Free-ranging cats kill **1.3–4.0 billion birds** (median 2.4 billion) and **6.3–22.3 billion mammals** (median 12.3 billion) annually in the contiguous US.
  - Unowned cats cause **~69% of bird mortality** and **~89% of mammal mortality**; owned pet cats are a secondary source.
  - Cats are "likely the single greatest source of anthropogenic mortality for US birds and mammals."
  - Free-ranging cats on islands have contributed to or caused **33 (14%) of recorded modern bird, mammal, and reptile extinctions** globally (citing IUCN Red List).
- **Methodology quality:** Peer-reviewed in a high-impact journal. Systematic review of published predation-rate studies; Monte Carlo simulation to propagate uncertainty. Geographic scope: contiguous US. Key limitation acknowledged by authors: primary predation-rate data are mostly from owned cats and small-scale studies; unowned cat density estimates carry high uncertainty. Widely cited; this is the foundational US mortality paper.
- **Known critiques:** Significant pushback on the upper-bound estimates and extrapolation from owned-cat studies to unowned populations (Blancher 2013; Marra & Santella response). A 2022 *Frontiers in Veterinary Science* review (Tschanz et al.) argued the study "overrates" mortality by assuming killed prey = total mortality impact. The Monte Carlo intervals are very wide (an order of magnitude), reflecting genuine data scarcity for unowned cat densities. Nonetheless, even the lower bounds place cat predation among the top anthropogenic threats.
- **Integration friction:** No raw dataset; WildlifeStats would cite this as a key literature anchor rather than ingest primary data from it.

---

### 1.2 Doherty, Glen, Nimmo, Ritchie & Dickman (2016) — *PNAS*

- **Full citation:** Doherty TS, Glen AS, Nimmo DG, Ritchie EG, Dickman CR. "Invasive predators and global biodiversity loss." *PNAS* 113(40):11261–11265 (2016). DOI: [10.1073/pnas.1602480113](https://doi.org/10.1073/pnas.1602480113)
- **PubMed:** [PMID 27638204](https://pubmed.ncbi.nlm.nih.gov/27638204/)
- **Open PDF:** [pnas.org/doi/pdf/10.1073/pnas.1602480113](https://www.pnas.org/doi/pdf/10.1073/pnas.1602480113)
- **Scope:** Global metaanalysis of invasive mammalian predators and their contribution to species extinctions and endangerment. Cats are one of 30 invasive predator species analyzed.
- **Access:** Open access; supplementary dataset (Dataset S1) lists all 738 impacted species, available at PNAS.
- **License:** PNAS open access license; supplementary data publicly downloadable.
- **Data format:** Species-level dataset (Dataset S1, Excel/CSV), aggregated from IUCN Red List and primary literature. Published 2016; not updated as a living dataset.
- **Key claims supported:**
  - Invasive mammalian predators are implicated in the extinction of 87 bird, 45 mammal, and 10 reptile species — **58% of all modern bird, mammal, and reptile extinctions** globally.
  - Cats are linked to **63 extinctions** (40 bird, 21 mammal, 2 reptile species) — **26% of all such extinctions**.
  - Cats and rodents together account for **44% of all modern bird/mammal/reptile extinctions**.
  - Cats threaten **430 species** currently listed as vulnerable, endangered, or critically endangered.
  - Feral cats and red foxes have driven the decline or extinction of **two-thirds of Australia's digging mammal species** over 200 years.
- **Methodology quality:** Peer-reviewed at high-impact journal. Global scope; systematic literature review combined with IUCN Red List data. Limitation: attribution of extinctions to a single predator species is inherently uncertain and likely underestimates multi-cause extinctions. Causal attribution relies on historical records of varying quality.
- **Known critiques:** Some ecologists (see Wallach et al. 2019, *Conservation Biology*) dispute attributing extinction causation to cats where multiple stressors co-occurred. The paper itself notes that 23 "possibly extinct" critically endangered species were excluded, meaning the 58% figure is likely an underestimate in one direction. No critique disputes the core finding that cats are among the most damaging invasive predators globally.
- **Integration friction:** Dataset S1 is directly machine-readable and could be ingested as a species-level extinction-attribution table.

---

### 1.3 Medina, Bonnaud, Vidal et al. (2011) — *Global Change Biology*

- **Full citation:** Medina FM, Bonnaud E, Vidal E, Tershy BR, Zavaleta ES, Donlan CJ, Keitt BS, Le Corre M, Horwath SV, Nogales M. "A global review of the impacts of invasive cats on island endangered vertebrates." *Global Change Biology* 17(11):3503–3510 (2011). DOI: [10.1111/j.1365-2486.2011.02464.x](https://doi.org/10.1111/j.1365-2486.2011.02464.x)
- **Wiley Online Library:** [onlinelibrary.wiley.com/doi/abs/10.1111/j.1365-2486.2011.02464.x](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1365-2486.2011.02464.x)
- **Scope:** Systematic global review of cat impacts on island-endemic vertebrates. Islands are the primary locus of cat-caused extinction globally.
- **Access:** Subscription access via Wiley; abstract freely available. Author manuscript available at institutional repositories.
- **License:** Standard copyright; no open license.
- **Data format:** Literature synthesis; species-level tables of cat-impacted island species.
- **Key claims supported:**
  - Documents cat impacts across hundreds of islands globally, particularly Pacific island endemic birds, lizards, and mammals.
  - Established the 14% figure for cat contribution to modern island extinctions, later cited in Loss et al. 2013 and Doherty et al. 2016.
  - Hawaii, New Zealand, and sub-Antarctic island endemic species are central case studies.
- **Methodology quality:** Peer-reviewed; broad geographic scope (global islands); systematic literature review. Strong foundation for island extinction attribution. Less applicable to mainland continental populations.
- **Known critiques:** Focus on islands means findings do not directly translate to mainland US/continental contexts, though they strongly support the "invasive species" framing.
- **Integration friction:** Paywall; WildlifeStats would need institutional access or rely on the publicly available abstract and cited data in open papers.

---

### 1.4 Longcore, Rich & Sullivan (2009) — *Conservation Biology*

- **Full citation:** Longcore T, Rich C, Sullivan LM. "Critical assessment of claims regarding management of feral cats by trap-neuter-return." *Conservation Biology* 23(4):887–894 (2009). DOI: [10.1111/j.1523-1739.2009.01174.x](https://doi.org/10.1111/j.1523-1739.2009.01174.x)
- **PubMed:** [PMID 19245489](https://pubmed.ncbi.nlm.nih.gov/19245489/)
- **ABC-hosted PDF:** [abcbirds.org/wp-content/uploads/2016/01/Longcore-et-al.-2009-Critical-assessment-of-TNR-claims.pdf](https://abcbirds.org/wp-content/uploads/2016/01/Longcore-et-al.-2009-Critical-assessment-of-TNR-claims.pdf)
- **Scope:** Systematic critical review of scientific claims made by TNR advocates; evaluates whether published evidence supports those claims.
- **Access:** Open PDF hosted by ABC; original paywalled at Wiley.
- **Key claims supported:**
  - For TNR to reduce a colony to zero requires sterilization of **>75% of the colony** sustained over time, a threshold that field programs consistently fail to achieve due to cat immigration/abandonment.
  - A countywide TNR program in San Diego (10-year study) showed **no consistent reduction** in feral cat populations.
  - A similar 7-year Alachua County, Florida study found **no consistent population decline**.
  - Colonies subject to TNR in Florida (Castillo & Clarke sites) **increased in size** owing to illegal dumping of unwanted cats.
  - TNR proponents' claim that colonies are "temporary and will decrease in size" is **contradicted by the scientific literature**.
  - TNR may violate the Migratory Bird Treaty Act and Endangered Species Act in some jurisdictions.
- **Methodology quality:** Peer-reviewed; literature review methodology; no primary field data collected. Strong as a synthesis of existing evidence against TNR efficacy. Acknowledged by opponents as the primary anti-TNR review paper; a detailed response was published at voxfelina.com but does not appear in peer-reviewed literature.
- **Known critiques:** Authors are affiliated with urban wildlands conservation advocacy; critics argue the paper selectively cites failure cases. A 2010 blog-based "critical assessment of Critical Assessment" challenges some citations but is not peer-reviewed.
- **Integration friction:** Available as open PDF; directly citable.

---

### 1.5 Castillo & Clarke (2003) — *Natural Areas Journal*

- **Full citation:** Castillo D, Clarke AL. "Trap/Neuter/Release methods ineffective in controlling domestic cat 'colonies' on public lands." *Natural Areas Journal* 23(3):247–253 (2003).
- **ABC-hosted PDF:** [abcbirds.org/wp-content/uploads/2015/05/Castillo-and-Clarke-2003-TNR-ineffective-in-controlling-cat-colonies1.pdf](https://abcbirds.org/wp-content/uploads/2015/05/Castillo-and-Clarke-2003-TNR-ineffective-in-controlling-cat-colonies1.pdf)
- **Scope:** Empirical field study of two TNR-managed cat colonies in Miami-Dade County parks (A.D. Barnes Park and Crandon Marina) over time, using photographic and observational capture-recapture.
- **Access:** Available via ABC PDF.
- **Key claims supported:**
  - Colony at A.D. Barnes Park **increased in size** over the study period despite TNR.
  - Colony at Crandon Marina **neither increased nor decreased**.
  - Illegal dumping of unwanted cats and attraction of strays to provisioned food **offset** reductions from death and adoption.
  - Establishes the **"dumping zone" phenomenon**: visible, provisioned cat colonies actively attract cat abandonment.
  - Well-fed TNR colony cats were observed **stalking and killing wildlife** including a Common Yellowthroat.
- **Methodology quality:** Peer-reviewed in a specialized conservation journal. Small sample (two colonies, one jurisdiction); photographic capture-recapture is a legitimate methodology. Limited geographic scope (subtropical urban parks, Florida). Cannot generalize to all geographies, but the dumping/immigration mechanism it documents has been replicated in other studies.
- **Known critiques:** Two-colony sample is small. Critics argue the Florida urban park context is not representative of all TNR settings.
- **Integration friction:** Available as open PDF.

---

### 1.6 Foley, Foley, Levy & Paik (2005) — *Journal of the American Veterinary Medical Association*

- **Full citation:** Foley P, Foley JE, Levy JK, Paik T. "Analysis of the impact of trap-neuter-return programs on populations of feral cats." *JAVMA* 227(11):1775–1781 (2005). DOI: [10.2460/javma.2005.227.1775](https://doi.org/10.2460/javma.2005.227.1775)
- **PubMed:** [PMID 16342526](https://pubmed.ncbi.nlm.nih.gov/16342526/)
- **Scope:** Population-level analysis of TNR outcomes using data from 14,452 cats in San Diego County (1992–2003) and 11,822 cats in Alachua County, Florida (1998–2004).
- **Access:** Available through AVMA institutional access; abstract open on PubMed.
- **Key claims supported:**
  - In **both counties**, analyses did not indicate a consistent reduction in per capita growth, the population multiplier, or the proportion of female cats that were pregnant.
  - The two largest countywide TNR datasets in the US at the time of publication failed to show population decline.
  - Provides the modeling basis for the >75% sterilization threshold cited in Longcore et al. 2009.
- **Methodology quality:** Peer-reviewed; large sample sizes (n = ~26,000 cats combined); longitudinal data. Strong empirical foundation for TNR inefficacy at population scale. Published in a veterinary journal — the evidence that even pro-management veterinary data shows no population decline carries particular weight.
- **Known critiques:** Critics note that Alachua County's program (run by Alley Cat Allies affiliate) was arguably not representative of intensive TNR; Foley et al. 2005 themselves note that intensive local programs may show different results than countywide surveillance.
- **Integration friction:** Paywall; abstract and key findings are publicly quoted extensively.

---

### 1.7 Conrad, Miller, Melli et al. (2005) — *International Journal for Parasitology*

- **Full citation:** Conrad PA, Miller MA, Kreuder C, et al. "Transmission of Toxoplasma: Clues from the study of sea otters as sentinels of Toxoplasma gondii flow into the marine environment." *International Journal for Parasitology* 35(11–12):1155–1168 (2005).
- **ABC-hosted PDF:** [abcbirds.org/wp-content/uploads/2015/07/Conrad-et-al.-2005-Transmission-of-Toxoplasma-clues-from-th-study-of-sea-otters.pdf](https://abcbirds.org/wp-content/uploads/2015/07/Conrad-et-al.-2005-Transmission-of-Toxoplasma-clues-from-th-study-of-sea-otters.pdf)
- **Scope:** Transmission pathways for *Toxoplasma gondii* from terrestrial cat feces into marine ecosystems via freshwater runoff; sea otters as sentinels.
- **Key claims supported:**
  - *T. gondii* sexually reproduces **only in the digestive tract of felids**; only cats shed environmentally resistant oocysts.
  - Oocysts are transported via freshwater runoff into marine environments.
  - Toxoplasmosis is a **major cause of mortality** in southern sea otters (*Enhydra lutris nereis*) and contributes to slow population recovery.
  - Type X *T. gondii* isolates found in Pacific harbor seals and California sea lions.
- **Methodology quality:** Peer-reviewed; multi-year surveillance data on sea otter necropsies. Foundational paper in establishing the cat → land → ocean spillover pathway. **Important caveat:** A 2015 PMC review (Lafferty, *IJPPW*) presents evidence that wild cats (mountain lions, bobcats) — not domestic/feral cats — may dominate *T. gondii* transmission in remote coastal areas of California, as sea otters near human-dense Monterey were *less* infected than wild Big Sur otters. This complicates simple attribution to feral domestic cats in non-urban coastal settings.
- **Integration friction:** Available as open PDF via ABC; original may require institutional access.

---

### 1.8 NOAA / Hawaii Sea Grant — Toxoplasmosis and Hawaiian monk seals

- **URL:** [fisheries.noaa.gov/pacific-islands/endangered-species-conservation/toxoplasmosis-and-its-effects-hawaii-marine](https://www.fisheries.noaa.gov/pacific-islands/endangered-species-conservation/toxoplasmosis-and-its-effects-hawaii-marine)
- **Scope:** NOAA Fisheries synthesis of *T. gondii* impacts on Hawaiian monk seals (*Neomonachus schauinslandi*), Hawaiian spinner dolphins, nēnē, and ʻalalā in Hawaiʻi.
- **Access:** Open; freely available as NOAA public education/science summary.
- **License:** US federal government; no copyright, public domain.
- **Key claims supported:**
  - **All monk seals diagnosed with toxoplasmosis have died**, even with treatment; no successful treatment or vaccine.
  - **15 confirmed monk seal deaths** due to toxoplasmosis in Hawaiʻi as of 2023.
  - Toxoplasmosis is the **third leading threat** to monk seals in the main Hawaiian Islands.
  - **Spinner dolphin** deaths from toxoplasmosis estimated at up to 60 over 30 years (5% carcass recovery rate assumption).
  - Toxoplasmosis is the **most common infectious disease** encountered by nēnē (Hawaiian goose) and causes ~4% of nēnē mortalities.
  - Only outdoor cats shed infective oocysts; indoor cats pose low risk.
  - Cats shed **3 to 800 million oocysts** in the weeks after initial infection; a single oocyst can cause infection.
- **Methodology quality:** NOAA government summary, not itself a primary study, but cites peer-reviewed surveillance data. The monk seal case counts are from NOAA marine mammal stranding records, which are systematic and well-documented.
- **Known critiques:** The "all deaths" figure for monk seals reflects a small absolute number; sample size is inherently limited by the endangered population size (~1,600 total animals). The direction of effect is clear; the magnitude question is irreducible.
- **Integration friction:** Freely available, government-authored, no licensing issues.

---

### 1.9 Roebling, Johnson, Blanton et al. (2014) — *Zoonoses and Public Health*

- **Full citation:** Roebling AD, Johnson D, Blanton JD, et al. "Rabies prevention and management of cats in the context of Trap-Neuter-Vaccinate-Release programmes." *Zoonoses and Public Health* 61(4):290–296 (2014). DOI: [10.1111/zph.12070](https://doi.org/10.1111/zph.12070)
- **PMC full text:** [pmc.ncbi.nlm.nih.gov/articles/PMC5120395/](https://pmc.ncbi.nlm.nih.gov/articles/PMC5120395/)
- **ABC-hosted PDF:** [abcbirds.org/wp-content/uploads/2015/06/Roebling-et-al.-2013-Rabies-prevention-and-management-of-cats-in-TNVR-programs.pdf](https://abcbirds.org/wp-content/uploads/2015/06/Roebling-et-al.-2013-Rabies-prevention-and-management-of-cats-in-TNVR-programs.pdf)
- **Scope:** Epidemiological analysis of rabies risk from feral cats and the limitations of TNR/TNVR programs as public health interventions.
- **Key claims supported:**
  - In 2010, **303 rabid cats** were reported in US national surveillance vs. only 69 rabid dogs — cats are the most frequently reported rabid domestic animal.
  - **More than 25,000 cats** are submitted for rabies diagnosis annually in the US.
  - An estimated **16% of post-exposure prophylaxis (PEP)** in the US is attributable to cat exposures; in some jurisdictions (Pennsylvania 67 counties: 44%; New York state: 32%; Montgomery County VA: 63%) cats dominate PEP burden.
  - Most cat-attributed PEP stems from **feral/stray/unowned cats** (82% of cat-attributed PEP cases in Pennsylvania study).
  - Feral cats are more likely to interact with rabies-reservoir wildlife and less likely to be vaccinated than owned pets.
  - TNR/TNVR programs face critical vaccination coverage shortfalls that leave herd immunity unachievable in open populations.
  - **Cats disproportionately expose more people to rabies than wildlife** because humans, especially children, are more likely to approach cats.
- **Methodology quality:** Peer-reviewed; synthesis of national surveillance data plus state-level epidemiological studies. Core finding on cat-attributed PEP is well-supported; the 16% national estimate is modeled (not directly measured) but consistent with multiple state studies. Widely cited in CDC, TWS, AZA, and NASPHV documents.
- **Known critiques:** No known methodological critiques of the PEP attribution analysis. Note: rabid cats are not reservoirs for rabies in the same sense as raccoons/bats; they are spillover hosts who amplify human exposure risk.
- **Integration friction:** Full text available via PMC; no access barriers.

---

### 1.10 CDC Rabies Surveillance Annual Reports

- **URL:** [cdc.gov/rabies/php/protecting-public-health/index.html](https://www.cdc.gov/rabies/php/protecting-public-health/index.html)
- **URL (2025 MMWR case report on urban colony outbreak):** [cdc.gov/mmwr/volumes/74/wr/mm7431a2.htm](https://www.cdc.gov/mmwr/volumes/74/wr/mm7431a2.htm)
- **Scope:** Annual surveillance of animal and human rabies cases in the US, including species-level breakdown. Published annually in *MMWR*.
- **Access:** Open; federal government public domain.
- **Data format:** Annual MMWR report; tabular data on rabies-positive animals by species. State health departments contribute data.
- **Update cadence:** Annual.
- **Key claims supported:**
  - Cats are the **most frequently reported rabid domestic animal** in the US, with approximately **200–300 cats reported rabid each year**.
  - In 2023 Maryland data, feral cats accounted for **10% of all reported rabid animals**.
  - Domestic animals overall account for <10% of animal rabies cases; within domestic animals, cats dominate.
- **Methodology quality:** Gold-standard federal surveillance. All reports go through state public health laboratories; CDC provides confirmatory testing. Limitation: does not track ownership status of rabid cats (noted explicitly in 2025 MMWR report).
- **Integration friction:** Direct API access via CDC data APIs for MMWR data is limited; structured tables are in PDFs/HTML. Programmatic access requires parsing MMWR publications.

---

### 1.11 McRuer, Clark & Pearce (2017) — *Journal of Wildlife Management*

- **Full citation:** McRuer DL, Clark EE, Pearce JM. "Free-ranging domestic cat predation on wildlife admitted to a wildlife hospital." *Journal of Wildlife Management* 81(1):188–196 (2017). DOI: [10.1002/jwmg.21181](https://doi.org/10.1002/jwmg.21181)
- **Wildlife Center of Virginia news release:** [wildlifecenter.org/news-events/news/2016/new-study-reveals-extensive-damage-wildlife-caused-domestic-cats](https://wildlifecenter.org/news-events/news/2016/new-study-reveals-extensive-damage-wildlife-caused-domestic-cats)
- **TWS summary:** [wildlife.org/jwm-study-domestic-cat-attacks-cause-variety-of-wildlife-deaths/](https://wildlife.org/jwm-study-domestic-cat-attacks-cause-variety-of-wildlife-deaths/)
- **Scope:** 11-year retrospective study of nearly 21,000 wildlife admission records (2000–2010) at the Wildlife Center of Virginia, analyzing cat-attack-caused admissions and mortality outcomes.
- **Access:** Paywall (Wiley); open summary via WCV and TWS.
- **Key claims supported:**
  - **84 species** (62 bird, 21 mammal, 1 reptile) admitted to WCV due to cat attacks over 11 years.
  - Cat attacks account for **~14% of all study-population admissions** — equivalent fractions among birds and small mammals.
  - **>70% of small mammals** and **~80–81% of birds** admitted after cat attacks die or require euthanasia — the highest case fatality rate of any cause of admission.
  - Most commonly attacked birds: American robin, mourning dove, blue jay, northern cardinal. Most commonly attacked mammals: eastern cottontail, eastern gray squirrel, chipmunk, southern flying squirrel.
  - Figures are explicitly **conservative**: cases with puncture wounds consistent with cat attack but no witness were excluded as "unknown trauma."
  - Study cannot distinguish owned vs. unowned cats as attackers.
- **Methodology quality:** Peer-reviewed; large sample, 11-year longitudinal data from a single facility. Geographic limitation: central Virginia only. Conservatively constructed methodology strengthens ecological validity of findings. Represents the most detailed published study using wildlife rehabilitation admission records as a cat-impact data source.
- **Known critiques:** Single-facility study; facilities vary in catchment area, species served, and record-keeping quality. Does not represent national burden.
- **Integration friction:** Paywall; WCV will share data via request. This is the "tier 4 rehabilitation data" most directly published and peer-reviewed.

---

### 1.12 Crooks & Soulé (1999) — *Nature*

- **Full citation:** Crooks KR, Soulé ME. "Mesopredator release and avifaunal extinctions in a fragmented system." *Nature* 400:563–566 (1999). DOI: [10.1038/23028](https://doi.org/10.1038/23028)
- **Scope:** Empirical study in fragmented Southern California urban/suburban landscape showing that coyote absence in habitat fragments correlates with increased cat abundance and lower songbird diversity — establishing the mesopredator release mechanism for cats.
- **Access:** Paywalled via Nature; widely cited and summarized in open sources.
- **Key claims supported:**
  - In fragments **without coyotes**, cats were more abundant and **songbird diversity was lower**.
  - Coyote presence suppresses feral cat populations, and this suppression benefits avian communities.
  - Cats function as **ecological mesopredators** whose impact on wildlife is amplified when top predators are extirpated.
- **Methodology quality:** Peer-reviewed in *Nature*; landscape ecology field methodology; replicated fragmentary design. One of the most influential papers in urban fragmentation ecology. The basic mesopredator release mechanism for cats has been corroborated in subsequent studies.
- **Known critiques:** Some subsequent studies (Gehrt & Clark 2003) found the coyote–mesopredator relationship less consistent for other predators; the direct cat-bird causal chain is strong but the predator guild complexity varies by geography.
- **Integration friction:** Paywall; well-cited and summarized in open sources.

---

### 1.13 Woinarski, Murphy, Legge et al. (2017, 2018, 2019) — Australian predation studies

- **Birds paper:** Woinarski JCZ, Murphy BP, Legge SM, et al. "How many birds are killed by cats in Australia?" *Biological Conservation* 214:76–87 (2017). [sciencedirect.com/science/article/abs/pii/S0006320719300746](https://www.sciencedirect.com/science/article/abs/pii/S0006320719300746)
- **Mammals paper:** Woinarski JCZ, Legge SM, Garnett ST, et al. "How many mammals are killed by cats in Australia?" *Mammal Review* 48(3):173–182 (2018).
- **Extinction linkage paper:** Woinarski JCZ et al. (2019) — feral cats linked to 27 of 47 Australian reptile/bird/mammal extinctions since European settlement.
- **Scope:** National synthesis of feral cat diet and predation-rate data from Australia; estimates of total annual wildlife kills.
- **Access:** Mix of open and subscription access; Legge et al. 2017 cat density paper freely available via Sciencedirect abstract.
- **Key claims supported:**
  - Feral cats in Australia kill an estimated **272 million birds**, **466 million reptiles**, and **815 million mammals** annually.
  - Combined with pet/stray cats: **~2.2 billion vertebrates** killed per year in Australia.
  - Feral cats contributed to predation pressure in **27 of 47 extinctions** of Australian birds, mammals, and reptiles since 1788.
  - Feral cats **threaten 75 critically endangered/near-threatened mammal species**, 40 threatened birds, 21 reptiles, and 4 amphibians.
  - Feral cat population in Australia estimated at **1.4–5.6 million in natural environments** (Legge et al. 2017), covering >99.8% of Australia's landmass.
- **Methodology quality:** Peer-reviewed, national scope, rigorous synthesis methodology. Australia is the global epicenter for documented feral cat impacts on mammals; methodology advances beyond US equivalent studies.
- **Integration friction:** Mix of open/paywalled access; a Western Australian synthesis ([wabsi.org.au/wp-content/uploads/2020/04/WABSI_Mitigating-cat-impacts_FINAL.pdf](https://wabsi.org.au/wp-content/uploads/2020/04/WABSI_Mitigating-cat-impacts_FINAL.pdf)) is freely available and summarizes the full body of Australian data.

---

## Tier 2: Federal and state agency data

### 2.1 USDA APHIS Wildlife Services — "Free-ranging and Feral Cats" management guide

- **URL:** [aphis.usda.gov/sites/default/files/free-ranging-and-feral-cats.pdf](https://www.aphis.usda.gov/sites/default/files/free-ranging-and-feral-cats.pdf)
- **DigitalCommons citation:** [digitalcommons.unl.edu/nwrcwdmts/31/](https://digitalcommons.unl.edu/nwrcwdmts/31/)
- **Scope:** Federal agency management guidance document on free-ranging and feral cats. Synthesizes ecological impact, disease transmission, and management interventions from APHIS's wildlife services perspective.
- **Access:** Open; public domain federal government document.
- **License:** US government public domain.
- **Key claims supported:**
  - Free-ranging cats are the **most common domestic animal rabies vector** in the US.
  - An analysis of data from **82 rehabilitation centers across North America** found cats responsible for **52% of bird intake**, and **78% of those admissions died or required euthanasia** (citing Loyd et al. 2013 and subsequent data).
  - USDA explicitly opposes TNR as a wildlife management strategy, stating removal is the most effective approach.
  - Cats spread **plague and typhus** via flea proliferation in the southwestern US.
  - Outdoor cats spread **toxoplasmosis** to livestock (abortion risk) and wildlife.
  - TWS, ABC, and American Society of Mammologists collectively support humane removal over TNR.
- **Methodology quality:** Government synthesis document drawing on peer-reviewed literature; not itself a primary research publication. The 82-rehabilitation-center statistic is a useful aggregate claim but its primary source citation (Loyd et al. 2013 + APHIS data) should be traced for methodology details.
- **Integration friction:** Open PDF; directly citable.

---

### 2.2 CDC — Rabies Surveillance in the United States (annual)

- **URL:** [cdc.gov/rabies/php/protecting-public-health/index.html](https://www.cdc.gov/rabies/php/protecting-public-health/index.html)
- **MMWR annual report series:** Published in *Morbidity and Mortality Weekly Report* annually; searchable at [cdc.gov/mmwr](https://www.cdc.gov/mmwr).
- **Scope:** National rabies case surveillance by species and state. The most authoritative dataset on domestic animal rabies incidence in the US.
- **Access:** Open; CDC public domain data.
- **Data format:** Annual MMWR narrative + tabular data; state-level breakdowns.
- **Update cadence:** Annual.
- **Key claims supported:** See Section 1.10. Cats consistently lead domestic animals in rabies positivity; ~200–300 rabid cats reported annually.
- **Integration friction:** Annual surveillance data are in HTML/PDF MMWR reports, not in a machine-readable API. WildlifeStats could parse MMWR tables or use CDC Wonder for some data queries.

---

### 2.3 CDC — Plague surveillance data / MMWR

- **2025 MMWR early-season plague:** [cdc.gov/mmwr/volumes/74/wr/mm7426a2.htm](https://www.cdc.gov/mmwr/volumes/74/wr/mm7426a2.htm)
- **Scope:** CDC plague case surveillance for the southwestern US; periodically documents cat-transmitted plague cases.
- **Key claims supported:**
  - *Yersinia pestis* can be transmitted to humans through **exposure to ill pets, especially cats**, which are highly susceptible to plague.
  - Cats with plague can transmit **infectious plague droplets** causing pneumonic plague to owners or veterinarians — a distinctly high-risk transmission route not seen from most wildlife reservoir hosts.
  - 2025 Arizona pneumonic plague death linked to cat contact ([Medscape, July 2025](https://www.medscape.com/viewarticle/pneumonic-plague-death-confirmed-arizona-2025a1000ip4)).
- **Methodology quality:** Government surveillance; case-by-case epidemiological investigations. Sample sizes small (plague is rare), but the mechanism is well-established.
- **Integration friction:** Open MMWR; federal public domain.

---

### 2.4 NASPHV — Compendium of Animal Rabies Prevention and Control

- **Current compendium intro:** [nasphv.org/Documents/NASPVCompendiumIntro.pdf](http://www.nasphv.org/Documents/NASPVCompendiumIntro.pdf)
- **2008 version (archived):** [cdc.gov/mmwr/preview/mmwrhtml/rr5702a1.htm](https://www.cdc.gov/mmwr/preview/mmwrhtml/rr5702a1.htm)
- **Scope:** The national standard for animal rabies prevention and control, issued by the National Association of State Public Health Veterinarians (NASPHV). Governs vaccine requirements, management protocols, and public health standards for domestic animals including cats.
- **Access:** Open; published in *MMWR* as a supplement.
- **License:** Public domain / federal co-publication.
- **Key claims supported:**
  - All cats should be vaccinated against rabies and stray/feral cats should be removed from the landscape (NASPHV's official policy stance).
  - Establishes the epidemiological framing of cats as the leading domestic animal species for rabies PEP burden.
  - Notes knowledge gaps in national surveillance data for rabid domestic animals (ownership status, neuter status not systematically tracked).
- **Methodology quality:** Authoritative regulatory/public health document; not a primary research study. Updated periodically.
- **Integration friction:** PDFs; no machine-readable data format. Cited as policy authority.

---

### 2.5 USFWS — Letters opposing TNR on federal and protected lands

- **ABC resource page listing USFWS letters:** [abcbirds.org/strategies/cats-birds/](https://abcbirds.org/strategies/cats-birds/)
- **Specific letters cited:**
  - USFWS Panama City Field Office letter to Escambia County Board of Commissioners
  - USFWS New Jersey Field Office letter to NJ DEP
  - USFWS New England Field Office letter to Seacoast Area Feline Education and Rescue Inc.
- **Scope:** Field office letters establishing USFWS's position that TNR on public/federal lands is incompatible with wildlife protection obligations under MBTA and ESA.
- **Access:** Hosted as PDFs via ABC; original letters are federal public documents.
- **Key claims supported:**
  - USFWS formally opposes establishment of feral cat colonies on federal lands and adjacent areas where migratory birds and ESA-listed species are present.
  - Letters cite specific species at risk at each location.
- **Methodology quality:** Not a scientific study; regulatory/policy correspondence. Authoritative as agency position.
- **Integration friction:** PDFs; archive on ABC website.

---

### 2.6 Association of Fish and Wildlife Agencies (AFWA) — Toolkit on Free-ranging Cats

- **URL:** [fishwildlife.org/application/files/5716/1436/9203/Cat-Toolkit-v6-Web.pdf](https://www.fishwildlife.org/application/files/5716/1436/9203/Cat-Toolkit-v6-Web.pdf)
- **Scope:** Toolkit for state and federal wildlife agencies managing free-ranging domestic cats on agency lands; synthesizes science, legal frameworks, and management options.
- **Access:** Open PDF; public.
- **Key claims supported:** Synthesizes TNR inefficacy evidence; notes cats as leading domestic animal for rabies PEP (citing Roebling et al.); provides state-agency framing for opposing TNR on managed wildlife lands.
- **Methodology quality:** Agency synthesis document, not primary research.
- **Integration friction:** Open PDF.

---

### 2.7 New Zealand Department of Conservation — Feral cat profile

- **URL:** [doc.govt.nz/nature/pests-and-threats/animal-pests-and-threats/feral-cats/](https://www.doc.govt.nz/nature/pests-and-threats/animal-pests-and-threats/feral-cats/)
- **Scope:** NZ DOC's official profile of feral cat impacts, with documented case studies (107 bats killed in one week by one cat; 17 skinks found in one cat's stomach; 20% of monitored kea killed by cats 2019–2021).
- **Access:** Open; NZ government public domain.
- **Key claims supported:**
  - Feral cats contributed to **>29 bird species** extinctions or local extirpations on Auckland Island alone.
  - Feral cats have a **devastating and documented** effect on kea, black stilt/kakī, Otago/grand skinks, native bats/pekapeka, and southern NZ dotterel.
  - NZ DOC **explicitly does not support TNR** for stray cats: "cats are predatory animals that continue to pose a threat to wildlife."
  - New Zealand government has added feral cats to the **Predator Free 2050** national eradication target list ([ACAP, 2025](https://acap.aq/latest-news/good-news-for-burrowing-petrels-and-shearwaters-feral-cats-to-be-added-to-new-zealands-predator-free-2050-strategy)).
- **Methodology quality:** Government agency summary, citing field monitoring data from DOC's conservation programs. Case studies are field-verified; population-level impact assessments are from DOC monitoring datasets.
- **Integration friction:** Open web source; NZ government public domain.

---

## Tier 3: Wildlife professional societies and NGO data

### 3.1 The Wildlife Society (TWS) — Issue Statement on Feral and Free-Ranging Domestic Cats (2025)

- **URL:** [wildlife.org/tws-issue-statement-feral-and-free-ranging-domestic-cats/](https://wildlife.org/tws-issue-statement-feral-and-free-ranging-domestic-cats/)
- **PDF (via ABC):** [abcbirds.org/wp-content/uploads/2025/05/2025.03-TWS-Issue-Statement-Feral-and-Free-ranging-Domestic-Cats.pdf](https://abcbirds.org/wp-content/uploads/2025/05/2025.03-TWS-Issue-Statement-Feral-and-Free-ranging-Domestic-Cats.pdf)
- **Scope:** Approved by TWS Council March 2025. Comprehensive policy and science statement from the primary professional society of wildlife scientists and managers in North America.
- **Access:** Open.
- **Key claims and citations compiled in statement:**
  - US bird mortality: 1.3–4.0 billion/year (Loss et al. 2013)
  - US mammal mortality: 6.3–22.3 billion/year (Loss et al. 2013)
  - Australia wildlife mortality: 609 million reptiles, 399 million birds, >1 billion mammals annually (Stobo-Wilson et al. 2022)
  - 63 global species extinctions attributed to cats (Doherty et al. 2016)
  - Florida domestic cats: 19% of confirmed rabies cases in 2022
  - *T. gondii*: second leading cause of death from foodborne illness in humans in US (Scallan et al. 2011)
  - TNR is "usually ineffective" (Longcore et al. 2009; Crawford et al. 2019)
  - TWS **opposes TNR** and supports humane elimination (removal) of free-ranging cat populations.
- **Methodology quality:** Not primary research; comprehensive policy synthesis by the primary professional body. Its credibility derives from membership (wildlife scientists) and vetting process. Approved 2025, meaning it incorporates latest evidence.
- **Integration friction:** Open PDF; directly citable.

---

### 3.2 American Bird Conservancy (ABC) — Cats Indoors Program

- **URL:** [abcbirds.org/solutions/keep-cats-indoors/](https://abcbirds.org/solutions/keep-cats-indoors/)
- **Resources page:** [abcbirds.org/strategies/cats-birds/](https://abcbirds.org/strategies/cats-birds/)
- **Scope:** ABC is the primary US conservation NGO driving the scientific and policy case against outdoor cats. The Cats Indoors program hosts the most extensive public repository of anti-TNR and cat-impact scientific literature, fact sheets, and policy documents in the US.
- **Access:** Most resources open; some position documents available only as PDFs.
- **License:** ABC copyright; materials may be cited and linked.
- **Key resources:**
  - ABC position statement on free-roaming cats (PDF link on resources page)
  - Curated scientific literature library (Longcore, Conrad, Castillo, Medina, etc.)
  - Cats Indoors Advocacy Toolkit for policymakers
  - USFWS field office letters (hosted)
  - Sample ordinances
  - Fact sheets: Toxoplasma, rabies, bird mortality
- **Key claims supported:** 2.4 billion birds/year killed (median of Loss et al. 2013); cats are the top direct anthropogenic cause of bird mortality; TNR does not reduce populations.
- **Methodology quality:** ABC is an advocacy organization, but it rigorously hosts and links peer-reviewed literature. The scientific claims ABC makes are properly sourced to the primary literature. Known framing bias: the resources page exclusively represents the ecological-harm side.
- **Integration friction:** Curated PDF library is useful for WildlifeStats but requires individual document tracking; no structured API.

---

### 3.3 IUCN Invasive Species Specialist Group (ISSG) — Global Invasive Species Database

- **URL:** [iucngisd.org/gisd/100_worst.php](https://www.iucngisd.org/gisd/100_worst.php)
- **Full GISD database:** [iucngisd.org/gisd/](https://www.iucngisd.org/gisd/)
- **Scope:** *Felis catus* is listed in the **IUCN's 100 of the World's Worst Invasive Alien Species**. The GISD contains a species profile with ecological impact data, global distribution, and management records.
- **Access:** Open online; GISD has data export functionality.
- **License:** IUCN data; CC-BY for educational use.
- **Key claims supported:** IUCN formally classifies domestic cat as one of the 100 worst invasive alien species globally, with particular reference to island bird predation. This classification provides the regulatory/nomenclatural foundation for treating free-roaming *Felis catus* as an invasive species in policy contexts.
- **Methodology quality:** IUCN ISSG listings are expert-reviewed; credibility derives from international scientific authority. Individual species profiles vary in detail.
- **Integration friction:** Online database; limited structured data export. Species page is directly linkable.

---

### 3.4 AZA / SAFE / NAS — Joint Position Statement on Roaming Domestic Cats (2024)

- **PDF (via ABC):** [abcbirds.org/wp-content/uploads/2024/03/AZA-SAFE-NAS-Position-Statement-on-Roaming-Cats.pdf](https://abcbirds.org/wp-content/uploads/2024/03/AZA-SAFE-NAS-Position-Statement-on-Roaming-Cats.pdf)
- **Scope:** Joint position from the Association of Zoos and Aquariums (AZA), Species Survival Plans (SAFE), and the North American Species Survival Program (NAS) on roaming domestic cats.
- **Access:** Open PDF.
- **Key claims supported:**
  - Roaming cats are a **potential reservoir of feline leukemia virus (FeLV)** and transmission pathway for **Florida panther** (*Puma concolor*) infection.
  - Cats are the **top carrier of rabies among domestic animals** in the US for over 30 years, and disproportionately expose people to rabies (citing Roebling et al. 2014).
  - NASPHV advises all domestic cats be kept current on rabies vaccination and stray/feral cats be removed from the landscape.
- **Methodology quality:** Joint institutional position statement, not primary research; cites peer-reviewed sources.
- **Integration friction:** Open PDF.

---

### 3.5 Audubon Society — Position on outdoor cats

- **Audubon.org news piece (2013, responding to Loss et al.):** [audubon.org/news/cats-pose-even-bigger-threat-birds-previously-thought](https://www.audubon.org/news/cats-pose-even-bigger-threat-birds-previously-thought)
- **Sacramento Audubon Society cat policy (detailed local policy example):** [sacramentoaudubon.org/cat-policy](https://www.sacramentoaudubon.org/cat-policy)
- **Scope:** National Audubon Society endorses ABC's Loss et al. mortality figures and supports keeping cats indoors. Local chapters (e.g., Sacramento) have published detailed policy documents opposing TNR on natural areas, with specific recommendations for policymakers.
- **Access:** Open.
- **Key claims supported:** Cats kill 2.4 billion birds/year in the US (Loss et al.); cat colonies should be prohibited in designated wild areas; pet cats should be kept indoors.
- **Integration friction:** No structured dataset; policy documents in HTML/PDF.

---

## Tier 4: Wildlife rehabilitation center intake records (the underrepresented data layer)

**Context:** Wildlife rehabilitation centers represent the most direct empirical record of cat-caused wildlife harm at the individual-patient level. Despite collectively admitting hundreds of thousands of patients annually nationwide, this data layer remains almost entirely unpublished. The two principal barriers are (1) no national aggregated database, and (2) heterogeneous record-keeping across ~700+ licensed rehabilitation facilities in the US. WildlifeStats has a unique opportunity to fill this gap by directly partnering with rehabilitation networks.

---

### 4.1 Wildlife Center of Virginia (WCV) — Published intake records study

- **WCV publications page:** [wildlifecenter.org/about/publications](https://wildlifecenter.org/about/publications)
- **2016 study news release:** [wildlifecenter.org/news-events/news/2016/new-study-reveals-extensive-damage-wildlife-caused-domestic-cats](https://wildlifecenter.org/news-events/news/2016/new-study-reveals-extensive-damage-wildlife-caused-domestic-cats)
- **Scope:** The only published 11-year longitudinal analysis of cat-attack admissions at a single major US wildlife hospital. See Section 1.11 (McRuer et al. 2017) for full detail.
- **Access for raw data:** The WCV maintains electronic medical records; data access for research collaboration would require a formal data-sharing agreement. WCV has demonstrated willingness to publish data (McRuer et al. 2017).
- **Key figures:** ~21,000 records studied; 14% of all admissions = cat attacks; 83 species; >70% small mammal / ~81% bird mortality post-cat attack.
- **Ongoing data:** WCV continues to admit patients; post-2010 data exist but have not been published as a follow-up study.
- **Integration friction for WildlifeStats:** Direct outreach to WCV Director of Veterinary Services for data-sharing MOU is recommended. Data is electronic, likely in a case management system (e.g., WildTrax or similar). Standardizing intake code definitions across facilities will be critical.

---

### 4.2 USDA APHIS / AAU / Boston University — Large-scale rehabilitation intake analysis

- **AAU press release:** [aau.edu/research-scholarship/featured-research-topics/new-study-identifies-greatest-threat-wildlife-across](https://www.aau.edu/research-scholarship/featured-research-topics/new-study-identifies-greatest-threat-wildlife-across)
- **Published paper (PLoS ONE 2021):** [pmc.ncbi.nlm.nih.gov/articles/PMC8454955/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8454955/)
- **Scope:** Analysis of **over 600,000 wildlife rehabilitation center records** from multiple facilities across North America, examining the full spectrum of anthropogenic causes of wildlife injury and mortality. The largest published analysis of rehabilitation intake records in North America. (Note: this study covered all causes, not cats exclusively, but cat attacks appear as a major admission category.)
- **Access:** PLoS ONE (open access); primary dataset may be available via USFWS Wildlife Rehabilitation data programs.
- **License:** PLoS ONE open access.
- **Key claims supported:**
  - **40% of animals** admitted to wildlife rehab centers arrive due to "human disturbances" broadly defined.
  - The dataset confirms cat attacks, vehicle collisions, and building strikes as dominant anthropogenic causes.
  - Provides the largest published rehabilitation-intake dataset for potential future cat-specific analysis.
- **Methodology quality:** Peer-reviewed, open access, large-N multi-facility study. Limitation: "cat attack" cause coding varies across facilities; the 2021 paper's focus was broad anthropogenic causes, not cat-specific analysis.
- **Integration friction:** Open access paper; primary dataset should be pursued through paper authors (Boston University / USFWS collaboration).

---

### 4.3 USDA APHIS 82-rehabilitation-center aggregate statistic

- **Source document:** USDA APHIS "Free-ranging and Feral Cats" PDF (Section 2.1 above)
- **Claim:** Data from **82 rehabilitation centers across North America** found cats responsible for **52% of bird intake**, and **78% of those cat-related admissions died or had to be euthanized** (citing Loyd et al. 2013 and APHIS-compiled data).
- **Access:** This aggregate figure appears in the APHIS document but the underlying multi-facility dataset is not published as a standalone resource.
- **Integration friction:** The aggregate statistic is in an open government document, but the primary dataset it draws on (compiled by APHIS / NWRA) is not publicly accessible. A formal data-sharing request to USDA APHIS Wildlife Services would be required.

---

### 4.4 National Wildlife Rehabilitators Association (NWRA)

- **URL:** [nwrawildlife.org](https://www.nwrawildlife.org)
- **Scope:** NWRA is the primary professional membership association for wildlife rehabilitators in North America (~1,500+ member facilities). NWRA sets minimum standards for record-keeping at rehabilitation facilities (see ODFW Minimum Standards 3rd edition) and periodically surveys members.
- **Access:** Membership organization; public website.
- **Data held:** NWRA does not maintain a national intake database itself, but its standards documents specify what data elements licensed facilities must record (species, date admitted, intake location, cause of injury, treatment outcomes). NWRA members collectively hold tens of millions of patient records.
- **Key gap NWRA can address:** Member surveys could aggregate cat-attack intake rates across facilities. NWRA has published survey-based national estimates in the past; a targeted survey on cat-caused intake would be methodologically feasible.
- **Integration friction:** No centralized database; WildlifeStats would need to work through NWRA leadership to design and execute a member survey or facilitate a data-sharing network. This is the single highest-value untapped data source in this domain — the data exist in distributed rehab facility records and have never been systematically aggregated.

---

### 4.5 Cornell Wildlife Health Lab — Rehabilitation data perspective

- **URL:** [cwhl.vet.cornell.edu/article/whats-data-got-do-it](https://cwhl.vet.cornell.edu/article/whats-data-got-do-it)
- **Scope:** Cornell's Wildlife Health Lab has engaged with the question of using rehabilitation data as a wildlife surveillance tool. They have noted the data-quality challenges and the potential value of harmonized intake records.
- **Access:** Open web article.
- **Integration friction:** Would be an important academic partner for any national rehabilitation data harmonization effort.

---

### 4.6 Tufts Wildlife Clinic — Annual intake data (qualitative)

- **URL:** [vet.tufts.edu/tufts-wildlife-clinic](https://vet.tufts.edu/tufts-wildlife-clinic)
- **Scope:** Tufts University Cummings School of Veterinary Medicine's Wildlife Clinic in North Grafton, Massachusetts. Treats ~2,000–4,400 wildlife patients annually (record 4,428 in 2025). Regularly treated cats as a cause of injury in intake reports.
- **Access:** Annual intake summary published via clinic communications; detailed data in medical records not publicly available.
- **Integration friction:** Requires data-sharing agreement with Tufts Cummings School.

---

### 4.7 USFWS — Wildlife Rehabilitation Conservation Value Report (2024)

- **URL:** [fws.gov/sites/default/files/documents/2024-12/conservation-value-of-wildlife-rehabilitation.pdf](https://www.fws.gov/sites/default/files/documents/2024-12/conservation-value-of-wildlife-rehabilitation.pdf)
- **Scope:** USFWS report on the conservation value of wildlife rehabilitation, including discussion of cat attacks, vehicle collisions, and building strikes as common intake causes. Establishes the federal government's recognition that rehabilitation intake data is a valid wildlife impact monitoring tool.
- **Access:** Open; federal public domain.
- **Integration friction:** PDF; policy document, not a primary dataset.

---

## Additional cross-cutting sources

### A.1 Lepczyk, Conole & Duffy (various) — Urban cat ecology review

- **Lepczyk CA** is a University of Hawaii at Manoa researcher who has published extensively on outdoor cat ecology, Hawaii-specific cat impacts, and the urban cat literature. Key papers include co-authored reviews on outdoor cats in urban environments, cat-wildlife interactions, and Hawaiian island impacts.
- **Representative co-authored work:** Aronson et al. 2016 (*Ecology*, urban community assembly) cites Lepczyk's work on cat predation across urban gradients.
- **Hawaii focus:** Lepczyk has published on *T. gondii* spread and bird mortality in Hawaii, where both endangered native bird species and monk seals are affected. Hawaii has the highest per-capita cat density and the highest density of endangered species — making it a uniquely high-stakes case study.
- **Access:** Mix of open and paywalled journal publications.

---

### A.2 Loss & Marra 2015 — Supplementary US review

- **Full citation:** Loss SR, Marra PP. "Population impacts of free-ranging domestic cats on mainland birds in the United States." *Frontiers in Ecology and the Environment* 13(9):480–487 (2015).
- **Scope:** Follow-up to 2013 paper; focuses on population-level impacts (not just mortality counts), reviewing evidence that cat predation affects bird population trends in the US.
- **Methodology quality:** Peer-reviewed; advances the evidence from "cats kill a lot" to "cats affect population dynamics." Stronger argument for conservation concern than the mortality-count paper alone.

---

### A.3 Crawford, Calver & Fleming (2019) — *Animals* (MDPI)

- **Full citation:** Crawford HM, Calver MC, Fleming PA. "A case of letting the cat out of the bag – why trap-neuter-return is not an ethical solution for stray cat (Felis catus) management." *Animals* 9(4):171 (2019).
- **PMC full text:** [pmc.ncbi.nlm.nih.gov/articles/PMC6523511/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6523511/)
- **Access:** Open access.
- **Scope:** Australian perspective review arguing TNR is neither ethically nor practically justified. Reviews modeling requirements, welfare costs to TNR cats, and wildlife harm. Concludes TNR is "unsuitable for Australia in almost all situations."
- **Key claims:** The weight of data indicates TNR is unlikely to solve problems in most cases and is "unethical on animal welfare grounds" (arguing that life as a feral cat constitutes suffering). Provides modeling analysis of sterilization thresholds.

---

## Recommended ingestion priority order

The following ranking weighs **data value × accessibility × methodology quality** for WildlifeStats's goal of balanced, evidence-based presentation of the cat-wildlife conflict. Publicly accessible, peer-reviewed, or government sources with machine-readable or easily parseable data are ranked highest.

| Rank | Source | Rationale |
|------|--------|-----------|
| 1 | **Loss, Will & Marra 2013** (*Nature Communications*, open PDF + PubMed) | Foundational US mortality paper; highest citation count in the field; sets the quantitative baseline for all downstream analysis. Open access PDF. |
| 2 | **CDC Rabies Surveillance Annual Reports** (MMWR, open, annually updated) | Primary federal surveillance data; directly connects free-roaming cats to a quantified, ongoing public health burden; annually updated; government public domain. |
| 3 | **Doherty et al. 2016** (*PNAS*, open access + Dataset S1) | Global extinction attribution; machine-readable supplementary species dataset directly ingestible; peer-reviewed; most comprehensive global-scope dataset available. |
| 4 | **USDA APHIS "Free-ranging and Feral Cats" guidance** (open PDF) | Federal agency synthesis; cites the 82-rehabilitation-center aggregate; authoritative for policy context; public domain. |
| 5 | **TWS Issue Statement (2025)** (open PDF) | Most current comprehensive synthesis from the primary professional society; approved March 2025; consolidates all major evidence streams in one citable document. |
| 6 | **NOAA Fisheries toxoplasmosis / Hawaiian monk seal page** (open, federal) | Best available public-domain source for the marine wildlife disease spillover claim; directly quantifies monk seal deaths; federal source. |
| 7 | **McRuer et al. 2017 / Wildlife Center of Virginia** (paywall, but open WCV summary) | Only published peer-reviewed study using rehabilitation intake records as primary data; highly specific to cat-caused mortality burden at the facility level; opens the rehabilitation-data conversation. |
| 8 | **Longcore, Rich & Sullivan 2009** (*Conservation Biology*, open PDF via ABC) | Definitive peer-reviewed critique of TNR efficacy; the document that the entire anti-TNR scientific literature cites. Must-ingest for balanced TNR coverage. |
| 9 | **New Zealand DOC feral cat profile** (open, government) | High-quality government source with verified case-level impact data (individual cat kills documented); represents best available international policy-relevant non-US dataset. |
| 10 | **NWRA + distributed wildlife rehabilitation data** (requires direct partnership) | Highest long-term strategic value as an **untapped** data source that no existing database covers. The rehabilitation intake layer is the most underrepresented dataset in the entire field. WildlifeStats partnering with NWRA for a national survey or a multi-facility data aggregation initiative would produce original data not available elsewhere. Priority not for immediate ingestion but for WildlifeStats's unique contribution to this evidence base. |

---

*Report compiled for WildlifeStats national research framework. All sources reviewed for methodology quality and data accessibility. This report maps the data landscape; it does not endorse any single management policy. The companion report (`08-cats-TNR-humane.md`) covers the TNR-efficacy and community-cat evidence base.*
