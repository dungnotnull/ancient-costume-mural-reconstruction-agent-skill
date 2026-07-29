# Changelog

All notable changes to **ancient-costume-mural-reconstruction** are documented
in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — 2026-07-13

### Added
- Production-grade `tools/knowledge_updater.py` rewrite: `KnowledgeConfig`
  dataclass, optional JSON config file, Crossref source alongside ArXiv,
  Semantic Scholar, and RSS; exponential-backoff retry, `User-Agent` header,
  brain backup-before-write, structured `logging` to `logs/`, DOI
  normalization for dedup, `--academic-only` / `--config` / `--max-new` /
  `--brain` / `--verbose` CLI flags.
- `tools/validate_project.py` — 8-File Contract validator per
  `SKILL-STANDARD.md` (exit 0 on success, JSON report optional).
- `tools/run_test_scenarios.py` rewrite — domain-aware `ScenarioRunner` with
  5 ancient-costume scenarios (Dunhuang Tang robe, minimal-input, Han vs
  Tang comparison, fragmentary Coptic textile, degraded-mode Sassanian),
  gate-evidence mapping, and optional JSON report.
- `tools/test_knowledge_updater.py` rewrite — `unittest` framework, 22 tests
  covering hashing, DOI normalization, scoring monotonicity, formatting,
  dedup, config overrides, CLI parsing, and offline pipeline wiring.
- Open-source scaffolding: `LICENSE` (MIT), `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `pyproject.toml`, `progression.json`.
- Deeper domain content across all sub-skills: iconography protocol,
  construction/material/dye recovery, evidence hierarchy decision tree,
  3D reconstruction guidance, verdict rubric.
- More seeded DOI-cited references in `SECOND-KNOWLEDGE-BRAIN.md`.

### Changed
- `requirements.txt` — pinned, deduplicated, `feedparser`/`requests`/
  `python-dateutil` + dev tooling (`pytest`).
- `README.md` — full open-source sections per `SKILL-STANDARD.md`.
- `CLAUDE.md`, `PROJECT-detail.md` — reflect v1.1.0 and new tooling.
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — adds Phase 6 (Open-Source
  Hardening) and marks every task across all phases 100% complete.
- `tests/test-scenarios.md` — concrete ancient-costume scenarios with
  gate-coverage matrix.
- `tests/TEST_RESULTS.md` — updated results for the upgraded suite.

### Fixed
- Dedup now normalizes DOI resolver prefixes before hashing so the same
  reference captured as `https://doi.org/10.x` and `10.x` no longer
  duplicates.
- Brain append is now idempotent and writes a timestamped backup before
  modification.

## [1.0.0] — 2026-07-10

### Added
- Initial release: 5 sub-skills + `main.md` harness, `SECOND-KNOWLEDGE-BRAIN.md`,
  `tools/knowledge_updater.py`, `tools/test_knowledge_updater.py`,
  `tools/run_test_scenarios.py`, `tests/test-scenarios.md`,
  `tests/TEST_RESULTS.md`, CLAUDE.md, PROJECT-detail.md,
  PROJECT-DEVELOPMENT-PHASE-TRACKING.md, README.md, requirements.txt,
  .gitignore. Phases 0–5 marked complete.