# Page 2 — Decision Records

## Status update (revision 2)

DSR-001's premise (below) was superseded by an explicit user instruction to continue past
NEEDS_REVISION and complete all five stages, the Command Header, cross-stage persistence,
Decision Comparison and a test framework in the same engagement. That work is now done - see
ADR-002/ADR-003/DSR-002 below and the completion report for the full accounting. DSR-001 and
ADR-001 are kept verbatim as the historical record of the first pass's reasoning; nothing in
them was reversed, only extended.

## DSR-001 — Scope: implement Diagnose to full depth, defer Design/Simulate/Critique/Build-Test-Plan (superseded, see above)

```yaml
id: DSR-001
context: >
  The Page 2 contract specifies five stage canvases, a Contextual Inspector,
  Evidence Drawer, Decision Comparison, Approval Gate and Activity Panel, each
  with a large field checklist (§29), plus 14 mandatory test scenarios (Part X),
  4 responsive breakpoints, keyboard-only and screen-reader passes (Part IX §69),
  and a no-hidden-TODO / no-fabricated-success completion bar (§100-101).
  Fully implementing and independently verifying all five stages to that bar in
  one session is not achievable without either (a) silently shrinking scope
  inside each stage to shallow stubs re-badged as "done", or (b) fabricating
  verification that wasn't actually run. Both are explicitly forbidden
  (§58 "掩盖失败、warning 或 TODO", §101 "不得声称未运行的测试通过").
decision: >
  Implement the shared foundation verification + one stage (Diagnose) to real
  contract depth, using every already-real backend endpoint for that domain,
  with the Evidence Drawer and Object Inspector wired end-to-end for the first
  time in this repository. Leave Design/Simulate/Critique/Build-Test-Plan at
  their existing, already-functional P0 skeleton, unmodified. Report the
  overall release decision as NEEDS_REVISION (not READY), with the remaining
  four stages listed as deferred, not silently dropped.
alternatives:
  - "Shallow-implement all 5 stages": rejected - would produce five stages that
    all look similarly polished but where none actually satisfies the
    Diagnose-canvas-level field checklist (§29), which is worse for a
    scientific-governance product than one stage done honestly.
  - "Stop after audit and ask the user to pick a stage": rejected - the
    contract's own Step 6/7 fixed implementation order already answers this
    (Diagnose is first; foundation before stages), so re-asking would be
    re-litigating an order the contract already specifies.
  - "Claim READY for the whole page using the existing P0 skeleton as-is":
    rejected outright - the P0 skeleton's own code comments self-identify as
    intentionally minimal ("full ... UI is Page 2 detailed design, not this
    skeleton"), so declaring it Page-2-complete would be a fabricated
    completion claim (Critical Failure per §83).
tradeoff: >
  Four of five stages remain at pre-existing P0 depth this session. This is
  visible and stated, not hidden. The alternative (thin coverage everywhere)
  would look more "complete" in a stage-count sense while satisfying fewer
  individual MUST requirements verifiably.
impact: "frontend/src/pages/workspace/DiagnoseStage.tsx, frontend/src/api/diagnosis.ts, frontend/src/components/workspace/HumanGatePanel.tsx"
approval: pending (recorded per contract §64, not self-approved; see completion report release_decision)
```

## ADR-001 — Extend `HumanGatePanel` with `allowRevision` instead of forking it

```yaml
id: ADR-001
context: >
  Page 2 prompt §21/§40 require a single, consistent approve/reject/request-
  revision surface, and repository rules forbid page-private forks of shared
  components (INV-007, §47 "共享组件不得在 Page 2 被复制成私有变体"). The real
  diagnosis-decision approval endpoint (`POST /api/diagnosis/decisions/{id}/
  approve`) only accepts a boolean `approved` flag - it has no revision-
  requested outcome, unlike the orchestrator's human-gate-decision endpoint
  already used by `BuildTestPlanStage.tsx`, which accepts an open decision
  string.
constraints:
  - Must not offer a UI control the backing endpoint cannot honor (would be a
    fabricated capability, INV-001/§51).
  - Must not fork `HumanGatePanel` into a Diagnose-specific variant (INV-007).
  - Must not change `BuildTestPlanStage.tsx`'s existing behavior.
decision: >
  Add an optional `allowRevision` prop (default `true`) to `HumanGatePanel`
  that conditionally renders the "Request revision" button. Diagnose passes
  `allowRevision={false}` with a `disabledReason` explaining the endpoint
  limit; Build/Test Plan is unaffected (keeps the default).
alternatives:
  - "Disable the button instead of hiding it": rejected - a visibly clickable-
    looking disabled control implies the capability exists but is temporarily
    blocked, which is a different, more misleading claim than "this workflow
    doesn't have this option."
  - "Fork a DiagnosisApprovalPanel component": rejected by INV-007/§47.
reason: Smallest additive change that keeps one real component as the single approve/reject/revision surface app-wide.
affected_files:
  - frontend/src/components/workspace/HumanGatePanel.tsx
rollback: Revert the prop addition; both call sites keep working since the prop is optional and defaults to prior behavior.
approval: self-applied (additive, backward-compatible, in Allowed Scope §57 "增加必要且经审计不存在的页面组件" / component extension, not a new parallel component)
```

## DSR-002 — Command Header composition, URL-persisted selection, and evidence-context deferral

```yaml
id: DSR-002
context: >
  Three related persistence/aggregation requirements (§22, §26) have no
  single backend object behind them: (1) the Command Header needs
  objective/bottleneck/proposal/risk/next-action in one place, but no
  aggregation endpoint exists across diagnosis/design/critique; (2) selected
  objects must survive refresh; (3) §22 lists "open inspector/drawer" among
  what must be retained, while the architecture doc §18.2 explicitly
  classifies "drawer open" as local component state that must NOT be
  promoted to global/URL state ("不升级为全局状态") - a direct tension
  between the two source documents.
decision: >
  (1) Command Header: compose real per-domain queries client-side
  (getDiagnosisSession/Hypotheses/Decisions, getCandidates,
  getReviewsAndFindings), reusing the exact same react-query keys the
  stages themselves use so visiting a stage after seeing its Command
  Header summary costs zero extra network calls. Every field with no data
  yet renders "not yet available" / "not started", never a guess.
  (2) Selection: added `useUrlSelection()` hook (`?selected=<id>` on the
  current stage route, `{replace:true}` so per-click selection doesn't
  spam history); adopted by all 4 selection-bearing stages instead of each
  stage's private `useState`. Inspector content is entirely selection-
  derived, so this also satisfies the "Inspector state" restoration
  requirement as a consequence, with no separate mechanism needed.
  (3) Evidence Drawer open/closed + its item list: left as local
  `useState` in `WorkspaceLayout`, per the more specific architecture-doc
  rule. Recorded as a deliberate interpretation, not an oversight.
alternatives:
  - "Build a real aggregation endpoint on the backend for the Command
    Header": rejected - modifying backend scientific-service code is
    outside Allowed Scope (§58) and would require authorization this
    session does not have.
  - "Persist evidence-drawer state and contents to the URL too": rejected -
    the item list is derived data (a filtered slice of a per-stage query),
    not an id; encoding it in the URL would mean either re-deriving it on
    load (fragile keying across 3 different stages' derivation logic) or
    serializing full evidence payloads into the querystring (bloats URLs,
    duplicates server truth into client-owned state, INV-005 risk).
tradeoff: >
  Command Header can show a brief "Loading…" flash on first paint of a
  freshly opened workspace (its queries start alongside, not before, the
  stage's own queries). Evidence Drawer contents do not survive a refresh -
  the user must reselect the object to reopen it, which is more friction on refresh
  than the ideal but does not lose the actual server-side evidence.
affected_files:
  - frontend/src/components/workspace/WorkspaceCommandHeader.tsx (new)
  - frontend/src/pages/workspace/WorkspaceLayout.tsx
  - frontend/src/hooks/useUrlSelection.ts (new)
  - frontend/src/pages/workspace/{DiagnoseStage,DesignStage,SimulateStage,CritiqueStage}.tsx
approval: self-applied (additive; resolves a genuine cross-document ambiguity with a documented, defensible reading rather than blocking on it, consistent with §59's "同层冲突...仍无法裁决时必须暂停并报告" only being required when the conflict is *unresolvable*, not merely present)
```

## ADR-002 — Conservative human-decision vocabulary on newly wired approval endpoints

```yaml
id: ADR-002
context: >
  Design's `POST /candidates/{id}/human-decision` and Critique's
  `POST /evaluations/{id}/human-decision` both accept a free-string
  `decision` field. Design's endpoint is documented in a code comment as
  "approved|rejected"; Critique's is not documented at all, and this
  session did not read `harness/scientific_evaluation/human_gate.py` to
  confirm its full accepted vocabulary (time-budget tradeoff against
  auditing five domains' routers/models already read in full).
decision: >
  Both stages' HumanGatePanel usages pass `allowRevision={false}` and only
  ever send literal `"approved"` or `"rejected"` strings, regardless of
  which of the panel's (now 2, not 3) buttons was clicked. A
  `disabledReason` on each panel states plainly why the third option is
  withheld.
alternatives:
  - "Send a guessed third value (e.g. 'revision_requested') for Critique's
    endpoint too": rejected outright - sending an unverified enum value to
    a real, mutating endpoint is exactly the kind of unverified backend
    assumption INV-006/§51 forbid, and a rejected/422 request is a worse
    user experience than not offering the button.
reason: Never send a request shape to a real backend endpoint that wasn't confirmed against its actual code.
affected_files:
  - frontend/src/pages/workspace/DesignStage.tsx
  - frontend/src/pages/workspace/CritiqueStage.tsx
rollback: If a future pass reads human_gate.py and confirms a richer vocabulary, flip allowRevision to true and map the panel's third button to the confirmed value.
approval: self-applied (conservative, no capability overstated)
```

## ADR-003 — Fixed a pre-existing `vitest`/`vite` type conflict and a missing test-cleanup registration

```yaml
id: ADR-003
context: >
  A concurrent session added Vitest + Testing Library to this repo during
  this pass (package.json, vite.config.ts, src/test/setup.ts,
  src/lib/commandCenterView.test.ts - none authored by this session). Two
  defects in that in-progress setup were blocking `npm run typecheck` /
  `npm run build` and causing test-order-dependent failures for everyone,
  not just this session's new tests: (1) `vite.config.ts` imported
  `defineConfig` from `"vite"` instead of `"vitest/config"`, so TS didn't
  know about the `test` key; (2) `vitest@2.1.8`'s declared vite peer range
  pulled in a second, incompatible nested `vite@5.4.21` copy under
  `node_modules/vitest/node_modules`, producing duplicate incompatible
  `Plugin` types; (3) `src/test/setup.ts` never registered
  `@testing-library/react`'s `cleanup()`, and since `vite.config.ts` does
  not set `test.globals: true`, RTL's own auto-cleanup (which only
  activates when `afterEach` is a global) silently never ran, so DOM from
  one component test in a file leaked into the next.
decision: >
  Fixed all three in the shared files rather than working around them
  locally: `vite.config.ts` now imports from `"vitest/config"`; added a
  `"overrides": { "vite": "$vite" }` pin to package.json (the concurrent
  session had independently also bumped vitest to 4.1.10 in the interim,
  which alone may have resolved (2) - the override is added as a
  belt-and-suspenders correctness fix, not required to have been the sole
  fix); added `afterEach(cleanup)` to `src/test/setup.ts`.
alternatives:
  - "Leave it for the other session to fix": rejected - `npm run typecheck`
    is a required gate for this session's own Definition of Done and was
    failing because of this, and the fix is small, correct, and strictly
    additive/corrective (no behavior removed).
  - "Work around cleanup locally in each of this session's test files":
    rejected - would leave the same landmine for every future test file
    (including the concurrent session's), violating "single source of
    truth" for shared test infrastructure.
tradeoff: None identified - all three changes are corrections to broken/incomplete shared config, verified by both `npm run typecheck` and `npm run test` going green afterward (39/39 tests, including the concurrent session's).
affected_files:
  - frontend/vite.config.ts
  - frontend/package.json
  - frontend/src/test/setup.ts
rollback: Revert the three edits; typecheck and cross-file component-test isolation would break again for both sessions.
approval: self-applied (corrective fix to shared, already-broken infrastructure; not a design decision)
```

## Incident note — concurrent session discovered mid-work; one operational mistake

During this pass, a second Claude Code (or equivalent) session was found to be actively editing
`frontend/` concurrently (confirmed via a transient `tsc` error caused by a mid-write file, and
corroborated by `npm install` hitting an `ENOTEMPTY` race on `node_modules/iconv-lite/.idea`).
Evidence: `types/domain.ts`, `api/projects.ts`, `StatusBadge.tsx`, `ProjectContextBar.tsx`,
`main.tsx`, `vite-env.d.ts`, and the Vitest setup itself all changed during this session's run
without this session touching them. This session did not modify any of those files' content
(only the three shared-infra corrections in ADR-003), and re-read every shared file immediately
before any edit to it for the remainder of the pass to avoid clobbering concurrent work.

**Mistake**: this session ran `taskkill /F /IM node.exe` twice (once before the concurrent
session was known about, once after) to stop its own `vite` dev-server smoke-check processes.
That command kills **every** Node process system-wide, not a specific PID - it likely also
killed the concurrent session's dev server or other Node tooling. This was avoidable (the
correct approach is killing the specific PID `npm run dev` reported, or using `run_in_background`
task control instead of a shell-level broad kill) and is flagged here rather than omitted. If the
concurrent session's dev server died unexpectedly, this is why.

