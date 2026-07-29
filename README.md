# ancient-costume-mural-reconstruction

**Ancient Costume Reconstruction via Murals/Statues** — a professional-grade
Claude Code skill harness for **Ancient Costume Reconstruction &
Archaeological Textile History**.

[![Claude Skill](https://img.shields.io/badge/Claude-Skill-blue)](https://claude.ai/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.1.0-brightgreen)](CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-production--ready-success)](PROJECT-DEVELOPMENT-PHASE-TRACKING.md)

It gathers authoritative real-time data, applies recognized domain methods,
integrates academic research, and delivers evidence-backed, risk-disclosed
outputs — with a continuously self-improving knowledge pipeline.

## Overview

This skill turns Claude into a domain-expert that reconstructs ancient
costumes from murals, statues, and reliefs: it reads iconography, recovers
period construction and materials/dyes, applies the evidence hierarchy
(extant textiles > iconographic > textual > ethnographic), and proposes
evidence-graded 3D reconstructions. Every output is fully evidenced,
risk/limitation-disclosed, and traceable to authoritative sources. A weekly
crawl pipeline (`tools/knowledge_updater.py`) keeps the knowledge base
current with new academic papers and heritage-textile news.

<details>
<summary><b>Features</b></summary>

- Real-time data aggregation from authoritative museum + academic sources
- Systematic domain analysis: iconography → construction → materials/dyes → 3D
- Academic research integration with an auto-updating knowledge base
- Risk/limitation-disclosed outputs with best/base/worst scenarios
- Self-improving knowledge pipeline (ArXiv + Semantic Scholar + Crossref + RSS)
- 10 quality gates (U1–U6 universal + G1–G4 domain) with auto-fix + degradation
- Production-grade Python tooling: dataclass config, logging, backup-before-
  write, DOI-normalized dedup, structured tests
- Open-source scaffolding: LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG,
  pyproject.toml

</details>

## Why This Skill

Practitioners in Ancient Costume Reconstruction & Archaeological Textile
History face three structural gaps: **data fragmentation** (authoritative data
scattered across museums, journals, conservation bodies), **methodology gaps**
(most advice lacks systematic, evidence-graded methods), and **no
self-improvement** (static tools do not learn from new research). This skill
unifies authoritative real-time data, recognized domain methods, and a
continuously-updated academic knowledge base into one evidence-backed,
risk-disclosed workflow.

## Installation

```bash
git clone https://github.com/dungnotull/ancient-costume-mural-reconstruction.git
cd ancient-costume-mural-reconstruction
pip install -r requirements.txt
# or, for the full dev tooling:
pip install -e ".[dev]"
```

Install the skill files into `~/.claude/skills/` or use them in-place via the
project `CLAUDE.md`.

## Quick Start

```bash
/ancient-costume-mural-reconstruction Reconstruct the court robe depicted in Mogao Cave 220 (Tang dynasty) from the mural
```

The harness runs 6 steps in order: requirements → evidence → core analysis →
knowledge → synthesis → quality gate, then delivers a single report.

## Usage

Invoke the skill with any reconstruction query. Examples:

```text
/ancient-costume-mural-reconstruction Analyse a 1st-century AD Roman tunic from a wall painting
/ancient-costume-mural-reconstruction Compare the upper garment of Han vs Tang women in tomb murals; which is better supported?
/ancient-costume-mural-reconstruction Reconstruct a 4th-c. AD Coptic tunic where iconography is partial — assess confidence
/ancient-costume-mural-reconstruction Reconstruct a Sassanian royal robe from a damaged relief (sources offline)
```

### Analysis types

| Type | When to use |
|------|-------------|
| `combined` (default) | Full reconstruction: iconography + construction + materials + 3D |
| `iconography` | Garment-form reading only |
| `construction` | Pattern/seaming/draping focus |
| `materials` | Fiber/weave/dye focus |
| `3d` | 3D reconstruction proposal focus |
| `comparison` | Side-by-side comparison of two objects |

## Architecture

```
USER INPUT
    │
[main.md — ancient-costume-mural-reconstruction]
    │
├──► sub-gather-requirements  → structured requirements
├──► sub-evidence-collector   → evidence bundle (museum + academic)
├──► sub-core-analysis        → iconography → construction → materials → 3D
├──► sub-knowledge-updater    → Tier-labelled citations + crawl gaps
├──► sub-advisor              → risk-disclosed conclusion + evidence chain
    │
└──► [QUALITY GATE — main.md]
        ✓ U1–U6 universal + G1–G4 domain
        ✓ Disclosure before recommendation
        ✓ Output per declared template
```

See `PROJECT-detail.md` for the full architecture and sub-skill catalog.

### File structure

```
ancient-costume-mural-reconstruction/
├── CLAUDE.md                          # identity card
├── PROJECT-detail.md                  # full technical spec
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md
├── README.md                          # this file
├── SECOND-KNOWLEDGE-BRAIN.md          # living knowledge base
├── LICENSE  CONTRIBUTING.md  CODE_OF_CONDUCT.md  CHANGELOG.md
├── pyproject.toml  requirements.txt  .gitignore  progression.json
├── skills/
│   ├── main.md                        # harness orchestrator + quality gate
│   └── sub-*.md                       # 5 sub-skills
├── tools/
│   ├── knowledge_updater.py           # crawl pipeline (ArXiv/S2/Crossref/RSS)
│   ├── test_knowledge_updater.py      # unit tests
│   ├── run_test_scenarios.py          # scenario runner + structural validator
│   └── validate_project.py            # 8-File Contract validator
└── tests/
    ├── test-scenarios.md
    └── TEST_RESULTS.md
```

## Quality Gates

Universal gates **U1–U6** plus domain gates **G1–G4** (defined in
`skills/main.md`):

| Gate | Check |
|------|-------|
| U1 | ≥3 sources cited, ≥1 academic/authoritative |
| U2 | Disclosure/limitations before recommendation |
| U3 | Evidence hierarchy stated per source (Tier 1–4) |
| U4 | Language matches user preference |
| U5 | Output uses declared template |
| U6 | Every claim traceable to a source or flagged |
| G1 | Iconographic analysis performed |
| G2 | Construction & materials/dyes recovered |
| G3 | Evidence hierarchy stated (extant > iconographic > textual > ethnographic) |
| G4 | 3D reconstruction produced |

Graceful degradation has 5 levels (0–4) with explicit LIMITATION banners; a
gate that cannot pass after 2 retries is flagged as a limitation in the
output.

## Data Sources

- Museum/collection references (Met, V&A, British Museum, Louvre)
- Archaeological textile references (CTR, Coptic textile database, Tarim finds)
- Art-history iconography references (Dunhuang Academy, Getty)
- Pattern-cutting/period references
- Dye/material history references (Cardon, Sandberg compendia)
- Conservation references (AIC, ICOMOS, ICCROM, CIETA)
- Academic journals: Costume, Textile History, J. Archaeol. Sci., Antiquity,
  Fashion Theory

## Testing

```bash
# 8-File Contract + structural / content validation
python tools/validate_project.py
python tools/run_test_scenarios.py --validate

# End-to-end scenario simulation (all 5 scenarios)
python tools/run_test_scenarios.py --all

# Unit tests for the crawl pipeline
python tools/test_knowledge_updater.py

# Machine-readable report
python tools/run_test_scenarios.py --all --json report.json
```

All three must exit 0 (see `CONTRIBUTING.md`). See `tests/test-scenarios.md`
for the 5 end-to-end scenarios and `tests/TEST_RESULTS.md` for results.

## Knowledge Base

`SECOND-KNOWLEDGE-BRAIN.md` is the living knowledge base, updated by
`tools/knowledge_updater.py`. It seeds verified Tier-1/2 references and
authoritative institutional URLs; the pipeline enriches it weekly with new
academic papers (ArXiv, Semantic Scholar, Crossref) and news (RSS).

```bash
python tools/knowledge_updater.py --dry-run            # preview new entries
python tools/knowledge_updater.py                       # full crawl + append
python tools/knowledge_updater.py --news-only           # RSS only
python tools/knowledge_updater.py --keywords "Coptic tunic" "dye HPLC"
```

Cron (documented in `CLAUDE.md`):

```cron
# Weekly academic update (Mondays 08:00)
0 8 * * 1 python tools/knowledge_updater.py >> logs/knowledge_update.log 2>&1
# Daily news update (07:00)
0 7 * * * python tools/knowledge_updater.py --news-only >> logs/knowledge_news.log 2>&1
```

## Development

See `CONTRIBUTING.md`. Branch from `main`, use Conventional Commits, run all
validators before a PR, and keep `CHANGELOG.md` + `PROJECT-DEVELOPMENT-PHASE-
TRACKING.md` current. The skill standard lives at `D:\972026\SKILL-STANDARD.md`.

## Roadmap

- [x] Phase 0: Research & skill architecture
- [x] Phase 1: Core sub-skills (5)
- [x] Phase 2: Main harness + quality gates
- [x] Phase 3: Knowledge pipeline + tests + cron
- [x] Phase 4: Testing & validation
- [x] Phase 5: Integration & polish
- [x] Phase 6: Open-source hardening — **PRODUCTION READY v1.1.0**

## Contributing

Contributions are welcome — domain expertise, new evidence sources, code
hardening, tests, and docs. See `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.
All claims must cite a Tier 1–4 source with a DOI/URL; limitations must be
disclosed.

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

- Centre for Textile Research (CTR), University of Copenhagen
- The Met, V&A, and British Museum open collections
- The costume, textile-history, and archaeological-science communities whose
  peer-reviewed work feeds the knowledge pipeline

## Citation

```bibtex
@software{ancient-costume-mural-reconstruction,
  title  = {ancient-costume-mural-reconstruction: Ancient Costume Reconstruction via Murals/Statues},
  author = {dungnotull},
  year   = {2026},
  version= {1.1.0},
  url    = {https://github.com/dungnotull/ancient-costume-mural-reconstruction},
  license= {MIT}
}
```