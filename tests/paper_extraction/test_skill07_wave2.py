import threading
import time

from tools.skill07_wave2 import (
    InvocationIdentity, align_experiments, blank_telemetry, compare_aligned_outputs,
    normalize_comparison_id, provenance_gate, run_bounded,
)


def _identity(**changes):
    values=dict(provider="poe",source_default_model="claude-sonnet-4.6",configured_model="kimi-k3",resolved_runtime_model="kimi-k3",invocation_model_argument="kimi-k3",provider_resolved_model="UNKNOWN",model_revision="UNKNOWN",cli_tool="poe-code-cli",prompt_hash="p",skill_hash="s",schema_hash="h",validator_hash="v",representation_version="baseline",candidate_id="A_BASELINE",source_document_hash="d",run_id="r",timestamp="2026-08-12T00:00:00Z",alias="kimi-k3",model_parameters={"seed":"NOT_AVAILABLE"})
    values.update(changes); return InvocationIdentity(**values)


def _surfaces():
    x={"provider":"poe","model":"kimi-k3","candidate_id":"A_BASELINE","representation_version":"baseline","source_document_hash":"d","prompt_hash":"p","skill_hash":"s","schema_hash":"h","validator_hash":"v"}
    return x.copy(),x.copy()


def _out(experiments): return {"experimental_design_object":{"experiments":experiments}}


def test_runtime_identity_captured_and_default_cannot_masquerade():
    m,c=_surfaces(); assert provenance_gate(_identity(),m,c)["status"]=="PASS"
    assert provenance_gate(_identity(resolved_runtime_model="claude-sonnet-4.6"),m,c)["status"].startswith("BENCHMARK_BLOCKED")


def test_manifest_or_cache_mismatch_fails_closed_and_no_secrets_serialize():
    m,c=_surfaces(); c["candidate_id"]="G_SAFE_COMBINED"
    assert provenance_gate(_identity(),m,c)["status"].startswith("BENCHMARK_BLOCKED")
    assert not any("key" in k.lower() or "secret" in k.lower() for k in _identity().public_dict())


def test_id_normalization_is_conservative():
    assert normalize_comparison_id("EXP-01")==normalize_comparison_id("exp1")
    assert normalize_comparison_id("EXP1")!=normalize_comparison_id("EXP10")


def test_format_only_ids_and_object_formatting_do_not_create_false_critical():
    a=_out([{"experiment_id":"EXP-01","objects":["Escherichia coli K-12"],"intervention":"delete gene x","outcomes":["growth"]}])
    b=_out([{"experiment_id":"EXP1","objects":["E. coli K 12"],"intervention":"delete gene x","outcomes":["growth"]}])
    result=compare_aligned_outputs(a,b)
    assert result["counts"]["CRITICAL_SCIENTIFIC_DIFFERENCE"]==0


def test_genuinely_different_intervention_is_critical():
    a=_out([{"experiment_id":"EXP1","intervention":"delete gene x"}]); b=_out([{"experiment_id":"EXP01","intervention":"overexpress gene x"}])
    assert compare_aligned_outputs(a,b)["counts"]["CRITICAL_SCIENTIFIC_DIFFERENCE"]==1


def test_evidence_locator_change_is_critical():
    a=_out([{"experiment_id":"EXP1","evidence_paragraphs":["p1"]}]); b=_out([{"experiment_id":"EXP01","evidence_paragraphs":["p2"]}])
    result=compare_aligned_outputs(a,b); assert "evidence" in result["differences"][0]["changed_dimensions"]


def test_ambiguity_is_surfaced_not_forced():
    a=_out([{"experiment_id":"L1","intervention":"delete x"}]); b=_out([{"experiment_id":"R1","intervention":"delete x"},{"experiment_id":"R2","intervention":"delete x"}])
    assert align_experiments(a,b)["unresolved"][0]["reason"]=="AMBIGUOUS_ALIGNMENT_REQUIRES_HUMAN"


def test_gold_ids_can_be_stable_and_review_explicit():
    gold={"gold_experiment_id":"GOLD-P01-E001","source_model_ids":["EXP9"],"review_state":"AWAITING_HUMAN_ADJUDICATION"}
    assert gold["gold_experiment_id"] not in gold["source_model_ids"] and gold["review_state"].startswith("AWAITING")


def test_telemetry_fields_present():
    t=blank_telemetry(final_status="succeeded"); assert t["final_status"]=="succeeded" and t["first_pass_ms"]=="UNKNOWN"


def test_bounded_concurrency_retry_and_failure_isolation():
    active=maximum=0; lock=threading.Lock(); seen={}
    def worker(value):
        nonlocal active,maximum
        seen[value]=seen.get(value,0)+1
        if value==2 and seen[value]==1: raise RuntimeError("transient")
        if value==3: raise ValueError("terminal")
        with lock: active+=1; maximum=max(maximum,active)
        time.sleep(.01)
        with lock: active-=1
        return value
    result=run_bounded([1,2,3,4],worker,2,retry_limit=1)
    assert maximum<=2 and result[1]["attempts"]==2 and result[2]["status"]=="failed" and result[3]["status"]=="succeeded"
