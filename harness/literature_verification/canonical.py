from __future__ import annotations
import hashlib,re
from pathlib import Path
from pydantic import BaseModel,Field

class Anchor(BaseModel):
    anchor_id:str;page_number:int|None=None;section_id:str;char_start:int;char_end:int;quote_hash:str
class Section(BaseModel):
    section_id:str;heading:str;normalized_type:str;page_start:int|None=None;page_end:int|None=None;char_start:int;char_end:int;text:str
class CanonicalDocument(BaseModel):
    contract_version:str="canonical-document/1.1";document_id:str;paper_id:str;parser_name:str;parser_version:str;source_pdf_sha256:str;pages:list[dict]=Field(default_factory=list);sections:list[Section]=Field(default_factory=list);tables:list[dict]=Field(default_factory=list);figures:list[dict]=Field(default_factory=list);anchors:list[Anchor]=Field(default_factory=list);text:str

TYPES=(("methods",r"materials? and methods?|methods?|experimental procedures?|strain construction"),("results",r"results?|findings"),("discussion",r"discussion"),("conclusion",r"conclusions?"),("introduction",r"introduction|background"),("abstract",r"abstract|summary"),("references",r"references|bibliography"),("supplement",r"supplement"))
def normalize_type(h):
 low=h.casefold()
 for typ,pat in TYPES:
  if re.search(pat,low):return typ
 return "other"
def from_markdown(paper_id:str,markdown:str,pdf_sha:str,parser_name="unknown",parser_version="unknown",page_map=None,tables=None,figures=None):
 hits=list(re.finditer(r"(?m)^(#{1,6})\s+(.+?)\s*$",markdown));sections=[]
 if not hits:hits=[type('M',(),{'start':lambda s:0,'end':lambda s:0,'group':lambda s,n:'Document' if n==2 else '#'})()]
 for i,m in enumerate(hits):
  start=m.end();end=hits[i+1].start() if i+1<len(hits) else len(markdown);heading=m.group(2);sid=f"sec_{i+1:04d}";sections.append(Section(section_id=sid,heading=heading,normalized_type=normalize_type(heading),char_start=start,char_end=end,text=markdown[start:end].strip()))
 anchors=[]
 for s in sections:
  for j,pm in enumerate(re.finditer(r"\S(?:.*?)(?=\n\s*\n|$)",s.text,re.S)):
   q=pm.group(0).strip();a=s.char_start+pm.start();anchors.append(Anchor(anchor_id=f"{paper_id}:{s.section_id}:p{j+1}:{hashlib.sha256(' '.join(q.split()).casefold().encode()).hexdigest()[:12]}",section_id=s.section_id,char_start=a,char_end=a+len(q),quote_hash=hashlib.sha256(' '.join(q.split()).casefold().encode()).hexdigest()))
 return CanonicalDocument(document_id="doc_"+hashlib.sha256((paper_id+pdf_sha+parser_name).encode()).hexdigest()[:20],paper_id=paper_id,parser_name=parser_name,parser_version=parser_version,source_pdf_sha256=pdf_sha,sections=sections,anchors=anchors,tables=tables or [],figures=figures or [],text=markdown)

def from_skill06(clean:dict,pdf_sha:str="unknown"):
 meta=clean.get('document_metadata',{});parts=[];sections=[]
 for i,s in enumerate(clean.get('sections',[])):
  heading=s.get('title') or 'Untitled';content=s.get('content') or '';start=sum(len(x) for x in parts);chunk=f"# {heading}\n{content}\n\n";parts.append(chunk);sections.append(Section(section_id=s.get('id') or f'sec_{i+1:04d}',heading=heading,normalized_type=normalize_type(heading),char_start=start+len(heading)+3,char_end=start+len(chunk),text=content))
 text=''.join(parts);doc=from_markdown(meta.get('paper_id','unknown'),text,pdf_sha,meta.get('parser','MinerU'),meta.get('parser_version','unknown'),tables=clean.get('tables',[]),figures=clean.get('figures',[]));doc.sections=sections;return doc

def from_opendataloader(data:dict,markdown:str,pdf_sha:str,paper_id:str):
 pages={};tables=[];figures=[]
 for x in data.get('kids',[]):
  p=x.get('page number');pages.setdefault(p,[]).append(x)
  if x.get('type')=='table':tables.append(x)
  if x.get('type') in {'image','caption'}:figures.append(x)
 return from_markdown(paper_id,markdown,pdf_sha,'OpenDataLoader','2.5.0',page_map=pages,tables=tables,figures=figures).model_copy(update={'pages':[{'page_number':p,'blocks':v,'text':'\n'.join(str(x.get('content','')) for x in v)} for p,v in sorted(pages.items())]})

def resolve_anchor(anchor:dict,target:CanonicalDocument):
 exact=[a for a in target.anchors if a.anchor_id==anchor.get('anchor_id')]
 if exact:return {'status':'EXACT','anchor':exact[0].model_dump()}
 q=anchor.get('quote_hash');sec=anchor.get('section_id');hits=[a for a in target.anchors if a.quote_hash==q and a.section_id==sec]
 if len(hits)==1:return {'status':'RELOCATED_EXACT_QUOTE','anchor':hits[0].model_dump()}
 hits=[a for a in target.anchors if a.quote_hash==q]
 if len(hits)==1:return {'status':'RELOCATED_NORMALIZED_QUOTE','anchor':hits[0].model_dump()}
 return {'status':'AMBIGUOUS' if len(hits)>1 else 'UNRESOLVED','candidates':len(hits)}
