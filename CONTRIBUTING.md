# Contributing to ancient-costume-mural-reconstruction

Thank you for your interest in improving this skill. This project is a
**Claude Code skill** (a markdown harness + supporting Python tooling) for
**Ancient Costume Reconstruction & Archaeological Textile History**. All
contributions are welcome — domain expertise, new evidence sources, code
hardening, tests, and documentation.

## Code of Conduct

By participating you agree to uphold the standards in `CODE_OF_CONDUCT.md`.
Please be respectful, evidence-oriented, and constructive.

## How to contribute

### 1. Domain content & evidence

The heart of this skill is evidence discipline. If you add or amend a claim,
you **must**:

- Cite a Tier 1–4 source (see `SECOND-KNOWLEDGE-BRAIN.md` §2 for the tier
  definitions). Prefer Tier 1–2 (peer-reviewed, official standards).
- Record the DOI or stable URL, the authors, year, and venue.
- Flag any limitation or interpretive assumption in the Disclosure section.

### 2. Code (Python tools)

- Target Python 3.10+.
- Use type hints, dataclasses where appropriate, and `logging` (no bare
  `print` in library code; CLI entry points may print a final summary).
- Keep functions pure and testable; mock network in tests.
- Run the full validation gate before opening a PR:

```bash
python tools/validate_project.py
python tools/test_knowledge_updater.py
python tools/run_test_scenarios.py --all
```

All three must exit 0.

### 3. Skill markdown (`skills/*.md`)

Every sub-skill file **must** keep the required sections: frontmatter
(`name`, `description`), `Role & Persona`, `Workflow`, `Output Format`,
`Quality Gates`. Do not remove quality gates or the graceful-degradation
protocol — they are mandatory per `D:\972026\SKILL-STANDARD.md`.

### 4. Tests

- Add or update `tests/test-scenarios.md` whenever you change harness
  behaviour.
- Update `tests/TEST_RESULTS.md` with the new run results.
- Add unit tests to `tools/test_knowledge_updater.py` for any new
  `knowledge_updater` logic.

## Pull request checklist

- [ ] `python tools/validate_project.py` exits 0
- [ ] `python tools/test_knowledge_updater.py` exits 0
- [ ] `python tools/run_test_scenarios.py --all` exits 0
- [ ] New claims have a Tier-labelled citation with DOI/URL
- [ ] Limitations/assumptions are disclosed
- [ ] `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` reflects the change
- [ ] `CHANGELOG.md` has an entry under `[Unreleased]`

## Branching & commits

- Branch from `main`: `feat/<short-slug>`, `fix/<short-slug>`,
  `docs/<short-slug>`.
- Use [Conventional Commits](https://www.conventionalcommits.org/):
  `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.

## Releasing

Maintainers cut releases by tagging `vMAJOR.MINOR.PATCH` and updating the
`CHANGELOG.md`. The skill version lives in `pyproject.toml`,
`skills/main.md`, and `CLAUDE.md`.

## Attribution

Contributors will be credited in `CHANGELOG.md`. Significant domain
contributions may also be acknowledged in `README.md`.