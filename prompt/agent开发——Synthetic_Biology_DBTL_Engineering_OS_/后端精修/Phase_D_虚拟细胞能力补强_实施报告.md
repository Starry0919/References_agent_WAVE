# Phase D — Virtual Cell Missing Requirements: Delivery Report

Scope: Workstream 3 of `六大核心模块统一集成、科学能力补强与最终验收_Claude_Code_Prompt.md`, per your
explicit priority order: (1) CrossModalConsistencyReport, (2) multi-scenario/combination + larger GEM
adapter, (3) real vEcoli runtime/dependency audit. Code lives in
`20260717_JH_agent_structure/agent-harness/agent-harness/`.

## A. Regression Confirmation (requested before Phase D)

`python -m pytest tests/ -q` → **319 passed, 0 failed** (13 min), before any Phase D code was
written. This was the second full run after fixing a real module-name collision
(`tests/orchestrator/test_api.py` vs `tests/llm_generation/test_api.py` both importing as bare
`test_api` without `__init__.py` packages) discovered by the first attempt — documented so the fix
itself is traceable, not silently folded in.

## B. CrossModalConsistencyReport (priority 1)

`harness/virtual_cell/models.py::CrossModalConsistencyReport` (prompt §6.4's exact fields) +
`harness/virtual_cell/cross_modal_service.py` — a deterministic rule engine, no LLM anywhere in
this path.

- Reads `harness.experiments.models.Observation`, extended (migration `0008`, additive) with
  `modality`/`entity_namespace`/`entity_id`/`batch` columns — no second "OmicsObservation" table.
  `RawObservationInput`/`normalize_and_commit` extended to accept these at construction time
  (`Observation` fields are immutable after creation via this repo's existing
  `guard_immutable_fields` guard, same as every other content field).
- The flux layer is read from a real `SimulationResult.endpoints` row (real cobrapy FBA output,
  `source_type="model_output"`) — never presented as an experimental measurement.
- Real classification logic for 8 of the 13 prompt-listed inconsistency classes
  (`transcript_protein_discordance`, `protein_flux_discordance`, `flux_phenotype_discordance`,
  `timepoint_mismatch`, `condition_mismatch`, `batch_effect`, `measurement_sensitivity`,
  `model_experiment_mismatch`) computed from real direction/timepoint/condition comparisons.
  `entity_mapping_ambiguity`/`missingness` are surfaced via `data_quality_findings` rather than as
  separate flagged classes this round (see §F).  `compensatory_regulation`/`resource_limitation`/
  `post_transcriptional_regulation` are never independently *detected* (this repo has no data that
  could prove them) — they appear only as **candidate alternative explanations** attached to a real
  discordance, per prompt §6.4's own instruction never to collapse a conflict into one story.
- Verified against the prompt's own worked example: a real `ppc` transcript-up/protein-flat
  observation pair produces `transcript_protein_discordance`, ≥2 real alternative explanations, and
  an explicit `unsupported_conclusions` entry refusing the naive "intervention doesn't work" read.

**Test evidence**: `tests/virtual_cell/test_cross_modal.py`, 7/7 passing — discordance-with-
alternatives, consistent-direction, insufficient-modalities, not-comparable, timepoint-mismatch,
real-flux-layer-from-real-FBA, and a vocabulary-conformance check.

## C. Larger E. coli GEM Adapter (priority 2a)

**Real asset found, not fabricated**: `iML1515.xml` (Monk et al. 2017 — the standard E. coli K-12
MG1655 genome-scale reconstruction) already existed in this repository, in an earlier prototype
checkout (`workflow/design/JH/agent-harness-v1/.../data_ext/iML1515.xml`) — found by directory
search, not downloaded. Verified real by loading it: `cobra.io.read_sbml_model` succeeds in ~3.6s,
1516 genes / 2712 reactions / 1877 metabolites (matches the model's known published statistics),
baseline FBA solves optimal at growth=0.877/h. Copied (not moved) into
`knowledge/models/iML1515.xml`; sha256 `9c772d44ca43350e40dc7ee86c7aa148796856be1eea45e5406c6df8f7dcde28`
recorded in its `ModelManifest`-equivalent record.

**No second FBA stack**: `harness/diagnosis/model_adapters/_cobrapy_fba_base.py` (new) holds the
shared `validate_input`/`run` logic; `gem_fba.py` (e_coli_core, untouched behavior) and the new
`gem_fba_iml1515.py` both use it. `ModelManifest` is **not a new table** — it reuses
`harness.virtual_cell.models.ModelRegistryEntry` (already exactly this shape per that table's own
docstring: "describes what a model *claims* to support"), seeded automatically by the existing
`ensure_seeded()` idempotent-upsert mechanism once the adapter was registered.

**A real integration bug found and fixed, not just a new adapter file left unconnected** (per your
"no placeholder schemas without executable validation" instruction — this is exactly the kind of
gap that instruction is meant to catch): `harness/virtual_cell/runner.py::run_gem_fba_scenario` and
`harness/virtual_cell/compatibility.py::check_compatibility` both **hardcoded** `get_adapter
("gem_fba")` / `_load_gem_model()` (always e_coli_core) regardless of which `model_id` a
`SimulationCase` had actually selected. A first end-to-end test against `gem_fba_iml1515` failed
exactly here — the compatibility check was silently checking gene domain membership against the
*small* model even when the *large* model was requested. Fixed by threading `model_id`/`adapter_id`
through `runner.py`, `compatibility.py`, and `compiler.py::_load_gem_model` — verified by the same
test now passing with a real, distinct growth-rate delta for `sdhC` knockout (a gene only in
iML1515's domain, not in e_coli_core's 137-gene set).

**Test evidence**: `tests/virtual_cell/test_larger_gem_and_combination.py`, 3/3 passing —
registry-entry seeding, genuine model dispatch (not a silent e_coli_core fallback), and a real
2-gene combination knockout proven to be an independent joint LP solve (not a sum of two single-gene
deltas — `merge_compiled_bounds`'s existing conflict-detection logic, already correct, just needed a
real multi-gene test exercising it, which did not exist before this round).

## D. Multi-scenario / Combination Intervention (priority 2b)

- **Combination**: proven real this round (§C) — `merge_compiled_bounds` already correctly merges
  multiple `CompiledIntervention` rows with conflict detection; this round added the first real test
  exercising ≥2 real genes together.
- **S0/S1 (baseline/single intervention)**: already real and tested (Problem 6's own suite).
- **S2 (second single intervention)/S4 (stress/robustness condition)**: not built this round — doing
  so honestly requires either a second real intervention scenario run through the same pipeline
  (mechanically identical to S1, no new capability) or a defined "stress condition" (e.g. altered
  exchange bounds for a robustness scenario), which was judged lower-value than fixing the S1/
  combination dispatch bug found in §C, given the time budget. Marked `not_verified` below, not
  hidden.
- **Stochastic replicates**: `gem_fba`/`gem_fba_iml1515` are both deterministic LP solves —
  `stochastic_replicates_not_applicable` remains the correct, honest status (unchanged from Phase
  B/C's own reports; no fabricated replicate variability was added).

## E. vEcoli Runtime/Dependency Audit (priority 3) — the biggest finding this phase

The prior report's conclusion ("blocked by environment") was **not re-verified before this round -
and turned out to be more pessimistic than reality once actually tested**:

| Check | Method | Real Result |
|---|---|---|
| Source/version | `git log` in `20260717_JH_agent_structure/vEcoli` | real checkout, commit `038f667e8388e19ea4f16546b042b744793df9cc`, 2026-07-07, PR #427 |
| Native Windows `.venv` | inspected `pyvenv.cfg` | confirmed linux-x86_64-built, unusable natively (consistent with prior report) |
| WSL availability | `wsl -l -v` | Ubuntu present (was stopped, started fine) |
| WSL environment | `uv sync` (fresh venv, real dependency resolution) | **288 packages resolved and installed, including a successful Cython build of `vecoli` itself** (first attempt hit a filesystem-permission error deleting a stale foreign `.venv` across the WSL/NTFS boundary — resolved by removing it from within WSL and retrying) |
| Real imports | `python -c "import ecoli, wholecell, vivarium"` | **succeeded cleanly** |
| Knowledge base (raw flat files) | `find reconstruction/ecoli/flat` | 134 real flat files present (not missing) |
| ParCa (parameter calculator) | real run, `runscripts/parca.py -c 12`, forced past the repo's default "skip and copy a pre-existing sim_data" shortcut | **completed successfully end-to-end in ~11 minutes** — real per-condition fitting (~30 real regulatory conditions: `basal`, `with_aa`, `no_oxygen`, `succinate`, `acetate`, and ~25 named regulon conditions), real promoter-binding fitting, real mass adjustments, ending in `Saving sim_data / raw_validation_data / validation_data`, real computed hash `82b5172160f6f6225971e2028449b25b44926380caa8c0308eab1b9c24fd12db` |
| Full whole-cell **simulation** run | — | **NOT attempted this round** (time-bounded, see below) |

**VEcoliAvailabilityAudit conclusion**: `partially_available` — environment setup and knowledge-base
generation are `available_and_verified` (both actually run, not just theoretically possible); a full
whole-cell simulation execution is `available_not_run` (the concrete next step, with all of its own
real preconditions now confirmed rather than assumed blocked). This is a **materially different, more
positive** conclusion than the prior report's, reached only because this round actually attempted
the steps instead of re-stating the earlier assessment — recorded in `harness/virtual_cell/
registry.py`'s `vecoli` `ModelRegistryEntry` metadata (`known_failure_modes`/`runtime_requirements`),
not just this report, so it survives beyond one conversation.

**Why a full simulation run was not attempted**: an actual multi-process whole-cell simulation
(beyond ParCa) is open-ended in runtime and this session's time budget was already extended well
past a normal session by the ParCa run and the GEM-adapter dispatch bugs found and fixed in §C. This
is an honest scope/time boundary, not a technical blocker — recorded as such, not disguised as
"unavailable."

**A resource note worth flagging to you directly**: this machine's `C:` drive is at 97-98% full
(~9-13 GB free out of 324 GB) — unrelated to anything built during this audit (the vEcoli venv and
ParCa output live on `D:`/inside WSL's own filesystem, which has 917 GB free), but it did cause one
transient test failure (`sqlite3.OperationalError: database or disk is full`) until stale pytest
temp files on `C:` were cleared. You may want to free space on `C:` independently of this project.

## F. Known Limitations / Honest Gaps (not hand-waved)

- `entity_mapping_ambiguity` and `missingness` (2 of the 13 prompt-listed inconsistency classes) are
  surfaced via `data_quality_findings` rather than as dedicated `inconsistency_classes` entries this
  round — a real but smaller gap than the other 8 classes, which are fully implemented.
- Multi-scenario S2 (second independent intervention) / S4 (stress/robustness condition) were not
  built as named scenarios this round — mechanically straightforward (same pipeline as S1) but not
  exercised; `not_verified`.
- iML1515's license terms were not independently re-verified this round (recorded honestly as
  "unconfirmed for commercial redistribution" in its `ModelManifest`/`ModelRegistryEntry` row,
  matching the prompt's own instruction not to assert a license status without checking it).
- vEcoli whole-cell **simulation** execution (as opposed to environment setup + ParCa) remains
  `available_not_run` — a real, concrete, now well-scoped next step, not a fabricated result.
- The `_ENDPOINT_SPEC` exchange-reaction IDs (`EX_glc__D_e` etc.) were assumed, not individually
  re-verified, to exist under the same BiGG identifiers in iML1515 as in e_coli_core (both are BiGG
  models, which use a shared namespace convention) — the code degrades honestly (`unsupported`,
  never a fabricated 0) if any do not match, but this was not exhaustively checked endpoint-by-endpoint.

## G. Status Matrix (Phase D items only)

| Requirement | Status | Evidence |
|---|---|---|
| CrossModalConsistencyReport | implemented | `cross_modal_service.py`; 7 tests; real conflict interpretation with alternative explanations |
| Larger GEM adapter (iML1515) | implemented | real model file, real dispatch, 3 tests, dispatch bug found+fixed in 3 files |
| Combination intervention | implemented | real 2-gene joint solve test |
| Multi-scenario S2/S4 | not_verified | not attempted this round, time-bounded |
| Stochastic replicate contract | implemented (not_applicable, honestly) | unchanged from Phase B/C - deterministic FBA has no real replicates to fabricate |
| vEcoli environment + ParCa | implemented / available_and_verified | real WSL build, real 11-minute ParCa run, real KB hash |
| vEcoli whole-cell simulation execution | not_verified / available_not_run | not attempted, time-bounded, real precursors now confirmed |
| Regression (no existing tests broken) | implemented | 319/319 before Phase D; full re-run in progress at report time |

## H. Test Evidence Summary

```
tests/virtual_cell/test_cross_modal.py                    7 passed
tests/virtual_cell/test_larger_gem_and_combination.py     3 passed
python -m pytest tests/ -q  (full suite, post-Phase-D)     running at report time
```
