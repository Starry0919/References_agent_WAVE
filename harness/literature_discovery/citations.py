from __future__ import annotations
from .models import PaperCandidate,SourceRecord

def expand_citations(seeds,provider,max_seeds=5,max_backward=10,max_forward=10,max_total=30,depth=1):
 if depth>1:raise ValueError("citation expansion depth must be <= 1")
 out=[];seen=set()
 for seed in seeds[:max_seeds]:
  for mode,limit in (("BACKWARD_CITATION_EXPANSION",max_backward),("FORWARD_CITATION_EXPANSION",max_forward)):
   for raw in provider(seed,mode,limit)[:limit]:
    item=raw if isinstance(raw,PaperCandidate) else PaperCandidate.model_validate(raw)
    key=item.doi or item.pmid or item.openalex_id or item.canonical_title.casefold()
    if key in seen:continue
    seen.add(key);item.source_records.append(SourceRecord(source="citation_expansion",query_id=f"citation:{seed.candidate_id}",raw={"mode":mode,"seed_paper_id":seed.candidate_id,"provenance":"DISCOVERED_FROM_REVIEW_CITATION" if (seed.route or {}).get('value')=='REVIEW_SYNTHESIS_ROUTE' else "DISCOVERED_FROM_SEED_CITATION"}))
    out.append(item)
    if len(out)>=max_total:return out
 return out
