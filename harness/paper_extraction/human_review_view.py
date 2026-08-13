"""Deterministic, evidence-bounded data for Skill07 human review surfaces."""
from __future__ import annotations
import re
from typing import Any
from .gold_infrastructure import PACKAGES, load_draft, read, validate_draft

ROLES={"ANNOTATOR_A","ANNOTATOR_B","ADJUDICATOR"}

def humanize_locator(value:str|None)->str:
    raw=str(value or '').strip()
    if not raw:return 'Unsectioned'
    raw=re.sub(r'_p\d+$','',raw,flags=re.I)
    if re.fullmatch(r'(?:[a-z]_){2,}[a-z]',raw,flags=re.I):raw=raw.replace('_','')
    words=re.sub(r'\s+',' ',raw.replace('_',' ')).strip()
    known={'abstract':'Abstract','articleinfo':'Article information','references':'References','author contributions':'Author contributions','declaration of competing interest':'Declaration of competing interest'}
    return known.get(words.lower(),words[:1].upper()+words[1:])

def _clean(value:Any)->str:
    text=re.sub(r'!\[[^]]*\]\([^)]*\)','',str(value or ''))
    text=re.sub(r'<[^>]+>','',text)
    text=text.replace('\\_','_').replace('\\*','*')
    return re.sub(r'\s+',' ',text).strip()

def canonical_section(value:str|None)->str:
    label=humanize_locator(value)
    lowered=label.lower()
    if lowered.startswith('abstract'):return 'Abstract'
    if 'introduction' in lowered:return 'Introduction'
    if any(x in lowered for x in ('materials and methods','methods','bacterial strains','construction of','assay','rna seq','data processing')):return 'Materials and Methods · '+re.sub(r'^\d+(?: \d+)*\s*','',label)
    if lowered.startswith('discussion'):return 'Discussion'
    if lowered.startswith('references'):return 'References'
    if re.match(r'^\d',lowered):return 'Results · '+re.sub(r'^\d+(?: \d+)*\s*','',label)
    return label

def build_understanding(benchmark_id:str)->dict[str,Any]:
    package=PACKAGES/benchmark_id;source=read(package/'source_index.json')
    context=read(package/'candidate_context.json') if (package/'candidate_context.json').is_file() else {}
    paragraphs=source.get('paragraphs',[])
    abstract=next((_clean(p.get('text')) for p in paragraphs if humanize_locator(p.get('section'))=='Abstract'),'')
    title=next((humanize_locator(p.get('section')) for p in paragraphs if len(humanize_locator(p.get('section')))>20 and not humanize_locator(p.get('section')).lower().startswith(('abstract','article information'))),source.get('paper_id','Title unavailable'))
    experiments=[]
    for index,item in enumerate(context.get('union_candidate_inventory',[]),1):
        c=item.get('candidate',{}); evidence=[{'label':humanize_locator(x),'locator':x} for x in c.get('evidence_paragraphs',[])]
        experiments.append({'display_number':index,'name':_clean(c.get('title')) or f'Candidate experiment {index}','classification':'AGENT_SCIENTIFIC_INTERPRETATION','review_status':item.get('truth_status','UNREVIEWED'),'scientific_question':'Requires human confirmation from the cited source passages.','engineering_problem':_clean(c.get('problem') or c.get('rationale')) or 'Not explicitly captured; human review required.','strategy':_clean(c.get('intervention')) or 'Measurement/analysis strategy requires human review.','implementation':{'objects':c.get('objects',[]),'conditions':_clean(c.get('conditions')),'controls':_clean(c.get('controls')),'replicates':_clean(c.get('replicates')),'readouts':_clean(c.get('readouts'))},'observation':_clean(c.get('outcomes')) or 'Not captured.','engineering_meaning':'Candidate interpretation only; accept, edit, split, merge, or reject after source review.','evidence':evidence,'confidence':'UNASSESSED','workflow':[{'stage':'Problem','value':_clean(c.get('problem')) or 'Human review required'},{'stage':'Strategy','value':_clean(c.get('intervention')) or 'Human review required'},{'stage':'Action','value':_clean(c.get('analysis')) or _clean(c.get('readouts')) or 'Human review required'},{'stage':'Observation','value':_clean(c.get('outcomes')) or 'Human review required'},{'stage':'Engineering Decision','value':'Pending human review'}]})
    return {'title':title,'paper_fact':{'research_goal_and_strategy':abstract or 'Abstract unavailable in the indexed source.','evidence_label':'Abstract'},'agent_scientific_interpretation':{'summary':'The candidate inventory reconstructs the experimental flow shown below; it is reference material, not Human Gold.','experiment_count':len(experiments)},'hypothesis':{'value':None,'status':'NOT_DIRECTLY_STATED_OR_NOT_REVIEWED'},'experiments':experiments}

def human_source(benchmark_id:str)->dict[str,Any]:
    source=read(PACKAGES/benchmark_id/'source_index.json')
    result={k:v for k,v in source.items() if k not in {'source_document_path','paragraph_ids'}}
    paragraphs=[]
    for index,p in enumerate(source.get('paragraphs',[]),1):
        text=_clean(p.get('text'))
        if not text:continue
        paragraphs.append({'paragraph_id':f'Paragraph {index}','section':canonical_section(p.get('section')),'text':text,'provenance':{'raw_locator':p.get('paragraph_id'),'fingerprint':p.get('fingerprint')}})
    result['paragraphs']=paragraphs
    abstract=next((p['text'] for p in paragraphs if p['section']=='Abstract'),'')
    keywords=next((p['text'].removeprefix('Keywords:').strip() for p in paragraphs if p['section']=='Article information' and p['text'].lower().startswith('keywords:')),'')
    organism='Escherichia coli' if re.search(r'Escherichia coli|E\. coli',f"{abstract} {paragraphs[0]['section'] if paragraphs else ''}",re.I) else None
    result['paper_overview']={'research_area':keywords or None,'organism_or_chassis':organism,'engineering_goal':abstract or None}
    result['figures']=[{'figure_id':x.get('figure_id'),'caption':_clean(x.get('caption'))} for x in source.get('figures',[]) if _clean(x.get('caption'))]
    result['tables']=[{'table_id':x.get('table_id'),'title':_clean(x.get('title'))} for x in source.get('tables',[]) if _clean(x.get('title'))]
    return result

def machine_export(benchmark_id:str,role:str)->dict[str,Any]:
    if role not in ROLES:raise ValueError('invalid role')
    package=PACKAGES/benchmark_id;draft=load_draft(benchmark_id,role);source=human_source(benchmark_id)
    title=next((p['section'] for p in source['paragraphs'] if len(p['section'])>20 and not p['section'].startswith(('Abstract','Article information'))),draft['paper_id'])
    logic=[{'experiment_id':e.get('gold_experiment_id'),'engineering_objective':e.get('biological_engineering_problem'),'design_rationale':e.get('rationale'),'engineering_intervention':e.get('intervention_or_design_action'),'construct_or_system':e.get('implementation'),'validation':e.get('readouts'),'measured_phenotype':e.get('results'),'engineering_knowledge':e.get('annotator_notes')} for e in draft['experiments']]
    validation=validate_draft(draft,read(package/'source_index.json'))
    return {'schema':'skill07.human-gold.machine-readable.v3','schema_version':'3.0.0','gold_status':'WORKING_ANNOTATION_NOT_GOLD','metadata':{'benchmark_paper_id':benchmark_id,'title':title},'full_engineering_design_representation':{'workflow':logic,'design_rounds':draft['experiments'],'detailed_steps':[x for x in draft['decisions'] if x.get('action') in {'ADD_MISSED_STEP','MOVE_STEP','ADD_BRANCH','REMOVE_BRANCH','EDIT_RELATION'}]},'experiments':draft['experiments'],'claims':draft['claims'],'evidence':draft['evidence'],'human_decisions':draft['decisions'],'review_status':draft['review_state'],'provenance':{'source_document_hash':read(package/'source_index.json')['source_document_hash']},'validation':validation,'annotation_source':'INDEPENDENT_HUMAN_REVIEW'}

def review_export(benchmark_id:str,role:str)->dict[str,Any]:
    if role not in ROLES:raise ValueError('invalid role')
    package=PACKAGES/benchmark_id;draft=load_draft(benchmark_id,role);validation=validate_draft(draft,read(package/'source_index.json'))
    field_states=[{'item_id':d.get('payload',{}).get('gold_experiment_id'),'state':d.get('payload',{}).get('field_state','NOT_REVIEWED'),'action':d.get('action')} for d in draft['decisions']]
    return {'schema':'skill07.human-gold.review.v3','schema_version':'3.0.0','benchmark_paper_id':benchmark_id,'reviewer':{'role':role,'annotator_id':draft.get('annotator_id')},'annotation':{'experiments':draft['experiments'],'claims':draft['claims']},'field_level_review_states':field_states,'edits':[x for x in draft['decisions'] if x.get('action')=='EDIT_FIELDS'],'additions':[x for x in draft['decisions'] if str(x.get('action','')).startswith('ADD_')],'deletions_or_rejections':[x for x in draft['decisions'] if x.get('action') in {'NOT_AN_EXPERIMENT','REMOVE_BRANCH'}],'review_state':draft['review_state'],'decisions':draft['decisions'],'unresolved':validation.get('blockers',[]),'comments':[e.get('annotator_notes') for e in draft['experiments'] if e.get('annotator_notes')],'evidence_corrections':[x for x in draft['decisions'] if x.get('action')=='ADD_MISSED_EVIDENCE'],'evidence_links':draft['evidence'],'completion_state':draft.get('source_coverage_review_complete',False),'adjudication_state':draft['review_state'] if role=='ADJUDICATOR' else 'NOT_APPLICABLE_BEFORE_ADJUDICATION','validation':validation}
