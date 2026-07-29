---
name: ancient-costume-mural-reconstruction
description: Ancient Costume Reconstruction & Archaeological Textile History harness — production-grade evidence-backed analysis with real-time data aggregation, recognized domain methods, academic research integration, and continuous self-improvement via knowledge crawl pipeline. Use for ANY ancient costume reconstruction, textile archaeology, iconographic analysis, period construction recovery, materials/dye identification, 3D garment modeling, or comparative analysis tasks involving murals, statues, reliefs, or extant textiles. Even if the user doesn't explicitly say "reconstruct", ANY query about historical costumes, archaeological textiles, garment analysis, museum collection records, or period dress patterns should trigger this skill.
---

# SKILL.md — Skill Registry & Architecture

## What This Skill Does

This skill transforms Claude into a **Senior Ancient Costume Reconstruction & Archaeological Textile History Specialist**. When users ask about reconstructing garments from murals/statues, identifying historical textiles, analyzing period construction, recovering ancient dye recipes, or producing 3D reconstructions of archaeological dress, this skill:

1. **Clarifies requirements** (object, scope, timeframe, inputs, audience, language)
2. **Fetches authoritative evidence** (museum records, extant textiles, academic sources)
3. **Applies domain methods** (iconography → construction → materials → 3D reconstruction)
4. **Surfaces academic evidence** (Tier-labelled citations from SECOND-KNOWLEDGE-BRAIN)
5. **Delivers risk-disclosed conclusions** (evidence-graded verdict with full disclosure)

**Key capability**: This is NOT just costume design — it's archaeologically-grounded reconstruction that respects evidence hierarchies (extant textiles > iconography > textual > ethnographic) and always discloses limitations before conclusions.

---

## When This Skill Triggers

This skill should trigger for **ANY** user query involving:

### Direct Reconstruction Tasks
- "Reconstruct the [garment] from [mural/cave/tomb]"
- "What did [historical figure] wear in [painting/relief]?"
- "Build a 3D model of [period] costume based on [statue]"

### Analysis & Identification
- "Analyze this textile fragment"
- "Identify the dye used in [archaeological find]"
- "What materials would this [period] garment be made of?"
- "Examine the construction of [garment in artwork]"

### Comparative & Historical
- "Compare Han and Tang dynasty court robes"
- "How did [garment type] change from [period A] to [period B]?"
- "What's the evidence for [costume element] in [culture]?"

### Museum & Collection Queries
- "Find museum records for [accession number]"
- "What extant [garment type] examples survive from [period]?"
- "Show me comparable textiles to [artifact]"

### Materials & Techniques
- "What dyes were available in [period/region]?"
- "How was [fabric type] made in [culture]?"
- "Reconstruct the weave structure of [textile]"

**Even if the user doesn't say "reconstruct"** — if they're asking about historical garments, archaeological textiles, period dress, or museum costume collections, this skill should trigger.

---

## Skill Registry Architecture

### Registration Model

Skills are registered in `assets/skill_manifest.json` with:

```json
{
  "version": "2.0.0",
  "skills": [
    {
      "name": "skill-name",
      "kind": "orchestrator|router|sub-agent",
      "path": "skills/skill-name.md",
      "description": "One-line summary",
      "step": N,
      "inputs_schema": "assets/schemas/xxx.schema.json",
      "outputs_schema": "assets/schemas/yyy.schema.json",
      "tools": ["Tool1", "Tool2"],
      "quality_gates": ["U1", "G1"],
      "routing": {...},
      "fallback_skill": "fallback-name"
    }
  ]
}
```

### Skill Kinds

| Kind | Purpose | Examples |
|------|---------|----------|
| `orchestrator` | Top-level harness, manages workflow, quality gates | `main.md` |
| `router` | Chain-of-thought routing to specialized agents | `sub-router.md` |
| `sub-agent` | Domain-specialized analysis agent | All sub-*.md files |

### Skill Resolution Pipeline

```
User invokes /ancient-costume-mural-reconstruction
    ↓
Load SKILL.md (this file) → skill_manifest.json
    ↓
Resolve execution chain via sub-router
    ↓
Sequential invocation:
  1. sub-gather-requirements (intake)
  2. sub-evidence-collector (data)
  3. sub-router (routing decision)
  4. [Specialized agents per routing plan]
  5. sub-knowledge-updater (academic evidence)
  6. sub-advisor (synthesis → verdict)
    ↓
Quality gate evaluation (U1-U6, G1-G4)
    ↓
Graceful degradation if gates fail
    ↓
Render final report via render_report tool
    ↓
Deliver to user
```

---

## Input/Output JSON Schemas

### Requirements Schema (inputs to Steps 1-2)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RequirementsBundle",
  "type": "object",
  "required": ["object", "period", "scope"],
  "properties": {
    "object": {
      "type": "string",
      "description": "The mural/statue/relief/site or garment being analyzed"
    },
    "period": {
      "type": "string",
      "description": "Historical period/culture (e.g., 'Tang Dynasty', 'Han China')"
    },
    "scope": {
      "type": "string",
      "enum": ["iconography", "construction", "materials", "3d", "comparison", "combined"],
      "description": "Analysis type focus"
    },
    "timeframe": {
      "type": "string",
      "description": "Urgency or deadline constraints"
    },
    "available_inputs": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Available sources (images, documents, artifacts)"
    },
    "target_audience": {
      "type": "string",
      "description": "Who will use this analysis"
    },
    "language": {
      "type": "string",
      "enum": ["en", "vi"],
      "description": "Output language"
    },
    "analysis_type": {
      "type": "string",
      "description": "Specific analysis type if different from scope"
    }
  }
}
```

### Evidence Bundle Schema (outputs from Step 2)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EvidenceBundle",
  "type": "object",
  "properties": {
    "current_collection_records": {
      "type": "array",
      "items": {"$ref": "https://example.org/evidence_item.schema.json"}
    },
    "extant_parallels": {
      "type": "array",
      "items": {"$ref": "https://example.org/evidence_item.schema.json"}
    },
    "authoritative_docs": {
      "type": "array",
      "items": {"$ref": "https://example.org/evidence_item.schema.json"}
    },
    "recent_developments": {
      "type": "array",
      "items": {"$ref": "https://example.org/evidence_item.schema.json"}
    },
    "reference_benchmarks": {
      "type": "object",
      "description": "Period-specific benchmarks from SECOND-KNOWLEDGE-BRAIN"
    }
  }
}
```

### Reconstruction Schema (outputs from Step 4)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ReconstructionReport",
  "type": "object",
  "required": ["iconographic_analysis", "construction_recovery", "materials_analysis", "evidence_hierarchy_applied", "3d_reconstruction"],
  "properties": {
    "iconographic_analysis": {
      "type": "object",
      "description": "Garment form, drape, layering, accessories, status markers"
    },
    "construction_recovery": {
      "type": "object",
      "description": "Pattern, seaming, draping, period techniques"
    },
    "materials_analysis": {
      "type": "object",
      "description": "Fiber identification, dye analysis, textile technology"
    },
    "evidence_hierarchy_applied": {
      "type": "boolean",
      "description": "Whether evidence hierarchy was explicitly applied"
    },
    "3d_reconstruction": {
      "type": "object",
      "description": "Layered 3D model with confidence levels and scenarios"
    },
    "cultural_context": {
      "type": "object",
      "description": "Social/cultural significance of the garment"
    }
  }
}
```

### Verdict Schema (final output)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ReconstructionVerdict",
  "type": "object",
  "required": ["verdict", "evidence_chain", "key_risks", "disclosure"],
  "properties": {
    "verdict": {
      "type": "string",
      "enum": [
        "Evidence-Based Reconstruction",
        "Plausible (interpretive)",
        "Speculative",
        "Inconclusive"
      ]
    },
    "scenarios": {
      "type": "array",
      "description": "Best/base/worst case scenarios"
    },
    "key_risks": {
      "type": "array",
      "minItems": 3,
      "items": {
        "type": "object",
        "properties": {
          "description": {"type": "string"},
          "probability": {"type": "string"},
          "impact": {"type": "string"}
        }
      }
    },
    "evidence_chain": {
      "type": "object",
      "description": "Full evidence chain from sources to conclusion"
    },
    "recommended_actions": {
      "type": "array",
      "items": {"type": "string"}
    },
    "disclosure": {
      "type": "string",
      "description": "MUST appear before the verdict in output"
    }
  }
}
```

---

## Tool Definitions & Execution Handlers

### Tool Registry

All tools are defined in `assets/tool_definitions.json` with:

- `name`: Tool identifier
- `description`: What the tool does
- `category`: "knowledge" | "retrieval" | "analysis" | "validation" | "io" | "utility"
- `input_schema`: Path to JSON schema for inputs
- `output_schema`: Path to JSON schema for outputs
- `handler`: Python function path in `tools/agent_tools.py`
- `timeout_seconds`: Maximum execution time
- `idempotent`: Whether repeated calls produce same result
- `requires_network`: Whether tool needs internet access

### Tool Execution Flow

```
Agent invokes tool by name
    ↓
Load tool definition from tool_definitions.json
    ↓
Validate inputs against input_schema
    ↓
Call handler function in tools/agent_tools.py
    ↓
Enforce timeout (raises TimeoutError if exceeded)
    ↓
Validate outputs against output_schema
    ↓
Return structured result
```

### Available Tools

| Tool | Handler | Category | Description |
|------|---------|----------|-------------|
| `search_knowledge_base` | `search_knowledge_base()` | knowledge | Search SECOND-KNOWLEDGE-BRAIN for Tier-labelled citations |
| `fetch_museum_record` | `fetch_museum_record()` | retrieval | Fetch museum collection record by accession number |
| `build_3d_layer` | `build_3d_layer()` | analysis | Build 3D reconstruction layer with material assignment |
| `queue_crawl_gap` | `queue_crawl_gap()` | knowledge | Queue crawl gap for knowledge pipeline |
| `run_quality_gate` | `run_quality_gate()` | validation | Evaluate quality gate (U1-U6, G1-G4) |
| `validate_verdict` | `validate_verdict()` | validation | Validate verdict against schema |
| `render_report` | `render_report()` | io | Render final report from components |
| `emit_event` | `emit_event()` | utility | Emit lifecycle event to hooks bus |

---

## Quality Gates (Validation Rules)

### Universal Gates (U1-U6)

Apply to **ALL** harness outputs:

| Gate | Check | Auto-Fix |
|------|-------|----------|
| U1 | ≥3 sources cited, ≥1 Tier 1 (academic/authoritative) | Add 2+ sources, include Tier 1 |
| U2 | Disclosure BEFORE recommendation | Move disclosure to appear first |
| U3 | Evidence hierarchy stated per source | Add Tier labels (Tier 1-4) |
| U4 | Language matches user preference | Ensure all text in declared language |
| U5 | Output follows template | Add missing sections |
| U6 | All claims traceable to source OR flagged as judgment | Add citations or flag as judgment |

### Domain Gates (G1-G4)

Apply to ancient costume reconstruction specifically:

| Gate | Check | Auto-Fix |
|------|-------|----------|
| G1 | Iconographic analysis completed | Perform visual source analysis |
| G2 | Construction & materials/dyes recovered | Add period construction & materials |
| G3 | Evidence hierarchy applied per claim | State hierarchy (extant > iconographic > textual > ethnographic) |
| G4 | 3D reconstruction produced with confidence | Build layered 3D model with H/M/L confidence |

### Gate Enforcement Logic

```
For each gate:
  1. Run gate check against payload
  2. If PASS → continue
  3. If FAIL → apply auto-fix (if enabled) → retry
  4. If still FAIL after 2 retries → flag limitation → continue
  5. If enforcing mode (default) → fail the step → escalate degradation level
```

---

## Graceful Degradation Strategy

### Degradation Levels

| Level | Condition | Behavior |
|-------|-----------|----------|
| 0 | All gates pass | Full execution, no limitations |
| 1 | Non-critical gates fail | Add limitation banner, continue |
| 2 | Critical gates fail, fallback available | Use fallback agent, add limitation |
| 3 | Major limitations | Best-effort analysis, heavy disclosure |
| 4 | Severe failures | Minimum viable output, Inconclusive verdict |

### Degradation Banners

When degradation occurs, output MUST include:

```markdown
---
**LIMITATION**: This analysis has [data/method] limitations.
[Specific limitation description]
Confidence: [Low/Moderate/High]
Verdict may be affected: [Yes/No]
---
```

---

## Hooks System (Lifecycle Events)

### Event Types

Events are emitted via `emit_event` tool:

| Event Type | When | Payload |
|------------|------|---------|
| `routing_decision` | After sub-router completes | execution_chain, rationale, fallback |
| `quality_gate_pass` | After each gate passes | gate_id, payload |
| `quality_gate_fail` | After gate fails (with auto-fix) | gate_id, failure_reason, auto_fix |
| `degradation` | When degradation level increases | old_level, new_level, reason |
| `step_complete` | After each sub-skill completes | skill_name, outputs, duration_ms |
| `analysis_complete` | After full harness completes | verdict, total_duration_ms |

### Hook Handlers

Hooks are registered in `assets/hooks.json` and can:

- Log structured events
- Trigger notifications
- Update metrics
- Call external services
- Modify execution flow (rare, requires explicit enable)

---

## Error Handling & Recovery

### Error Categories

| Error Type | Recovery Strategy |
|------------|------------------|
| `ValidationError` | Return validation error, don't proceed |
| `TimeoutError` | Return timeout, suggest simplification |
| `ToolError` | Log error, try fallback, add limitation |
| `AgentError` (LLM failure) | Retry with exponential backoff (max 3) |
| `ConfigError` | Return configuration error, don't proceed |

### Retry Policy

```
Retry attempt 1: immediate
Retry attempt 2: 1.5s delay
Retry attempt 3: 3s delay
After 3 failures: flag as limitation, continue or fail
```

---

## Configuration Management

### Config Resolution Order

1. Explicit keyword arguments to `load_config()`
2. Environment variables (`ACMR_*` prefix)
3. Config file (`config/config.json`, `config/config.yaml`, or `$ACMR_CONFIG`)
4. Built-in defaults (dataclass defaults)

### Key Config Sections

- `llm`: Model parameters, temperature, token budgets, retry policy
- `harness`: Language policy, gate enforcement, degradation behavior
- `knowledge_pipeline`: Crawl keywords, sources, schedules, limits
- `features`: Feature flags for incremental rollout
- `logging`: Log level, output targets, rotation settings

### Environment Variables

```bash
ACMR_CONFIG=/path/to/config.yaml
ACMR_LLM__MODEL=claude-sonnet-4-5
ACMR_HARNESS__DEFAULT_LANGUAGE=vi
ACMR_FEATURES__ENABLE_KNOWLEDGE_CRAWL=true
```

---

## Knowledge Pipeline Integration

### SECOND-KNOWLEDGE-BRAIN.md Structure

```markdown
# Core Methods
[Domain methodology entries]

# Key Papers & References
[Tier 1/2 academic papers with DOIs]

# State of the Art
[Current research directions]

# Data Sources
[Museum collections, databases]

# Self-Update Protocol
[Crawl configuration, last updated]

# Update Log
[Append-only log of new entries]
```

### Crawl Pipeline (`tools/knowledge_updater.py`)

- **Sources**: ArXiv (cs.GR, cs.CV, cs.AI), Semantic Scholar, Crossref, RSS feeds
- **Dedup**: SHA-256 of normalized DOI
- **Scoring**: Recency (0.4) + Keyword relevance (0.4) + Citation count (0.2)
- **Schedule**: Weekly academic (Mondays 8:00), Daily news (Daily 7:00)
- **Safety**: Backup-before-write, idempotent append, graceful degradation

---

## Language Support (English/Vietnamese)

### Language Detection

Pre-flight step detects language from input:
- **Vietnamese**: Diacritics (à, á, ả, ã, ạ, ă, â, đ, è, é, ê, ì, í, ò, ó, ô, ơ, ù, ú, ư, ý)
- **English**: Default
- **Other**: Default to English, ask user to confirm

### Translation Table

All output templates support both languages:

| English | Tiếng Việt |
|---------|------------|
| Analysis Report | Báo cáo phân tích |
| Executive Summary | Tóm tắt tổng quan |
| Evidence-Based Reconstruction | Phục dựng dựa bằng chứng |
| Key Risks | Rủi ro chính |
| Disclosure / Limitations | Công bố / Giới hạn phân tích |

---

## Performance & Token Management

### Context Budgeting

```
Total context window: 200,000 tokens
Reserved for output: 4,096 tokens
Available for prompt + retrieval: 195,904 tokens
```

### Token Allocation Strategy

| Component | Typical Token Usage |
|-----------|-------------------|
| Requirements gathering | 500-1,000 |
| Evidence collection | 2,000-5,000 (varies by source count) |
| Core analysis | 5,000-10,000 (iconography + construction + materials) |
| Knowledge base query | 1,000-2,000 |
| Verdict synthesis | 2,000-3,000 |
| **Total** | ~10,000-20,000 tokens |

### Optimization Strategies

- **Cache knowledge base queries**: Same keywords hit cache
- **Prioritize Tier 1 sources**: Higher quality, less noise
- **Limit parallel branches**: Avoid combinatorial explosion in comparison tasks
- **Summarize intermediate results**: Don't carry full context forward unnecessarily

---

## Testing & Validation

### Test Scenarios (`tests/test-scenarios.md`)

Five end-to-end scenarios exercising all gates and verdicts:

1. **Standard**: Full reconstruction with all evidence sources
2. **Minimal-input**: Fragmentary evidence, heavy degradation
3. **Comparison**: Two garments, parallel analysis branches
4. **Risk/conflict**: Conflicting evidence, strong disclosure
5. **Degraded-mode**: Multiple source failures, severe limitations

### Validation Tools

- `tools/validate_project.py`: 8-File Contract validator
- `tools/run_test_scenarios.py`: Scenario runner + gate coverage matrix
- `tools/test_knowledge_updater.py`: Unit tests (22 tests)

---

## Open-Source Compliance

### Required Files (8-File Contract)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Skill identity, harness diagram, cron schedule |
| `PROJECT-detail.md` | Full technical specification |
| `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` | Build roadmap with phases |
| `README.md` | Public-facing documentation |
| `skills/main.md` | Main harness orchestrator |
| `SECOND-KNOWLEDGE-BRAIN.md` | Self-improving knowledge base |
| `tools/knowledge_updater.py` | Crawl pipeline |
| `LICENSE` | MIT License |

### Open-Source Scaffolding

- `CONTRIBUTING.md`: Contribution guidelines
- `CODE_OF_CONDUCT.md`: Community standards
- `CHANGELOG.md`: Version history
- `pyproject.toml`: Python packaging metadata
- `progression.json`: Build status tracking

---

## Version History

### v2.0.0 (Current)

- **Modular agent architecture**: Router-based execution with chain-of-thought
- **Production-grade tooling**: Type-safe config, structured logging, comprehensive error handling
- **Enhanced schemas**: Full JSON Schema validation for all inputs/outputs
- **Hooks system**: Lifecycle events for monitoring and integration
- **Specialized skills**: Iconography, construction, materials, 3D architect sub-skills
- **Improved degradation**: 5-level graceful degradation with explicit banners
- **Better Vietnamese support**: Full language detection and translation

### v1.1.0

- Open-source hardening
- Production-grade Python tooling
- Comprehensive testing suite

### v1.0.0

- Initial release
- 6-step harness flow
- Quality gates (U1-U6, G1-G4)
- Knowledge crawl pipeline
