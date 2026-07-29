#!/usr/bin/env python3
"""
scripts/setup.py — Skill 240: ancient-costume-mural-reconstruction

Project setup and initialization script. Creates directory structure,
initializes configuration files, and validates the installation.
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProjectSetup:
    """Project setup and initialization."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.logs_dir = project_root / "logs"
        self.assets_dir = project_root / "assets"
        self.references_dir = project_root / "references"
        self.scripts_dir = project_root / "scripts"

    def create_directories(self) -> bool:
        """Create required directory structure."""
        logger.info("Creating directory structure...")

        directories = [
            self.config_dir,
            self.logs_dir,
            self.assets_dir / "schemas" / "tool_inputs",
            self.assets_dir / "schemas" / "tool_outputs",
            self.references_dir / "iconography",
            self.references_dir / "construction",
            self.references_dir / "materials",
            self.references_dir / "3d_reference",
            self.references_dir / "academic",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created: {directory.relative_to(self.project_root)}")

        return True

    def create_env_file(self) -> bool:
        """Create .env file from example."""
        env_example = self.project_root / "config" / ".env.example"
        env_file = self.project_root / ".env"

        if env_example.exists() and not env_file.exists():
            shutil.copy(env_example, env_file)
            logger.info(f"Created .env from example")
        elif not env_example.exists():
            # Create default .env
            default_env = """# Ancient Costume Mural Reconstruction - Environment Configuration

# LLM Configuration
ACMR_LLM__MODEL=claude-sonnet-4-5
ACMR_LLM__TEMPERATURE=0.2
ACMR_LLM__MAX_OUTPUT_TOKENS=4096

# Harness Configuration
ACMR_HARNESS__DEFAULT_LANGUAGE=en
ACMR_HARNESS__MAX_CLARIFYING_QUESTIONS=2
ACMR_HARNESS__MAX_GATE_RETRIES=2

# Features
ACMR_FEATURES__ENABLE_KNOWLEDGE_CRAWL=true
ACMR_FEATURES__ENABLE_ROUTER_CHAIN_OF_THOUGHT=true
ACMR_FEATURES__ENABLE_3D_RECONSTRUCTION=true

# Logging
ACMR_LOGGING__LEVEL=INFO
ACMR_LOGGING__LOG_DIR=logs
"""
            env_file.write_text(default_env)
            logger.info(f"Created default .env file")

        return True

    def create_config_file(self) -> bool:
        """Create default config file."""
        config_file = self.config_dir / "config.json"

        if config_file.exists():
            logger.info(f"Config file already exists: {config_file}")
            return True

        default_config = {
            "app_name": "ancient-costume-mural-reconstruction",
            "version": "2.0.0",
            "environment": "development",
            "llm": {
                "model": "claude-sonnet-4-5",
                "temperature": 0.2,
                "max_output_tokens": 4096,
            },
            "harness": {
                "default_language": "en",
                "max_clarifying_questions": 2,
                "max_gate_retries": 2,
            },
            "knowledge_pipeline": {
                "max_results_per_source": 10,
                "backup_brain_before_write": True,
            },
            "features": {
                "enable_knowledge_crawl": True,
                "enable_3d_reconstruction": True,
            },
            "logging": {
                "level": "INFO",
                "log_dir": "logs",
            }
        }

        config_file.write_text(json.dumps(default_config, indent=2))
        logger.info(f"Created config file: {config_file}")

        return True

    def initialize_crawl_gaps(self) -> bool:
        """Initialize empty crawl gaps queue."""
        gaps_file = self.config_dir / "crawl_gaps.json"

        if not gaps_file.exists():
            gaps_file.write_text(json.dumps([], indent=2))
            logger.info(f"Initialized crawl gaps queue: {gaps_file}")

        return True

    def validate_installation(self) -> bool:
        """Validate that required files exist."""
        logger.info("Validating installation...")

        required_files = [
            "CLAUDE.md",
            "PROJECT-detail.md",
            "PROJECT-DEVELOPMENT-PHASE-TRACKING.md",
            "README.md",
            "SECOND-KNOWLEDGE-BRAIN.md",
            "SKILL.md",
            "skills/main.md",
            "skills/sub-router.md",
            "skills/sub-gather-requirements.md",
            "skills/sub-evidence-collector.md",
            "skills/sub-core-analysis.md",
            "skills/sub-knowledge-updater.md",
            "skills/sub-advisor.md",
            "skills/sub-iconography-analyzer.md",
            "skills/sub-construction-expert.md",
            "skills/sub-materials-specialist.md",
            "skills/sub-3d-architect.md",
            "tools/agent_tools.py",
            "tools/knowledge_updater.py",
            "tools/validate_project.py",
            "tools/run_test_scenarios.py",
            "tools/test_knowledge_updater.py",
            "assets/skill_manifest.json",
            "assets/tool_definitions.json",
            "config/settings.py",
        ]

        missing = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing.append(file_path)

        if missing:
            logger.error(f"Missing required files: {missing}")
            return False

        logger.info("All required files present")
        return True

    def print_summary(self) -> None:
        """Print setup summary."""
        logger.info("=" * 60)
        logger.info("Setup Complete!")
        logger.info("=" * 60)
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Config directory: {self.config_dir}")
        logger.info(f"Logs directory: {self.logs_dir}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Review and edit .env for your environment")
        logger.info("2. Review config/config.json for harness settings")
        logger.info("3. Run: python -m tools.validate_project")
        logger.info("4. Run: python -m tools.run_test_scenarios --all")
        logger.info("5. Run: python tools/test_knowledge_updater.py")
        logger.info("=" * 60)


def main() -> int:
    """Main setup entry point."""
    parser = argparse.ArgumentParser(
        description="Set up ancient-costume-mural-reconstruction project"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Project root directory"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip installation validation"
    )

    args = parser.parse_args()
    setup = ProjectSetup(args.project_root)

    # Run setup steps
    success = True
    success &= setup.create_directories()
    success &= setup.create_env_file()
    success &= setup.create_config_file()
    success &= setup.initialize_crawl_gaps()

    if not args.skip_validation:
        success &= setup.validate_installation()

    if success:
        setup.print_summary()
        return 0
    else:
        logger.error("Setup failed - see errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
