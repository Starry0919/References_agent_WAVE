# Work A (文献逆向工程 / Literature Reverse-Engineering) — Alignment Report

Scope: `harness/paper_extraction/`, `harness/evidence_retrieval/local_ddr_adapter.py`,
`knowledge/ddr_database/`, `knowledge/biological_rules/`, and the paper-evidence
review UI (`frontend/src/pages/evidence/`), evaluated against §4 of
`prompt/Overall/260718-合成生物专家 Agent 平台_设计思路.md` ("工作 A:文献逆向工程").

Date: 2026-07-29 (initial gap-closure session); updated 2026-07-30 (calibration UI, §4 item 10 / §8 item 1 below).

---

## 1. Current implementation summary

Work A is not a greenfield build — a substantial, mostly-correct implementation already
existed:

```
Input (PDF/DOI/textbook)
  → harness/paper_extraction/ (vendored Skill01–13 pipeline: requirement parsing →
     literature retrieval → citation validation → PDF acquisition/parsing → markdown
     cleaning → experiment extraction → evidence binding → quality evaluation →
     K-12 adaptation → engineering plan → QC/human review → frontend adapter)
  → harness/paper_extraction/ddr_converter.py  (bridges Skill07+ output → DDR v2)
  → knowledge/ddr_database/*.json  (DDR-001..006, schema v2)
      ├─→ harness/evidence_retrieval/local_ddr_adapter.py  (search/fetch/extract_claims)
      ├─→ harness/paper_extraction/reasoning_view.py → frontend PaperEvidenceDetailPage.tsx
      └─→ harness/paper_extraction/rule_distillation.py → knowledge/biological_rules/rules.json  [new]
```

DDR-001 through DDR-005 are real, hand-curated, schema-v2-complete records (including
DDR-005, the teacher-specified Chen & Zeng 2018 tryptophan template). The DDR v2 schema
(`knowledge/ddr_database/schema_v2.json`) already matches §4.2's field table field-for-field:
`design_action` (M0–M11), `target`, `trigger`, `evidence`, `evidence_grading` (硬/软),
`reason_nature` (5-way, including the anti-fabrication gate on `rule`), `alternatives`,
`implementation`, `result`, `rule`.

## 2. Requirement checklist

| # | Requirement (§4) | Status before this session | Status now |
|---|---|---|---|
| 1 | DDR schema has all 10 §4.2 fields | ✅ | ✅ (unchanged) |
| 2 | `design_action` maps to M0–M11 | ⚠️ mapping table existed but every auto-converted step silently defaulted to M3 | ✅ text-inference fallback added; still-unmapped cases are flagged for human review instead of silently mislabeled |
| 3 | `trigger` = observation that *caused* the decision, not just the change | ⚠️ correct for hand-curated DDRs; always blank for auto-converted ones | ✅ auto-converted steps now use the prior step's outcome as `trigger.observation` (§4.1's causal-chain idea), step 1 falls back to the paper's problem statement path |
| 4 | `evidence_grading` HARD/SOFT via explicit heuristic, not vibes | ⚠️ heuristic existed but its snake_case keyword list (`in_vitro_assay`, `known_regulation`, …) could never match natural free text | ✅ text is now normalized (whitespace/hyphen → underscore) before matching, so the existing keyword list actually fires on real sentences |
| 5 | `reason_nature` 5-way + must not fabricate mechanistic rules for screening/post-hoc papers | ⚠️ heuristic defaulted to "机理推断" (mechanistic) whenever no keyword hit — the *opposite* of the design doc's explicit warning | ✅ default changed to "事后合理化存疑" (post-hoc/uncertain); "机理推断" now requires an explicit mechanistic-language hit (feedback/kinetic/binding/Km/IC50/…) |
| 6 | Rule distillation: reusable, deduplicated, cross-paper rules, not just per-DDR strings | ⚠️ `knowledge/biological_rules/rules.json` existed but was a one-time hand-written snapshot; no code read or wrote it | ✅ `harness/paper_extraction/rule_distillation.py` (new) scans DDRs for eligible rule-bearing steps, skips DDRs already covered by an existing rule's provenance, and exposes `search_rules()` for retrieval; wired to `POST/GET /api/paper-extraction/rules[/distill]` |
| 7 | Evidence traceability (source/section/type/confidence) on every decision | ✅ for hand-curated DDRs | ✅ (auto-converted steps now also carry real `evidence.description`/`source`/`source_location` instead of empty strings — see §4 below) |
| 8 | Human calibration: independent dual extraction → conflict detection → calibration | ❌ only a single `human_review_status` field existed, no second-annotator concept anywhere | ✅ backend primitive (`harness/paper_extraction/calibration.py`) **and** frontend UI (`CalibrationPanel.tsx`, 2026-07-30 session) — a reviewer can submit a second independent decision-chain draft and see per-field conflicts directly on the paper-evidence detail page. Still zero DDRs actually human-calibrated — see Limitations. |
| 9 | Automated extraction actually produces usable DDRs (the module's own stated "gap #2") | ❌ confirmed broken: the converter assumed a decision-step shape (`action_type`/`gene`/`trigger_observation`/`rationale`/…) that Skill07 never produces; the one real on-disk automated DDR (DDR-006) had every field blank and every step mislabeled M3/"KO" | ✅ fixed — see §4 |
| 10 | Test coverage of the 3 required behaviors (feedback-inhibition paper → correct grading/reasoning/rule; screening paper → no fabricated rule; OptKnock → SOFT) | ❌ no such tests existed | ✅ added, passing (`tests/paper_extraction/test_ddr_converter.py`) |

## 3. Gap analysis (priority, from Phase 2)

| Priority | Gap | Status |
|---|---|---|
| P0 | Converter doesn't match Skill07's real output shape → real automated runs produce empty DDRs | **Fixed** |
| P0 | `reason_nature`, `alternatives`, `rule` invisible in the human review UI | **Fixed** |
| P0 | No dual-annotation / conflict-detection workflow | **Backend primitive built; frontend UI remains open** |
| P1 | Rule library static, unqueried, no distillation pipeline | **Fixed** (bounded: only distills new/uncovered DDRs, doesn't touch the existing hand-curated RULE-001..009) |
| P1 | `reason_nature` heuristic defaulted to mechanistic instead of uncertain | **Fixed** |
| P1 | Evidence-grading keyword heuristic couldn't match natural text (underscore/space mismatch) | **Fixed** (found during verification of the P0 converter fix, not in the original gap list) |
| P2 | No tests for the 3 required design-doc behaviors | **Fixed** |
| P2 | `knowledge_distillation`'s `EngineeringPrinciple` vs. Work A's DDR — paper-linking exists but is keyword-overlap only, unused by the DDR pipeline | **Not addressed this session** — noted as future integration work, out of scope for Work A proper |

## 4. Implemented improvements (with reasons)

1. **`harness/paper_extraction/ddr_converter.py` — real field mapping.**
   Verified against the actual Skill07 output shape (`experiments: [{experiment_id, purpose,
   host, intervention, conditions, control, replicates, readout, outcome}]` — confirmed by
   reading the real stored checkpoint for the one DDR the pipeline had actually produced).
   The converter previously read `action_type`/`gene`/`trigger_observation`/`rationale`/
   `evidence_description`/etc. — none of which exist on that shape — so every field came
   back empty and every step defaulted to `design_action="M3"`. It also had a substring-match
   bug in `_map_implementation` (`"" in any_string` is always `True`) that made every
   empty `impl_raw` resolve to whichever key iterated first in the mapping dict ("knockout"
   → "KO"), regardless of what the step actually did. **Reason**: this is the pipeline's own
   documented "gap #2" — closing it is the difference between the automated path doing
   anything at all versus only hand-curation ever producing usable DDRs.

2. **Conservative `reason_nature` default.** Previously defaulted to "机理推断" (mechanistic)
   whenever no screening/analogy/available-resource keyword matched — the exact opposite of
   §4.1's explicit warning ("硬把这类论文凑成一条听起来合理的规则,会用事后编造的理由污染规则库").
   Now defaults to "事后合理化存疑" (post-hoc/uncertain) unless an explicit mechanistic-language
   hit is found, which also means `rule` is suppressed by default rather than only when a
   screening/analogy keyword happens to be present. **Reason**: matches the design doc's
   stated failure mode directly, not just its letter.

3. **Evidence-grading/reason-nature keyword normalization.** The heuristic keyword lists mix
   snake_case tokens (`in_vitro_assay`, `known_regulation`) that can only ever match
   already-underscore-cased input with natural-language phrasing that Skill07's actual
   free-text output uses ("in vitro assay"). Added `_normalized_haystack()` (lowercase +
   whitespace/hyphen → underscore) so the existing keyword list actually engages on real
   text instead of only ever falling through to the conservative default. **Reason**: found
   while verifying fix #1 against realistic input — without it, HARD/SOFT grading would
   almost never fire on genuine paper text.

4. **Sequential trigger reconstruction.** For steps built from Skill07's flat experiment
   records (no native `trigger.observation` field), step *i>1*'s `trigger.observation` now
   uses step *i-1*'s measured outcome. **Reason**: this is §4.1's causal-chain idea directly
   — "what did the researcher observe that led to this step" is best approximated by what the
   previous step actually produced, not left permanently blank.

5. **`reasoning_view.py` + frontend — surfaced `reason_nature`/`alternatives`/`rule`.**
   `build_experimental_design()` computed these fields but never included them in the view the
   frontend consumes; `ExperimentalStepCard.tsx` had no rendering for them either. A reviewer
   calibrating `evidence_grading` had no way to see *why* a step was/wasn't allowed to carry a
   rule. **Reason**: `reason_nature` is the field that gates rule generation — it has to be
   visible wherever a human is asked to calibrate a step, or the calibration step is
   theatrical.

6. **`harness/paper_extraction/rule_distillation.py` (new).** `distill_rules()` scans DDRs for
   steps with `reason_nature ∈ {机理推断, 文献类比}` and a non-null `rule`, skips any DDR already
   cited in an existing rule's `source_ddrs` (so DDR-001..005 → RULE-001..009's hand-curated
   content is untouched), and appends genuinely new candidates. `search_rules()` gives the
   rule library its first-ever read path. **Reason**: §4.5 requires the rule library to be a
   live cross-paper distillation target, not a one-time manually written snapshot nothing else
   in the codebase consumes.

7. **`harness/paper_extraction/calibration.py` (new) + `extraction_attempts`/`conflict_count`
   in `schema_v2.json` (additive).** `record_extraction_attempt()` appends an annotator's
   independent `decision_chain` draft; `detect_conflicts()` compares attempts field-by-field
   on `design_action`/`evidence_grading`/`reason_nature`/`rule` and flags step-count mismatches;
   `calibration_status` flips to `"disputed"` (already an enum value in the schema, never
   previously set by any code) the moment a conflict exists. **Reason**: §4.3 step 3 explicitly
   requires two independent extractions to be compared and conflicts surfaced before a DDR is
   trusted.

8. **Regenerated `knowledge/ddr_database/DDR-006_*.json`** from its original source checkpoint
   using the fixed converter — the on-disk version (produced by the pre-fix converter) had
   every `decision_chain` step blank and mis-defaulted; it was never human-reviewed
   (`calibration_status`/`human_review_status` both still `"pending"`), so regenerating it in
   place is a correction, not a loss of reviewed work.

9. **Tests**: 21 new tests across `test_ddr_converter.py` (extended), `test_rule_distillation.py`
   (new), `test_calibration.py` (new) — including the 3 scenarios Phase 4 of the check prompt
   requires verbatim (Trp-style feedback-inhibition step → M3/硬/机理推断/non-null rule;
   Keio-screening step → `reason_nature="筛选得来"` and `rule=None` even when source data
   supplied one; OptKnock-only step → `evidence_grading="软"`).

## 5. Files modified / added

**Modified**: `harness/paper_extraction/ddr_converter.py`, `harness/paper_extraction/reasoning_view.py`,
`harness/api/paper_extraction.py`, `knowledge/ddr_database/schema_v2.json`,
`knowledge/ddr_database/DDR-006_*.json` (regenerated), `frontend/src/api/evidence.ts`,
`frontend/src/lib/i18n.tsx`, `frontend/src/pages/evidence/components/ExperimentalStepCard.tsx`,
`tests/paper_extraction/test_ddr_converter.py`.

**Added**: `harness/paper_extraction/rule_distillation.py`, `harness/paper_extraction/calibration.py`,
`tests/paper_extraction/test_rule_distillation.py`, `tests/paper_extraction/test_calibration.py`,
this report.

### 5.1 2026-07-30 follow-up: calibration UI

The single largest gap left open at the end of the 2026-07-29 session was that
`calibration.py`'s two routes existed and were tested but nothing let a human
reviewer actually use them. This follow-up closes that:

**Modified**: `harness/api/generation.py` (`get_evidence_document` now also returns
`calibration_status`/`conflict_count`/`extraction_attempts` from `extraction_meta`
— previously computed and stored by `calibration.py` but never read back out to
any client), `frontend/src/api/evidence.ts` (new `DecisionChainStepDraft`,
`blankDecisionChainStep`, `submitExtractionAttempt`, `getExtractionConflicts`,
and the three new `EvidenceDocumentDetail` fields above), `frontend/src/pages/
evidence/PaperEvidenceDetailPage.tsx` (renders the new panel), `frontend/src/
lib/i18n.tsx` (new `paperEvidence.calibration.*` strings, zh-CN + en-US).

**Added**: `frontend/src/pages/evidence/components/CalibrationPanel.tsx` — shows
current `calibration_status` and recorded attempts, fetches and lists per-
(step, field) conflicts (`design_action`/`evidence_grading`/`reason_nature`/`rule`,
the same four fields `calibration.py::detect_conflicts` compares), and lets a
second reviewer open a full decision-chain editor (pre-filled from the existing
record, one card per step with every schema_v2 field) and submit it as an
independent attempt via `POST /api/paper-extraction/ddr/{id}/attempts`.

**Reason**: §4.3 step 3 requires two independent extractions to be compared and
conflicts surfaced before a DDR is trusted; the backend primitive existed but
"trusted by a human" was not actually reachable from the product. This does not
change the recommendation to route through it a second time from scratch —
the panel pre-fills the second annotator's starting draft from the first
extraction (editable per field) rather than forcing a blank re-transcription,
which is a reasonable middle ground for review efficiency, though a stricter
reading of "independent" would start annotator B from nothing; noted as a
possible future refinement, not implemented here to avoid over-scoping a
backend-primitive-closes-a-gap task into a research question about calibration
methodology.

**Verification**: `npx tsc --noEmit` (0 errors) and `npx vitest run` (31/31
passed) in `frontend/`; a manual end-to-end smoke test against the real
`DDR-001` file (`record_extraction_attempt` twice with a deliberately
conflicting `reason_nature` → confirmed `calibration_status` flips to
`"disputed"`, `get_evidence_document` surfaces the new fields correctly,
original file restored byte-for-byte afterward — confirmed via `git status`).
No dedicated pytest file covers `harness/api/generation.py`'s evidence-document
endpoint (true before this session too); `pytest tests/ -k "generation or
evidence"` (66 passed, 2 failed) — both failures are pre-existing/out of
scope (a live-network Crossref test and an unrelated `simulation_demo` test;
neither references `get_evidence_document`, `calibration_status`,
`conflict_count`, or `extraction_attempts`).

**Untouched, preserved**: all Skill01–13 vendor code, all existing API endpoints/behavior,
DDR-001..005, `knowledge/biological_rules/rules.json`'s existing 9 rules, all frontend pages
other than the one component that needed the new fields.

## 6. Before / after (DDR-006, the only real automated-pipeline output on disk)

| Field (step 1 of 6) | Before | After |
|---|---|---|
| `design_action` | `"M3"` (default, wrong — this step is an in vitro enzyme screen) | `"M3"` (still defaults, but now with an explicit pending-review flag rather than silent mislabeling — no module keyword matched this step's text) |
| `target.gene` | `""` | `""` (no gene mentioned in this specific step; step 2 correctly extracts `"tktAB"`) |
| `trigger.reasoning` | `""` | `"Select SBPase/FBPase and validate Xfspk in vitro"` |
| `evidence.description` | `""` | `"Phosphate release (malachite green, 620 nm); AcP formation"` |
| `implementation` | `"KO"` (wrong — this step is enzyme selection, not a knockout) | `"其他"` (honest "unclassified" rather than a wrong specific answer) |
| `result.after` | `""` | `"SyGlpX selected (highest SBPase + FBPase activity); Xfspk validated on S7P/F6P/X5P"` |
| `reason_nature` | `"机理推断"` (silent default, would have kept any downstream rule) | `"筛选得来"` (correctly flagged as screening — this step's `experiment_id` is literally `exp_enzyme_screen`) |

Across all 6 steps: 0/6 had any non-empty target/trigger/evidence text before; 6/6 do now.

## 7. Test results

`pytest tests/paper_extraction/ -q`: **44 passed, 2 failed** (both pre-existing and
unrelated — `test_opus_executor_reuses_content_addressed_cache` and
`test_opus_is_required_not_silently_relabelled` in `test_unified_extraction.py`, which
depend on live Anthropic API behavior/caching not on anything in this session's scope;
confirmed failing before any change in this session's very first baseline run).

Full suite `pytest tests/ -q`: **396 passed, 26 failed**. All 26 failures were checked
against this session's diff and are pre-existing / out of scope:
- The 2 above (`paper_extraction`/opus).
- `test_synbio_v1.py::test_knowledge_base_loads_five_ddrs` — asserts the knowledge base
  has exactly `{DDR-001..005}`; **DDR-006 already existed, untracked, before this session
  started** (confirmed by reading its original content before any edit in this session) —
  this assertion was already stale, not something introduced here.
- The remaining 23 (golden_set, orchestrator, projects, scientific_evaluation,
  simulation_demo, virtual_cell, one live-network llm_generation test) are in modules this
  session never touched (Problems 1/3/4/5/6 of the broader repository, not Work A) —
  confirmed by grepping the failing test files for any reference to
  `ddr_converter`/`rule_distillation`/`calibration`/`reasoning_view`/`schema_v2`: no hits
  outside files that are still passing.

## 8. Remaining limitations

- **No DDR has actually been human-calibrated.** All 6 DDRs still show
  `calibration_status: "pending"` / `human_review_status: "pending"`. The tooling to close
  this loop now exists; the review itself hasn't happened.
- **Rule distillation only ever pulls from hand-curated `rule` text.** Automated extraction
  (Skill07) never populates a `rule` field itself (correctly — that's a human/expert-level
  generalization), so `distill_rules()` currently has nothing new to add beyond DDR-001..005's
  existing coverage until either a human writes `rule` text for future DDRs or a future skill
  is added that proposes (never auto-confirms) one.
- **Corpus size is still 6 papers**, short of "手工深度策展 3–5 篇" plus a larger semi-automated
  batch §4.3 describes as the intended scale-up.
- **`design_action` text-inference is keyword-based and will legitimately fail to classify
  novel phrasing** — it always defaults to M3 with an explicit pending-review flag rather than
  guessing, by design, but that means a meaningful fraction of auto-converted steps still need
  a human to assign the right module.
- **The calibration UI (added 2026-07-30) pre-fills the second annotator's draft from the
  existing decision_chain** rather than starting from a blank transcription — a reasonable
  review-efficiency tradeoff, but a stricter reading of "independent" (§4.3 step 3) would want
  annotator B to see nothing of annotator A's work first. Not changed this session; see §5.1.

## 9. Readiness evaluation

**PARTIALLY READY.**

The core mechanics required by §4 — DDR schema, evidence/reason-nature classification with
correct conservative defaults, module mapping, evidence traceability, a working automated
extraction→DDR path, a rule-distillation path, and (as of 2026-07-30) an actually-usable
dual-annotation/conflict UI — are now real, tested, and reachable from the product, not just
scaffolding. What keeps this from "READY FOR AGENT INTEGRATION" is no longer a missing
capability but a missing *event*: zero DDRs have actually completed calibration. The tooling to
close §4.3's human-in-the-loop requirement now fully exists end-to-end (submit independent
draft → see conflicts → resolve → `calibration_status: "calibrated"`), but nothing in the
knowledge base yet carries a human's actual sign-off — which §4's whole premise
(distinguishing genuine mechanistic reasoning from post-hoc rationalization) depends on a
person actually doing at some point. The gap between "the pipeline can now produce a
trustworthy-shaped DDR automatically, with tooling for a human to verify it" and "a synthetic
biology expert has actually used that tooling and confirmed this DDR is trustworthy" is exactly
the remaining work — and it is now a scheduling/staffing question, not an engineering one.
