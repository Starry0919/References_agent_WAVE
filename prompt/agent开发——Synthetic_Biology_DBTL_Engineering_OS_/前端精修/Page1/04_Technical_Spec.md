```yaml
page_id: page-01
page_name: Project Command Center
spec_type: Technical Spec
version: 0.1.0
status: Draft
owners:
  - Frontend Architect
reviewers:
  - Frontend Architect
parent_contract: Page Design Contract v1.2.0
parent_architecture: Frontend Architecture Prompt v1.2
last_updated: 2026-07-23
dependencies:
  - 01_Product_Spec.md
  - 02_UI_Spec.md
  - 03_Interaction_Spec.md
  - 05_Content_Spec.md
open_questions:
  - This entire document is BLOCKED pending a real Repository Audit against the actual frontend
    codebase (see Provenance note below). No section may be marked Approved until §61
    Repository-First Rule has been executed against real files.
approved_exceptions: []
```

> **Provenance note (2026-07-23)**: this file replaces the prior `Page1/04_Technical_Spec.md`, which
> did not contain a Page 1 technical spec — it was a discussion draft proposing a global, cross-page
> "Operating System Architecture" constitution (relocated, verbatim, to
> `Page1/references/Proposal_Global_OS_Architecture_Constitution.md`). A genuine Technical Spec
> requires the Repository-First Rule (Contract §61) to be executed against the real frontend
> repository — inspecting framework/router/styling/tokens/shared components/state
> libraries/API clients/schemas/auth/tests/build commands/dirty files. **This normalization task was
> explicitly scoped to not touch frontend code**, so that inspection was not performed here. A
> real, dated repository audit already exists at
> `workflow/design/evolution/前端精修/整体架构/repository_truth_audit.md` (Phase 0, whole-architecture
> level, not Page-1-specific) and a real frontend codebase exists at
> `workflow/design/JH/agent-harness-v1/agent-harness-v1/frontend`; neither has been re-verified
> against Page 1's specific component/route/state needs in this pass. Every section below is
> therefore `BLOCKED`, not filled with invented technical decisions.

---

## 1. Repository Findings — `BLOCKED`
Requires re-running §61 Repository-First Rule scoped to Page 1's actual needs against the real
frontend repository referenced above.

## 2. Existing Assets to Reuse — `BLOCKED`
Depends on §1.

## 3. React Architecture — `BLOCKED`
Depends on §1 (must adapt to the real repository per Contract §62, not invent a parallel structure).

## 4. Component Tree — `BLOCKED`
Depends on `02_UI_Spec.md` Page-Specific Component Inventory (currently `Partial`/`GAP` per its Part Z)
and §1.

## 5. Folder / Module Placement — `BLOCKED`
Depends on §1.

## 6. Route Registration — `BLOCKED`
Depends on §1 and the parent architecture's route pattern
(`/projects/:projectId`, per `前端整体架构设计.md` §6.3).

## 7. Domain Types — `BLOCKED`
Depends on `05_Content_Spec.md` (Scientific Objects, Required Fields) and real backend schemas.

## 8. State Ownership — `BLOCKED`
The State Ownership Matrix pattern is already defined at the Global Contract level (§64) and parent
architecture level (§18.2); Page-1-specific instantiation (which state, which owner) is not yet
mapped.

## 9. Context and Providers — `BLOCKED`
Depends on §1.

## 10. API Contract — `BLOCKED`
Depends on real backend endpoint discovery (§1) and `05_Content_Spec.md`.

## 11. Backend Mapping Matrix — `BLOCKED`
A whole-architecture-level `backend_mapping_matrix.md` exists at
`整体架构/backend_mapping_matrix.md`; it has not been re-verified as sufficient or complete for
Page 1's specific UI needs in this pass.

## 12. Adapter and Normalization — `BLOCKED`
Depends on §10, §11.

## 13. Data Flow — `BLOCKED`
Depends on §1, §10.

## 14. Caching and Revalidation — `BLOCKED`

## 15. Optimistic Update Rules — `BLOCKED`

## 16. Lazy Loading — `BLOCKED`

## 17. Virtualization — `BLOCKED`
Likely low-relevance for Page 1 (a summary surface, not a large-table view) but not confirmed against
real content volume.

## 18. Memoization — `BLOCKED`

## 19. Error Boundaries — `BLOCKED`
Global Contract §70 requires at minimum an application, route/module, and heavy-visualization
boundary; Page-1-specific placement is not yet mapped.

## 20. Animation Library — `BLOCKED`
Depends on §1 (must reuse existing repository animation approach per Contract §18 "不因个人偏好重写前端").

## 21. Three.js Usage or Explicit Non-Use — Provisional, not `BLOCKED`
No Page 1 content in `01_Product_Spec.md` or `02_UI_Spec.md` requests spatial/3D interaction; nothing
in the approved product or UI definition justifies Three.js per Global Contract §58 ("A decorative
E. coli model is not sufficient justification"). Provisional position: **Explicit Non-Use** for
Page 1, pending confirmation at Gate 3.

## 22. Performance Budget — `BLOCKED`
Global baseline exists at Contract §68; Page-1-specific budget (e.g., real card/module count) not
yet set.

## 23. Accessibility Implementation — `BLOCKED`
Depends on `02_UI_Spec.md` Accessibility Layout Requirements (`Partial` per its Part Z).

## 24. Internationalization — `BLOCKED`
Parent architecture §14.5 requires Chinese/English switch support at the architecture level; Page-1
specific string/locale handling not yet mapped.

## 25. Permissions — `BLOCKED`

## 26. Telemetry — `BLOCKED`

## 27. Testing Strategy — `BLOCKED`
Depends on §1 (existing test tooling) and `06_Acceptance_Spec.md`.

## 28. Feature Flags — `BLOCKED`

## 29. Migration and Compatibility — `BLOCKED`

## 30. File Change Plan — `BLOCKED`
Cannot be produced without §1.

## 31. Explicitly Protected Files / Logic — Provisional
The Global Contract's Protected Repository Surface list (§"Protected Repository Surface") applies by
default: AppShell/global layout, global tokens/themes, primary navigation/routing, global domain
model, global types/API contracts, shared component public APIs, auth/approval/audit logic, backend
scientific reasoning, existing migrations/schemas, and unrelated user files. No Page-1-specific
additions to this list have been identified because §1 has not been executed.

---

## Backend Mapping Table (Contract §80 required table)

| UI need | Object | Endpoint/event | Schema | Adapter | Source of truth | Missing behavior |
| --- | --- | --- | --- | --- | --- | --- |
| *(empty — depends on §1 and §11 above)* | | | | | | |

---

**Recommended next step (decision, not executed here):** before Gate 3 (Engineering), commission a
Page-1-scoped Repository Audit against the real frontend codebase and cross-check it against
`整体架构/repository_truth_audit.md` and `整体架构/backend_mapping_matrix.md`. This document must not
be marked `Approved` until that audit is complete and every `BLOCKED` section above is replaced with
verified findings.
