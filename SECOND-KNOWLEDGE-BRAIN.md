# SECOND-KNOWLEDGE-BRAIN.md — Skill 240: ancient-costume-mural-reconstruction

> **Living Knowledge Base** for Ancient Costume Reconstruction & Archaeological
> Textile History. Updated by `tools/knowledge_updater.py` on a weekly schedule
> (Mondays 08:00 academic, daily 07:00 news). All entries are date-stamped; new
> entries are appended at the bottom of section 7. Evidence hierarchy:
> Systematic Review > Meta-Analysis > Guideline/Peer-reviewed RCT > Cohort >
> Expert Consensus > News.
>
> **Seeding note:** this baseline is hand-curated with verified Tier-1/2
> entries and authoritative institutional URLs. DOI-cited academic entries are
> enriched automatically by the crawl pipeline on its first real run
> (`python tools/knowledge_updater.py`). Maintainers should run the pipeline to
> reach the full 4+ DOI-cited academic reference target.

---

## 1. Core Concepts & Frameworks

### 1.1 Foundational Methods

| Concept | Definition | Primary evidence |
|---------|-----------|------------------|
| Iconography | Reading garment form, drape, layering, accessories, and status markers from murals, statues, and reliefs | Mural/statue/relief depictions + comparanda |
| Construction | Period pattern-cutting, seaming, draping; rectangular vs. tailored; undergarments | Extant textiles, technical analysis |
| Materials/dyes | Fibers (linen, wool, silk, hemp, cotton), weaves (tabby, twill, compound, tapestry), natural dyes (madder, woad/indigo, kermes, Tyrian purple, weld) | Extant textiles + HPLC/FTIR/SEM dye & fiber analysis |
| Evidence hierarchy | `extant textiles > iconographic > textual > ethnographic` | Applied per claim |
| 3D reconstruction | Evidence-graded digital twin: layer build, scale (cm), per-panel material, confidence H/M/L | Model intent + comparanda |
| Cultural/social context | Rank, ritual function, gender, age, trade links | Iconography + textual + context |

### 1.2 Evidence Hierarchy (this domain)

- **Tier 1**: Systematic review / meta-analysis / official standard (UNESCO,
  ICOMOS, AIC conservation standards, CITES for materials, ISO textile test
  methods).
- **Tier 2**: Peer-reviewed academic paper / RCT-equivalent technical study
  (dye HPLC, fiber SEM, C14 dating) in a recognised journal.
- **Tier 3**: Industry report / museum collection record / professional
  association guideline (AATCC, CTR, CIETA).
- **Tier 4**: News / blog / vendor material.

### 1.3 Decision Logic — Verdict Mapping

| Evidence state | Verdict |
|----------------|---------|
| Extant parallel + clear iconography + dated materials/dye evidence | Evidence-Based Reconstruction |
| Strong iconography + partial construction/materials inferred from comparanda | Plausible (interpretive) |
| Fragmentary iconography, no extant parallel, materials by analogy | Speculative |
| Decisive input missing or sources unreachable (degradation Level ≥3) | Inconclusive |

---

## 2. Key Research Papers & Standards

| Title | Authors | Year | Venue | DOI/URL | Tier |
|------|---------|------|-------|---------|------|
| Archaeological Textiles: A Review of Current Research | Good, I. | 2001 | Annual Review of Anthropology 30:209–226 | 10.1146/annurev.anthro.30.1.209 | 2 |
| The Silk Road in World History | Liu, X. | 2010 | Oxford University Press | 10.1093/acprof:oso/9780195391746.001.0001 | 2 |
| Prehistoric Textiles | Barber, E.J.W. | 1991 | Princeton UP | https://press.princeton.edu/books/paperback/9780691002248/prehistoric-textiles | 2 |
| North European Textiles until AD 1000 | Bender Jørgensen, L. | 1992 | Aarhus UP / CTR | https://ctr.hum.ku.dk/research/ | 2 |
| Egyptian Archaeological Textiles (CTR bibliography) | Centre for Textile Research | — | U. Copenhagen | https://ctr.hum.ku.dk/ | 3 |
| The Metropolitan Museum of Art — Costume & Textile collection | The Met | — | Museum collection | https://www.metmuseum.org/art/collection#!?q=textile | 3 |
| Victoria & Albert Museum — Textiles collection | V&A | — | Museum collection | https://collections.vam.ac.uk/ | 3 |
| British Museum — collection online | British Museum | — | Museum collection | https://www.britishmuseum.org/collection | 3 |
| Textile History (journal) | Taylor & Francis | — | Journal | https://www.tandfonline.com/journals/ytex20 | 3 |
| Journal of Archaeological Science (journal) | Elsevier | — | Journal | https://www.sciencedirect.com/journal/journal-of-archaeological-science | 3 |
| Antiquity (journal) | Cambridge UP | — | Journal | https://www.cambridge.org/core/journals/antiquity | 3 |
| Fashion Theory (journal) | Taylor & Francis | — | Journal | https://www.tandfonline.com/journals/rftz20 | 3 |

**Authoritative sources registered (crawl targets):**
- The Journal of the Costume Society (Costume) — Taylor & Francis
- Textile History — Taylor & Francis
- Journal of Archaeological Science — Elsevier
- Archaeological Textiles Newsletter
- Antiquity — Cambridge
- Fashion Theory — Taylor & Francis

---

## 3. State-of-the-Art Methods & Tools

State of the art for ancient-costume reconstruction:

- **3D garment reconstruction from iconography**: photogrammetry of
  statues/reliefs → draped garment simulation (Marvelous Designer, CLO,
  OpenSourceCloth) with physics-validated drape.
- **AI-assisted drape & material inference**: ML classifiers trained on
  extant-textile weave libraries to predict fiber/weave from iconographic
  drape signatures.
- **Hyperspectral & multispectral pigment analysis**: non-invasive
  identification of pigments/dyes on murals and extant textiles.
- **HPLC/FTIR/SEM dye & fiber analysis**: gold-standard for dye and fiber ID
  on extant fragments.
- **Comparative textile databases**: CTR, NATCC, EU Textile Idioms, BNR
  textile databases for parallel search.
- **Digital-twin heritage**: photoreal digital twins for museum display,
  with provenance metadata (IIIF, CIDOC-CRM).

Crawl targets: Costume, Textile History, J. Archaeol. Sci., Antiquity, Fashion
Theory, plus Semantic Scholar keyword clusters and Crossref for DOI enrichment.

---

## 4. Authoritative Data Sources

### 4.1 Domain authoritative sources
- Museum/collection references (Met, V&A, British Museum, Louvre)
- Archaeological textile references (CTR, Coptic Textile database, Tarim
  mummy textiles reports)
- Art-history iconography references (Dunhuang Academy, Getty)
- Pattern-cutting/period references (period treatises, rectangular-construction
  typology)
- Dye/material history references (Cardon, Sandberg natural-dye compendia)
- Conservation references (AIC, ICOMOS, ICCROM, CIETA)

### 4.2 Academic & research sources
- The Journal of the Costume Society (Costume) — Taylor & Francis
- Textile History — Taylor & Francis
- Journal of Archaeological Science — Elsevier
- Archaeological Textiles Newsletter
- Antiquity — Cambridge
- Fashion Theory — Taylor & Francis

### 4.3 Crawl pipeline sources (knowledge_updater.py)
- ArXiv (cs.GR, cs.CV, cs.AI — 3D/visual reconstruction methods)
- Semantic Scholar (keyword clusters for the domain)
- Crossref (DOI enrichment of recent works)
- RSS feeds (Textile Society, Costume Society)

---

## 5. Analytical Frameworks

Knowledge categories covered (cross-reference sub-skills in `skills/*.md`):

- **Iconographic analysis** — `skills/sub-core-analysis.md` §2.1
- **Period garment construction & pattern** — `skills/sub-core-analysis.md` §2.2
- **Material/dye history** — `skills/sub-core-analysis.md` §2.3
- **Reconstruction methodology (evidence hierarchy)** — `skills/sub-core-analysis.md` §2.4
- **Cultural/social context** — `skills/sub-core-analysis.md` §2.5
- **3D modeling & display** — `skills/sub-core-analysis.md` §2.5

The fixed bookends (requirements → evidence → knowledge → synthesis → quality
gate) are mandatory; the core analysis sub-skill implements the domain-specific
methods.

---

## 6. Self-Update Protocol

- **Crawl pipeline:** `tools/knowledge_updater.py`
- **Schedule:** weekly academic (Mondays 08:00) + daily news (07:00);
  documented in `CLAUDE.md`.
- **Dedup:** SHA-256 of the normalized DOI/URL (case/whitespace-insensitive;
  `https://doi.org/` prefix stripped) so the same reference cannot be appended
  twice.
- **Scoring:** composite 0–10 =
  `recency(0.4) + keyword_relevance(0.4) + citation_count(0.2)`.
- **Crawl targets:** ArXiv (cs.GR/CV/AI), Semantic Scholar keyword clusters,
  Crossref (DOI enrichment), RSS feeds (Textile Society, Costume Society).
- **Gap-fill:** `sub-knowledge-updater` flags missing values as crawl queries;
  optional 2-query WebSearch gap-fill marks finds `[pending append]`.
- **Append rule:** new entries appended under section 7 with a date stamp and a
  relevance score; the brain file is backed up before write.
- **Safety:** backup-before-write, idempotent append, graceful degradation if
  network sources are unreachable.

---

## 7. Knowledge Update Log

_(Appended automatically by the crawl pipeline. Baseline seeded with the
references in section 2 — hand-curated, DOI-cited where verifiable, with
authoritative institutional URLs otherwise. Run
`python tools/knowledge_updater.py` to enrich with new academic + news
entries.)_