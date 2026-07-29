"""
test_knowledge_updater.py — Skill 240: ancient-costume-mural-reconstruction

Unit tests for tools/knowledge_updater.py covering:
  * SHA-256 dedup hashing (case/whitespace insensitive, DOI normalization)
  * Composite scoring (recency + relevance + citations, monotonicity)
  * Entry formatting (markdown schema, required fields)
  * Dedup against an existing brain file
  * Config dataclass defaults + JSON override
  * CLI argument parsing and pipeline wiring (offline, sources mocked)

Run:
    python -m unittest tools.test_knowledge_updater -v
or:
    python tools/test_knowledge_updater.py
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

# Make `tools` importable as a package-less path.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import knowledge_updater as ku  # noqa: E402


class TestComputeHash(unittest.TestCase):
    def test_stable_for_same_identifier(self):
        self.assertEqual(
            ku.compute_hash("https://doi.org/10.1234/x"),
            ku.compute_hash("https://doi.org/10.1234/x"),
        )

    def test_distinct_identifiers_hash_differently(self):
        self.assertNotEqual(
            ku.compute_hash("https://doi.org/10.1234/x"),
            ku.compute_hash("https://doi.org/10.1234/y"),
        )

    def test_whitespace_insensitive(self):
        self.assertEqual(
            ku.compute_hash("  https://doi.org/10.1234/x  "),
            ku.compute_hash("https://doi.org/10.1234/x"),
        )

    def test_case_insensitive(self):
        self.assertEqual(
            ku.compute_hash("HTTPS://DOI.ORG/10.1234/X"),
            ku.compute_hash("https://doi.org/10.1234/x"),
        )


class TestNormalizeDoi(unittest.TestCase):
    def test_strips_resolver_prefix(self):
        self.assertEqual(
            ku._normalize_doi("https://doi.org/10.1234/abc"),
            "10.1234/abc",
        )
        self.assertEqual(
            ku._normalize_doi("http://doi.org/10.1234/abc"),
            "10.1234/abc",
        )

    def test_passes_through_plain_doi(self):
        self.assertEqual(ku._normalize_doi("10.1234/abc"), "10.1234/abc")


class TestScoring(unittest.TestCase):
    def setUp(self):
        self.config = ku.get_default_config()
        self.now = datetime(2026, 7, 13)
        self.kws = self.config.keywords

    def _entry(self, **overrides):
        defaults = dict(
            title="ancient costume reconstruction mural iconography",
            authors=["A"],
            year=2026,
            venue="V",
            doi_or_url="https://doi.org/10.1/x",
            abstract="mural statue iconography garment archaeological dye history",
            published_date=self.now - timedelta(days=10),
            citation_count=50,
            source="crossref",
            tier=2,
        )
        defaults.update(overrides)
        return ku.PaperEntry(**defaults)

    def test_score_in_zero_to_ten(self):
        s = ku.score_entry(self._entry(), self.kws, self.now, self.config)
        self.assertGreaterEqual(s, 0.0)
        self.assertLessEqual(s, 10.0)

    def test_recent_beats_old(self):
        recent = self._entry(published_date=self.now - timedelta(days=10))
        old = self._entry(published_date=self.now - timedelta(days=700))
        sr = ku.score_entry(recent, self.kws, self.now, self.config)
        so = ku.score_entry(old, self.kws, self.now, self.config)
        self.assertGreater(sr, so)

    def test_more_citations_scores_higher(self):
        low = self._entry(citation_count=0)
        high = self._entry(citation_count=500)
        sl = ku.score_entry(low, self.kws, self.now, self.config)
        sh = ku.score_entry(high, self.kws, self.now, self.config)
        self.assertGreater(sh, sl)

    def test_missing_published_date_zero_recency(self):
        e = self._entry(published_date=None)
        s = ku.score_entry(e, self.kws, self.now, self.config)
        self.assertGreaterEqual(s, 0.0)

    def test_irrelevant_entry_scores_lower_than_relevant(self):
        relevant = self._entry(
            title="ancient costume reconstruction",
            abstract="mural statue iconography garment archaeological dye history",
        )
        irrelevant = self._entry(title="quantum computing", abstract="neural network transformer")
        sr = ku.score_entry(relevant, self.kws, self.now, self.config)
        si = ku.score_entry(irrelevant, self.kws, self.now, self.config)
        self.assertGreater(sr, si)


class TestFormatEntry(unittest.TestCase):
    def test_format_contains_required_fields(self):
        entry = ku.PaperEntry(
            title="T", authors=["A B"], year=2026, venue="Costume",
            doi_or_url="https://doi.org/10.1/xx", abstract="ab",
            published_date=datetime(2026, 1, 1), citation_count=3,
            source="crossref", tier=2,
        )
        out = ku.format_entry(entry, 7.5)
        for needle in ["### ", "**Authors:**", "**Year:**", "**Venue:**",
                       "**DOI/URL:**", "**Tier:**", "**Relevance Score:** 7.5",
                       "**Key Finding:**", "T", "A B", "Costume", "https://doi.org/10.1/xx"]:
            self.assertIn(needle, out, "missing %r in formatted entry" % needle)


class TestLoadExistingHashes(unittest.TestCase):
    def test_finds_doi_urls_in_brain_text(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
            fh.write("# brain\n- **DOI/URL:** https://doi.org/10.1/a\n- **DOI/URL:** 10.1/b\n")
            path = Path(fh.name)
        try:
            hashes = ku.load_existing_hashes(path)
            self.assertEqual(len(hashes), 2)
            self.assertIn(ku.compute_hash(ku._normalize_doi("https://doi.org/10.1/a")), hashes)
            self.assertIn(ku.compute_hash(ku._normalize_doi("10.1/b")), hashes)
        finally:
            os.unlink(path)

    def test_missing_file_returns_empty_set(self):
        self.assertEqual(ku.load_existing_hashes(Path("does-not-exist.md")), set())


class TestAppendToBrain(unittest.TestCase):
    def _write_brain(self, path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

    def test_dedup_skips_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            brain = Path(tmp) / "brain.md"
            self._write_brain(brain, "# brain\n\n## 7. Knowledge Update Log\n")
            cfg = ku.get_default_config()
            cfg.brain_path = str(brain)
            cfg.backup_brain_before_write = False
            entry = ku.PaperEntry(
                title="T", authors=["A"], year=2026, venue="V",
                doi_or_url="https://doi.org/10.1/new", abstract="ancient costume",
                published_date=datetime(2026, 7, 1), citation_count=10,
                source="crossref", tier=2,
            )
            n_appended, appended = ku.append_to_brain([entry], cfg, dry_run=True)
            self.assertEqual(n_appended, 1)
            self.assertEqual(len(appended), 1)
            # Run again: now the entry is in `existing` because we added its hash
            # but the file was not written (dry-run). A second dry-run after a real
            # append must skip it.
            ku.append_to_brain([entry], cfg, dry_run=False)
            n2, _ = ku.append_to_brain([entry], cfg, dry_run=True)
            self.assertEqual(n2, 0)

    def test_empty_identifier_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            brain = Path(tmp) / "brain.md"
            self._write_brain(brain, "# brain\n\n## 7. Knowledge Update Log\n")
            cfg = ku.get_default_config()
            cfg.brain_path = str(brain)
            cfg.backup_brain_before_write = False
            entry = ku.PaperEntry(
                title="T", authors=["A"], year=2026, venue="V",
                doi_or_url="", abstract="x",
                published_date=datetime(2026, 7, 1), citation_count=0,
                source="crossref", tier=2,
            )
            n, appended = ku.append_to_brain([entry], cfg, dry_run=True)
            self.assertEqual(n, 0)
            self.assertEqual(appended, [])

    def test_missing_brain_returns_zero(self):
        cfg = ku.get_default_config()
        cfg.brain_path = str(Path("nope-does-not-exist.md"))
        n, appended = ku.append_to_brain([], cfg, dry_run=True)
        self.assertEqual(n, 0)


class TestConfig(unittest.TestCase):
    def test_defaults_populated(self):
        cfg = ku.get_default_config()
        self.assertTrue(cfg.keywords)
        self.assertGreater(cfg.max_results_per_source, 0)
        self.assertAlmostEqual(cfg.scoring.recency + cfg.scoring.keyword_relevance + cfg.scoring.citation_count, 1.0)

    def test_from_json_file_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "cfg.json"
            p.write_text('{"keywords": ["x"], "max_new_entries_per_run": 3, '
                         '"scoring": {"recency": 0.5, "keyword_relevance": 0.3, "citation_count": 0.2}}',
                         encoding="utf-8")
            cfg = ku.KnowledgeConfig.from_json_file(p)
            self.assertEqual(cfg.keywords, ["x"])
            self.assertEqual(cfg.max_new_entries_per_run, 3)
            self.assertEqual(cfg.scoring.recency, 0.5)


class TestArgParsing(unittest.TestCase):
    def test_news_only_and_academic_only_mutually_exclusive(self):
        with self.assertRaises(SystemExit):
            ku.main(["--news-only", "--academic-only"])

    def test_resolve_config_keywords_override(self):
        args = ku.build_arg_parser().parse_args(["--keywords", "alpha", "beta"])
        cfg = ku.resolve_config(args)
        self.assertEqual(cfg.keywords, ["alpha", "beta"])


class TestPipelineWiring(unittest.TestCase):
    """Offline pipeline test: all fetchers mocked so no network is required."""

    def _entry(self, title="ancient costume reconstruction", doi="https://doi.org/10.1/wired"):
        return ku.PaperEntry(
            title=title, authors=["A"], year=2026, venue="V",
            doi_or_url=doi, abstract="mural statue iconography garment dye",
            published_date=datetime(2026, 7, 1), citation_count=5,
            source="crossref", tier=2,
        )

    def test_run_pipeline_appends_when_fetchers_mocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            brain = Path(tmp) / "brain.md"
            brain.write_text("# brain\n\n## 7. Knowledge Update Log\n", encoding="utf-8")
            cfg = ku.get_default_config()
            cfg.brain_path = str(brain)
            cfg.backup_brain_before_write = False
            with mock.patch.object(ku, "fetch_arxiv", return_value=[self._entry("a1", "https://doi.org/10.1/a1")]), \
                 mock.patch.object(ku, "fetch_semantic_scholar", return_value=[self._entry("a2", "https://doi.org/10.1/a2")]), \
                 mock.patch.object(ku, "fetch_crossref", return_value=[self._entry("a3", "https://doi.org/10.1/a3")]), \
                 mock.patch.object(ku, "fetch_rss", return_value=[]), \
                 mock.patch.object(ku.time, "sleep", return_value=None):
                n = ku.run_pipeline(cfg, dry_run=False, news_only=False, academic_only=False)
            self.assertEqual(n, 3)
            text = brain.read_text(encoding="utf-8")
            self.assertIn("a1", text)
            self.assertIn("a2", text)
            self.assertIn("a3", text)
            # Second run must dedup everything.
            with mock.patch.object(ku, "fetch_arxiv", return_value=[self._entry("a1", "https://doi.org/10.1/a1")]), \
                 mock.patch.object(ku, "fetch_semantic_scholar", return_value=[]), \
                 mock.patch.object(ku, "fetch_crossref", return_value=[]), \
                 mock.patch.object(ku, "fetch_rss", return_value=[]), \
                 mock.patch.object(ku.time, "sleep", return_value=None):
                n2 = ku.run_pipeline(cfg, dry_run=False, news_only=False, academic_only=False)
            self.assertEqual(n2, 0)
            text = brain.read_text(encoding="utf-8")
            self.assertEqual(text.count("**DOI/URL:** https://doi.org/10.1/a1"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)