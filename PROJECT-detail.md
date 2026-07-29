# PROJECT-detail.md — Skill 240: ancient-costume-mural-reconstruction

## Executive Summary

`ancient-costume-mural-reconstruction` is a professional-grade harness for
Claude Code targeting the **Ancient Costume Reconstruction & Archaeological
Textile History** domain. It transforms Claude into a domain-expert that
delivers structured, evidence-backed outputs by combining real-time data
aggregation, recognized domain methods, and academic research into a single
orchestrated workflow ending in a risk/limitation-disclosed reconstruction
proposal. A continuously-updated knowledge crawl pipeline keeps the skill
current with new research.

---

## Problem Statement

Practitioners in this domain face three structural gaps:
1. **Data fragmentation**: authoritative data scattered across museums,
   journals, and conservation bodies.
2. **Methodology gaps**: most advice lacks systematic, evidence-graded
   methods and the extant-textile-first hierarchy.
3. **No self-improvement**: static tools don't learn from new research.

This skill addresses all three via real-time aggregation, professional
frameworks, and a continuously-updated knowledge crawl pipeline.

---

## Target Users & Use Cases

| User | Trigger Example | Skill Response |
|------|----------------|----------------|
| Practitioner | "Reconstruct the court robe in Mogao Cave 220 (Tang)" | Full evidenced reconstruction report |
| Curator | "How confident is a reconstruction of this fragmentary Coptic tunic?" | Confidence-graded assessment with scenarios |
| Conservator | "Assess dye/material evidence for this Sassanian relief" | Materials/dye evidence review with remediation |
| Researcher | "Compare Han vs Tang women's upper garment reconstructions" | Side-by-side scorecard with evidence-based winner |
| Learner | "Explain the evidence hierarchy for ancient-costume reconstruction" | Educational framing with evidence |

---

## Harness Architecture

```
USER INPUT
    │
[main.md — ancient-costume-mural-reconstruction]
    │
├──► sub-gather-requirements  → structured requirements (object + period/culture + scope)
├──► sub-evidence-collector   → evidence bundle (museum records + extant parallels + docs)
├──► sub-core-analysis        → iconography → construction → materials/dyes → 3D reconstruction
├──► sub-knowledge-updater    → Tier-labelled citations + crawl gaps
├──► sub-advisor              → risk-disclosed conclusion + evidence chain + remediation
    │
└──► [QUALITY GATE — main.md]
        ✓ U1–U6 universal + G1–G4 domain gates
        ✓ Disclosure before recommendation
        ✓ Output formatted per template
```

---

## Full Sub-Skill Catalog

### 1. `sub-gather-requirements.md`
- **Purpose:** Clarify the object of analysis, constraints, timeframe, available inputs, target audience, and language before any data fetching.
- **Role:** intake specialist for an Ancient Costume Reconstruction & Archaeological Textile History engagement.
- **Inputs:** Raw user message + any provided materials/inputs.
- **Outputs:** Structured requirements: `{object, scope, timeframe, available_inputs, target_audience, language, analysis_type}`.
- **Tools:** Conversation only (no external tools).
- **Quality Gate:** At least one object of analysis (object + period/culture) confirmed before proceeding; at most 2 clarifying questions.

### 2. `sub-evidence-collector.md`
- **Purpose:** Fetch authoritative real-time and reference data: museum collection records, extant textile parallels, iconographic comparanda, period standards, and recent academic developments.
- **Role:** Ancient Costume Reconstruction & Archaeological Textile History data librarian.
- **Inputs:** Requirements object from Step 1.
- **Outputs:** Evidence bundle: `{current_collection_records, extant_parallels, authoritative_docs, recent_developments, reference_benchmarks}` with source + Tier label + access date per item.
- **Tools:** WebSearch, WebFetch (museum + academic sources); image analysis (vision); Read (SECOND-KNOWLEDGE-BRAIN.md for cached benchmarks).
- **Quality Gate:** At least one current collection record + 1 authoritative document retrieved, or an explicit limitation flag if unavailable; degradation level stated.

### 3. `sub-core-analysis.md`
- **Purpose:** Reconstruct from iconography: analyze garment form, drape, layering, accessories, status markers; recover period construction (pattern, seaming, draping) and materials/dyes; apply the evidence hierarchy; produce an evidence-graded 3D reconstruction with best/base/worst scenarios.
- **Role:** ancient-costume reconstruction & textile-history specialist.
- **Inputs:** Iconographic sources, period, target garment, language, evidence bundle.
- **Outputs:** Analysis + construction + materials/dyes + evidence hierarchy + 3D reconstruction + scenarios.
- **Tools:** Image analysis (vision); Read (SECOND-KNOWLEDGE-BRAIN.md §1, §3); WebFetch (museum collection APIs, textile-history references).
- **Quality Gate:** G1 iconographic analysis done; G2 construction & materials/dyes recovered; G3 evidence hierarchy stated and applied per claim; G4 3D reconstruction produced (layer build, scale cm, per-panel material, confidence H/M/L).

### 4. `sub-knowledge-updater.md`
- **Purpose:** Query SECOND-KNOWLEDGE-BRAIN.md for authoritative academic and professional evidence; surface 3–5 citations with Tier labels and flag gaps for the crawl pipeline.
- **Role:** research librarian for Ancient Costume Reconstruction & Archaeological Textile History.
- **Inputs:** Topic keywords from the current analysis.
- **Outputs:** 3–5 knowledge-base citations with Tier labels + flagged gaps (crawl queries) + coverage rating.
- **Tools:** Read (SECOND-KNOWLEDGE-BRAIN.md); WebSearch (gap-fill, max 2 queries); Bash (`tools/knowledge_updater.py --dry-run`, optional).
- **Quality Gate:** At least 1 academic/authoritative source surfaced; coverage rating (Strong/Moderate/Weak) provided; gaps converted to crawl queries.

### 5. `sub-advisor.md`
- **Purpose:** Synthesize all prior analysis into a risk-disclosed conclusion with a full evidence chain and recommended actions.
- **Role:** senior Ancient Costume Reconstruction & Archaeological Textile History advisor.
- **Inputs:** Core analysis scorecard + evidence bundle + knowledge-base evidence.
- **Outputs:** Conclusion (exactly one verdict category) + scenarios + key risks (≥3, with probability & impact) + evidence chain + remediation + mandatory disclosure (before the conclusion).
- **Tools:** Reasoning / synthesis; `Skill("sub-knowledge-updater")` optional.
- **Quality Gate:** Conclusion is exactly one of: Evidence-Based Reconstruction / Plausible (interpretive) / Speculative / Inconclusive; disclosure appears before the conclusion.

---

## Skill File Format Specification

```markdown
---
name: {skill-name}
description: {one-line summary}
---
## Role & Persona
## Workflow (Harness Flow)
## Sub-skills Available   (main.md only)
## Tools
## Output Format
## Quality Gates
```

---

## E2E Execution Flow

```
1. User invokes /ancient-costume-mural-reconstruction [query]
2. main.md → sub-gather-requirements → structured requirements
3. sub-evidence-collector → evidence bundle
4. sub-core-analysis → iconography + construction + materials + 3D + scenarios
5. sub-knowledge-updater → academic evidence entries + crawl gaps
6. sub-advisor → risk-disclosed conclusion + evidence chain
7. main.md Quality Gate → verify U1–U6 + G1–G4, auto-fix, deliver
```

**Error handling:** primary sources fail → fallback chain → knowledge base →
explicit limitation flag; never silently proceed with stale data.

---

## SECOND-KNOWLEDGE-BRAIN Integration

- **Sources crawled:** ArXiv (cs.GR/CV/AI), Semantic Scholar keyword clusters,
  Crossref (DOI enrichment), RSS feeds (Textile Society, Costume Society).
- **Crawl config:** `KnowledgeConfig` dataclass in `tools/knowledge_updater.py`;
  overridable via JSON config file (`--config`) or CLI flags.
- **Dedup:** SHA-256 of the normalized DOI/URL (case/whitespace-insensitive;
  `https://doi.org/` prefix stripped).
- **Scoring:** composite 0–10 = `recency(0.4) + keyword_relevance(0.4) + citation_count(0.2)`.
- **Safety:** backup-before-write; idempotent append; graceful degradation.

---

## Quality Gates Definition

Universal gates U1–U6 (see library SKILL-STANDARD.md) plus the domain gates
defined in `skills/main.md`: G1 (iconography), G2 (construction & materials),
G3 (evidence hierarchy), G4 (3D reconstruction). Each gate has an auto-fix and
an enforcement logic; after 2 failed retries a gate is flagged as a limitation.

---

## Test Scenarios

See `tests/test-scenarios.md` for 5 concrete end-to-end scenarios (standard,
minimal-input, comparison, risk/conflict, degraded-mode) exercising all gates
and all four verdict categories. `tools/run_test_scenarios.py` runs them
offline and emits a JSON report on request.

---

## Key Design Decisions

1. Domain sub-skills kept separate (distinct methods/data).
2. Extant-textile-first evidence hierarchy enforced; iconography never
   overrules an extant parallel on construction/materials.
3. Disclosure enforced at the quality-gate level, not optional.
4. SECOND-KNOWLEDGE-BRAIN as living memory updated by the crawl pipeline.
5. Graceful degradation to knowledge base with explicit limitation flags.
6. Production-grade tooling: dataclass config, logging, backup-before-write,
   DOI-normalized dedup, structured unittest suite, offline scenario runner.
7. Open-source scaffolding (LICENSE, CONTRIBUTING, COC, CHANGELOG,
   pyproject.toml) for community contribution.

---

## Idea (Vietnamese)

> Tạo Agent "Chuyên gia Phục dựng và Phân tích Trang phục Cổ đại qua Tranh tượng", tự động tái tạo mô hình 3D của trang phục cổ, đưa ra các đề xuất chất liệu dựa trên các phương pháp đánh giá uy tín trên thế giới và đưa ra các đề xuất, giải pháp cải tiến, không ngừng đi crawl data từ các tài liệu khảo cổ học trang phục hoặc document uy tín liên quan để cập nhật kiến thức cho Agent ngày càng tốt hơn, xu hướng hơn.