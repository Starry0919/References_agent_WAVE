"""Section-aware lexical/semantic retrieval with reciprocal-rank fusion."""
from __future__ import annotations

import math, re
from dataclasses import dataclass
from typing import Callable

SECTION_AUTHORITY={"results":1.0,"methods":.95,"table":.95,"figure_caption":.85,"supplement":.85,
                   "abstract":.7,"discussion":.55,"title":.5,"database_record":.45,"DDR":.65,
                   "engineering_rule":.5,"failure_case":.75}

@dataclass(frozen=True)
class RetrievalUnit:
    unit_id: str; text: str; unit_type: str; source_id: str; metadata: dict

def _tokens(text): return set(re.findall(r"[A-Za-z0-9_.+-]+",text.lower()))

def lexical_rank(query: str, units: list[RetrievalUnit]) -> list[tuple[str,float]]:
    q=_tokens(query); ranked=[]
    for unit in units:
        t=_tokens(unit.text); overlap=sum(1+math.log1p(len(x)) for x in q&t)
        ranked.append((unit.unit_id,overlap/max(1,math.sqrt(len(t)))*SECTION_AUTHORITY.get(unit.unit_type,.4)))
    return sorted(ranked,key=lambda x:x[1],reverse=True)

def hybrid_retrieve(query: str, units: list[RetrievalUnit], *, dense_score: Callable[[str,str],float] | None=None, limit: int=10):
    lexical=lexical_rank(query,units); dense=sorted(((u.unit_id,dense_score(query,u.text)) for u in units),key=lambda x:x[1],reverse=True) if dense_score else []
    fused={}; details={}
    for name,ranking in (("lexical",lexical),("dense",dense)):
        for rank,(uid,score) in enumerate(ranking,1):
            fused[uid]=fused.get(uid,0)+1/(60+rank); details.setdefault(uid,{})[name]={"rank":rank,"score":score}
    by_id={u.unit_id:u for u in units}
    return [{"unit":by_id[uid],"rrf_score":score,"component_scores":details[uid],
             "claim_authority":"experimental_fact" if by_id[uid].unit_type in {"methods","results","table"} else "interpretation_or_prior"}
            for uid,score in sorted(fused.items(),key=lambda x:x[1],reverse=True)[:limit]]

