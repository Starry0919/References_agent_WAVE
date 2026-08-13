# Evidence-ready output and Skill08 handoff

Evidence bundles have stable IDs and one or more spans. Spans preserve locator, section/page/paragraph/figure/table/supplement metadata, source text/hash, attribution, resolvability and role: `DIRECT_SUPPORT`, `CONTEXT`, `METHOD`, `COMPARISON_BASELINE`, `RATIONALE`, `INTERPRETATION`, `CONTRADICTORY`, or `LIMITATION`.

Skill08 verifies atomic claims first: E1 resolves bundle spans, E2 checks biological attribution/binding, and E3 tests the exact qualified proposition. Context-only or method-only spans cannot satisfy direct outcome support. Multi-span support is allowed only within one paper/experiment with compatible roles and explicit lineage; unrelated stitching remains unresolved. Thresholds are unchanged.
