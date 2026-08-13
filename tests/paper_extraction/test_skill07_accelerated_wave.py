import copy,json
from pathlib import Path
from harness.paper_extraction import accelerated_wave as aw

def test_current_state_is_human_blocked_and_no_fabrication():
 s=aw.inspect_state();assert s['state']=='P01_AWAITING_HUMANS';assert s['counts']['gold_experiments']==0
def test_dry_run_is_zero_calls_and_does_not_write(tmp_path,monkeypatch):
 monkeypatch.setattr(aw,'STATE_PATH',tmp_path/'state.json');monkeypatch.setattr(aw,'BUDGET_PATH',tmp_path/'budget.json')
 out=aw.advance(dry_run=True);assert out['model_calls_executed']==0 and not aw.STATE_PATH.exists() and not aw.BUDGET_PATH.exists()
def test_calls_blocked_before_gold_even_with_permission():
 out=aw.advance(dry_run=True,allow_model_calls=True);assert out['model_calls_executed']==0 and out['model_calls_planned_now']==0
def test_resume_does_not_modify_role_drafts():
 paths=list(aw.PACKAGES.glob('GOLD-P??/annotations/*.json'));before={p:p.read_bytes() for p in paths};aw.advance();assert all(p.read_bytes()==v for p,v in before.items())
def test_coverage_aids_are_not_gold_and_cover_skipped_regions():
 x=aw.coverage_aids('GOLD-P01');assert x['truth_status']=='DETERMINISTIC_REVIEW_AID_NOT_GOLD' and 'unlinked_source_regions' in x
def test_iaa_ineligible_until_real_a_and_b():
 x=aw.calibration_report(aw.inspect_state());assert not x['eligible'] and x['agreement']=='NOT_COMPUTED'
def test_p01_history_is_read_only_during_advance():
 a=aw.load_draft('GOLD-P01','ANNOTATOR_A');before=copy.deepcopy(a.get('history'));aw.advance();assert aw.load_draft('GOLD-P01','ANNOTATOR_A').get('history')==before
def test_budget_has_68_primary_and_zero_completed():
 b=aw.call_budget();assert b['primary_plan']['maximum_before_repairs_and_concurrency']==68 and b['completed_valid']==0
def test_provenance_preflight_captures_runtime_and_no_secrets():
 p=aw.provenance_preflight();assert p['status']=='PASS' and p['resolved_runtime_model']=='kimi-k3' and p['secrets_serialized'] is False
def test_early_downstream_phases_are_explicitly_blocked():
 x=aw.advance(dry_run=True);names={p['phase'] for p in x['blocked_phases']};assert 'GOLD_FREEZE' in names and 'PILOT_ROUND1_REPETITIONS_CONCURRENCY' in names
