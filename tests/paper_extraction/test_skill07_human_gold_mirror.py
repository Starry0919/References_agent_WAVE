from fastapi.testclient import TestClient
from harness.server import create_app
from harness.paper_extraction.human_review_view import machine_export,review_export

def test_mirror_exports_are_human_gold_not_agent_extraction():
    machine=machine_export('GOLD-P01','ANNOTATOR_A')
    review=review_export('GOLD-P01','ANNOTATOR_A')
    assert machine['annotation_source']=='INDEPENDENT_HUMAN_REVIEW'
    assert {'workflow','design_rounds','detailed_steps'} <= machine['full_engineering_design_representation'].keys()
    assert 'agent_trace' not in str(machine).lower() and 'confidence' not in str(machine).lower()
    assert review['reviewer']['role']=='ANNOTATOR_A'
    assert {'field_level_review_states','edits','additions','deletions_or_rejections','evidence_corrections'} <= review.keys()

def test_workspace_is_per_paper_blind_and_routes_are_available():
    client=TestClient(create_app())
    p1=client.get('/api/skill07-gold/papers/GOLD-P01/workspace?role=ANNOTATOR_A').json()
    p2=client.get('/api/skill07-gold/papers/GOLD-P02/workspace?role=ANNOTATOR_A').json()
    assert p1['manifest']['benchmark_paper_id']=='GOLD-P01'
    assert p2['manifest']['benchmark_paper_id']=='GOLD-P02'
    assert p1['candidate_context']['hidden'] and p2['candidate_context']['hidden']
    assert 'ANNOTATOR_B' not in str(p1['draft'])

def test_new_workflow_review_actions_are_accepted_without_touching_agent_data(monkeypatch):
    # Endpoint action vocabulary is covered without mutating the repository's
    # real role drafts: save is intercepted after the action is appended.
    import harness.api.skill07_gold as api
    draft={'revision':0,'decisions':[]}
    monkeypatch.setattr(api,'load_draft',lambda paper,role:draft)
    monkeypatch.setattr(api,'save_draft',lambda paper,role,value,revision:value)
    body=api.DecisionBody(role='ANNOTATOR_A',action='EDIT_RELATION',payload={'gold_experiment_id':'GOLD-P01-E001'})
    result=api.decision('GOLD-P01',body)
    assert result['decisions']==[{'action':'EDIT_RELATION','payload':body.payload}]
