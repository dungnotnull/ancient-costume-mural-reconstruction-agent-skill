# CLAUDE.md — Skill 240: ancient-costume-mural-reconstruction

## Skill Identity
- **Skill Name:** `ancient-costume-mural-reconstruction`
- **Tagline:** Ancient Costume Reconstruction via Murals/Statues — Ancient Costume Reconstruction & Archaeological Textile History analysis & decision-support harness.
- **Current Phase:** Phase 6 — Open-Source Hardening (complete)
- **Folder:** `D:\972026\240-ancient-costume-mural-reconstruction\`
- **Version:** 1.1.0

---

## Problem This Skill Solves

This skill provides a structured, evidence-backed analytical workflow for
**Ancient Costume Reconstruction & Archaeological Textile History**. It gathers
authoritative real-time and reference data, applies recognized domain methods,
cross-references academic research, and delivers actionable outputs that are
fully evidenced, risk/limitation-disclosed, and traceable to authoritative
sources — continuously self-improving through an automated knowledge crawl
pipeline.

---

## Harness Flow Summary

```
/ancient-costume-mural-reconstruction invoked
│
├─ Step 1: sub-gather-requirements   → Clarify object, scope, timeframe, available inputs, audience, language before any data fetching.
├─ Step 2: sub-evidence-collector    → Fetch museum collection records, extant textile parallels, authoritative docs, and recent developments.
├─ Step 3: sub-core-analysis         → Reconstruct from iconography: form/drape → construction → materials/dyes → evidence hierarchy → 3D.
├─ Step 4: sub-knowledge-updater     → Query SECOND-KNOWLEDGE-BRAIN.md for Tier-labelled citations; flag gaps for the crawl pipeline.
├─ Step 5: sub-advisor               → Synthesize into a risk-disclosed conclusion with a full evidence chain + remediation.
└─ Step 6: main (quality gate)       → verify U1–U6 + G1–G4 gates, auto-fix, disclosure, output polish
```

---

## Sub-Skills

| `skills/sub-gather-requirements.md` | Clarify the object of analysis, constraints, timeframe, available inputs, target audience, and language before any data fetching. |
| `skills/sub-evidence-collector.md` | Fetch authoritative real-time and reference data for the object: museum collection records, extant textile parallels, iconographic comparanda, period standards, and recent academic developments. |
| `skills/sub-core-analysis.md` | Reconstruct ancient costumes from murals/statues: analyze iconography, recover period construction & materials, and produce evidence-graded 3D reconstructions. |
| `skills/sub-knowledge-updater.md` | Query SECOND-KNOWLEDGE-BRAIN.md for authoritative academic and professional evidence; surface citations with tier labels and flag gaps for the crawl pipeline. |
| `skills/sub-advisor.md` | Synthesize all prior analysis into a risk-disclosed conclusion with a full evidence chain and recommended actions. |

---

## Tools Required

- **WebSearch** — live domain news, reports, standards updates
- **WebFetch** — scrape Ancient Costume Reconstruction & Archaeological Textile History authoritative sources (museum collections, journals)
- **Image analysis (vision)** — read murals/statues/reliefs for iconographic analysis
- **Read / Write** — read SECOND-KNOWLEDGE-BRAIN.md; append knowledge entries
- **Bash** — run `tools/knowledge_updater.py` for periodic crawl
- **Skill** — invoke sub-skills sequentially through the harness

---

## Knowledge Sources

### Domain Authoritative Sources
- Museum/collection references (Met, V&A, British Museum, Louvre)
- Archaeological textile references (CTR, Coptic textile database, Tarim finds)
- Art-history iconography references (Dunhuang Academy, Getty)
- Pattern-cutting/period references
- Dye/material history references (Cardon, Sandberg compendia)
- Conservation references (AIC, ICOMOS, ICCROM, CIETA)

### Academic & Research Sources
- The Journal of the Costume Society (Costume) — Taylor & Francis
- Textile History — Taylor & Francis
- Journal of Archaeological Science — Elsevier
- Archaeological Textiles Newsletter
- Antiquity — Cambridge
- Fashion Theory — Taylor & Francis

### Academic Crawl Targets
- ArXiv (cs.GR, cs.CV, cs.AI — 3D/visual reconstruction methods)
- Semantic Scholar keyword clusters for the domain
- Crossref (DOI enrichment of recent works)
- RSS feeds (Textile Society, Costume Society)

---

## Supporting Python Tools

| File | Purpose |
|------|---------|
| `tools/knowledge_updater.py` | Crawl pipeline: ArXiv + Semantic Scholar + Crossref + RSS → score → dedup (SHA-256 of normalized DOI/URL) → backup → append to SECOND-KNOWLEDGE-BRAIN.md |
| `tools/test_knowledge_updater.py` | Unit tests (unittest, 22 tests): hashing, DOI normalization, scoring, formatting, dedup, config, CLI, offline pipeline wiring |
| `tools/run_test_scenarios.py` | Domain-aware scenario runner (5 scenarios) + structural / 8-File Contract validator; optional JSON report |
| `tools/validate_project.py` | 8-File Contract validator per SKILL-STANDARD.md; optional JSON report |

---

## Automated Knowledge Update Schedule

```cron
# Weekly academic update (Mondays 8:00 AM)
0 8 * * 1 python D:/972026/240-ancient-costume-mural-reconstruction/tools/knowledge_updater.py >> logs/knowledge_update.log 2>&1

# Daily news update (Daily 7:00 AM)
0 7 * * * python D:/972026/240-ancient-costume-mural-reconstruction/tools/knowledge_updater.py --news-only >> logs/knowledge_news.log 2>&1
```

Manual: `python tools/knowledge_updater.py --dry-run` | `--news-only` |
`--academic-only` | `--keywords "..."` | `--config cfg.json` | `--max-new N`

---

## Active Development Tasks

- [x] Phase 0: Architecture & source map (CLAUDE.md, PROJECT-detail.md, PDPT.md)
- [x] Phase 1: Core sub-skills (production-grade)
- [x] Phase 2: Main harness + quality gates + degradation
- [x] Phase 3: Knowledge pipeline + tests + cron
- [x] Phase 4: Testing & validation (all validators pass)
- [x] Phase 5: Integration & polish
- [x] Phase 6: Open-source hardening (LICENSE, CONTRIBUTING, COC, CHANGELOG,
      pyproject.toml, progression.json, production-grade tooling) — v1.1.0

---

## References

- `PROJECT-detail.md` — full technical specification
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — build roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — self-improving knowledge base
- `D:\972026\SKILL-STANDARD.md` — library-wide standard
- Reference impl: `D:\vn-finance-analysis-hd-skill`