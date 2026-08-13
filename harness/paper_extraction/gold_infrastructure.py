"""Source-first Skill07 human-Gold lifecycle; never calls a model."""
from __future__ import annotations

import hashlib, json, os, re, shutil, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
GOLD_ROOT=ROOT/'benchmarks/skill07_human_gold'
SCHEMAS=GOLD_ROOT/'schemas'; PACKAGES=GOLD_ROOT/'packages'; RELEASES=GOLD_ROOT/'releases'; AUDIT=GOLD_ROOT/'audit'
TIERS=('UNANNOTATED','SILVER_CANDIDATE','HUMAN_DRAFT','HUMAN_REVIEWED','ADJUDICATED_GOLD','FROZEN_GOLD')
ROLES=('ANNOTATOR_A','ANNOTATOR_B','ADJUDICATOR')
HUMAN_TIERS={'HUMAN_DRAFT','HUMAN_REVIEWED','ADJUDICATED_GOLD','FROZEN_GOLD'}
ID_PATTERNS={'experiment':re.compile(r'^GOLD-P\d{2}-E\d{3}$'),'claim':re.compile(r'^GOLD-P\d{2}-E\d{3}-C\d{3}$'),'evidence':re.compile(r'^GOLD-P\d{2}-E\d{3}-V\d{3}$')}

def now(): return datetime.now(timezone.utc).isoformat()
def sha(path:Path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path:Path): return json.loads(path.read_text(encoding='utf-8'))
def atomic_write(path:Path,value:Any):
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=path.parent,delete=False,suffix='.tmp') as f:
        json.dump(value,f,ensure_ascii=False,indent=2); temp=Path(f.name)
    os.replace(temp,path)

def schema(kind:str)->dict[str,Any]: return read(SCHEMAS/f'{kind}.schema.json')
def validate_schema(kind:str,value:Any)->list[dict[str,str]]:
    return [{'code':f'SCHEMA_{kind.upper()}','path':'/'.join(map(str,e.path)),'message':e.message} for e in Draft202012Validator(schema(kind)).iter_errors(value)]

def role_draft_path(paper_id:str,role:str)->Path:
    if role not in ROLES: raise ValueError('invalid role')
    return PACKAGES/paper_id/'annotations'/f'{role}.json'

def load_draft(paper_id:str,role:str)->dict[str,Any]: return read(role_draft_path(paper_id,role))
def save_draft(paper_id:str,role:str,draft:dict[str,Any],expected_revision:int|None=None)->dict[str,Any]:
    path=role_draft_path(paper_id,role); current=read(path)
    if current['role']!=role: raise ValueError('role isolation violation')
    if expected_revision is not None and current['revision']!=expected_revision: raise ValueError('revision conflict')
    if draft.get('role')!=role or draft.get('benchmark_paper_id')!=paper_id: raise ValueError('cross-role or cross-paper overwrite denied')
    draft=dict(draft); draft['revision']=current['revision']+1; draft['updated_at']=now()
    atomic_write(path,draft); append_audit(paper_id,role,'SAVE_DRAFT',{'revision':draft['revision']}); return draft

def append_audit(paper_id:str,actor:str,action:str,details:dict[str,Any]):
    path=AUDIT/'actions.jsonl'; path.parent.mkdir(parents=True,exist_ok=True)
    safe={k:v for k,v in details.items() if not re.search(r'(?i)(secret|token|api.?key|authorization)',k)}
    with path.open('a',encoding='utf-8') as f: f.write(json.dumps({'timestamp':now(),'paper_id':paper_id,'actor':actor,'action':action,'details':safe},ensure_ascii=False)+'\n')

def add_missed_experiment(draft:dict[str,Any])->dict[str,Any]:
    paper=draft['benchmark_paper_id']; used={x['gold_experiment_id'] for x in draft['experiments']}
    n=1
    while f'{paper}-E{n:03d}' in used:n+=1
    exp={'gold_experiment_id':f'{paper}-E{n:03d}','benchmark_paper_id':paper,'paper_id':draft['paper_id'],'annotation_tier':'HUMAN_DRAFT','review_state':'DRAFT','experiment_title':'','experiment_role':'UNCERTAIN','experiment_granularity':'UNCERTAIN','parent_experiment_id':None,'iteration_or_stage':'UNKNOWN','relations':[],'biological_objects':[],'intervention_or_design_action':'UNKNOWN','trigger':'UNKNOWN','conditions':[],'implementation':'UNKNOWN','controls':[],'replicates':{'status':'NOT_REPORTED'},'readouts':[],'analysis':[],'results':[],'rationale':'UNKNOWN','supported_alternatives':[],'supported_rule':'UNKNOWN','rule_scope':'UNKNOWN','atomic_claim_ids':[],'evidence_ids':[],'critical_provenance':[],'known_ambiguities':[],'annotator_notes':'','created_by':draft['role'],'created_at':now(),'updated_at':now(),'schema_version':'1.0.0','origin_flags':['HUMAN_ADDED']}
    draft['experiments'].append(exp); return exp

def validate_draft(draft:dict[str,Any],source_index:dict[str,Any]|None=None)->dict[str,Any]:
    blockers=[]; warnings=[]
    experiments=draft.get('experiments',[]); claims=draft.get('claims',[]); evidence=draft.get('evidence',[])
    for kind,items,idkey in [('experiment',experiments,'gold_experiment_id'),('claim',claims,'claim_id'),('evidence',evidence,'evidence_id')]:
        ids=[x.get(idkey) for x in items]
        if len(ids)!=len(set(ids)): blockers.append({'code':'G0_DUPLICATE_ID','kind':kind})
        for item in items:
            blockers += validate_schema(kind,item)
            if item.get(idkey) and not ID_PATTERNS[kind].fullmatch(item[idkey]): blockers.append({'code':'G0_INVALID_STABLE_ID','id':item[idkey]})
            if any(str(item.get(idkey,'')).casefold()==str(x).casefold() for x in item.get('candidate_model_ids',[])): blockers.append({'code':'G0_MODEL_ID_DEFINES_GOLD','id':item.get(idkey)})
            if item.get('annotation_tier') not in HUMAN_TIERS: blockers.append({'code':'G6_NON_HUMAN_TIER','id':item.get(idkey)})
    expids={x.get('gold_experiment_id') for x in experiments}; claimids={x.get('claim_id') for x in claims}; evidenceids={x.get('evidence_id') for x in evidence}
    for exp in experiments:
        if exp.get('parent_experiment_id') and exp['parent_experiment_id'] not in expids: blockers.append({'code':'G2_INVALID_PARENT','id':exp['gold_experiment_id']})
        if exp.get('experiment_granularity')=='UNCERTAIN': blockers.append({'code':'G2_UNRESOLVED_GRANULARITY','id':exp['gold_experiment_id']})
        for x in exp.get('atomic_claim_ids',[]):
            if x not in claimids:blockers.append({'code':'G3_ORPHAN_CLAIM_REFERENCE','id':x})
        for x in exp.get('evidence_ids',[]):
            if x not in evidenceids:blockers.append({'code':'G4_ORPHAN_EVIDENCE_REFERENCE','id':x})
    for claim in claims:
        if claim.get('gold_experiment_id') not in expids:blockers.append({'code':'G3_ORPHAN_CLAIM','id':claim.get('claim_id')})
        if claim.get('criticality')=='CRITICAL' and claim.get('epistemic_status')=='DIRECTLY_REPORTED' and not claim.get('evidence_ids'):blockers.append({'code':'G4_CRITICAL_CLAIM_WITHOUT_EVIDENCE','id':claim.get('claim_id')})
        for x in claim.get('evidence_ids',[]):
            if x not in evidenceids:blockers.append({'code':'G4_MISSING_EVIDENCE','id':x})
        if claim.get('claim_type') in {'CAUSAL_RESULT','MECHANISTIC_INTERPRETATION'} and claim.get('epistemic_status')=='DIRECTLY_REPORTED' and claim.get('support_status')!='SUPPORTED': blockers.append({'code':'G5_UNSUPPORTED_CAUSAL_UPGRADE','id':claim.get('claim_id')})
    anchors=set((source_index or {}).get('paragraph_ids',[]))
    for ev in evidence:
        if not ev.get('supports_claim_ids'): warnings.append({'code':'G4_ORPHAN_EVIDENCE','id':ev.get('evidence_id')})
        for x in ev.get('supports_claim_ids',[]):
            if x not in claimids:blockers.append({'code':'G4_EVIDENCE_ORPHAN_CLAIM','id':x})
        pid=ev.get('paragraph_id')
        if pid and anchors and pid not in anchors and ev.get('availability')=='AVAILABLE':blockers.append({'code':'G4_NONEXISTENT_LOCATOR','id':ev.get('evidence_id'),'paragraph_id':pid})
    if not draft.get('source_coverage_review_complete'):blockers.append({'code':'G1_SOURCE_COVERAGE_NOT_CONFIRMED'})
    if draft.get('role')!='ADJUDICATOR' or draft.get('review_state') not in {'ADJUDICATED_GOLD','FROZEN_GOLD'}:blockers.append({'code':'G6_ADJUDICATION_INCOMPLETE'})
    if not draft.get('history'):blockers.append({'code':'G7_HISTORY_MISSING'})
    return {'valid':not blockers,'blockers':blockers,'warnings':warnings,'gate_summary':{f'G{i}':not any(b['code'].startswith(f'G{i}') for b in blockers) for i in range(8)}}

def agreement(a:dict[str,Any],b:dict[str,Any])->dict[str,Any]:
    ae={x['gold_experiment_id'] for x in a.get('experiments',[])}; be={x['gold_experiment_id'] for x in b.get('experiments',[])}
    matched=len(ae&be); precision=matched/len(be) if be else 1.; recall=matched/len(ae) if ae else 1.
    return {'inventory':{'matched':matched,'annotator_a_only':len(ae-be),'annotator_b_only':len(be-ae),'precision_style_overlap':precision,'recall_style_overlap':recall,'f1':2*precision*recall/(precision+recall) if precision+recall else 0.,'jaccard':matched/len(ae|be) if ae|be else 1.},'boundary_granularity_agreement':'NOT_COMPUTABLE_UNTIL_MATCHED_SOURCE_IDENTITIES','field_level_agreement':'NOT_COMPUTABLE_UNTIL_MATCHED_SOURCE_IDENTITIES','atomic_claim_agreement':'NOT_COMPUTABLE_UNTIL_ANNOTATED','evidence_anchor_agreement':'NOT_COMPUTABLE_UNTIL_ANNOTATED','critical_claim_agreement':'NOT_COMPUTABLE_UNTIL_ANNOTATED','adjudication_rate':'NOT_APPLICABLE_BEFORE_ADJUDICATION','limitations':['Open-set discovery is not assigned fixed negatives; kappa is not used for inventory.']}

def build_adjudication_package(paper_id:str)->dict[str,Any]:
    a=load_draft(paper_id,'ANNOTATOR_A'); b=load_draft(paper_id,'ANNOTATOR_B')
    value={'benchmark_paper_id':paper_id,'created_at':now(),'annotation_a':a,'annotation_b':b,'agreement':agreement(a,b),'adjudicator_decisions':[],'prior_versions':{'A':a['revision'],'B':b['revision']}}
    atomic_write(PACKAGES/paper_id/'adjudication'/'reconciliation.json',value); return value

def freeze(version:str,actor_id:str)->dict[str,Any]:
    if not re.fullmatch(r'skill07-gold-v\d+\.\d+\.\d+',version):raise ValueError('version must be skill07-gold-vMAJOR.MINOR.PATCH')
    target=RELEASES/version
    if target.exists():raise FileExistsError('release already exists; frozen releases are immutable')
    validations=[]; sources=[]
    for package in sorted(PACKAGES.glob('GOLD-P??')):
        draft=load_draft(package.name,'ADJUDICATOR'); source=read(package/'source_index.json'); result=validate_draft(draft,source); validations.append({'paper':package.name,**result})
        if not result['valid']:raise ValueError(f'{package.name} cannot freeze: {result["blockers"]}')
        sources.append((package,draft,source))
    if len(sources)!=10:raise ValueError('exactly 10 validated papers required')
    temp=RELEASES/f'.{version}.tmp'; temp.mkdir(parents=True,exist_ok=False)
    try:
        (temp/'annotations').mkdir(); (temp/'schemas').mkdir()
        files=[]
        for package,draft,source in sources:
            atomic_write(temp/'annotations'/f'{package.name}.json',draft); files.append(temp/'annotations'/f'{package.name}.json')
        for p in SCHEMAS.glob('*.json'): shutil.copy2(p,temp/'schemas'/p.name); files.append(temp/'schemas'/p.name)
        manifest={'release':version,'schema_version':'1.0.0','papers':[p.name for p,_,_ in sources],'freeze_timestamp':now(),'actor_id':actor_id,'parent_release':None,'known_uncertainties':[],'files':{str(p.relative_to(temp)).replace('\\','/'):sha(p) for p in files},'source_fingerprints':{p.name:source['source_document_hash'] for p,_,source in sources},'validation':validations,'policy':'PATCH correction; MINOR additive adjudicated coverage; MAJOR semantic policy/schema change'}
        atomic_write(temp/'release_manifest.json',manifest); os.replace(temp,target)
    except Exception:
        if temp.exists():shutil.rmtree(temp)
        raise
    return verify_release(version)

def verify_release(version:str)->dict[str,Any]:
    target=RELEASES/version; manifest=read(target/'release_manifest.json'); expected=set(manifest['files'])|{'release_manifest.json'}
    actual={str(p.relative_to(target)).replace('\\','/') for p in target.rglob('*') if p.is_file()}
    mismatches=[{'code':'MISSING_FILE','file':x} for x in sorted(expected-actual)]+[{'code':'UNEXPECTED_FILE','file':x} for x in sorted(actual-expected)]
    for rel,digest in manifest['files'].items():
        p=target/rel
        if p.is_file() and sha(p)!=digest:mismatches.append({'code':'HASH_MISMATCH','file':rel})
    return {'valid':not mismatches,'release':version,'mismatches':mismatches}

def score_candidate(version:str,paper_id:str,candidate:dict[str,Any],granularity_map:list[dict[str,Any]]|None=None)->dict[str,Any]:
    verification=verify_release(version)
    if not verification['valid']:raise ValueError('frozen release verification failed')
    gold=read(RELEASES/version/'annotations'/f'{paper_id}.json'); gold_exps=gold['experiments']; cand=((candidate.get('experimental_design_object') or candidate).get('experiments',[]))
    mappings=granularity_map or []; mapped_gold={g for m in mappings for g in m.get('gold_ids',[])}; mapped_cand={c for m in mappings for c in m.get('candidate_ids',[])}
    unresolved=[]
    # Conservative scientific signature, never ID-only.
    for gi,g in enumerate(gold_exps):
        if g['gold_experiment_id'] in mapped_gold:continue
        matches=[]
        gt=' '.join(map(str,[g.get('intervention_or_design_action'),g.get('results'),g.get('biological_objects')])).casefold()
        for ci,c in enumerate(cand):
            ct=' '.join(map(str,[c.get('intervention'),c.get('design_action'),c.get('outcomes'),c.get('objects')])).casefold()
            gs=set(re.findall(r'[a-z0-9]+',gt)); cs=set(re.findall(r'[a-z0-9]+',ct)); sim=len(gs&cs)/len(gs|cs) if gs|cs else 0
            if sim>=.45:matches.append((sim,ci))
        if len(matches)==1:mapped_gold.add(g['gold_experiment_id']);mapped_cand.add(str(matches[0][1]))
        else:unresolved.append({'gold_id':g['gold_experiment_id'],'candidate_indices':[x[1] for x in matches]})
    omissions=len(gold_exps)-len(mapped_gold); spurious=max(0,len(cand)-len(mapped_cand)); hard=[]
    if omissions:hard.append({'code':'CRITICAL_EXPERIMENT_OMISSION','count':omissions})
    for c in cand:
        text=json.dumps(c,ensure_ascii=False).casefold()
        if ('caus' in text or 'mechanism' in text) and not c.get('evidence_paragraphs'):hard.append({'code':'UNSUPPORTED_MECHANISTIC_CLAIM'})
    return {'release':version,'paper_id':paper_id,'experiment_metrics':{'gold_total':len(gold_exps),'candidate_total':len(cand),'matched_gold':len(mapped_gold),'recall':len(mapped_gold)/len(gold_exps) if gold_exps else 1.,'precision':len(mapped_cand)/len(cand) if cand else (1. if not gold_exps else 0.),'true_omission_count':omissions,'spurious_experiment_count':spurious,'granularity_error_count':sum(len(m.get('gold_ids',[]))!=len(m.get('candidate_ids',[])) for m in mappings),'unresolved_alignment_count':len(unresolved)},'field_metrics':'REQUIRES_ADJUDICATED_ATOMIC_CLAIMS','claim_metrics':'REQUIRES_ADJUDICATED_ATOMIC_CLAIMS','evidence_metrics':'REQUIRES_ADJUDICATED_EVIDENCE','unresolved':unresolved,'hard_gate_failures':hard,'scientifically_non_inferior':not hard and not unresolved,'performance_compensation_allowed':False}

def readiness()->dict[str,Any]:
    releases=[]
    for p in RELEASES.glob('skill07-gold-v*'):
        v=verify_release(p.name)
        if v['valid']:releases.append(p.name)
    return {'eligible_for_two_paper_pilot':False if not releases else True,'required_10_paper_gold_complete':bool(releases),'independent_review_adjudication_complete':bool(releases),'validator_passed':bool(releases),'frozen_release_verified':bool(releases),'scoring_tests_required':True,'unresolved_critical_gold_blockers':'AWAITING_HUMAN_ANNOTATION' if not releases else 'CHECK_RELEASE','benchmark_decision':'HOLD'}
