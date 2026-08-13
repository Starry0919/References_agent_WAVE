from fastapi.testclient import TestClient
from harness.server import create_app
from harness.paper_extraction.human_review_view import human_source,machine_export

def test_canonical_document_removes_parser_artifacts_for_p01_p02():
    for paper in ('GOLD-P01','GOLD-P02'):
        source=human_source(paper)
        rendered=' '.join(p['text'] for p in source['paragraphs'])
        assert source['paragraphs'] and 'engineering_goal' in source['paper_overview']
        assert not any(token in rendered for token in ('![](', '<sup>', 'images/'))
        assert all(p['paragraph_id'].startswith('Paragraph ') for p in source['paragraphs'])

def test_human_workspace_is_blind_and_has_no_agent_understanding_payload():
    payload=TestClient(create_app()).get('/api/skill07-gold/papers/GOLD-P01/workspace').json()
    assert payload['candidate_context']['hidden'] is True
    assert 'understanding' not in payload
    assert 'source_document_path' not in str(payload['source'])

def test_human_machine_export_contains_only_human_annotation_logic():
    payload=machine_export('GOLD-P01','ANNOTATOR_A')
    assert payload['annotation_source']=='INDEPENDENT_HUMAN_REVIEW'
    assert 'agent_scientific_interpretation' not in str(payload)
    assert 'paper_id' not in payload['metadata']
