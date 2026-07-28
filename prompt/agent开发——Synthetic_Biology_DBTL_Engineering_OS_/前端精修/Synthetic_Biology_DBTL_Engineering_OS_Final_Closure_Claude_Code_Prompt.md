# Synthetic Biology DBTL Engineering OS

# Final Closure Prompt

**Execution target:** Claude Code  
**Phase:** Post-certification closure  
**Goal:** Close the last release-verification gaps and issue the final release decision

---

## 0. Mission

The main implementation and Release Certification are complete. The current `NEEDS_REVISION` decision is caused by unfinished closure validation, not by a request for further product development.

Complete only:

1. i18n coverage closure;
2. failure injection validation;
3. optional density benchmark;
4. focused regression and final release decision.

```text
NO REDESIGN
NO FEATURE EXPANSION
NO ARCHITECTURE CHANGE
NO BACKEND INVENTION
NO SCIENTIFIC LOGIC CHANGE
ONLY FINAL CLOSURE TASKS
```

When the final report is complete, stop.

---

## 1. Non-Negotiable Rules

1. Inspect before editing.
2. Preserve accepted Page 1–Page 4 behavior and visual structure.
3. Fix only verified defects required by this prompt.
4. Do not reopen accepted backend or product limitations.
5. Never create fake data, endpoints, evidence, simulations, approvals, or successful states.
6. Failure validation requires runtime evidence; finding an error string in source code is not a pass.
7. Do not claim `READY` without browser and regression evidence.
8. If an issue does not reduce scientific comprehension, task completion, accessibility, language consistency, failure transparency, or governance clarity, do not modify it.

Before editing, record:

```bash
git status --short
git branch --show-current
git diff --stat
```

Preserve all pre-existing user changes. If the worktree changes unexpectedly during execution, stop and report a concurrent-change conflict. Do not perform unrelated formatting, refactoring, dependency migration, or destructive Git operations.

---

## 2. Preconditions and Allowed Scope

Read the latest Release Certification report, repository instructions, existing i18n implementation, relevant tests, and package scripts.

This prompt applies only if:

- Page 1–Page 4 are already implemented;
- the application is runnable;
- the earlier release decision is blocked only by the closure items below.

Otherwise stop with:

```text
FINAL CLOSURE NOT APPLICABLE
Reason: <specific reason>
Required next phase: <stabilization or implementation>
```

Allowed:

- add missing translations through the existing i18n system;
- replace verified hard-coded UI strings with existing translation calls;
- add deterministic test-only fixtures or Playwright interception for failure injection;
- make the smallest frontend correction required by a failed closure test;
- update the final closure report.

Forbidden:

- redesigning pages, navigation, layouts, or information architecture;
- adding pages, tabs, workflows, scientific functions, or backend contracts;
- implementing missing Knowledge Graph, reuse, RBAC, approval, Memory, Golden Set, or export capabilities;
- adding production mock modes;
- hiding limitations to improve demo appearance.

---

## 3. Execution Order

```text
Phase 0 — Confirm baseline and closure gaps
Phase 1 — Close i18n coverage
Phase 2 — Run failure injection
Phase 3 — Run optional density benchmark
Phase 4 — Run focused regression
Phase 5 — Issue final release decision
STOP
```

At the end of Phase 0, record the confirmed gaps, routes, test mechanism, expected changed files, and stop conditions. Continue automatically only if no architecture decision, concurrent change, destructive action, new backend contract, or scope expansion is required.

---

# Task 1 — i18n Coverage Closure

## 4. Required Work

Use the existing `LanguageProvider`, `useI18n()`, translation dictionaries, and persistence mechanism. Do not replace the i18n architecture.

Audit Page 1–Page 4 and shared shell for user-facing:

- navigation, titles, tabs, headings, buttons, filters, forms, drawers, dialogs, and tooltips;
- status badges and explanations;
- loading, empty, error, restricted, unavailable, partial, failed, retry, and recovery states;
- language-dependent accessibility labels.

Do not translate stable scientific objects:

```text
E. coli K-12
L-tryptophan
gene/protein symbols
DOI / PMID / PXD identifiers
established scientific abbreviations
```

Translate the surrounding UI label and explanation.

## 4.1 Browser Acceptance

In the real application:

1. select English and traverse Page 1–Page 4;
2. refresh and confirm persistence;
3. select Chinese and repeat;
4. refresh and confirm persistence;
5. verify scientific identifiers remain unchanged;
6. verify switching language does not reset route or unrelated selected state;
7. repeat the essential check at desktop width and `390px`.

`PASS` requires:

- no verified mixed-language UI within the audited surface;
- no missing-key output;
- no untranslated application error/unavailable state;
- no translation-induced layout break;
- persistence and navigation state remain correct.

Record intentionally untranslated terms and the reason.

---

# Task 2 — Failure Injection Validation

## 5. Required Work

Prove the system remains honest and recoverable under failure.

Use, in order of preference:

1. existing deterministic test hooks;
2. Playwright route interception;
3. an existing test-only mock layer;
4. safe, reversible local service shutdown.

Do not modify production data. Do not claim a scenario was tested through source inspection alone.

## 5.1 Required Matrix

| ID | Injected condition | Required behavior |
|---|---|---|
| F-01 | Core API `500` or backend unavailable | No white screen; show unavailable/error reason and retry or recovery path |
| F-02 | API timeout/interruption | No infinite misleading loading; show timeout/partial state and allow recovery |
| F-03 | Empty or partial response | Render supported data only; label missing sections; fabricate nothing |
| F-04 | Evidence missing | Show unavailable/unknown; never show unsupported `High confidence` |
| F-05 | Simulation/solver failure | Show failed/unavailable and reason; never show `Completed` or invented output |
| F-06 | Approval rejected or request fails | Preserve status, reason, timestamp, reviewer when supplied, and prior history |
| F-07 | Restricted/unsupported governance capability | Show explicit backend limitation; do not expose a fake actionable control |

For every scenario verify:

- `unknown`, `unavailable`, `partial`, `failed`, `restricted`, `rejected`, and `completed` remain distinct;
- confidence, evidence quality, approval, execution, and evaluation are not conflated;
- missing evidence cannot increase confidence;
- failed simulation cannot create successful evaluation;
- rejected approval cannot disappear from history;
- unavailable backend capability cannot become enabled;
- secrets, tokens, stack traces, and raw internals are not exposed.

Then restore the normal response, use the visible retry/recovery path where available, and confirm valid state returns without an uncaught console error.

If a scenario truly cannot be injected, report:

```text
NOT TESTABLE
Reason: <technical evidence>
Release impact: <blocker or accepted limitation>
```

Do not mark it `PASS`.

For every case record route, injection method, expected/observed behavior, screenshot or trace, console/network result, recovery result, and verdict.

The release is blocked if a supported core path crashes, fabricates scientific/governance state, reports success after failure, loses approval/audit history, exposes an unsupported action, or cannot recover safely.

---

# Task 3 — Optional Density Benchmark

## 6. Required Work

Run only if large-scale fixtures already exist or can remain entirely inside test code.

Suggested volumes:

| Surface | Volume |
|---|---:|
| Design candidates | 100; optionally 1,000 |
| Evidence records | 1,000; optionally 5,000 |
| Audit records | 10,000 |

Check render usability, search/filter correctness, selection and drawer behavior, scrolling/pagination/virtualization where already present, long-text layout, keyboard use, request loops, crashes, and severe interaction freezes.

Do not add a dependency, data service, pagination, or virtualization solely for this optional test.

If not run:

```text
DENSITY BENCHMARK: NOT RUN
Reason: <reason>
Release impact: non-blocking for the current research demo/prototype scope
Future capacity test: <specific recommendation>
```

This optional benchmark alone must not force `NEEDS_REVISION`, unless it reveals a real defect within the declared current operating scale.

---

# Task 4 — Focused Regression and Release Decision

## 7. Focused Regression

After allowed changes, run:

- existing lint, typecheck, build, and relevant tests;
- Page 1–Page 4 smoke navigation;
- English/Chinese switching and persistence;
- affected failure-injection cases;
- console and network checks;
- keyboard/focus checks for changed components;
- desktop and `390px` checks for changed UI.

Also verify one real cross-page path:

```text
Project Command Center
→ identify bottleneck
→ DBTL Engineering Workspace
→ inspect design candidate
→ inspect evidence
→ inspect simulation state
→ inspect human approval
→ inspect audit/provenance
```

A missing backend capability may be accepted only if it is explicit, non-deceptive, understandable, and does not prevent the supported workflow from being used.

---

## 8. Final Decision Rules

Use exactly one:

### `READY`

All required closure checks pass, no release-blocking defect remains, and no material limitation remains within the declared scope.

### `READY WITH ACCEPTED LIMITATIONS`

Supported frontend behavior, i18n, failure handling, and regression pass; remaining limitations are genuine backend/data/governance/prototype boundaries, are clearly visible, and do not block the declared research demo/prototype.

### `NEEDS_REVISION`

A verified frontend defect remains; required i18n fails; a supported failure path crashes, lies, loses history, or cannot recover; required evidence is missing; or closure changes cause regression.

### `BLOCKED`

The runtime cannot be evaluated, required access/tooling is unavailable, concurrent changes invalidate results, or a backend/architecture decision is required.

A gate without reproducible evidence is not a pass.

---

## 9. Required Final Report

Create or update:

```text
docs/前端精修/final_closure_report.md
```

Use the repository’s established equivalent path if different.

The report must contain:

### A. Executive result

```text
FINAL CLOSURE STATUS: COMPLETE | INCOMPLETE | BLOCKED
RELEASE DECISION: READY | READY WITH ACCEPTED LIMITATIONS | NEEDS_REVISION | BLOCKED
```

### B. Closure matrix

| Item | Result | Evidence | Release impact |
|---|---|---|---|
| i18n coverage | PASS/FAIL/BLOCKED |  |  |
| failure injection | PASS/FAIL/BLOCKED |  |  |
| density benchmark | PASS/FAIL/NOT RUN |  |  |
| focused regression | PASS/FAIL/BLOCKED |  |  |

### C. Page matrix

| Page | Final status | Evidence | Accepted limitations |
|---|---|---|---|
| Page 1 — Project Command Center |  |  |  |
| Page 2 — DBTL Engineering Workspace |  |  |  |
| Page 3 — Scientific Knowledge Production System |  |  |  |
| Page 4 — Trust & Provenance Center |  |  |  |

Use only `PASS`, `PASS WITH ACCEPTED LIMITATIONS`, `FAIL`, or `BLOCKED`.

### D. Failure Injection Matrix

For F-01–F-07 include the injection, route, mechanism, expected/observed behavior, recovery, evidence path, and verdict.

### E. Accepted Limitation Register

For each limitation give its capability, classification, technical evidence, visible behavior, reason it is non-blocking, future owner/phase, and production impact. Never relabel a frontend defect or missing validation as an accepted limitation.

### F. Change and evidence ledger

List every changed file and why it changed. Record commands, exit results, tested viewports, screenshots/traces/reports, and anything not run with the exact reason.

End with:

```text
The Synthetic Biology DBTL Engineering OS is [READY / READY WITH ACCEPTED LIMITATIONS / NEEDS_REVISION / BLOCKED] for the declared research demo/prototype release scope because <evidence-based reason>.
```

---

## 10. Stop Condition

After the report contains an unambiguous, evidence-backed decision:

```text
STOP
```

Do not begin a vNext plan, add polish, reopen Page 1–Page 4 design decisions, or implement recorded backend limitations.
