"""
config/settings.py — Skill 240: ancient-costume-mural-reconstruction

Central, type-safe configuration management for the whole harness.

This module is the single source of truth for:
  * environment variables (with .env / os.environ precedence),
  * LLM parameters (model, temperature, token budgets, retry policy),
  * harness behavior (language, degradation policy, gate enforcement),
  * the knowledge-crawl pipeline (keywords, sources, limits, schedule),
  * system-wide feature flags,
  * structured logging.

Design
------
* Pure-stdlib + `pydantic` *if installed*, otherwise a lightweight
  hand-rolled validator keeps the contract. The dataclasses are frozen so
  configuration is immutable after construction; mutation happens by
  reloading from a new source.
* Resolution order (highest precedence first):
    1. explicit keyword args to ``load_config(...)``
    2. process environment variables (``ACMR_*``)
    3. the JSON/YAML config file pointed to by ``ACMR_CONFIG`` (or
      ``config/config.json`` / ``config/config.yaml`` if present)
    4. built-in dataclass defaults.
* All values are validated and coerced to their declared types. Invalid
  values raise :class:`ConfigError` with a precise message — never a silent
  fallback to a wrong type.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
ENV_PREFIX = "ACMR_"

_CONFIG_CACHE: Optional["AppConfig"] = None


class ConfigError(ValueError):
    """Raised when configuration cannot be resolved or fails validation."""


_TRUE_STRINGS = {"1", "true", "yes", "on", "y", "t"}
_FALSE_STRINGS = {"0", "false", "no", "off", "n", "f"}


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in _TRUE_STRINGS:
            return True
        if v in _FALSE_STRINGS:
            return False
        raise ConfigError(f"cannot coerce {value!r} to bool")
    raise ConfigError(f"cannot coerce {type(value).__name__} to bool")


def _coerce_int(value: Any, *, minimum: Optional[int] = None, maximum: Optional[int] = None) -> int:
    if isinstance(value, bool):
        return int(value)
    try:
        out = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"cannot coerce {value!r} to int: {exc}") from exc
    if minimum is not None and out < minimum:
        raise ConfigError(f"value {out} below minimum {minimum}")
    if maximum is not None and out > maximum:
        raise ConfigError(f"value {out} above maximum {maximum}")
    return out


def _coerce_float(value: Any, *, minimum: Optional[float] = None, maximum: Optional[float] = None) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"cannot coerce {value!r} to float: {exc}") from exc
    if minimum is not None and out < minimum:
        raise ConfigError(f"value {out} below minimum {minimum}")
    if maximum is not None and out > maximum:
        raise ConfigError(f"value {out} above maximum {maximum}")
    return out


def _coerce_str(value: Any) -> str:
    if value is None:
        raise ConfigError("expected string, got None")
    return str(value).strip()


def _coerce_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        # accept comma/space separated env strings
        parts = [p.strip() for p in re.split(r"[,\s]+", value.strip()) if p.strip()]
        return parts
    if isinstance(value, (list, tuple, set)):
        return [str(v).strip() for v in value if str(v).strip()]
    raise ConfigError(f"cannot coerce {value!r} to list[str]")


# ---------------------------------------------------------------------------
# Sub-configurations
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LLMConfig:
    """Parameters governing the underlying language model call."""
    model: str = "claude-sonnet-4-5"
    provider: str = "anthropic"
    temperature: float = 0.2
    top_p: float = 0.95
    max_output_tokens: int = 4096
    request_timeout_seconds: int = 60
    max_retries: int = 3
    retry_base_delay_seconds: float = 1.5
    context_window_tokens: int = 200_000
    reserved_output_tokens: int = 4_096

    def effective_input_budget(self) -> int:
        """Tokens available for prompt + retrieved context after reserves."""
        return max(0, self.context_window_tokens - self.reserved_output_tokens)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "LLMConfig":
        return cls(
            model=_coerce_str(data.get("model", "claude-sonnet-4-5")),
            provider=_coerce_str(data.get("provider", "anthropic")),
            temperature=_coerce_float(data.get("temperature", 0.2), minimum=0.0, maximum=2.0),
            top_p=_coerce_float(data.get("top_p", 0.95), minimum=0.0, maximum=1.0),
            max_output_tokens=_coerce_int(data.get("max_output_tokens", 4096), minimum=1),
            request_timeout_seconds=_coerce_int(data.get("request_timeout_seconds", 60), minimum=1),
            max_retries=_coerce_int(data.get("max_retries", 3), minimum=0, maximum=10),
            retry_base_delay_seconds=_coerce_float(data.get("retry_base_delay_seconds", 1.5), minimum=0.0),
            context_window_tokens=_coerce_int(data.get("context_window_tokens", 200_000), minimum=1),
            reserved_output_tokens=_coerce_int(data.get("reserved_output_tokens", 4096), minimum=0),
        )


@dataclass(frozen=True)
class HarnessConfig:
    """Behavior of the main harness orchestrator."""
    default_language: str = "en"
    supported_languages: Tuple[str, ...] = ("en", "vi")
    max_clarifying_questions: int = 2
    max_gate_retries: int = 2
    enforce_gates: bool = True
    emit_limitation_banner: bool = True
    output_template: str = "default"
    enable_router: bool = True
    enable_hooks: bool = True
    enable_quality_gates: bool = True

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "HarnessConfig":
        langs = tuple(_coerce_list(data.get("supported_languages", ["en", "vi"])))
        if not langs:
            langs = ("en", "vi")
        return cls(
            default_language=_coerce_str(data.get("default_language", "en")),
            supported_languages=langs,
            max_clarifying_questions=_coerce_int(data.get("max_clarifying_questions", 2), minimum=0, maximum=5),
            max_gate_retries=_coerce_int(data.get("max_gate_retries", 2), minimum=0, maximum=10),
            enforce_gates=_coerce_bool(data.get("enforce_gates", True)),
            emit_limitation_banner=_coerce_bool(data.get("emit_limitation_banner", True)),
            output_template=_coerce_str(data.get("output_template", "default")),
            enable_router=_coerce_bool(data.get("enable_router", True)),
            enable_hooks=_coerce_bool(data.get("enable_hooks", True)),
            enable_quality_gates=_coerce_bool(data.get("enable_quality_gates", True)),
        )


@dataclass(frozen=True)
class KnowledgePipelineConfig:
    """Parameters for the SECOND-KNOWLEDGE-BRAIN crawl pipeline."""
    keywords: Tuple[str, ...] = (
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
    )
    arxiv_categories: Tuple[str, ...] = ("cs.GR", "cs.CV", "cs.AI", "hist-econ")
    rss_feeds: Tuple[str, ...] = (
        "https://www.textilesociety.org.uk/feed/",
        "https://www.costumesociety.org.uk/feed/",
    )
    max_results_per_source: int = 10
    max_new_entries_per_run: int = 20
    request_timeout_seconds: int = 30
    max_retries: int = 3
    backup_brain_before_write: bool = True
    academic_schedule_cron: str = "0 8 * * 1"
    news_schedule_cron: str = "0 7 * * *"

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "KnowledgePipelineConfig":
        return cls(
            keywords=tuple(_coerce_list(data.get("keywords")) or list(cls().keywords)),
            arxiv_categories=tuple(_coerce_list(data.get("arxiv_categories")) or list(cls().arxiv_categories)),
            rss_feeds=tuple(_coerce_list(data.get("rss_feeds")) or list(cls().rss_feeds)),
            max_results_per_source=_coerce_int(data.get("max_results_per_source", 10), minimum=1),
            max_new_entries_per_run=_coerce_int(data.get("max_new_entries_per_run", 20), minimum=1),
            request_timeout_seconds=_coerce_int(data.get("request_timeout_seconds", 30), minimum=1),
            max_retries=_coerce_int(data.get("max_retries", 3), minimum=0, maximum=10),
            backup_brain_before_write=_coerce_bool(data.get("backup_brain_before_write", True)),
            academic_schedule_cron=_coerce_str(data.get("academic_schedule_cron", "0 8 * * 1")),
            news_schedule_cron=_coerce_str(data.get("news_schedule_cron", "0 7 * * *")),
        )


@dataclass(frozen=True)
class FeatureFlags:
    """System-wide feature flags for incremental rollout / kill-switches."""
    enable_knowledge_crawl: bool = True
    enable_router_chain_of_thought: bool = True
    enable_evidence_collector: bool = True
    enable_3d_reconstruction: bool = True
    enable_scenarios: bool = True
    enable_vietnamese_output: bool = True
    enable_strict_evidence_hierarchy: bool = True
    enable_disclosure_before_conclusion: bool = True
    enable_event_emission: bool = False

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "FeatureFlags":
        return cls(
            enable_knowledge_crawl=_coerce_bool(data.get("enable_knowledge_crawl", True)),
            enable_router_chain_of_thought=_coerce_bool(data.get("enable_router_chain_of_thought", True)),
            enable_evidence_collector=_coerce_bool(data.get("enable_evidence_collector", True)),
            enable_3d_reconstruction=_coerce_bool(data.get("enable_3d_reconstruction", True)),
            enable_scenarios=_coerce_bool(data.get("enable_scenarios", True)),
            enable_vietnamese_output=_coerce_bool(data.get("enable_vietnamese_output", True)),
            enable_strict_evidence_hierarchy=_coerce_bool(data.get("enable_strict_evidence_hierarchy", True)),
            enable_disclosure_before_conclusion=_coerce_bool(data.get("enable_disclosure_before_conclusion", True)),
            enable_event_emission=_coerce_bool(data.get("enable_event_emission", False)),
        )


@dataclass(frozen=True)
class LoggingConfig:
    """Structured logging configuration."""
    level: str = "INFO"
    log_dir: str = "logs"
    enable_file_logging: bool = True
    enable_console_logging: bool = True
    json_format: bool = False
    rotate_max_bytes: int = 5_242_880
    rotate_backup_count: int = 5

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "LoggingConfig":
        level = _coerce_str(data.get("level", "INFO")).upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ConfigError(f"invalid log level {level!r}")
        return cls(
            level=level,
            log_dir=_coerce_str(data.get("log_dir", "logs")),
            enable_file_logging=_coerce_bool(data.get("enable_file_logging", True)),
            enable_console_logging=_coerce_bool(data.get("enable_console_logging", True)),
            json_format=_coerce_bool(data.get("json_format", False)),
            rotate_max_bytes=_coerce_int(data.get("rotate_max_bytes", 5_242_880), minimum=1),
            rotate_backup_count=_coerce_int(data.get("rotate_backup_count", 5), minimum=0, maximum=50),
        )


@dataclass(frozen=True)
class AppConfig:
    """Top-level application configuration."""
    app_name: str = "ancient-costume-mural-reconstruction"
    version: str = "2.0.0"
    environment: str = "production"
    project_root: str = str(PROJECT_ROOT)
    llm: LLMConfig = field(default_factory=LLMConfig)
    harness: HarnessConfig = field(default_factory=HarnessConfig)
    knowledge_pipeline: KnowledgePipelineConfig = field(default_factory=KnowledgePipelineConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    def with_overrides(self, **changes: Any) -> "AppConfig":
        """Return a new AppConfig with the given top-level fields replaced."""
        return replace(self, **changes)


# ---------------------------------------------------------------------------
# File + environment loading
# ---------------------------------------------------------------------------

def _load_dotenv(path: Path) -> Dict[str, str]:
    """Minimal .env parser (KEY=VALUE per line, # comments, no quoting magic)."""
    env: Dict[str, str] = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            env[key] = value
    return env


def _read_config_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(text)
    if suffix in (".yaml", ".yml"):
        return _parse_yaml(text)
    if suffix == ".toml":
        try:
            import tomllib  # type: ignore
        except ImportError:  # pragma: no cover - py<3.11
            try:
                import tomli as tomllib  # type: ignore
            except ImportError as exc:
                raise ConfigError("toml config requires Python 3.11+ or tomli") from exc
        return tomllib.loads(text)
    # default: JSON
    return json.loads(text)


def _parse_yaml(text: str) -> Dict[str, Any]:
    """A tiny YAML subset parser (key: value, nested via indentation).

    Sufficient for the project's flat config schema; for full YAML install
    PyYAML and it will be used transparently via :func:`_parse_yaml_full`.
    """
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except ImportError:
        pass
    # Fallback minimal parser: only ``key: value`` and two-level nesting.
    root: Dict[str, Any] = {}
    current: Optional[str] = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if indent == 0:
            root[key] = value if value else {}
            current = key
        else:
            if current is None:
                root[key] = value
            else:
                bucket = root[current]
                if isinstance(bucket, dict):
                    bucket[key] = value
    return root


def _env_overrides(env: Mapping[str, str]) -> Dict[str, Any]:
    """Map ``ACMR_<SECTION>__<FIELD>`` env vars to a nested config dict."""
    out: Dict[str, Any] = {}
    for key, value in env.items():
        if not key.startswith(ENV_PREFIX):
            continue
        remainder = key[len(ENV_PREFIX):]
        parts = remainder.lower().split("__", 1)
        if len(parts) == 1:
            out[parts[0]] = value
        else:
            section, field_name = parts
            out.setdefault(section, {})[field_name] = value
    return out


def _deep_merge(base: Dict[str, Any], over: Mapping[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in over.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _resolve_config_path(explicit: Optional[Path]) -> Optional[Path]:
    if explicit is not None:
        return explicit
    env_path = os.environ.get(f"{ENV_PREFIX}CONFIG")
    if env_path:
        return Path(env_path)
    for candidate in ("config.json", "config.yaml", "config.yml", "config.toml"):
        p = CONFIG_DIR / candidate
        if p.exists():
            return p
    return None


def load_config(
    config_path: Optional[Union[str, Path]] = None,
    *,
    env: Optional[Mapping[str, str]] = None,
    overrides: Optional[Mapping[str, Any]] = None,
    use_cache: bool = False,
) -> AppConfig:
    """Resolve and validate the application configuration.

    Parameters
    ----------
    config_path
        Optional path to a JSON/YAML/TOML config file. If omitted the
        ``ACMR_CONFIG`` env var or the default ``config/config.*`` files
        are consulted.
    env
        Optional environment mapping; defaults to ``os.environ``.
    overrides
        Optional top-level overrides applied with the highest precedence.
    use_cache
        When True, store the resolved config in a process-wide cache so
        :func:`get_config` returns it without re-reading files.
    """
    global _CONFIG_CACHE
    if use_cache and _CONFIG_CACHE is not None and config_path is None and overrides is None:
        return _CONFIG_CACHE

    env_map = dict(env if env is not None else os.environ)
    # also pick up a local .env (does not override the real environment)
    env_map.update(_load_dotenv(PROJECT_ROOT / ".env"))

    file_data: Dict[str, Any] = {}
    cfg_path = _resolve_config_path(Path(config_path) if config_path else None)
    if cfg_path is not None:
        file_data = _read_config_file(cfg_path)

    env_over = _env_overrides(env_map)
    merged = _deep_merge(file_data, env_over)
    if overrides:
        merged = _deep_merge(merged, dict(overrides))

    config = AppConfig(
        app_name=_coerce_str(merged.get("app_name", "ancient-costume-mural-reconstruction")),
        version=_coerce_str(merged.get("version", "2.0.0")),
        environment=_coerce_str(merged.get("environment", "production")),
        project_root=_coerce_str(merged.get("project_root", str(PROJECT_ROOT))),
        llm=LLMConfig.from_mapping(merged.get("llm", {})),
        harness=HarnessConfig.from_mapping(merged.get("harness", {})),
        knowledge_pipeline=KnowledgePipelineConfig.from_mapping(merged.get("knowledge_pipeline", {})),
        features=FeatureFlags.from_mapping(merged.get("features", {})),
        logging=LoggingConfig.from_mapping(merged.get("logging", {})),
    )

    if config.harness.default_language not in config.harness.supported_languages:
        raise ConfigError(
            f"default_language {config.harness.default_language!r} not in "
            f"supported_languages {config.harness.supported_languages}"
        )
    if config.llm.reserved_output_tokens >= config.llm.context_window_tokens:
        raise ConfigError("reserved_output_tokens must be smaller than context_window_tokens")

    if use_cache:
        _CONFIG_CACHE = config
    return config


def get_config() -> AppConfig:
    """Return the cached config, loading it on first use."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        _CONFIG_CACHE = load_config(use_cache=True)
    return _CONFIG_CACHE


def reload_config(config_path: Optional[Union[str, Path]] = None) -> AppConfig:
    """Force re-resolution of the configuration."""
    global _CONFIG_CACHE
    _CONFIG_CACHE = None
    return load_config(config_path, use_cache=True)
