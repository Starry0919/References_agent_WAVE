import copy,json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from harness.server import create_app
from harness.paper_extraction import gold_infrastructure as gi

def draft(role='ADJUDICATOR'):
 return {'benchmark_paper_id':'GOLD-P01','paper_id':'p','role':role,'annotator_id':'human-1','annotation_tier':'ADJUDICATED_GOLD','review_state':'ADJUDICATED_GOLD','revision':1,'source_coverage_review_complete':True,'experiments':[],'claims':[],'evidence':[],'decisions':[],'history':[{'human':'reviewed'}]}
def exp():
 d=draft('ANNOTATOR_A'); e=gi.add_missed_experiment(d);e['experiment_granularity']='ATOMIC_EXPERIMENT';e['experiment_role']='MEASUREMENT';return e
def claim():return {'claim_id':'GOLD-P01-E001-C001','gold_experiment_id':'GOLD-P01-E001','claim_type':'MEASURED_RESULT','subject':'strain','predicate':'grew','object_or_value':'reported','qualifiers':{},'claim_text_normalized':'strain grew','epistemic_status':'DIRECTLY_REPORTED','value_role':'MEASURED','support_status':'SUPPORTED','evidence_ids':['GOLD-P01-E001-V001'],'criticality':'CRITICAL','review_state':'ADJUDICATED','known_ambiguity':'NONE','provenance':{},'annotation_tier':'ADJUDICATED_GOLD'}
def evidence():return {'evidence_id':'GOLD-P01-E001-V001','benchmark_paper_id':'GOLD-P01','paper_id':'p','source_document_id':'d','source_attribution':'current paper','section':'Results','paragraph_id':'p1','page':'UNKNOWN','figure':'NOT_APPLICABLE','panel':'NOT_APPLICABLE','table':'NOT_APPLICABLE','supplement':'NOT_APPLICABLE','other_locator':'NOT_APPLICABLE','anchor_text_or_fingerprint':'abc','quote_or_excerpt':'short excerpt','evidence_scope':'MULTI_ANCHOR','supports_claim_ids':['GOLD-P01-E001-C001'],'support_type':'TEXT_DIRECT','support_strength':'DIRECT','directness':'direct','resolution':'RESOLVED','availability':'AVAILABLE','provenance':{},'review_state':'ADJUDICATED','annotation_tier':'ADJUDICATED_GOLD'}
def complete():
 d=draft();e=exp();e['created_by']='human-1';e['atomic_claim_ids']=['GOLD-P01-E001-C001'];e['evidence_ids']=['GOLD-P01-E001-V001'];d['experiments']=[e];d['claims']=[claim()];d['evidence']=[evidence()];return d

def test_schemas_accept_valid_and_reject_invalid_ids():
 assert not gi.validate_schema('experiment',exp())
 bad=exp();bad['gold_experiment_id']='EXP1';assert gi.validate_schema('experiment',bad)
 assert not gi.validate_schema('claim',claim()) and not gi.validate_schema('evidence',evidence())
def test_duplicate_invalid_reference_unknown_and_gold_independence():
 d=complete();d['experiments'].append(copy.deepcopy(d['experiments'][0]));assert any(x['code']=='G0_DUPLICATE_ID' for x in gi.validate_draft(d,{'paragraph_ids':['p1']})['blockers'])
 d=complete();d['experiments'][0]['candidate_model_ids']=['GOLD-P01-E001'];assert any(x['code']=='G0_MODEL_ID_DEFINES_GOLD' for x in gi.validate_draft(d,{'paragraph_ids':['p1']})['blockers'])
 d=complete();d['experiments'][0]['trigger']='UNKNOWN';assert gi.validate_draft(d,{'paragraph_ids':['p1']})['valid']
def test_silver_or_codex_cannot_pass_human_gate():
 d=complete();d['experiments'][0]['annotation_tier']='SILVER_CANDIDATE';assert not gi.validate_draft(d,{'paragraph_ids':['p1']})['valid']
def test_granularity_relations_and_invalid_parent():
 d=complete();d['experiments'][0]['experiment_granularity']='CAMPAIGN';sub=copy.deepcopy(d['experiments'][0]);sub['gold_experiment_id']='GOLD-P01-E002';sub['experiment_granularity']='SUBEXPERIMENT';sub['parent_experiment_id']='GOLD-P01-E001';sub['atomic_claim_ids']=[];sub['evidence_ids']=[];d['experiments'].append(sub);assert gi.validate_draft(d,{'paragraph_ids':['p1']})['valid']
 sub['parent_experiment_id']='GOLD-P01-E999';assert not gi.validate_draft(d,{'paragraph_ids':['p1']})['valid']
def test_evidence_gates_multi_anchor_unavailable_orphan_and_locator():
 d=complete();d['claims'][0]['evidence_ids']=[];assert any(x['code']=='G4_CRITICAL_CLAIM_WITHOUT_EVIDENCE' for x in gi.validate_draft(d,{'paragraph_ids':['p1']})['blockers'])
 d=complete();d['evidence'][0]['paragraph_id']='missing';assert any(x['code']=='G4_NONEXISTENT_LOCATOR' for x in gi.validate_draft(d,{'paragraph_ids':['p1']})['blockers'])
 d=complete();d['evidence'][0].update(paragraph_id=None,availability='UNAVAILABLE',supplement='S1');assert gi.validate_draft(d,{'paragraph_ids':['p1']})['valid']
def test_add_missed_and_independent_role_save(tmp_path,monkeypatch):
 monkeypatch.setattr(gi,'PACKAGES',tmp_path);p=tmp_path/'GOLD-P01'/'annotations';p.mkdir(parents=True)
 for r in gi.ROLES:gi.atomic_write(p/f'{r}.json',{**draft(r), 'revision':0,'annotation_tier':'UNANNOTATED','review_state':'AWAITING_HUMAN_ANNOTATION'})
 a=gi.load_draft('GOLD-P01','ANNOTATOR_A');gi.add_missed_experiment(a);gi.save_draft('GOLD-P01','ANNOTATOR_A',a,0)
 assert len(gi.load_draft('GOLD-P01','ANNOTATOR_A')['experiments'])==1 and not gi.load_draft('GOLD-P01','ANNOTATOR_B')['experiments']
 with pytest.raises(ValueError):gi.save_draft('GOLD-P01','ANNOTATOR_A',gi.load_draft('GOLD-P01','ANNOTATOR_A'),0)
def test_agreement_open_set_and_adjudication_preserves_versions(tmp_path,monkeypatch):
 monkeypatch.setattr(gi,'PACKAGES',tmp_path);p=tmp_path/'GOLD-P01'/'annotations';p.mkdir(parents=True)
 a=draft('ANNOTATOR_A');b=draft('ANNOTATOR_B');a['experiments']=[exp()];b['experiments']=[]
 gi.atomic_write(p/'ANNOTATOR_A.json',a);gi.atomic_write(p/'ANNOTATOR_B.json',b);gi.atomic_write(p/'ADJUDICATOR.json',draft())
 assert gi.agreement(a,a)['inventory']['f1']==1 and gi.agreement(a,b)['inventory']['annotator_a_only']==1
 package=gi.build_adjudication_package('GOLD-P01');assert package['annotation_a']==a and package['annotation_b']==b
def test_invalid_freeze_and_tamper_detection(tmp_path,monkeypatch):
 monkeypatch.setattr(gi,'PACKAGES',tmp_path/'packages');monkeypatch.setattr(gi,'RELEASES',tmp_path/'releases');monkeypatch.setattr(gi,'SCHEMAS',tmp_path/'schemas')
 gi.RELEASES.mkdir();gi.SCHEMAS.mkdir();gi.atomic_write(gi.SCHEMAS/'experiment.schema.json',{})
 with pytest.raises(ValueError):gi.freeze('skill07-gold-v1.0.0','human')
 rel=gi.RELEASES/'skill07-gold-v0.0.1';rel.mkdir();(rel/'x').write_text('a');gi.atomic_write(rel/'release_manifest.json',{'files':{'x':gi.sha(rel/'x')}})
 assert gi.verify_release('skill07-gold-v0.0.1')['valid'];(rel/'x').write_text('b');assert not gi.verify_release('skill07-gold-v0.0.1')['valid']
def test_scoring_exact_omission_spurious_granularity_ambiguity_and_hard_gates(tmp_path,monkeypatch):
 monkeypatch.setattr(gi,'RELEASES',tmp_path);rel=tmp_path/'skill07-gold-v1.0.0';(rel/'annotations').mkdir(parents=True)
 g=complete();gi.atomic_write(rel/'annotations/GOLD-P01.json',g);gi.atomic_write(rel/'release_manifest.json',{'files':{'annotations/GOLD-P01.json':gi.sha(rel/'annotations/GOLD-P01.json')}})
 c={'experiments':[{'intervention':'UNKNOWN','outcomes':[],'objects':[]}]};s=gi.score_candidate('skill07-gold-v1.0.0','GOLD-P01',c,[{'gold_ids':['GOLD-P01-E001'],'candidate_ids':['0','1']}]);assert s['experiment_metrics']['recall']==1 and s['experiment_metrics']['granularity_error_count']==1
 s=gi.score_candidate('skill07-gold-v1.0.0','GOLD-P01',{'experiments':[]});assert s['hard_gate_failures'][0]['code']=='CRITICAL_EXPERIMENT_OMISSION'
 mech={'experiments':[{'intervention':'mechanism causes growth','outcomes':[],'objects':[]}]};assert any(x['code']=='UNSUPPORTED_MECHANISTIC_CLAIM' for x in gi.score_candidate('skill07-gold-v1.0.0','GOLD-P01',mech,[{'gold_ids':['GOLD-P01-E001'],'candidate_ids':['0']}])['hard_gate_failures'])
def test_workbench_api_lists_packages_and_blind_default():
 c=TestClient(create_app());assert c.get('/api/skill07-gold/papers').status_code==200
 x=c.get('/api/skill07-gold/papers/GOLD-P01/workspace').json();assert x['candidate_context']['hidden'] is True
