from __future__ import annotations
import json
from pathlib import Path
import pytest

from harness.paper_extraction.execution_plan import OutputType, LiteratureExecutionBlocked, build_execution_plan
from harness.paper_extraction.quantitative_roles import (
    QuantitativeObservation, QuantitativeSemanticRole as R, assert_projection_allowed, classify_quantitative_role,
    classify_quantitative_mentions,
)

def doc(title, body):
    return {"document_metadata":{"paper_id":"p"},"sections":[{"title":title,"content":body}],
            "paragraphs":[{"paragraph_id":"p1","section":"results","text":body}]}

def test_method_benchmark_is_blocked_before_wet_lab_extraction():
    plan=build_execution_plan(doc("A dynamic reasoning framework for cell factory design", "We benchmarked 120 tasks. An 8-cycle computation completed in 2 min. Accuracy was 91.67%."))
    assert plan.execution_route == "BENCHMARK_ROUTE"
    with pytest.raises(LiteratureExecutionBlocked): plan.assert_output_allowed(OutputType.EXPERIMENT_INSTANCE)
    with pytest.raises(LiteratureExecutionBlocked): plan.assert_output_allowed(OutputType.K12_PROPOSAL)

def test_database_routes_to_resource_not_experiment():
    plan=build_execution_plan(doc("A database of over 15,000 strain design publications", "We constructed a database containing host, product, gene direction and co-occurrence records."))
    assert plan.execution_route == "RESOURCE_ROUTE"
    assert OutputType.HISTORICAL_PRIOR in plan.allowed_output_types
    assert OutputType.EXPERIMENT_INSTANCE in plan.forbidden_output_types

def test_primary_experiment_is_not_killed():
    plan=build_execution_plan(doc("Engineering E. coli for L-tryptophan production", "We cultured engineered E. coli in M9 glucose for 24 h and measured titer in three biological replicates."))
    assert plan.execution_route == "PRIMARY_EXPERIMENTAL_ROUTE"
    plan.assert_output_allowed(OutputType.EXPERIMENT_INSTANCE)

@pytest.mark.parametrize("text,value,unit,role",[
    ("The benchmark contained n=120 tasks",120,"n",R.BENCHMARK_SAMPLE_COUNT),
    ("Model inference completed in 2 min runtime",2,"min",R.COMPUTATION_RUNTIME),
    ("n=3 biological replicates were measured",3,"n",R.BIOLOGICAL_REPLICATE_COUNT),
    ("cultivated for 24 h",24,"h",R.CULTIVATION_DURATION),
    ("centrifuged for 10 min",10,"min",R.CENTRIFUGATION_TIME),
])
def test_quantitative_roles_do_not_cross(text,value,unit,role):
    actual, confidence, flags=classify_quantitative_role(text,value,unit)
    assert actual == role and confidence > .9 and not flags

def test_benchmark_count_cannot_populate_biological_replicates():
    obs=QuantitativeObservation(observation_id="q1",value=120,unit="n",semantic_role=R.BENCHMARK_SAMPLE_COUNT,confidence=.95)
    with pytest.raises(ValueError): assert_projection_allowed(obs,"biological_replicates")

@pytest.mark.parametrize("text,roles",[
    ("n=120 benchmark + n=3 biological replicates",[R.BENCHMARK_SAMPLE_COUNT,R.BIOLOGICAL_REPLICATE_COUNT]),
    ("2 min computation runtime + 24 h cultivation",[R.COMPUTATION_RUNTIME,R.CULTIVATION_DURATION]),
    ("10 min centrifugation + 12 h incubation",[R.CENTRIFUGATION_TIME,R.INCUBATION_DURATION]),
])
def test_mixed_context_quantities_have_zero_cross_contamination(text,roles):
    assert [x.semantic_role for x in classify_quantitative_mentions(text)] == roles
