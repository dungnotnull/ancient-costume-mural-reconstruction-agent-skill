# TEST_RESULTS.md — Skill 240: ancient-costume-mural-reconstruction

## Validation Summary

| Suite | Command | Checks | Result |
|-------|---------|--------|--------|
| 8-File Contract validator | `python tools/validate_project.py` | required files + structure + content | PASS |
| Structural & content validator | `python tools/run_test_scenarios.py --validate` | full structural suite | PASS |
| End-to-end scenario simulation | `python tools/run_test_scenarios.py --all` | 5 scenarios + gate coverage | PASS |
| Knowledge-updater unit tests | `python tools/test_knowledge_updater.py` | 22 tests (unittest) | PASS |

**Overall: PRODUCTION READY v1.1.0 — all validators pass (exit 0).**

## 8-File Contract (`validate_project.py`)

Verifies the contract defined in `D:\972026\SKILL-STANDARD.md`:

- Required files present (CLAUDE.md, PROJECT-detail.md,
  PROJECT-DEVELOPMENT-PHASE-TRACKING.md, README.md, SECOND-KNOWLEDGE-BRAIN.md,
  LICENSE, requirements.txt, pyproject.toml, skills/main.md, tools/*,
  tests/*).
- Every `skills/*.md` has frontmatter `name` + `description` and the required
  sections (Role & Persona, Workflow, Output Format, Quality Gates).
- `skills/main.md` contains the Quality Gate table, graceful-degradation block,
  pre-flight language detection, limitation banner, all gates U1–U6 + G1–G4,
  and all four verdict categories.
- `tools/knowledge_updater.py` defines `KnowledgeConfig`, dedup hashing,
  scoring, dry-run, backup-before-write.
- `PROJECT-detail.md` has the `Idea (Vietnamese)` section (verbatim).
- `README.md` has the required public-doc sections.
- `SECOND-KNOWLEDGE-BRAIN.md` has evidence tiers, ≥1 distinct DOI reference,
  ≥6 reference entries, and the required sections (§1, §4, §6, §7).
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` has ≥6 `100%` markers and all phases.

Result: **PASS** — exit 0.

## Knowledge-updater unit tests (`test_knowledge_updater.py`)

`unittest` framework, 22 tests:

- `TestComputeHash` — stable, distinct, whitespace- and case-insensitive
  SHA-256 dedup hashing.
- `TestNormalizeDoi` — strips `https://doi.org/` resolver prefix.
- `TestScoring` — 0–10 range, recent > old, more-citations > fewer,
  missing-date zero recency, relevant > irrelevant.
- `TestFormatEntry` — markdown schema with all required fields.
- `TestLoadExistingHashes` — finds DOI/URL hashes in brain text, missing-file
  → empty set.
- `TestAppendToBrain` — dedup skips existing, empty identifier skipped,
  missing brain → zero appended; idempotent after a real append.
- `TestConfig` — defaults populated, JSON-file overrides.
- `TestArgParsing` — mutually-exclusive flags, keyword override.
- `TestPipelineWiring` — offline pipeline with mocked fetchers appends and
  dedups correctly.

Result: **PASS** — 22/22 tests OK.

## Scenario simulation (`run_test_scenarios.py --all`)

Five offline scenarios (mirrors `tests/test-scenarios.md`):

| # | Scenario | Expected verdict | Result |
|---|----------|------------------|--------|
| 1 | Standard — Tang court robe (Mogao Cave 220) | Evidence-Based Reconstruction | PASS |
| 2 | Minimal-input — 1st-c. AD Roman tunic | Plausible (interpretive) | PASS |
| 3 | Comparison — Han vs Tang women's upper garment | Evidence-Based Reconstruction | PASS |
| 4 | Risk/conflict — fragmentary Coptic burial textile | Speculative | PASS |
| 5 | Degraded-mode — Sassanian royal robe, sources offline | Inconclusive | PASS |

Gate coverage: all universal gates U1–U6 and all domain gates G1–G4 are
exercised across the scenarios (see the coverage matrix in
`tests/test-scenarios.md`). All four verdict categories are covered.

Result: **PASS** — 5/5 scenarios passed.

## Reproducing

```bash
python tools/validate_project.py
python tools/run_test_scenarios.py --all
python tools/test_knowledge_updater.py
```

All three exit 0. A machine-readable report is available via:

```bash
python tools/run_test_scenarios.py --all --json report.json
python tools/validate_project.py --json contract-report.json
```

## Notes on the knowledge pipeline

`tools/knowledge_updater.py` is production-grade and fully tested offline. The
knowledge base is seeded with verified Tier-1/2 references and authoritative
institutional URLs; running the pipeline (`python tools/knowledge_updater.py`)
enriches it with new academic + news entries. Per the project constraint, no
real network crawl was executed during this validation run; all fetchers are
covered by mocked offline tests.