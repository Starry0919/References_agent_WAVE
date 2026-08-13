# Literature Routing v2 Implementation Report

Contract: `literature-route/2.0`.

Routes:

- `PRIMARY_EXPERIMENTAL_ROUTE`
- `REVIEW_SYNTHESIS_ROUTE`
- `MODEL_ROUTE`
- `METHOD_ROUTE`
- `RESOURCE_ROUTE`
- `SOFTWARE_ROUTE`
- `BENCHMARK_ROUTE`
- `BACKGROUND_ROUTE`
- `MANUAL_REVIEW_ROUTE`

Each route exposes confidence, concise reasons, and its source classification ID. Conflicts take the manual-review route. Review papers take the synthesis route. Model-only work is distinct from hybrid wet-lab/model work.

Ranking v2 combines scientific relevance, desired classification fit, route fit, evidence strength, and full-text availability. Citation/recency cannot dominate scientific relevance. Supported sort modes are `RELEVANCE`, `DIRECT_ENGINEERING`, `REVIEW_SYNTHESIS`, `RECENT`, and `EVIDENCE_STRENGTH`. Service filters cover all six axes, route, full-text state, year, and host relation.

The default ordering reserves bounded route diversity after prioritizing direct experimental results. Backward/forward citation expansion is P1: current normalized records do not consistently contain reference identifiers, and unbounded expansion was intentionally not added.

