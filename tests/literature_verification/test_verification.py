import httpx
from pathlib import Path
from harness.literature_discovery.models import PaperCandidate
from harness.literature_discovery.resolvers import ResolverRouter
from harness.literature_discovery.pdf_identity import verify_pdf_identity
from harness.literature_verification.verifier import verify_document
from harness.literature_verification.gold import evaluate
from harness.literature_verification.canonical import from_markdown,from_skill06,resolve_anchor
from harness.literature_verification.gold import agreement,adjudication_queue
from harness.literature_verification.admission import evaluate_admission

def test_router_priority_dedup_and_unpaywall_config_required():
 def h(r):
  u=str(r.url)
  if 'idconv' in u:return httpx.Response(200,json={'records':[{'pmcid':'PMC1'}]})
  if 'openalex' in u:return httpx.Response(200,json={'best_oa_location':{'pdf_url':'https://x/a.pdf'},'locations':[]})
  if 'semanticscholar' in u:return httpx.Response(429)
  return httpx.Response(200,json={'message':{'link':[]}})
 loc,ev=ResolverRouter(client=httpx.Client(transport=httpx.MockTransport(h)),unpaywall_email=None).resolve('10.1/x')
 assert [x.source for x in loc][:2]==['pmc','europe_pmc']
 assert any(x['status']=='config_required' for x in ev)
 assert any(x['source']=='semantic_scholar' and x['status']=='failed' for x in ev)

def test_direct_fulltext_and_future_proposal_gate():
 text='''# Methods\nEscherichia coli K-12 MG1655 was engineered by trpR deletion and aroG overexpression for L-tryptophan production.\n# Results\nFed-batch fermentation reached a titer of 42 g/L. '''
 r=verify_document({'candidate_id':'x','relevance':{'decision':'tier_2'}},text)
 assert r['judge']['decision']=='DIRECT_ENGINEERING_EVIDENCE'
 future=verify_document({'candidate_id':'y'},'Escherichia coli K-12. Future work could use overexpression for L-tryptophan production.')
 assert future['judge']['decision']!='DIRECT_ENGINEERING_EVIDENCE'

def test_review_wrong_product_unresolved_and_enzyme_only():
 assert verify_document({},'This review discusses Escherichia coli K-12 L-tryptophan production and deletion studies.')['judge']['decision']=='NOT_ELIGIBLE'
 assert verify_document({},'Escherichia coli K-12 was engineered for 5-hydroxytryptophan production by overexpression; 4 g/L.')['judge']['decision']=='NOT_ELIGIBLE'
 assert verify_document({},'Escherichia coli was engineered by deletion for L-tryptophan production.')['host']['relation']=='ECOLI_UNRESOLVED'
 assert verify_document({},'Purified enzyme in vitro enzymatic synthesis of L-tryptophan reached 2 g/L.')['judge']['decision']!='DIRECT_ENGINEERING_EVIDENCE'

def test_gold_pending_and_metrics():
 assert evaluate([])['status']=='GOLD_PENDING_HUMAN_ANNOTATION'
 rows=[{'paper_id':'a','gold':{'eligibility_label':True},'prediction':True},{'paper_id':'b','gold':{'eligibility_label':False},'prediction':True}]
 r=evaluate(rows,{'a':.9,'b':.8});assert r['confusion_matrix']=={'tp':1,'tn':0,'fp':1,'fn':0};assert r['precision']==.5

def test_identity_mismatch_blocks(tmp_path:Path):
 # A syntactically real one-page PDF with a different DOI/title.
 from pypdf import PdfWriter
 p=tmp_path/'x.pdf';w=PdfWriter();w.add_blank_page(width=200,height=200);w.add_metadata({'/Title':'Unrelated paper','/Subject':'10.9999/wrong'});w.write(p)
 c=PaperCandidate(candidate_id='x',canonical_title='Target tryptophan engineering',doi='10.1000/target')
 assert verify_pdf_identity(c,p)['status'] in {'MISMATCH','INSUFFICIENT_METADATA'}

def test_canonical_sections_stable_anchor_and_section_hard_rules():
 md='# Methods\nE. coli K-12 MG1655 was engineered by deletion for L-tryptophan production.\n\n# Results\nThe titer was 42 g/L.\n\n# Discussion\nFuture work could use overexpression.\n\n# References\nPrior deletion yielded 10 g/L.'
 doc=from_markdown('p',md,'abc','fixture','1')
 assert [s.normalized_type for s in doc.sections]==['methods','results','discussion','references']
 assert all(a.quote_hash and a.section_id for a in doc.anchors)
 r=verify_document({'candidate_id':'p'},doc.model_dump())
 assert r['judge']['decision']=='DIRECT_ENGINEERING_EVIDENCE'
 statuses={x['implementation_status'] for x in r['interventions']['all_mentions']}
 assert 'IMPLEMENTED' in statuses and 'PLANNED' in statuses and 'CITED_OTHER_WORK' in statuses
 assert all(x['measured_vs_cited']=='measured' for x in r['experimental_validation']['evidence'])

def test_identity_v11_score_breakdown(tmp_path:Path):
 from pypdf import PdfWriter
 p=tmp_path/'meta.pdf';w=PdfWriter();w.add_blank_page(width=200,height=200);w.add_metadata({'/Title':'Target tryptophan engineering','/Subject':'10.1000/target'});w.write(p)
 c=PaperCandidate(candidate_id='x',canonical_title='Target tryptophan engineering',doi='10.1000/target')
 r=verify_pdf_identity(c,p,verified_threshold=.4)
 assert 'identity_score' in r and 'signal_breakdown' in r and 'hard_conflicts' in r

def test_skill06_adapter_and_anchor_resolution():
 clean={'document_metadata':{'paper_id':'p','parser':'MinerU','parser_version':'3.4.4'},'sections':[{'id':'m','title':'Methods','content':'Implemented deletion.'}],'tables':[{'id':'t'}],'figures':[{'id':'f'}]}
 doc=from_skill06(clean,'sha');assert doc.sections[0].normalized_type=='methods';assert doc.tables and doc.figures;assert doc.parser_name=='MinerU'
 assert resolve_anchor(doc.anchors[0].model_dump(),doc)['status']=='EXACT'
 moved=doc.model_copy(deep=True);moved.anchors[0].anchor_id='new';assert resolve_anchor(doc.anchors[0].model_dump(),moved)['status']=='RELOCATED_EXACT_QUOTE'

def test_agreement_kappa_and_adjudication_missingness():
 p=[{'paper_id':'p','annotator_A':{'identity_correct':'yes','publication_type':'REVIEW','host_relation':'K12_EXACT','product_role':'TARGET_PRODUCT','implemented_engineering':'no','measured_production':'no','final_eligibility':'NOT_ELIGIBLE'},'annotator_B':{'identity_correct':'yes','publication_type':'REVIEW','host_relation':'K12_EXACT','product_role':'TARGET_PRODUCT','implemented_engineering':'no','measured_production':'no','final_eligibility':'NOT_ELIGIBLE'}}]
 a=agreement(p);assert a['identity_correct']['raw_agreement']==1;assert a['identity_correct']['cohen_kappa'] is None;assert adjudication_queue(p)==[]
 p[0]['annotator_B']['host_relation']='ECOLI_UNRESOLVED';assert adjudication_queue(p)

def test_production_admission_holds_for_gold():
 r=evaluate_admission({'contracts_compatible':True,'legal_bounded_acquisition':True,'production_parser_available':True,'canonical_adapter_tested':True,'verifier_safety_tests_pass':True,'human_gold_complete':False,'identity_calibrated':False,'judge_calibrated':False,'regressions_clear':True,'shadow_no_ddr_write':True})
 assert r['status']=='HOLD_FOR_GOLD';assert 'human_gold_complete' in r['blockers']
