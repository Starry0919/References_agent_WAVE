"""Fail-closed, resumable Human-Gold -> final benchmark orchestrator."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from .gold_infrastructure import PACKAGES,RELEASES,ROOT,agreement,atomic_write,build_adjudication_package,load_draft,read,readiness,validate_draft,verify_release

# Match the benchmark runner's resolved runtime configuration without ever
# serializing the environment or any credential value.
load_dotenv(ROOT/'.env',override=False)

SKILL07_DATA=ROOT/'artifacts'/'data'/'skill07'
GOLD_DATA=ROOT/'artifacts'/'data'/'gold'
STATE_PATH=SKILL07_DATA/'skill07_accelerated_wave_state.json'; BUDGET_PATH=SKILL07_DATA/'skill07_model_call_budget.json'
STATES=('INFRA_READY','P01_AWAITING_HUMANS','P01_READY_FOR_CALIBRATION','CALIBRATION_HOLD','CALIBRATION_PASS','P02_P10_ANNOTATING','AWAITING_ADJUDICATION','GOLD_VALIDATING','GOLD_FREEZE_READY','GOLD_FROZEN_VERIFIED','BENCHMARK_PROVENANCE_READY','PILOT_RUNNING','PILOT_PASS','ROUND1_RUNNING','ROUND1_PASS','REPETITIONS_RUNNING','QUALITY_BENCHMARK_COMPLETE','CONCURRENCY_RUNNING','FINAL_DECISION_READY','COMPLETE')
HUMAN_COMPLETE={'HUMAN_REVIEWED','ADJUDICATED_GOLD','FROZEN_GOLD'}

def role_complete(d:dict[str,Any])->bool:return d.get('review_state') in HUMAN_COMPLETE and bool(d.get('source_coverage_review_complete'))
def paper_status(paper:str)->dict[str,Any]:
    package=PACKAGES/paper; roles={r:load_draft(paper,r) for r in ('ANNOTATOR_A','ANNOTATOR_B','ADJUDICATOR')}
    source=read(package/'source_index.json'); validation=validate_draft(roles['ADJUDICATOR'],source)
    return {'paper':paper,'package_valid':all((package/x).is_file() for x in ('manifest.json','source_index.json','candidate_context.json','review_checklist.json')),'source_valid':bool(source.get('source_document_hash')),'roles':{r:{'revision':d['revision'],'review_state':d['review_state'],'source_coverage':d['source_coverage_review_complete'],'experiments':len(d['experiments']),'claims':len(d['claims']),'evidence':len(d['evidence']),'complete':role_complete(d)} for r,d in roles.items()},'gold_validation':validation,'freeze_eligible':validation['valid']}

def coverage_aids(paper:str)->dict[str,Any]:
    p=PACKAGES/paper; source=read(p/'source_index.json'); context=read(p/'candidate_context.json')
    linked=set()
    for c in context.get('union_candidate_inventory',[]):linked.update((c.get('candidate') or {}).get('evidence_paragraphs',[]))
    paragraphs=source.get('paragraphs',[])
    skipped=[{'paragraph_id':x['paragraph_id'],'section':x.get('section'),'fingerprint':x.get('fingerprint'),'alerts':[a for a,pat in [('INTERVENTION_CUE',r'\b(delete|knockout|overexpress|engineer|construct|evol|screen|treat|culture|assay)\b'),('READOUT_CUE',r'\b(measur|yield|growth|titer|activity|sequenc|significant|result)\b')] if re.search(pat,x.get('text',''),re.I)]} for x in paragraphs if x.get('paragraph_id') not in linked]
    figures=[x for x in source.get('figures',[]) if str(x.get('figure_id') or x.get('id')) not in json.dumps(context)]
    tables=[x for x in source.get('tables',[]) if str(x.get('table_id') or x.get('id')) not in json.dumps(context)]
    return {'paper':paper,'truth_status':'DETERMINISTIC_REVIEW_AID_NOT_GOLD','unlinked_source_regions':skipped,'unlinked_figures':figures,'unlinked_tables':tables,'priority_order':['critical omission/addition','split/merge/granularity','object/intervention/trigger/result','evidence/provenance','causality/mechanism','remaining source coverage','minor fields']}

def provenance_preflight()->dict[str,Any]:
    import harness.paper_extraction.opus_extractor as s
    corrected=read(SKILL07_DATA/'skill07_wave2_baseline_manifest.json')
    expected=corrected['wave1_drift']['resolved_runtime_model']; actual=s.MODEL
    return {'status':'PASS' if actual==expected else 'BENCHMARK_BLOCKED_PROVENANCE_MISMATCH','provider':'poe_code_cli','expected_model':expected,'resolved_runtime_model':actual,'provider_revision':'UNKNOWN','prompt_hash':s._system_prompt_hash(),'skill_hash':s._skill_hash(),'schema_hash':s._schema_hash(),'validator_version':s.VALIDATOR_VERSION,'secrets_serialized':False}

def inspect_state()->dict[str,Any]:
    papers=[paper_status(p.name) for p in sorted(PACKAGES.glob('GOLD-P??'))]; p01=papers[0]
    a_b_ready=p01['roles']['ANNOTATOR_A']['complete'] and p01['roles']['ANNOTATOR_B']['complete']
    frozen=[p.name for p in RELEASES.glob('skill07-gold-v*') if verify_release(p.name)['valid']]
    if frozen:state='GOLD_FROZEN_VERIFIED'
    elif a_b_ready and not p01['roles']['ADJUDICATOR']['complete']:state='P01_READY_FOR_CALIBRATION'
    else:state='P01_AWAITING_HUMANS'
    return {'version':'accelerated-wave-v1','state':state,'engineering_orchestration':'READY','human_gold':'AWAITING_HUMAN_ANNOTATION' if not frozen else 'FROZEN_GOLD','benchmark_decision':'HOLD','production_default':'UNCHANGED','papers':papers,'counts':{'packages':len(papers),'annotator_a_complete':sum(x['roles']['ANNOTATOR_A']['complete'] for x in papers),'annotator_b_complete':sum(x['roles']['ANNOTATOR_B']['complete'] for x in papers),'adjudicated_complete':sum(x['roles']['ADJUDICATOR']['complete'] for x in papers),'gold_experiments':sum(x['roles']['ADJUDICATOR']['experiments'] for x in papers)},'frozen_releases':frozen,'provenance':provenance_preflight(),'next_action':'Complete independent source-first ANNOTATOR_A and ANNOTATOR_B records for GOLD-P01.' if state=='P01_AWAITING_HUMANS' else 'Run deterministic calibration/adjudication workflow.','model_calls_completed':0}

def call_budget()->dict[str,Any]:return {'version':'skill07-model-call-budget-v1','permission_required':'--allow-model-calls','calls_before_verified_gold_allowed':0,'primary_plan':{'pilot':8,'round1':20,'repetitions_2_3':40,'maximum_before_repairs_and_concurrency':68},'completed_valid':0,'invalidated':0,'repair_calls':0,'remaining_primary':68,'historical_reuse_policy':'Compatible historical outputs are scored first after frozen Gold; they do not count as independent new repetitions.','concurrency_calls':'NOT_PLANNED_UNTIL_QUALITY_GATE','secrets_serialized':False}

def calibration_report(state:dict[str,Any])->dict[str,Any]:
    p=state['papers'][0];eligible=p['roles']['ANNOTATOR_A']['complete'] and p['roles']['ANNOTATOR_B']['complete']
    return {'paper':'GOLD-P01','status':'CALIBRATION_READY' if eligible else 'AWAITING_HUMANS','eligible':eligible,'agreement':agreement(load_draft('GOLD-P01','ANNOTATOR_A'),load_draft('GOLD-P01','ANNOTATOR_B')) if eligible else 'NOT_COMPUTED','issue_classes':['TRUE_SCIENTIFIC_DISAGREEMENT','ANNOTATION_GUIDELINE_AMBIGUITY','SCHEMA_LIMITATION','UI_WORKFLOW_PROBLEM','SOURCE_EVIDENCE_AMBIGUITY','GRANULARITY_POLICY_AMBIGUITY','OTHER'],'human_decisions_fabricated':False,'blocker':None if eligible else 'Independent A/B source coverage and reviewed drafts are incomplete.'}

def advance(*,all_papers:bool=True,dry_run:bool=False,allow_model_calls:bool=False)->dict[str,Any]:
    state=inspect_state(); actions=[]
    targets=[p['paper'] for p in state['papers']] if all_papers else ['GOLD-P01']
    for paper in targets:
        actions.append({'action':'REFRESH_COVERAGE_AIDS','paper':paper,'model_calls':0})
        if not dry_run:atomic_write(PACKAGES/paper/'coverage_aids.json',coverage_aids(paper))
    cal=calibration_report(state);actions.append({'action':'CALIBRATION_REPORT','status':cal['status'],'model_calls':0})
    if not dry_run:
        atomic_write(GOLD_DATA/'gold_p01_calibration.json',cal);atomic_write(STATE_PATH,state);atomic_write(BUDGET_PATH,call_budget())
    blocked=[]
    if state['state']=='P01_AWAITING_HUMANS':blocked += [{'phase':'P01_CALIBRATION','status':'NOT_EXECUTED','blocked_by':'P01 independent human A/B annotations incomplete'},{'phase':'GOLD_FREEZE','status':'NOT_EXECUTED','blocked_by':'10-paper adjudicated Gold missing'},{'phase':'EXISTING_A_G_SCORING','status':'NOT_EXECUTED','blocked_by':'verified frozen Gold missing'},{'phase':'PILOT_ROUND1_REPETITIONS_CONCURRENCY','status':'NOT_EXECUTED','blocked_by':'verified frozen Gold and quality gates missing'}]
    planned_calls=0
    if allow_model_calls and not state['frozen_releases']:blocked.append({'phase':'MODEL_CALLS','status':'BLOCKED','blocked_by':'No verified frozen Gold'})
    return {'dry_run':dry_run,'allow_model_calls':allow_model_calls,'model_calls_executed':0,'model_calls_planned_now':planned_calls,'state':state['state'],'actions':actions,'blocked_phases':blocked,'resume_safe':True}
