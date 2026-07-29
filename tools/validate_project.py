"""
validate_project.py — Skill 240: ancient-costume-mural-reconstruction

Validates the 8-File Contract defined in D:\\972026\\SKILL-STANDARD.md for this
skill project. It checks:

  1. Required files are present (CLAUDE.md, PROJECT-detail.md,
     PROJECT-DEVELOPMENT-PHASE-TRACKING.md, README.md, SECOND-KNOWLEDGE-BRAIN.md,
     requirements.txt, .gitignore, skills/main.md, sub-skills, tools/*, tests/*).
  2. Every skills/*.md has frontmatter with `name` and `description`.
  3. skills/main.md contains a Quality Gate table and graceful-degradation block.
  4. tools/knowledge_updater.py defines KNOWLEDGE_CONFIG (or KnowledgeConfig).
  5. PROJECT-detail.md contains the `Idea (Vietnamese)` section (verbatim origin).
  6. README.md contains the required public-doc sections.
  7. SECOND-KNOWLEDGE-BRAIN.md has the evidence tiers and a key-papers table.

Exit code 0 = all checks pass; non-zero on any violation.

Usage:
    python tools/validate_project.py
    python tools/validate_project.py --json report.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Optional

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

REQUIRED_FILES: List[str] = [
    "CLAUDE.md",
    "PROJECT-detail.md",
    "PROJECT-DEVELOPMENT-PHASE-TRACKING.md",
    "README.md",
    "SECOND-KNOWLEDGE-BRAIN.md",
    "requirements.txt",
    ".gitignore",
    "LICENSE",
    "pyproject.toml",
    "skills/main.md",
    "tools/knowledge_updater.py",
    "tools/test_knowledge_updater.py",
    "tools/run_test_scenarios.py",
    "tests/test-scenarios.md",
    "tests/TEST_RESULTS.md",
]

EXPECTED_SUBSKILLS = {
    "sub-gather-requirements",
    "sub-evidence-collector",
    "sub-core-analysis",
    "sub-knowledge-updater",
    "sub-advisor",
}

README_REQUIRED_SECTIONS = [
    "Overview", "Features", "Installation", "Usage", "Architecture",
    "Quality Gates", "Testing", "Knowledge Base", "License", "Citation",
]


@dataclass
class Check:
    label: str
    passed: bool
    detail: str = ""


def _read(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _frontmatter(text: str) -> Optional[str]:
    m = re.search(r"^---\s*\n(.*?\n)---", text, re.S)
    return m.group(1) if m else None


def run_validation() -> List[Check]:
    checks: List[Check] = []

    def require(cond: bool, label: str, detail: str = "") -> None:
        checks.append(Check(label, bool(cond), detail))

    # 1. File presence
    for rel in REQUIRED_FILES:
        require((ROOT / rel).exists(), f"file present: {rel}")

    # 2. Sub-skills
    subs = sorted(SKILLS_DIR.glob("sub-*.md"))
    stems = {p.stem for p in subs}
    require(stems == EXPECTED_SUBSKILLS, "sub-skill set", f"got {sorted(stems)}")
    require((SKILLS_DIR / "main.md").exists(), "skills/main.md present")
    for sub in subs:
        txt = sub.read_text(encoding="utf-8")
        fm = _frontmatter(txt)
        require(fm is not None, f"{sub.name}: frontmatter")
        if fm:
            require("name:" in fm and "description:" in fm, f"{sub.name}: name+description in frontmatter")
        for sec in ["Role & Persona", "Workflow", "Output Format", "Quality Gates"]:
            require(sec in txt, f"{sub.name}: section {sec}")

    # 3. main.md quality gates + degradation
    main_txt = _read("skills/main.md")
    require("Quality Gates" in main_txt, "main.md: Quality Gates section")
    require(re.search(r"Graceful Degradation", main_txt) is not None, "main.md: graceful degradation")
    require(re.search(r"Pre-Flight|language detection", main_txt, re.I) is not None,
            "main.md: pre-flight language detection")
    require(re.search(r"LIMITATION", main_txt, re.I) is not None, "main.md: limitation banner")
    for g in ["U1", "U2", "U3", "U4", "U5", "U6", "G1", "G2", "G3", "G4"]:
        require(g in main_txt, f"main.md: gate {g}")
    for v in ["Evidence-Based Reconstruction", "Plausible (interpretive)", "Speculative", "Inconclusive"]:
        require(v in main_txt, f"main.md: verdict {v}")

    # 4. knowledge_updater config
    ku = _read("tools/knowledge_updater.py")
    require("KnowledgeConfig" in ku or "KNOWLEDGE_CONFIG" in ku, "knowledge_updater: config class/const")
    require("compute_hash" in ku, "knowledge_updater: dedup hash")
    require("score_entry" in ku, "knowledge_updater: scoring")
    require("--dry-run" in ku, "knowledge_updater: dry-run flag")
    require("backup_brain_before_write" in ku, "knowledge_updater: backup-before-write")

    # 5. PROJECT-detail Idea (Vietnamese)
    pd = _read("PROJECT-detail.md")
    require("Idea (Vietnamese)" in pd, "PROJECT-detail: Idea (Vietnamese) section")
    require("Harness Architecture" in pd, "PROJECT-detail: harness architecture")
    require("Full Sub-Skill Catalog" in pd, "PROJECT-detail: sub-skill catalog")

    # 6. README sections
    readme = _read("README.md")
    for sec in README_REQUIRED_SECTIONS:
        require(sec in readme, f"README: section {sec}")

    # 7. Knowledge base
    brain = _read("SECOND-KNOWLEDGE-BRAIN.md")
    require("Tier 1" in brain and "Tier 4" in brain, "brain: evidence tiers")
    dois = set(re.findall(r"10\.\d{4,9}/[^\s|)]+", brain))
    ref_count = len(re.findall(r"\*\*DOI/URL:\*\*|\| .* \| .* \| .* \| .* \| .* \| .* \|", brain))
    require(len(dois) >= 1, "brain: >=1 distinct DOI reference", f"found {len(dois)}")
    require(ref_count >= 6, "brain: >=6 reference entries", f"found {ref_count}")
    for sec in ["## 1. Core Concepts & Frameworks",
                "## 4. Authoritative Data Sources",
                "## 6. Self-Update Protocol",
                "## 7. Knowledge Update Log"]:
        require(sec in brain, f"brain: section {sec}")

    # 8. PDPT completion markers
    pdpt = _read("PROJECT-DEVELOPMENT-PHASE-TRACKING.md")
    require(pdpt.count("100%") >= 6, "PDPT: >=6 100% markers", f"found {pdpt.count('100%')}")
    for phase in range(6):
        require(f"Phase {phase}" in pdpt, f"PDPT: Phase {phase} present")

    return checks


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="8-File Contract validator")
    parser.add_argument("--json", type=Path, default=None, help="Write JSON report to this path.")
    args = parser.parse_args(argv)

    checks = run_validation()
    passed = sum(1 for c in checks if c.passed)
    failed = len(checks) - passed
    total = len(checks)

    print("=" * 70)
    print("8-FILE CONTRACT VALIDATION — ancient-costume-mural-reconstruction")
    print("=" * 70)
    print(f"{passed}/{total} checks passed")
    if failed:
        print("Failures:")
        for c in checks:
            if not c.passed:
                print(f"  - FAIL {c.label}: {c.detail}")
    else:
        print("All checks passed.")
    print("=" * 70)

    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps({
            "passed": passed,
            "failed": failed,
            "total": total,
            "checks": [{"label": c.label, "passed": c.passed, "detail": c.detail} for c in checks],
        }, indent=2, ensure_ascii=False), encoding="utf-8")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())