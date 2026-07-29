#!/usr/bin/env python3
"""
scripts/ci_validate.py — Skill 240: ancient-costume-mural-reconstruction

CI/CD validation script. Runs all project checks and returns appropriate
exit codes for CI pipelines.
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class CIValidator:
    """CI/CD validation runner."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: List[Dict] = []

    def run_check(self, name: str, command: List[str], cwd: Path = None) -> bool:
        """Run a single check and record results."""
        logger.info(f"Running: {name}")

        start = datetime.now(timezone.utc)
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )

            duration = (datetime.now(timezone.utc) - start).total_seconds()
            passed = result.returncode == 0

            self.results.append({
                "name": name,
                "passed": passed,
                "duration_seconds": duration,
                "returncode": result.returncode,
                "stdout": result.stdout[:1000] if result.stdout else "",
                "stderr": result.stderr[:1000] if result.stderr else ""
            })

            if passed:
                logger.info(f"✓ {name} passed ({duration:.1f}s)")
            else:
                logger.error(f"✗ {name} failed (exit code {result.returncode})")

            return passed

        except subprocess.TimeoutExpired:
            logger.error(f"✗ {name} timed out")
            self.results.append({
                "name": name,
                "passed": False,
                "duration_seconds": 300,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out"
            })
            return False
        except Exception as e:
            logger.error(f"✗ {name} error: {e}")
            return False

    def validate_project_structure(self) -> bool:
        """Validate 8-file contract."""
        return self.run_check(
            "8-File Contract Validation",
            [sys.executable, "-m", "tools.validate_project", "--report"]
        )

    def run_knowledge_updater_tests(self) -> bool:
        """Run knowledge updater unit tests."""
        return self.run_check(
            "Knowledge Updater Tests",
            [sys.executable, "tools/test_knowledge_updater.py", "-v"]
        )

    def run_test_scenarios(self) -> bool:
        """Run end-to-end test scenarios."""
        return self.run_check(
            "Test Scenarios",
            [sys.executable, "-m", "tools.run_test_scenarios", "--all"]
        )

    def check_skill_manifest(self) -> bool:
        """Validate skill manifest JSON."""
        manifest_path = self.project_root / "assets" / "skill_manifest.json"
        if not manifest_path.exists():
            logger.error("skill_manifest.json not found")
            return False

        try:
            with open(manifest_path) as f:
                manifest = json.load(f)

            required_keys = ["version", "skills"]
            if not all(key in manifest for key in required_keys):
                logger.error(f"skill_manifest missing keys: {required_keys}")
                return False

            logger.info(f"skill_manifest.json valid (version {manifest['version']}, {len(manifest['skills'])} skills)")
            return True

        except Exception as e:
            logger.error(f"skill_manifest.json invalid: {e}")
            return False

    def check_tool_definitions(self) -> bool:
        """Validate tool definitions JSON."""
        tool_defs_path = self.project_root / "assets" / "tool_definitions.json"
        if not tool_defs_path.exists():
            logger.error("tool_definitions.json not found")
            return False

        try:
            with open(tool_defs_path) as f:
                tool_defs = json.load(f)

            required_keys = ["version", "tools"]
            if not all(key in tool_defs for key in required_keys):
                logger.error(f"tool_definitions missing keys: {required_keys}")
                return False

            logger.info(f"tool_definitions.json valid (version {tool_defs['version']}, {len(tool_defs['tools'])} tools)")
            return True

        except Exception as e:
            logger.error(f"tool_definitions.json invalid: {e}")
            return False

    def check_skill_files(self) -> bool:
        """Validate all skill files have required frontmatter."""
        skills_dir = self.project_root / "skills"
        if not skills_dir.exists():
            logger.error("skills/ directory not found")
            return False

        required_skills = [
            "main.md",
            "sub-router.md",
            "sub-gather-requirements.md",
            "sub-evidence-collector.md",
            "sub-core-analysis.md",
            "sub-knowledge-updater.md",
            "sub-advisor.md",
            "sub-iconography-analyzer.md",
            "sub-construction-expert.md",
            "sub-materials-specialist.md",
            "sub-3d-architect.md"
        ]

        all_valid = True
        for skill_file in required_skills:
            skill_path = skills_dir / skill_file
            if not skill_path.exists():
                logger.error(f"Skill file missing: {skill_file}")
                all_valid = False
                continue

            try:
                content = skill_path.read_text()
                if not content.startswith("---"):
                    logger.error(f"Skill missing frontmatter: {skill_file}")
                    all_valid = False
                else:
                    # Check for required frontmatter keys
                    if "name:" not in content[:200] or "description:" not in content[:500]:
                        logger.error(f"Skill frontmatter incomplete: {skill_file}")
                        all_valid = False

            except Exception as e:
                logger.error(f"Error reading skill file {skill_file}: {e}")
                all_valid = False

        if all_valid:
            logger.info(f"All {len(required_skills)} skill files valid")

        return all_valid

    def generate_report(self, output_path: Path = None) -> Dict:
        """Generate validation report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        total_duration = sum(r["duration_seconds"] for r in self.results)

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
                "total_duration_seconds": total_duration
            },
            "checks": self.results
        }

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to: {output_path}")

        return report

    def print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("CI VALIDATION SUMMARY")
        print("=" * 60)

        for result in self.results:
            status = "✓" if result["passed"] else "✗"
            print(f"{status} {result['name']} ({result['duration_seconds']:.1f}s)")

        print("-" * 60)

        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        print(f"Total: {passed}/{total} checks passed")

        if passed == total:
            print("Status: SUCCESS")
        else:
            print("Status: FAILED")

        print("=" * 60)


def main() -> int:
    """Main CI entry point."""
    parser = argparse.ArgumentParser(
        description="CI/CD validation for ancient-costume-mural-reconstruction"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Project root directory"
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Output JSON report path"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests (test scenarios)"
    )

    args = parser.parse_args()
    validator = CIValidator(args.project_root)

    # Run all checks
    all_passed = True
    all_passed &= validator.check_skill_manifest()
    all_passed &= validator.check_tool_definitions()
    all_passed &= validator.check_skill_files()
    all_passed &= validator.run_knowledge_updater_tests()
    all_passed &= validator.validate_project_structure()

    if not args.fast:
        all_passed &= validator.run_test_scenarios()

    # Generate report
    report = validator.generate_report(args.report)

    # Print summary
    validator.print_summary()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
