from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from harness.bootstrap import Base
from harness.scientific_runtime.service import complete_node, create_task, record_failure, record_human_action, task_view

def session():
    engine = create_engine("sqlite:///:memory:"); Base.metadata.create_all(engine); return Session(engine)

def test_task_graph_and_execution_history():
    with session() as db:
        task = create_task(db, project_id="P1", objective="Improve tryptophan", constraints={"maintain_growth": True}, actor_id="u")
        view = task_view(db, task.task_id); diagnosis = next(n for n in view["graph"] if n["capability_name"] == "diagnosis")
        complete_node(db, task_id=task.task_id, node_id=diagnosis["node_id"], output_refs={"diagnosis_id": "D1"}, provenance={"module": "module2"}, actor_id="system")
        updated = task_view(db, task.task_id)
        assert "diagnosis" in updated["task"]["completed_steps"]
        assert updated["executions"][0]["output_payload"] == {"diagnosis_id": "D1"}
        assert {n["capability_name"] for n in updated["graph"] if n["status"] == "ready"} == {"evidence_retrieval", "world_model_query"}

def test_failure_recovery_and_human_governance():
    with session() as db:
        task = create_task(db, project_id="P1", objective="Run DBTL", constraints={}, actor_id="u")
        node = next(n for n in task_view(db, task.task_id)["graph"] if n["status"] == "ready")
        record_failure(db, task_id=task.task_id, node_id=node["node_id"], classification="tool_unavailable", message="offline", retryable=False, actor_id="system")
        assert task.task_status == "human_review"
        record_human_action(db, task_id=task.task_id, decision="request_modification", actor_id="reviewer", reason="use another capability")
        assert task.task_status == "planning"
