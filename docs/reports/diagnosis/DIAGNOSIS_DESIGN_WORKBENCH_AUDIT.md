# Diagnosis / Engineering Design Workbench Repository Audit

Date: 2026-08-12  
Target project: `PROJ-3f77f638302b`

## Repository truth

The repository already contains two working scientific loops rather than empty dashboard shells:

- Diagnosis: versioned sessions, competing hypotheses, supporting/contradicting evidence links, model capability discovery, diagnostic tests, belief transitions, gated decisions, reports, and an event audit trail.
- Engineering design: mandatory diagnosis handoff, strategies, diversified candidate portfolios, evaluator suite, counterfactual requests, build/test packages, human approval, outcomes, lineage, and audit history.
- Shared truth: project context, DDR/rule knowledge, evidence resolution, provenance, applicability, workflow status, and a restrained bilingual UI system already exist.

The safe implementation strategy is therefore **reuse -> expose missing persisted fields -> compose expert workspaces**. No parallel diagnosis/design ontology is justified.

## Working-tree safety

The Git index describes a previous directory layout while the current application tree is largely untracked and many old paths are recorded as deleted. Existing `.gitignore` and `README.md` changes also predate this task. The current files cannot be reliably divided into prior user edits versus generated/untracked application files from Git metadata alone. This task will touch only the two workbenches, their direct typed API adapters/serializers, focused tests, and the required reports. No reset, cleanup, migration, or unrelated deletion will be performed.

## Real project inspection

Database: `project_ledger.db`

- Project: L-tryptophan; host E. coli K-12; project lifecycle `PROJECT_CONTEXT_READY`.
- Substrate: not stored in the project or diagnosis context; it must be shown as `Not specified`, never guessed as glucose.
- Diagnosis: one session (`DIAG-d23cfa28206e`), status `handed_off_to_design`, data sufficiency `sufficient`.
- Hypotheses: four competing hypotheses; two leading, two unresolved alternatives.
- Evidence: three linked evidence items, all `expert_rule`, `quality=low`, `directness=indirect`, sourced from `DDR-001`; no contradictory evidence was persisted.
- Decision: actionable handoff, medium qualitative confidence, explicit uncertainty that no GEM/kinetic model ran.
- Design: one project (`EDP-78ae7989000f`), status `portfolio_generated`, with two strategies and three candidate roles (reference/control, low-risk, information-gain).
- Evaluation/build: zero persisted evaluator results and zero build/test packages. No candidate is scientifically entitled to appear as selected or experimentally validated.

## Capability maturity matrix

| Capability | Maturity | Repository evidence | UI decision |
|---|---:|---|---|
| Project context | L4 | Project API + persisted host/product | Load real context; show missing substrate explicitly |
| Diagnosis session lifecycle | L5 | service, state machine, API, audit events, tests | Reuse without schema changes |
| Competing hypotheses | L4 | hypothesis versions + assessments + ranks | Render ranked alternatives, not a single cause |
| Evidence for/against | L4 | relation supports/contradicts + review ledger | Split positive and negative evidence; empty means none recorded |
| Evidence provenance | L4 | evidence item/source reference + strategy resolver | Provide source identifiers and epistemic labels |
| Evidence grading | L3 | quality/directness, source type | Map existing fields; do not invent hard evidence |
| Epistemic status | L2 | source/model types imply status; no unified column | Compatibility view mapping only; document inference |
| Diagnosis coverage | L2 | modules are not persisted as a matrix | Derive a conservative view from actual runs/findings; unobserved axes = not evaluated |
| Quantitative grounding | L3 platform / L0 project | model adapters exist; target project has no run | Show capability pending/no model result; no numeric placeholders |
| Pathway graph | L3 | mechanism graph endpoint exists | Reuse structured mechanism graph; no new graph ontology |
| Diagnosis -> design contract | L5 | immutable decision + versioned handoff + stale flag | Make trace visible on both workbenches |
| Strategy alternatives | L4 | strategy classes + excluded reasons | Render candidate space and why-not records |
| Candidate portfolio | L4 | diversified role-based portfolio | Compare real candidate fields and readiness |
| Dependencies/conflicts | L2 | epistasis assumptions and causal chain exist; no normalized edge model | Display declared assumptions; mark dependency graph partial |
| M11 evaluator suite | L4 platform / L0 project result | evaluator modules and evaluation persistence exist, no run for target | Show eight gates as pending until evaluated |
| Hard gates + soft ranking | L3 | hard constraints/findings + Pareto/recommendation | Preserve decomposition; never replace with one opaque score |
| Rejected candidates | L4 platform / L0 project result | statuses/rejection reasons and strategy exclusions exist | Show strategy exclusions now; candidate rejection waits for evaluator |
| Selected engineering stack | L3 platform / L0 project result | selected status exists, none selected | Honest `Awaiting evaluation/selection` state |
| Experimental validation | L4 platform / L0 project result | build/test package service exists, none persisted | Show pending package and next action |
| Fermentation/process design | L2 | process modifications supported, current candidates empty | Mark not proposed/evaluated |
| Consistency sampling | L3 | evaluation metrics consistency service/API | Keep as available optional analysis; not claim it ran |
| Design versioning | L4 | candidate lineage/version and design version bridge | Surface version/readiness/status |
| Final-report integration | L2 | diagnosis report exists; no confirmed unified final-report consumption | Record architectural gap; no scope expansion |

## Primary UX defects

1. The requested base routes are collection/creation pages. Scientific reasoning is hidden behind raw session/design identifiers on secondary routes.
2. The first screen does not answer goal, top finding, evidence strength, coverage, recommended direction, or current uncertainty.
3. Persisted causal chains, trade-offs, epistasis assumptions, provenance, evaluator findings, and build/test state are not all exposed by the candidate serializer.
4. Candidate roles are visible, but comparison, explicit exclusions, evaluator gates, selected stack, and validation readiness are not composed into a decision chain.
5. Missing computations are mostly absent rather than explicitly `Not evaluated`, making capability absence hard to distinguish from loading or error.

## Implementation gate

Proceed with a minimal compatible implementation. Backend changes are limited to read-only serialization of already-persisted fields. The workbench view-model will conservatively map existing vocabulary into presentation-only evidence/epistemic labels. Complex scientific calculations (FBA, enzyme kinetics, docking, fermentation optimization) will not be fabricated.
