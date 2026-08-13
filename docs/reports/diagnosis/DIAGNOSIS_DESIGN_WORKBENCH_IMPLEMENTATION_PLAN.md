# Diagnosis / Engineering Design Workbench Implementation Plan

1. Extend read-only serializers/adapters to expose persisted scientific fields hidden from the UI.
2. Add reusable scientific status, evidence, coverage, trace and evaluator presentation components.
3. Replace the Diagnosis base-route collection-first layout with a project-specific expert workspace while preserving session creation/history access.
4. Replace the Design base-route handoff-first layout with a diagnosis-driven decision workspace while preserving handoff creation/history access.
5. Keep detail routes and existing actions intact; link expert cards to deep operational views.
6. Add focused API/component tests for mapping, rich/partial/empty states and explicit unavailable states.
7. Run backend tests, frontend tests/typecheck/build, then launch the real application and validate both target URLs, network calls, console, provenance, alternatives, evaluator, rejection, stack and validation interactions.
8. Record implementation truth, validation evidence, pre-existing failures and final PASS/PARTIAL/FAIL.
