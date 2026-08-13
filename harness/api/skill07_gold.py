from __future__ import annotations
from typing import Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from harness.paper_extraction.gold_infrastructure import PACKAGES,add_missed_experiment,agreement,build_adjudication_package,load_draft,read,readiness,save_draft,validate_draft
from harness.paper_extraction.gold_exports import original_pdf,paper_metadata,review_pdf
from harness.paper_extraction.human_review_view import human_source,machine_export,review_export

router=APIRouter(prefix='/api/skill07-gold',tags=['skill07-gold'])
class SaveBody(BaseModel): role:str; expected_revision:int; draft:dict[str,Any]
class DecisionBody(BaseModel): role:str; action:str; payload:dict[str,Any]=Field(default_factory=dict)

@router.get('/papers')
def papers(): return {'papers':[read(p/'manifest.json') for p in sorted(PACKAGES.glob('GOLD-P??'))]}
@router.get('/papers/{paper}/workspace')
def workspace(paper:str,role:str='ANNOTATOR_A',show_candidates:bool=False):
    p=PACKAGES/paper
    if not p.is_dir():raise HTTPException(404,'paper package not found')
    return {'manifest':read(p/'manifest.json'),'metadata':paper_metadata(paper),'source':human_source(paper),'coverage_aids':read(p/'coverage_aids.json') if (p/'coverage_aids.json').is_file() else {},'draft':load_draft(paper,role),'candidate_context':read(p/'candidate_context.json') if show_candidates else {'hidden':True,'reason':'BLIND_SOURCE_FIRST'}}
@router.patch('/papers/{paper}/draft')
def put_draft(paper:str,body:SaveBody):
    try:return save_draft(paper,body.role,body.draft,body.expected_revision)
    except (ValueError,FileNotFoundError) as e:raise HTTPException(409,str(e))
@router.post('/papers/{paper}/decisions')
def decision(paper:str,body:DecisionBody):
    draft=load_draft(paper,body.role)
    if body.action=='ADD_MISSED_EXPERIMENT':add_missed_experiment(draft)
    elif body.action in {'MERGE_WITH','SPLIT_INTO','LINK_AS_SUBEXPERIMENT','ACCEPT_AS_EXPERIMENT','NOT_AN_EXPERIMENT','EDIT_FIELDS','MARK_UNCERTAIN','REQUEST_SECOND_REVIEW','ADD_MISSED_STEP','ADD_MISSED_EVIDENCE','ADD_MISSED_CLAIM','ADD_BRANCH','REMOVE_BRANCH','EDIT_RELATION','MOVE_STEP'}:draft['decisions'].append({'action':body.action,'payload':body.payload})
    else:raise HTTPException(422,'unsupported decision')
    return save_draft(paper,body.role,draft,draft['revision'])
@router.post('/papers/{paper}/validate')
def validate(paper:str,role:str='ANNOTATOR_A'):return validate_draft(load_draft(paper,role),read(PACKAGES/paper/'source_index.json'))
@router.get('/papers/{paper}/agreement')
def get_agreement(paper:str):return agreement(load_draft(paper,'ANNOTATOR_A'),load_draft(paper,'ANNOTATOR_B'))
@router.post('/papers/{paper}/adjudication-package')
def adjudication(paper:str):return build_adjudication_package(paper)
@router.get('/readiness')
def get_readiness():return readiness()
@router.get('/papers/{paper}/review-package.pdf')
def download_review_package(paper:str,role:str='ANNOTATOR_A',locale:str='zh-CN'):
    try:data,name=review_pdf(paper,role,locale)
    except (ValueError,FileNotFoundError) as e:raise HTTPException(409,str(e))
    return Response(data,media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename="{name}"','X-Gold-Tier':'WORKING_ANNOTATION_NOT_GOLD'})
@router.get('/papers/{paper}/original.pdf')
def download_original_pdf(paper:str):
    try:path,name=original_pdf(paper)
    except (ValueError,FileNotFoundError) as e:raise HTTPException(404,str(e))
    return FileResponse(path,media_type='application/pdf',filename=name)

@router.get('/papers/{paper}/machine-readable.json')
def download_machine_json(paper:str,role:str='ANNOTATOR_A'):
    try:data=machine_export(paper,role)
    except (ValueError,FileNotFoundError) as e:raise HTTPException(409,str(e))
    import json
    return Response(json.dumps(data,ensure_ascii=False,indent=2),media_type='application/json',headers={'Content-Disposition':f'attachment; filename="{paper}_{role}_machine-readable.json"'})

@router.get('/papers/{paper}/review.json')
def download_review_json(paper:str,role:str='ANNOTATOR_A'):
    try:data=review_export(paper,role)
    except (ValueError,FileNotFoundError) as e:raise HTTPException(409,str(e))
    import json
    return Response(json.dumps(data,ensure_ascii=False,indent=2),media_type='application/json',headers={'Content-Disposition':f'attachment; filename="{paper}_{role}_review.json"'})
