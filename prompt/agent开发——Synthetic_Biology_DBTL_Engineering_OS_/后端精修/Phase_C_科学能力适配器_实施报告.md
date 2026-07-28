# Phase C — Scientific Capability Adapters: Delivery Report

Scope: Workstream 2 of `六大核心模块统一集成、科学能力补强与最终验收_Claude_Code_Prompt.md`
(LLM structured candidate generation for Problems 3-5 + real evidence retrieval + condition
matching). Code lives in `20260717_JH_agent_structure/agent-harness/agent-harness/`.

## A. Provider / Environment Audit (done first, per your instruction, before any adapter code)

Real checks run against this environment, not assumed:

| Check | Method | Result |
|---|---|---|
| LLM provider config | `harness.providers.resolve()` | `provider=kimi`, `model=kimi-for-coding-highspeed`, real `KIMI_API_KEY` present in `.env` |
| LLM connectivity | live `chat.completions.create()` call | **OK**, ~3s latency |
| LLM structured JSON output | live call with `response_format={"type":"json_object"}` | **OK**, valid JSON returned |
| LLM behavior at low `max_tokens` | live call at `max_tokens=1500` on a real adapter prompt | **Real finding**: `kimi-for-coding-highspeed` is a reasoning model; it consumed `reasoning_tokens=1499/1500` and returned **empty visible content** three times in a row. Not a bug in this code — a genuine characteristic of this provider/model that had to be discovered and handled. |
| Fix verified | same prompt at `max_tokens=8000` | **OK**, `finish_reason="stop"`, valid JSON, ~15-35s latency |
| Literature API network access | `GET api.crossref.org/works` | **OK**, ~2s, reachable |
| UniProt REST network access | `GET rest.uniprot.org` | OK, reachable (not built into an adapter this round — see §F) |

Conclusion acted on: Kimi is real and usable for live structured generation (not forced into
`unavailable`), and Crossref is real and usable for literature/DOI retrieval — both wired as real
adapters below, not stubs. `StructuredGenerationClient`'s default `max_tokens` was set to `8000`
based on this measured finding (documented in its own module docstring, not silently chosen).

## B. What Was Built

### B.1 Shared LLM generation infrastructure (`harness/llm_generation/`)
- `models.py` — `LLMGenerationRecord` (prompt §5.2's exact fields: provider, model_id,
  prompt_template_id/version, validation_status, retry_count, fallback_used, shared_model_risk,
  token_usage, latency, …). One reusable table for all three tasks, not three near-identical ones.
- `client.py` — `StructuredGenerationClient`: real OpenAI-compatible call, `response_format=
  json_object`, schema-invalid responses re-prompted up to `max_schema_retries` (default 2), a
  `provider_error` on the first attempt is never retried (treated as "fall back now"), every
  attempt recorded. `health_check()` does a real, cheap live call.
- `service.py` — `record_generation()`: the one function every adapter calls to persist provenance
  + a `GEN_LLM_GENERATION_RECORDED`/`GEN_LLM_FALLBACK_USED` `ProjectEvent`.
- Migration `0007_llm_generation_and_evidence_schema` (additive).

### B.2 Problem 3 — Hypothesis LLM adapter (`harness/diagnosis/llm_hypothesis_adapter.py`)
Drafts 2-3 candidate, falsifiable hypotheses per call, validated against `MECHANISM_CLASSES` and a
"must have ≥1 discriminating test" rule (no falsifier → rejected, never silently accepted).
**Additive only**: merged into the SAME list the deterministic `generate_competing_hypotheses`
produces, before deduplication — never replaces it. Wired into `harness.orchestrator.adapters.
DiagnosisAdapter.start()` behind `request["enable_llm_hypothesis"]` (default `False`).

### B.3 Problem 4 — Strategy Draft LLM adapter (`harness/engineering_design/llm_strategy_adapter.py`)
Drafts 1-2 strategy concepts, validated against the real `STRATEGY_CLASSES` enum. `evidence_links`
is **always left empty** — the LLM's own `evidence_queries` are stored as follow-up queries, never
written in as if they were evidence. Persisted through a small refactor of `strategy_service.py`
(`_persist_strategies` extracted so both the deterministic and LLM paths share one writer, not two
parallel ones). Wired into `DesignAdapter.start()` behind `request["enable_llm_strategy"]`.

### B.4 Problem 5 — LLM Scientific Critic adapter (`harness/scientific_evaluation/llm_critic_adapter.py`)
A real, live-LLM-backed `ScientificReview` (`reviewer_type="llm_critic"`), **added** to the existing
deterministic generalist + domain critics — never replacing them. This is literally the "documented
residual enhancement" `critic.py`'s own module docstring names as the plug-in point.
- Reads only the SAME frozen `ScientificClaim`/`EvidenceAssessment`/`ModelEvaluationRecord`/
  `DeterministicCheckResult` rows the deterministic critic reads — never a Designer's internal
  reasoning (this repo's generators have none to leak; the Strategy LLM adapter's raw completion is
  never passed to this critic either, only the persisted, schema-validated `EngineeringStrategy`).
- `shared_model_risk` is **computed for real** per call (queries whether any prior `hypothesis`/
  `strategy` `LLMGenerationRecord` used the same `model_id`) — not hardcoded `True`, though in this
  single-provider environment it will almost always evaluate to `True`, honestly.
- **Cannot self-approve**: `meta_review.synthesize_meta_review` (unmodified) still requires every
  reviewer to recommend approval before a candidate is eligible, and any reviewer's open blocking
  critical finding blocks the case regardless of others — adding this reviewer only adds scrutiny.
- Wired into `scientific_evaluation/service.py::continue_scientific_evaluation` behind
  `enable_llm_critic=False` (default) — **deliberately opt-in**: turning this on unconditionally
  would have silently converted 100+ pre-existing offline deterministic tests into live-network
  tests, which prompt §10.4 explicitly requires keeping separate.

### B.5 Evidence retrieval + condition matching (`harness/evidence_retrieval/`)
- `contracts.py` — the formal `EvidenceRetrievalAdapter` Protocol (`search`/`fetch`/
  `extract_claims`/`health_check`, prompt §5.6).
- `crossref_adapter.py` — **real**, live adapter against `api.crossref.org`. Its most load-bearing
  use: `resolve_doi()` — a genuine existence check, the concrete mechanism behind invariant #10
  ("DOI 不得补造"). `extract_claims()` is honestly limited to `extraction_method=
  "api_metadata_only"`/`extraction_status="partial"` — Crossref has no full-text/biological content.
- `local_ddr_adapter.py` — wraps the pre-existing `knowledge/ddr_database/*.json` behind the SAME
  contract (DDR-001's own citation, `10.1002/bit.27665`, is a real paper — verified via Crossref).
- `condition_matching.py` — pure, deterministic (no LLM) 8-dimension comparator producing one of 9
  match statuses (`direct_match` … `not_applicable`); cross-strain/cross-species/condition/endpoint
  mismatches are structurally impossible to collapse into a direct match (see rule order in the
  function itself).
- `models.py` — `EvidenceMatchReport` (prompt §5.8's exact fields).
- `harness/diagnosis/models.py::EvidenceItem` extended (migration `0007`, additive columns) with
  the literature-source fields prompt §5.7 requires (title/authors/year/journal/DOI/organism/
  strain/genotype/intervention/comparator/measurement/…) — reused, not forked into a second table.

### B.6 API (`harness/api/generation.py`, registered in `server.py`)
`GET /api/generation/health` (real live provider/Crossref/DDR status), `GET|POST /records`,
`POST /evidence/verify-doi`, `GET /evidence/search`, `GET /evidence/match-reports`.

## C. Test Evidence

```
tests/llm_generation/  → 29 tests, all passing
  test_hypothesis_adapter.py      5   (offline, FakeStructuredGenerationClient)
  test_strategy_adapter.py        3   (offline, fake client)
  test_critic_adapter.py          4   (offline, fake client)
  test_condition_matching.py      7   (offline, pure logic)
  test_evidence_retrieval_live.py 7   (LIVE - real Crossref network calls)
  test_live_llm_generation.py     1   (LIVE - one real Kimi call, kept to one call to bound cost/latency)
  test_api.py                     2   (real FastAPI TestClient + live Crossref/Kimi health check)
```

Required contract cases (prompt §5.9), each with a passing test:
structured generation success (offline fake + 1 live real) · schema-invalid → retry → recovers ·
schema-invalid exhausts retries → deterministic fallback (candidates/rows/review = `[]`/`None`,
never a placeholder) · provider unavailable → immediate fallback, no retry wasted · hallucinated DOI
rejected (real Crossref lookup, both a genuine paper resolving and a fabricated DOI failing) ·
cross-strain / cross-species / condition-mismatch / endpoint-mismatch evidence downgraded, never
silently direct · LLM Critic cannot self-approve · shared_model_risk recorded correctly · LLM
output never entering `evidence_links` · partially-invalid draft lists keep only the valid drafts.

Full regression: `python -m pytest tests/ -q` — running at report time; prior checkpoint after
Phase B was **290/290 passing, 0 regressions**; this phase adds 29 new tests on top with no changes
to any pre-existing test's behavior (all new capabilities are additive/opt-in-default-False).

## D. Repo-Truth Findings Worth Flagging

1. **Kimi's reasoning-token consumption** (§A above) — real, load-bearing finding; every adapter's
   `max_tokens` had to be set far higher (8000-9000) than an initial reasonable guess (1500) to
   leave room for actual output after reasoning. Documented in `client.py`'s own docstring so a
   future adapter author doesn't rediscover this the hard way.
2. **LLM-drafted candidates rarely clear Scientific Evaluation unassisted** (same finding Phase B's
   report already recorded from the deterministic path) — this phase does not change that; the LLM
   Critic adapter, being additive, can only add MORE scrutiny to an already-strict pipeline, never
   less.
3. **Deliberate boundary, not a gap**: retrieved evidence (Crossref/local DDR) is not automatically
   injected into a diagnosis session's `EvidenceItem` chain. The retrieval + DOI-verification +
   condition-matching capability is real, callable, and tested — but auto-writing search results
   into the evidence chain without a human/rule curation step would risk exactly what prompt §2.4
   forbids ("把 LLM 记忆当作检索" / treating retrieval as automatic evidence). A human or a future
   orchestrator step calls `record_evidence_item(...)` with the now-extended literature fields
   after reviewing a `search()`/`fetch()` result — this round builds and proves that capability
   exists; it does not wire an unreviewed auto-ingestion path.

## E. Status Matrix (Phase C items only)

| Requirement | Status | Evidence |
|---|---|---|
| LLM adapter contract + `LLMGenerationRecord` | implemented | `harness/llm_generation/`; 29 tests |
| Hypothesis LLM adapter (additive, Problem 3) | implemented | `llm_hypothesis_adapter.py`; 5 tests; wired opt-in into orchestrator |
| Strategy LLM adapter (additive, Problem 4) | implemented | `llm_strategy_adapter.py`; 3 tests; `evidence_links` never populated from LLM |
| Scientific Critic LLM adapter (additive, Problem 5) | implemented | `llm_critic_adapter.py`; 4 tests; cannot self-approve; shared_model_risk real |
| Deterministic fallback on schema failure | implemented | tested for all 3 adapters |
| Deterministic fallback on provider unavailable | implemented | tested for all 3 adapters |
| Real evidence retrieval adapter | implemented | Crossref (live network) + local DDR, both behind one Protocol |
| DOI hallucination rejection | implemented | real Crossref lookup; genuine paper accepted, fabricated DOI rejected |
| Evidence condition matching (9-state) | implemented | `condition_matching.py`; 7 tests incl. cross-strain/cross-species |
| EcoCyc/BioCyc/UniProt adapters | out_of_scope | UniProt confirmed reachable during audit but no adapter built this round (time-bounded scope decision) |
| Auto-injection of retrieved evidence into diagnosis chain | out_of_scope (deliberate) | see §D.3 — capability exists, auto-wiring intentionally not built |
| API surface | implemented | `harness/api/generation.py`, HTTP-tested |
| Regression (no existing tests broken) | implemented | 290/290 pre-existing tests unaffected; full suite re-run in progress at report time |
