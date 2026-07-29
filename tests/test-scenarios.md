# test-scenarios.md — Skill 240: ancient-costume-mural-reconstruction

Five concrete end-to-end scenarios for the ancient-costume harness. Each lists
the trigger, the required outputs, the expected verdict, and the applicable
quality gates. Together they exercise all universal gates U1–U6, all domain
gates G1–G4, and all four verdict categories. The orchestrator
`tools/run_test_scenarios.py` implements these scenarios offline (no network,
no LLM) and validates gate coverage.

---

## Scenario 1: Standard analysis — Tang dynasty court robe (Mogao Cave 220)

- **Trigger:** Reconstruct the court robe depicted in Mogao Cave 220 (Tang
  dynasty) from the mural; recover construction, materials, dyes, and propose
  a 3D reconstruction.
- **Expected outputs:** iconographic_sources, garment_form_drape,
  construction_pattern, materials_dyes, evidence_hierarchy, 3d_reconstruction,
  academic_citations, scenarios_best_base_worst, risk_disclosure.
- **Expected verdict:** Evidence-Based Reconstruction.
- **Gates:** U1–U6 + G1, G2, G3, G4.

## Scenario 2: Minimal-input analysis (defaults)

- **Trigger:** `analyse an ancient roman tunic, period 1st c. AD`.
- **Expected outputs:** stated_assumptions, iconographic_sources_best_effort,
  construction_inferred, materials_inferred, evidence_hierarchy_stated,
  3d_best_effort, limitation_notice.
- **Expected verdict:** Plausible (interpretive).
- **Gates:** U2, U4, U5, U6 + G1, G2, G3, G4.
- **Notes:** defaults applied with explicit `[inferred]` / `[default]` flags;
  never fabricate missing values; best-effort hierarchy and 3D proposal still
  produced under graceful degradation.

## Scenario 3: Comparison scenario — Han vs Tang women's upper garment

- **Trigger:** Compare the upper garment of Han dynasty vs Tang dynasty women
  as depicted in tomb murals; which reconstruction is better supported?
- **Expected outputs:** comparison_table, iconography_both, construction_both,
  materials_dyes_both, evidence_hierarchy_both, 3d_reconstruction_both,
  academic_citations, winner_statement.
- **Expected verdict:** Evidence-Based Reconstruction.
- **Gates:** U1, U3, U6 + G1, G2, G3, G4.
- **Notes:** side-by-side scorecard; sub-core-analysis applied to both objects;
  evidence-based winner with stated precedence.

## Scenario 4: Risk / conflict scenario — fragmentary Coptic burial textile

- **Trigger:** Assess how confident a reconstruction can be for a fragmentary
  Coptic tunic (4th c. AD) where iconography is partial and no extant parallel
  exists; resolve conflicting dye interpretations.
- **Expected outputs:** conflict_resolution, precedence_statement,
  multi_scenario_risk, key_risks_min_3, evidence_chain, remediation,
  disclosure_before_conclusion, iconographic_sources, construction_pattern,
  evidence_hierarchy, 3d_reconstruction.
- **Expected verdict:** Speculative.
- **Gates:** U2, U6 + G1, G2, G3, G4.
- **Notes:** conflicting reconstructions resolved by stated precedence
  (extant > iconographic > textual); multi-scenario (best/base/worst) risk
  output with ≥3 key risks (probability + impact).

## Scenario 5: Degraded-mode scenario — Sassanian royal robe

- **Trigger:** Reconstruct a Sassanian royal robe from a damaged relief where
  museum databases are offline and the knowledge base has no direct entry.
- **Expected outputs:** limitation_notice_level_2_3, fallback_chain,
  no_fabricated_values, knowledge_gap_flags, iconographic_sources_best_effort,
  construction_inferred, evidence_hierarchy_stated, 3d_best_effort.
- **Expected verdict:** Inconclusive.
- **Gates:** U2, U6 + G1, G2, G3, G4.
- **Notes:** fallback chain + LIMITATION notice (degradation Level 2–3); no
  fabricated values; knowledge gaps flagged as crawl queries; verdict maps to
  Inconclusive when the missing input is decisive.

---

### Gate coverage matrix

| Gate | S1 | S2 | S3 | S4 | S5 |
|------|----|----|----|----|----|
| U1 | ✓ | – | ✓ | – | – |
| U2 | ✓ | ✓ | – | ✓ | ✓ |
| U3 | ✓ | – | ✓ | – | – |
| U4 | ✓ | ✓ | – | – | – |
| U5 | ✓ | ✓ | – | – | – |
| U6 | ✓ | ✓ | ✓ | ✓ | ✓ |
| G1 | ✓ | ✓ | ✓ | ✓ | ✓ |
| G2 | ✓ | ✓ | ✓ | ✓ | ✓ |
| G3 | ✓ | ✓ | ✓ | ✓ | ✓ |
| G4 | ✓ | ✓ | ✓ | ✓ | ✓ |

`✓` = applicable and asserted; `–` = not applicable for the scenario type.

### Verdict coverage

Evidence-Based Reconstruction (S1, S3), Plausible (interpretive) (S2),
Speculative (S4), Inconclusive (S5) — all four verdict categories exercised.

---

## Running the scenarios

```bash
python tools/run_test_scenarios.py --all            # all 5 scenarios + validation
python tools/run_test_scenarios.py --scenario 3      # single scenario
python tools/run_test_scenarios.py --validate        # 8-File Contract checks only
python tools/run_test_scenarios.py --all --json report.json   # machine-readable report
```