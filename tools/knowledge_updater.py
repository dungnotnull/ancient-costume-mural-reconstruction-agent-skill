"""
knowledge_updater.py — Skill 240: ancient-costume-mural-reconstruction

Production-grade crawl pipeline for the SECOND-KNOWLEDGE-BRAIN.md living
knowledge base. Pulls academic papers (ArXiv, Semantic Scholar, Crossref) and
heritage-textile news (RSS), deduplicates by SHA-256 of DOI/URL, scores each
candidate (recency + keyword relevance + citation count), and appends the
highest-scoring new entries to SECOND-KNOWLEDGE-BRAIN.md under section 7.

Design notes
------------
* Pure stdlib + optional `requests` / `feedparser` / `python-dateutil`.
  Missing optional deps degrade gracefully (source skipped with a warning).
* Idempotent: a run that finds no new entries writes nothing.
* Safe writes: brain file is backed up to a timestamped sibling before append.
* Fully configurable via the KNOWLEDGE_CONFIG dataclass; override keywords /
  sources / limits from the CLI or from an optional JSON config file.

Usage
-----
    python tools/knowledge_updater.py                       # full crawl + append
    python tools/knowledge_updater.py --dry-run             # preview, no write
    python tools/knowledge_updater.py --news-only           # RSS only
    python tools/knowledge_updater.py --keywords "a" "b"    # override keywords
    python tools/knowledge_updater.py --config cfg.json    # override config
    python tools/knowledge_updater.py --academic-only       # skip RSS

Schedule (cron)
--------------
    # Weekly academic update (Mondays 08:00)
    0 8 * * 1 python tools/knowledge_updater.py >> logs/knowledge_update.log 2>&1
    # Daily news update (07:00)
    0 7 * * * python tools/knowledge_updater.py --news-only >> logs/knowledge_news.log 2>&1
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

try:
    import requests  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    requests = None  # type: ignore

try:
    import feedparser  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    feedparser = None  # type: ignore

try:
    from dateutil import parser as dateutil_parser  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    dateutil_parser = None  # type: ignore

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
BRAIN_PATH = PROJECT_ROOT / "SECOND-KNOWLEDGE-BRAIN.md"
LOG_DIR = PROJECT_ROOT / "logs"

USER_AGENT = (
    "ancient-costume-mural-reconstruction-knowledge-crawler/1.1 "
    "(+https://github.com/dungnotull/ancient-costume-mural-reconstruction)"
)

SOURCE_ARXIV = "arxiv"
SOURCE_SEMANTIC_SCHOLAR = "semantic_scholar"
SOURCE_CROSSREF = "crossref"
SOURCE_RSS = "rss"

TIER_MAPPING = {
    SOURCE_ARXIV: 2,
    SOURCE_SEMANTIC_SCHOLAR: 2,
    SOURCE_CROSSREF: 2,
    SOURCE_RSS: 4,
}

log = logging.getLogger("knowledge_updater")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class ScoringWeights:
    recency: float = 0.40
    keyword_relevance: float = 0.40
    citation_count: float = 0.20


@dataclass
class KnowledgeConfig:
    domain: str = "Ancient Costume Reconstruction & Archaeological Textile History"
    keywords: List[str] = field(default_factory=lambda: [
        "ancient costume reconstruction",
        "mural statue iconography garment",
        "period pattern cutting textile",
        "archaeological dye history",
        "costume evidence hierarchy reconstruction",
        "3D garment model heritage",
        "archaeological textile fibre analysis",
        "natural dye madder woad indigo",
        "Coptic textile burial garment",
        "Tang Han dynasty silk robe",
    ])
    arxiv_categories: List[str] = field(default_factory=lambda: [
        "cs.GR",
        "cs.CV",
        "cs.AI",
        "hist-econ",
    ])
    arxiv_base: str = "https://export.arxiv.org/api/query"
    semantic_scholar_base: str = "https://api.semanticscholar.org/graph/v1/paper/search"
    crossref_base: str = "https://api.crossref.org/works"
    rss_feeds: List[str] = field(default_factory=lambda: [
        "https://www.textilesociety.org.uk/feed/",
        "https://www.costumesociety.org.uk/feed/",
    ])
    authoritative_docs: List[str] = field(default_factory=lambda: [
        "The Journal of the Costume Society (Costume) — Taylor & Francis",
        "Textile History — Taylor & Francis",
        "Journal of Archaeological Science — Elsevier",
        "Archaeological Textiles Newsletter",
        "Antiquity — Cambridge",
        "Fashion Theory — Taylor & Francis",
    ])
    scoring: ScoringWeights = field(default_factory=ScoringWeights)
    max_results_per_source: int = 10
    max_new_entries_per_run: int = 20
    request_timeout_seconds: int = 30
    max_retries: int = 3
    retry_base_delay_seconds: float = 2.0
    inter_source_delay_seconds: float = 1.0
    brain_path: str = str(BRAIN_PATH)
    backup_brain_before_write: bool = True

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_json_file(cls, path: Path) -> "KnowledgeConfig":
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if "scoring" in data and isinstance(data["scoring"], dict):
            data["scoring"] = ScoringWeights(**data["scoring"])
        return cls(**data)


def get_default_config() -> KnowledgeConfig:
    return KnowledgeConfig()


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def setup_logging(verbose: bool = False, log_file: Optional[Path] = None) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handlers: List[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def fetch_with_retry(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    config: Optional[KnowledgeConfig] = None,
) -> Optional[Any]:
    """GET with exponential backoff. Returns the requests.Response or None."""
    if requests is None:
        log.warning("requests not installed — skipping HTTP fetch to %s", url)
        return None
    config = config or get_default_config()
    base_headers = {"User-Agent": USER_AGENT, "Accept": "application/json, application/xml, */*"}
    if headers:
        base_headers.update(headers)
    for attempt in range(1, config.max_retries + 1):
        delay = config.retry_base_delay_seconds * (2 ** (attempt - 1))
        if attempt > 1:
            log.info("retry %d/%d after %.1fs for %s", attempt, config.max_retries, delay, url)
            time.sleep(delay)
        try:
            resp = requests.get(
                url,
                params=params or {},
                headers=base_headers,
                timeout=config.request_timeout_seconds,
            )
            if resp.status_code == 429:
                log.warning("rate limited (429) on attempt %d for %s", attempt, url)
                if attempt < config.max_retries:
                    continue
                return None
            if resp.status_code >= 500:
                log.warning("server error %d on attempt %d for %s", resp.status_code, attempt, url)
                if attempt < config.max_retries:
                    continue
                return None
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as exc:
            log.warning("request failed attempt %d for %s: %s", attempt, url, exc)
            if attempt < config.max_retries:
                time.sleep(delay)
            else:
                return None
    return None


# ---------------------------------------------------------------------------
# Entry model + utilities
# ---------------------------------------------------------------------------

@dataclass
class PaperEntry:
    title: str
    authors: List[str]
    year: int
    venue: str
    doi_or_url: str
    abstract: str
    published_date: Optional[datetime]
    citation_count: int
    source: str
    tier: int = 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "venue": self.venue,
            "doi_or_url": self.doi_or_url,
            "abstract": self.abstract,
            "published_date": self.published_date,
            "citation_count": self.citation_count,
            "source": self.source,
            "tier": self.tier,
        }


def compute_hash(identifier: str) -> str:
    """SHA-256 of a DOI/URL (case- and whitespace-insensitive) for dedup."""
    return hashlib.sha256(identifier.strip().lower().encode("utf-8")).hexdigest()


def load_existing_hashes(brain_path: Path) -> Set[str]:
    """Extract SHA-256 hashes of all DOI/URLs already in the brain file."""
    if not brain_path.exists():
        return set()
    hashes: Set[str] = set()
    content = brain_path.read_text(encoding="utf-8")
    pattern = re.compile(r"\*\*DOI/URL:\*\*\s*(\S+)")
    for match in pattern.finditer(content):
        hashes.add(compute_hash(_normalize_doi(match.group(1))))
    return hashes


def _normalize_doi(identifier: str) -> str:
    """Return the canonical DOI form when possible (without resolver prefix)."""
    ident = identifier.strip()
    if ident.lower().startswith("https://doi.org/"):
        ident = ident[len("https://doi.org/"):]
    elif ident.lower().startswith("http://doi.org/"):
        ident = ident[len("http://doi.org/"):]
    return ident


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_entry(entry: PaperEntry, keywords: Sequence[str], now: datetime, config: KnowledgeConfig) -> float:
    """Score a candidate on a 0–10 scale: recency + relevance + citations."""
    recency = 0.0
    pub = entry.published_date
    if pub is not None:
        try:
            delta_days = max(0, (now - pub).days)
            recency = max(0.0, 1.0 - delta_days / 730.0)
        except Exception:
            recency = 0.0
    text = (entry.title + " " + entry.abstract).lower()
    hits = sum(1 for kw in keywords if kw.lower() in text)
    relevance = min(hits / max(len(keywords), 1), 1.0)
    citations = entry.citation_count or 0
    citation_score = min(math.log1p(citations) / math.log1p(1000), 1.0)
    w = config.scoring
    total = (
        recency * w.recency
        + relevance * w.keyword_relevance
        + citation_score * w.citation_count
    ) * 10.0
    return round(total, 2)


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------

def _parse_arxiv_date(text: Optional[str]) -> Optional[datetime]:
    if not text:
        return None
    if dateutil_parser is not None:
        try:
            return dateutil_parser.parse(text).replace(tzinfo=None)
        except Exception:
            return None
    # Fallback: ISO-8601 prefix parsing
    try:
        return datetime.fromisoformat(text[:19])
    except Exception:
        return None


def fetch_arxiv(keywords: Sequence[str], config: KnowledgeConfig) -> List[PaperEntry]:
    """Fetch recent ArXiv papers matching keywords across configured categories."""
    if requests is None:
        log.warning("requests not installed — skipping ArXiv")
        return []
    if not config.arxiv_categories:
        log.info("no ArXiv categories configured — skipping ArXiv")
        return []
    cat_query = " OR ".join("cat:" + c for c in config.arxiv_categories)
    term_query = " OR ".join('"' + kw + '"' for kw in keywords[:5])
    query = "(" + cat_query + ") AND (" + term_query + ")"
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": config.max_results_per_source,
    }
    resp = fetch_with_retry(config.arxiv_base, params=params, config=config)
    if resp is None:
        log.warning("ArXiv fetch failed after retries")
        return []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as exc:
        log.warning("ArXiv XML parse error: %s", exc)
        return []
    out: List[PaperEntry] = []
    for entry_el in root.findall("atom:entry", ns):
        title_el = entry_el.find("atom:title", ns)
        summary_el = entry_el.find("atom:summary", ns)
        id_el = entry_el.find("atom:id", ns)
        published_el = entry_el.find("atom:published", ns)
        title = (title_el.text or "").strip().replace("\n", " ") if title_el is not None else ""
        url = (id_el.text or "").strip() if id_el is not None else ""
        if not title or not url:
            continue
        pub = _parse_arxiv_date(published_el.text if published_el is not None else None)
        authors: List[str] = []
        for author_el in entry_el.findall("atom:author", ns):
            name_el = author_el.find("atom:name", ns)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())
        out.append(PaperEntry(
            title=title,
            authors=authors[:3],
            year=pub.year if pub else datetime.now().year,
            venue="ArXiv",
            doi_or_url=url,
            abstract=(summary_el.text or "").strip()[:300] if summary_el is not None else "",
            published_date=pub,
            citation_count=0,
            source=SOURCE_ARXIV,
            tier=TIER_MAPPING[SOURCE_ARXIV],
        ))
    log.info("ArXiv: fetched %d papers", len(out))
    return out


def fetch_semantic_scholar(keywords: Sequence[str], config: KnowledgeConfig) -> List[PaperEntry]:
    """Fetch papers from the Semantic Scholar search API."""
    if requests is None:
        log.warning("requests not installed — skipping Semantic Scholar")
        return []
    params = {
        "query": " ".join(keywords[:4]),
        "fields": "title,authors,year,venue,externalIds,abstract,citationCount",
        "limit": config.max_results_per_source,
    }
    resp = fetch_with_retry(config.semantic_scholar_base, params=params, config=config)
    if resp is None:
        log.warning("Semantic Scholar fetch failed after retries")
        return []
    try:
        data = resp.json()
    except ValueError as exc:
        log.warning("Semantic Scholar JSON parse failed: %s", exc)
        return []
    out: List[PaperEntry] = []
    for paper in data.get("data", []):
        title = paper.get("title") or ""
        if not title:
            continue
        year = paper.get("year") or datetime.now().year
        ext = paper.get("externalIds") or {}
        doi = ext.get("DOI")
        arxiv_id = ext.get("ArXiv")
        if doi:
            ident = doi
        elif arxiv_id:
            ident = "https://arxiv.org/abs/" + str(arxiv_id)
        else:
            ident = "https://www.semanticscholar.org/paper/" + str(paper.get("paperId", ""))
        published_date = datetime(int(year), 1, 1) if year else None
        out.append(PaperEntry(
            title=title,
            authors=[a.get("name", "") for a in (paper.get("authors") or [])[:3]],
            year=year,
            venue=paper.get("venue") or "Unknown",
            doi_or_url=ident,
            abstract=(paper.get("abstract") or "")[:300],
            published_date=published_date,
            citation_count=paper.get("citationCount", 0) or 0,
            source=SOURCE_SEMANTIC_SCHOLAR,
            tier=TIER_MAPPING[SOURCE_SEMANTIC_SCHOLAR],
        ))
    log.info("Semantic Scholar: fetched %d papers", len(out))
    return out


def fetch_crossref(keywords: Sequence[str], config: KnowledgeConfig) -> List[PaperEntry]:
    """Fetch recent Crossref works matching the keyword query."""
    if requests is None:
        log.warning("requests not installed — skipping Crossref")
        return []
    params = {
        "query": " ".join(keywords[:4]),
        "rows": config.max_results_per_source,
        "sort": "published",
        "order": "desc",
        "select": "DOI,title,author,container-title,published,abstract,is-referenced-by-count",
    }
    headers = {"User-Agent": USER_AGENT + " (mailto:contact@example.org)"}
    resp = fetch_with_retry(config.crossref_base, params=params, headers=headers, config=config)
    if resp is None:
        log.warning("Crossref fetch failed after retries")
        return []
    try:
        data = resp.json()
    except ValueError as exc:
        log.warning("Crossref JSON parse failed: %s", exc)
        return []
    out: List[PaperEntry] = []
    for item in data.get("message", {}).get("items", []):
        titles = item.get("title") or []
        title = titles[0] if titles else ""
        if not title:
            continue
        doi = item.get("DOI", "")
        if not doi:
            continue
        authors = [a.get("family", "") + " " + a.get("given", "") for a in (item.get("author") or [])[:3]]
        authors = [a.strip() for a in authors if a.strip()]
        containers = item.get("container-title") or []
        venue = containers[0] if containers else "Unknown"
        published = item.get("published") or item.get("published-print") or item.get("published-online") or {}
        date_parts = published.get("date-parts", [[None]])
        year = date_parts[0][0] or datetime.now().year
        published_date = datetime(int(year), 1, 1) if year else None
        abstract = item.get("abstract") or ""
        abstract = re.sub(r"<[^>]+>", "", abstract)[:300]
        out.append(PaperEntry(
            title=title,
            authors=authors,
            year=int(year),
            venue=venue,
            doi_or_url=doi,
            abstract=abstract,
            published_date=published_date,
            citation_count=item.get("is-referenced-by-count", 0) or 0,
            source=SOURCE_CROSSREF,
            tier=TIER_MAPPING[SOURCE_CROSSREF],
        ))
    log.info("Crossref: fetched %d papers", len(out))
    return out


def fetch_rss(config: KnowledgeConfig) -> List[PaperEntry]:
    """Fetch news items from configured RSS feeds."""
    if feedparser is None:
        log.warning("feedparser not installed — skipping RSS")
        return []
    if not config.rss_feeds:
        log.info("no RSS feeds configured — skipping RSS")
        return []
    out: List[PaperEntry] = []
    for url in config.rss_feeds:
        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            log.warning("RSS %s failed: %s", url, exc)
            continue
        if getattr(feed, "bozo", 0) and getattr(feed, "bozo_exception", None):
            log.debug("RSS %s parse warning: %s", url, feed.bozo_exception)
        for item in feed.entries[:10]:
            title = item.get("title", "")
            link = item.get("link", "")
            if not title or not link:
                continue
            pp = item.get("published_parsed")
            if pp:
                try:
                    pub = datetime(*pp[:6])
                except Exception:
                    pub = datetime.now()
            else:
                pub = datetime.now()
            out.append(PaperEntry(
                title=title,
                authors=["Editorial"],
                year=pub.year,
                venue="RSS",
                doi_or_url=link,
                abstract=(item.get("summary", ""))[:200],
                published_date=pub,
                citation_count=0,
                source=SOURCE_RSS,
                tier=TIER_MAPPING[SOURCE_RSS],
            ))
    log.info("RSS: fetched %d items", len(out))
    return out


# ---------------------------------------------------------------------------
# Formatting + brain append
# ---------------------------------------------------------------------------

def format_entry(entry: PaperEntry, score: float) -> str:
    """Format a paper/news entry as a markdown block for the brain update log."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    authors = ", ".join(entry.authors) or "Unknown"
    return (
        "\n### " + date_str + " — " + (entry.title or "Untitled") + "\n"
        "- **Authors:** " + authors + "\n"
        "- **Year:** " + str(entry.year) + "\n"
        "- **Venue:** " + (entry.venue or "Unknown") + "\n"
        "- **DOI/URL:** " + (entry.doi_or_url or "") + "\n"
        "- **Tier:** " + str(entry.tier) + "\n"
        "- **Relevance Score:** " + str(score) + "/10\n"
        "- **Key Finding:** " + (entry.abstract or "No abstract available.") + "\n"
    )


def _backup_brain(brain_path: Path) -> Optional[Path]:
    if not brain_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = brain_path.with_name(brain_path.stem + ".bak." + ts + brain_path.suffix)
    try:
        shutil.copy2(brain_path, backup)
        log.info("backed up brain to %s", backup)
        return backup
    except OSError as exc:
        log.warning("brain backup failed: %s", exc)
        return None


def append_to_brain(
    entries: List[PaperEntry],
    config: KnowledgeConfig,
    dry_run: bool = False,
) -> Tuple[int, List[PaperEntry]]:
    """Dedup, score, sort, and append new entries to the brain file.

    Returns (number_appended, list_of_appended_entries).
    """
    brain_path = Path(config.brain_path)
    if not brain_path.exists():
        log.error("knowledge brain not found: %s", brain_path)
        return 0, []
    existing = load_existing_hashes(brain_path)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    new_entries: List[PaperEntry] = []
    for entry in entries:
        ident = entry.doi_or_url
        if not ident:
            continue
        ident_norm = _normalize_doi(ident)
        h = compute_hash(ident_norm)
        if h in existing:
            continue
        existing.add(h)
        new_entries.append(entry)
    if not new_entries:
        log.info("no new entries to append (all already present)")
        return 0, []
    scored: List[Tuple[float, PaperEntry]] = []
    for entry in new_entries:
        s = score_entry(entry, config.keywords, now, config)
        scored.append((s, entry))
    scored.sort(key=lambda kv: kv[0], reverse=True)
    top = scored[: config.max_new_entries_per_run]
    new_entries = [e for _, e in top]
    append_text = "".join(format_entry(entry, score) for score, entry in top)
    if dry_run:
        log.info("[DRY RUN] would append %d entries", len(new_entries))
        return len(new_entries), new_entries
    if config.backup_brain_before_write:
        _backup_brain(brain_path)
    content = brain_path.read_text(encoding="utf-8")
    if "## 7. Knowledge Update Log" in content:
        content = content + append_text
    else:
        content = content + "\n## 7. Knowledge Update Log\n" + append_text
    brain_path.write_text(content, encoding="utf-8")
    log.info("appended %d new entries to %s", len(new_entries), brain_path)
    return len(new_entries), new_entries


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="knowledge_updater.py",
        description="Crawl academic + news sources and update SECOND-KNOWLEDGE-BRAIN.md.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview new entries without writing.")
    parser.add_argument("--news-only", action="store_true", help="Only fetch RSS news (skip academic).")
    parser.add_argument("--academic-only", action="store_true", help="Only fetch academic sources (skip RSS).")
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=None,
        help="Override the keyword list used for fetching and scoring.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to a JSON config file overriding KnowledgeConfig defaults.",
    )
    parser.add_argument(
        "--max-new",
        type=int,
        default=None,
        help="Maximum number of new entries appended per run.",
    )
    parser.add_argument(
        "--brain",
        type=Path,
        default=None,
        help="Path to the knowledge brain markdown file (defaults to project SECOND-KNOWLEDGE-BRAIN.md).",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    return parser


def resolve_config(args: argparse.Namespace) -> KnowledgeConfig:
    if args.config is not None:
        config = KnowledgeConfig.from_json_file(args.config)
    else:
        config = get_default_config()
    if args.keywords is not None:
        config.keywords = list(args.keywords)
    if args.max_new is not None:
        config.max_new_entries_per_run = args.max_new
    if args.brain is not None:
        config.brain_path = str(args.brain)
    return config


def run_pipeline(config: KnowledgeConfig, dry_run: bool, news_only: bool, academic_only: bool) -> int:
    log.info("start — domain=%s | dry=%s | news_only=%s | academic_only=%s",
             config.domain, dry_run, news_only, academic_only)
    all_entries: List[PaperEntry] = []
    if not news_only:
        all_entries.extend(fetch_arxiv(config.keywords, config))
        time.sleep(config.inter_source_delay_seconds)
        all_entries.extend(fetch_semantic_scholar(config.keywords, config))
        time.sleep(config.inter_source_delay_seconds)
        all_entries.extend(fetch_crossref(config.keywords, config))
        time.sleep(config.inter_source_delay_seconds)
    if not academic_only:
        all_entries.extend(fetch_rss(config))
    log.info("total candidates before dedup: %d", len(all_entries))
    appended, _ = append_to_brain(all_entries, config, dry_run=dry_run)
    log.info("done — appended %d new entries", appended)
    return appended


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if args.news_only and args.academic_only:
        parser.error("--news-only and --academic-only are mutually exclusive")
    log_file = LOG_DIR / ("knowledge_dryrun.log" if args.dry_run else "knowledge_update.log")
    setup_logging(verbose=args.verbose, log_file=log_file)
    config = resolve_config(args)
    appended = run_pipeline(config, dry_run=args.dry_run, news_only=args.news_only, academic_only=args.academic_only)
    print("[" + ("DRY " if args.dry_run else "") + "DONE] appended " + str(appended) + " new entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())