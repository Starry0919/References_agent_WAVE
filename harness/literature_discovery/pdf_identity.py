from __future__ import annotations
import hashlib,re
from pathlib import Path
from pypdf import PdfReader
from .models import PaperCandidate

def _tokens(s):return set(re.findall(r"[a-z0-9]+",(s or '').casefold()))
def verify_pdf_identity(candidate:PaperCandidate,path:Path,verified_threshold=.72,probable_threshold=.48)->dict:
 try:r=PdfReader(str(path));text=' '.join((p.extract_text() or '') for p in r.pages[:5]);meta=dict(r.metadata or {})
 except Exception as e:return {'status':'INSUFFICIENT_METADATA','identity_score':0,'signal_breakdown':{},'hard_conflicts':[],'reason':f'parse:{type(e).__name__}'}
 low=(text+' '+str(meta)).casefold();dois=set(x.rstrip('.,;)') for x in re.findall(r"10\.\d{4,9}/\S+",low));expected=(candidate.doi or '').casefold();doi=1 if expected and expected in low else 0
 et=_tokens(candidate.canonical_title);pt=_tokens(text[:5000]);title=len(et&pt)/max(1,len(et));authors=[a.split()[-1].casefold() for a in candidate.authors if a];author=sum(a in low for a in authors)/max(1,len(authors)) if authors else 0
 venue=1 if candidate.venue and candidate.venue.casefold() in low else 0;year=1 if candidate.year and str(candidate.year) in low else 0
 score=.5*doi+.3*title+.1*author+.06*venue+.04*year;conf=[]
 if expected and dois and expected not in dois:conf.append('OTHER_DOI_EXPLICIT')
 if title<.15 and len(et)>=4:conf.append('TITLE_CONFLICT')
 status='MISMATCH' if len(conf)>=2 or ('OTHER_DOI_EXPLICIT' in conf and title<.15) else 'VERIFIED' if score>=verified_threshold else 'PROBABLE' if score>=probable_threshold else 'REVIEW_REQUIRED' if any((doi,title,author)) else 'INSUFFICIENT_METADATA'
 return {'status':status,'identity_score':round(score,4),'signal_breakdown':{'doi_exact':doi,'title_token_recall':round(title,4),'author_overlap':round(author,4),'venue_match':venue,'year_match':year},'hard_conflicts':conf,'expected_doi':candidate.doi,'dois_found':sorted(dois),'page_count':len(r.pages),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'thresholds':{'verified':verified_threshold,'probable':probable_threshold}}
