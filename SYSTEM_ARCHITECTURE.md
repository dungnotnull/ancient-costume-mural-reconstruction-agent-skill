# System Architecture Summary — v2.0.0

## Overview

This document provides a comprehensive overview of the ancient-costume-mural-reconstruction
harness architecture, including all components, their relationships, and data flows.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                        │
│              /ancient-costume-mural-reconstruction [query]                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MAIN HARNESS (skills/main.md)                         │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Pre-Flight: Language Detection (en/vi)                                │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Quality Gate Evaluation (U1-U6, G1-G4)                              │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Graceful Degradation (Levels 0-4)                                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                ┌───────────────────────┼───────────────────────┐
                │                       │                       │
                ▼                       ▼                       ▼
┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
│   CONFIG SYSTEM       │   │   HOOKS SYSTEM       │   │   TOOL SYSTEM         │
│ (config/settings.py)  │   │(tools/hooks_system)  │   │(tools/agent_tools.py) │
│                       │   │                       │   │                       │
│ • LLM Config          │   │ • Event Bus          │   │ • search_knowledge   │
│ • Harness Config      │   │ • State Management   │   │ • fetch_museum       │
│ • Knowledge Pipeline  │   │ • Event Handlers     │   │ • build_3d_layer     │
│ • Feature Flags       │   │ • Event Logging      │   │ • run_quality_gate   │
│ • Logging Config      │   │ • Metrics Collection  │   │ • validate_verdict   │
└───────────────────────┘   └───────────────────────┘   └───────────────────────┘
                │                       │                       │
                └───────────────────────┼───────────────────────┘
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SUB-ROUTER (skills/sub-router.md)                     │
│                   Chain-of-Thought Routing to Specialized Agents            │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Analyze Requirements (complexity, domain focus, evidence)           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Construct Execution Plan (chain, branches, fallbacks)               │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Emit Routing Event to Hooks Bus                                     │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            │                           │                           │
            ▼                           ▼                           ▼
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│ Step 1:                 │  │ Step 2:                 │  │ Step 3-6:              │
│ sub-gather-requirements │  │ sub-evidence-collector  │  │ Specialized Agents      │
│                         │  │                         │  │                         │
│ • Intake specialist     │  │ • Data librarian        │  │ (Routing-dependent)     │
│ • Clarify object/scope  │  │ • Museum records        │  │                         │
│ • Confirm requirements  │  │ • Extant parallels      │  │ • sub-iconography-analyzer│
│ • Language detection    │  │ • Academic sources      │  │ • sub-construction-expert│
│                         │  │ • Recent developments   │  │ • sub-materials-specialist│
└─────────────────────────┘  └─────────────────────────┘  │ • sub-3d-architect      │
            │                           │             │ • sub-core-analysis       │
            └───────────────────────────┼─────────────┴─────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Step 7: sub-knowledge-updater                            │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Query SECOND-KNOWLEDGE-BRAIN.md for Tier-labelled citations            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Flag crawl gaps for knowledge pipeline                                │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Step 8: sub-advisor                                 │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Synthesize all analysis into risk-disclosed conclusion               │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Determine verdict (Evidence-Based / Plausible / Speculative)          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Build scenarios (best/base/worst)                                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Evidence chain + recommended actions                                 │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FINAL QUALITY GATE                                   │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Verify U1-U6 (universal gates)                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Verify G1-G4 (domain gates)                                          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Apply auto-fix if gates fail                                         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Escalate degradation if needed                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RENDER OUTPUT                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Use render_report tool to format final output                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Apply template (default/academic/presentation)                      │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Translate to target language (en/vi)                                │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER OUTPUT                                      │
│              Structured, risk-disclosed reconstruction report               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Directory Structure

```
240-ancient-costume-mural-reconstruction/
├── assets/
│   ├── schemas/                  # JSON Schema definitions
│   │   ├── tool_inputs/         # Tool input schemas
│   │   ├── tool_outputs/        # Tool output schemas
│   │   ├── execution_plan.schema.json
│   │   ├── reconstruction.schema.json
│   │   ├── requirements.schema.json
│   │   └── verdict.schema.json
│   ├── hooks.json               # Hooks configuration
│   ├── skill_manifest.json      # Skill registry (7 skills)
│   └── tool_definitions.json    # Tool registry (8 tools)
├── config/
│   ├── settings.py              # Type-safe configuration management
│   ├── config.example.json
│   ├── config.example.yaml
│   ├── .env.example
│   └── crawl_gaps.json          # Knowledge crawl gaps queue
├── references/                  # Domain knowledge base
│   ├── iconography/
│   │   └── evidence_hierarchy_protocol.md
│   ├── construction/
│   │   └── period_methods_reference.md
│   ├── materials/
│   ├── 3d_reference/
│   │   └── reconstruction_guidelines.md
│   └── academic/
├── scripts/                     # Automation scripts
│   ├── setup.py                 # Project initialization
│   ├── initialize_knowledge_base.py
│   └── ci_validate.py           # CI/CD validation
├── skills/                      # Skill definitions (7 total)
│   ├── main.md                  # Main harness orchestrator
│   ├── sub-router.md            # Chain-of-thought router
│   ├── sub-gather-requirements.md
│   ├── sub-evidence-collector.md
│   ├── sub-core-analysis.md
│   ├── sub-knowledge-updater.md
│   ├── sub-advisor.md
│   ├── sub-iconography-analyzer.md
│   ├── sub-construction-expert.md
│   ├── sub-materials-specialist.md
│   └── sub-3d-architect.md
├── tools/                       # Tool implementations
│   ├── agent_tools.py           # 8 tool handlers
│   ├── hooks_system.py          # Hooks bus and handlers
│   ├── knowledge_updater.py     # Knowledge crawl pipeline
│   ├── test_knowledge_updater.py # Unit tests (22 tests)
│   ├── validate_project.py      # 8-File Contract validator
│   └── run_test_scenarios.py   # Scenario runner
├── tests/
│   ├── test-scenarios.md        # 5 end-to-end scenarios
│   └── TEST_RESULTS.md
├── logs/                        # Structured logs
│   ├── agent_tools.log
│   ├── hooks_system.log
│   └── hooks_*.log              # Per-event-type logs
├── SECOND-KNOWLEDGE-BRAIN.md    # Living knowledge base
├── SKILL.md                     # Comprehensive skill documentation
├── CLAUDE.md                    # Skill identity
├── PROJECT-detail.md            # Technical specification
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md
├── README.md                    # Public documentation
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE
├── pyproject.toml
├── progression.json
└── requirements.txt
```

---

## Skill Registry (7 Skills)

| Skill | Kind | Purpose | Input Schema | Output Schema |
|-------|------|---------|--------------|--------------|
| `main.md` | orchestrator | Main harness, quality gates, degradation | requirements | verdict |
| `sub-router.md` | router | Chain-of-thought routing to agents | requirements | execution_plan |
| `sub-gather-requirements.md` | sub-agent | Intake, clarify requirements | raw_input | requirements |
| `sub-evidence-collector.md` | sub-agent | Fetch museum records, extant parallels | requirements | evidence_bundle |
| `sub-core-analysis.md` | sub-agent | Iconography → construction → materials → 3D | evidence_bundle | reconstruction |
| `sub-knowledge-updater.md` | sub-agent | Query knowledge base, flag gaps | reconstruction | evidence_bundle |
| `sub-advisor.md` | sub-agent | Synthesize into risk-disclosed conclusion | reconstruction | verdict |

**Specialized Domain Skills (4):**
- `sub-iconography-analyzer.md` — Visual source analysis
- `sub-construction-expert.md` — Period pattern cutting
- `sub-materials-specialist.md` — Fiber/dye identification
- `sub-3d-architect.md` — 3D layered reconstruction

---

## Tool Registry (8 Tools)

| Tool | Category | Handler | Description |
|------|----------|---------|-------------|
| `search_knowledge_base` | knowledge | `search_knowledge_base()` | Search SECOND-KNOWLEDGE-BRAIN |
| `fetch_museum_record` | retrieval | `fetch_museum_record()` | Fetch museum collection by accession |
| `build_3d_layer` | analysis | `build_3d_layer()` | Build 3D reconstruction layer |
| `queue_crawl_gap` | knowledge | `queue_crawl_gap()` | Queue crawl query for pipeline |
| `run_quality_gate` | validation | `run_quality_gate()` | Evaluate quality gate |
| `validate_verdict` | validation | `validate_verdict()` | Validate verdict object |
| `render_report` | io | `render_report()` | Render final report |
| `emit_event` | utility | `emit_event()` | Emit lifecycle event |

---

## Quality Gates (10 Total)

### Universal Gates (U1-U6)
- **U1**: ≥3 sources, ≥1 Tier 1
- **U2**: Disclosure BEFORE recommendation
- **U3**: Evidence hierarchy per source
- **U4**: Language matches preference
- **U5**: Output follows template
- **U6**: Claims traceable to sources

### Domain Gates (G1-G4)
- **G1**: Iconographic analysis complete
- **G2**: Construction & materials recovered
- **G3**: Evidence hierarchy applied
- **G4**: 3D reconstruction produced

---

## Knowledge Pipeline

### Crawl Sources
- **ArXiv**: cs.GR, cs.CV, cs.AI, hist-econ
- **Semantic Scholar**: Keyword-based discovery
- **Crossref**: DOI enrichment
- **RSS Feeds**: Textile Society, Costume Society

### Schedule
- **Academic**: Weekly (Mondays 8:00 AM)
- **News**: Daily (7:00 AM)

### Processing
- **Deduplication**: SHA-256 of normalized DOI
- **Scoring**: Recency (0.4) + Keyword relevance (0.4) + Citation count (0.2)
- **Safety**: Backup-before-write, idempotent append

---

## Configuration System

### Resolution Order
1. Keyword arguments to `load_config()`
2. Environment variables (`ACMR_*` prefix)
3. Config file (`config/config.json` or `$ACMR_CONFIG`)
4. Built-in defaults

### Key Sections
- **llm**: Model parameters, temperature, token budgets
- **harness**: Language policy, gate enforcement
- **knowledge_pipeline**: Crawl keywords, sources, schedules
- **features**: Feature flags for incremental rollout
- **logging**: Log level, output targets

---

## Hooks System

### Event Types
- `routing_decision` — After sub-router completes
- `quality_gate_result` — After each gate evaluation
- `step_complete` — After each sub-skill completes
- `degradation` — When degradation level increases
- `analysis_complete` — After full harness completes

### Built-in Handlers
- `log_to_file` — Structured event logging
- `metrics` — Performance metrics collection
- `state_sync` — State synchronization
- `degradation_alert` — Degradation notifications

---

## Graceful Degradation

### Degradation Levels
- **Level 0**: Full execution, all gates pass
- **Level 1**: Non-critical gates fail, limitation banner
- **Level 2**: Critical gates fail, fallback available
- **Level 3**: Major limitations, best-effort analysis
- **Level 4**: Severe failures, Inconclusive verdict

### Banner Format
```markdown
---
**LIMITATION**: This analysis has [data/method] limitations.
[Specific limitation description]
Confidence: [Low/Moderate/High]
Verdict may be affected: [Yes/No]
---
```

---

## Data Flow Summary

1. **Input**: User query in English or Vietnamese
2. **Pre-flight**: Language detection, requirement clarification
3. **Routing**: Chain-of-thought router determines execution plan
4. **Collection**: Evidence from museum records, extant parallels, academic sources
5. **Analysis**: Specialized agents analyze iconography, construction, materials, 3D
6. **Knowledge**: Query SECOND-KNOWLEDGE-BRAIN for Tier-labelled citations
7. **Synthesis**: Advisor produces risk-disclosed verdict with scenarios
8. **Validation**: Quality gates check all requirements
9. **Degradation**: Apply graceful degradation if needed
10. **Output**: Render structured report in target language

---

## Key Features

### Modular Architecture
- Router-based flexible execution
- Pluggable specialized agents
- Independent tool handlers
- Configurable hooks system

### Production-Grade
- Type-safe configuration
- Structured logging
- Comprehensive error handling
- Graceful degradation
- Automated testing

### Evidence Discipline
- Tier-labelled sources
- Evidence hierarchy enforced
- Confidence grading per element
- Scenario building (best/base/worst)
- Transparent disclosure

### Continuous Improvement
- Automated knowledge crawl
- Living knowledge base
- Gap flagging for research
- Community contributions

---

## Version History

### v2.0.0 (Current)
- Modular agent architecture
- Specialized domain skills
- Production-grade tooling
- Hooks system
- Comprehensive documentation

### v1.1.0
- Open-source hardening
- Production tooling
- Testing suite

### v1.0.0
- Initial harness
- Quality gates
- Knowledge pipeline

---

**Document Version:** 2.0.0
**Last Updated:** 2025-01-27
**Maintained By:** ancient-costume-mural-reconstruction project
