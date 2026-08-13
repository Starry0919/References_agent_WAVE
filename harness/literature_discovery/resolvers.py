from __future__ import annotations
import os
from dataclasses import dataclass, field
from urllib.parse import quote
import httpx

@dataclass
class ResolvedLocation:
    source: str; url: str; priority: int; metadata: dict = field(default_factory=dict)

class ResolverRouter:
    def __init__(self, client=None, unpaywall_email=None):
        self.client=client or httpx.Client(timeout=15,follow_redirects=True,headers={"User-Agent":"WAVE-Literature/0.2"})
        self.email=unpaywall_email or os.getenv("UNPAYWALL_EMAIL")
    def resolve(self, doi:str)->tuple[list[ResolvedLocation],list[dict]]:
        d=quote(doi,safe="") ; loc=[]; events=[]
        def get(name,url):
            try:r=self.client.get(url);r.raise_for_status();events.append({"source":name,"status":"ok"});return r.json()
            except Exception as e:events.append({"source":name,"status":"failed","reason":type(e).__name__});return {}
        pmc=get("ncbi_idconv",f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={d}&format=json")
        rec=(pmc.get("records") or [{}])[0]; pmcid=rec.get("pmcid")
        if pmcid:
            loc += [ResolvedLocation("pmc",f"https://europepmc.org/articles/{pmcid}?pdf=render",1,{"pmcid":pmcid}),ResolvedLocation("europe_pmc",f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmcid}&blobtype=pdf",2,{"pmcid":pmcid})]
        if self.email:
            u=get("unpaywall",f"https://api.unpaywall.org/v2/{d}?email={quote(self.email,safe='@')}")
            for x in [u.get("best_oa_location"),*(u.get("oa_locations") or [])]:
                if isinstance(x,dict) and x.get("url_for_pdf"):loc.append(ResolvedLocation("unpaywall",x["url_for_pdf"],3,{"license":x.get("license")}))
        else: events.append({"source":"unpaywall","status":"config_required","reason":"CONFIG_REQUIRED"})
        oa=get("openalex",f"https://api.openalex.org/works/doi:{d}")
        for x in [oa.get("best_oa_location"),*(oa.get("locations") or [])]:
            if isinstance(x,dict) and x.get("pdf_url"):loc.append(ResolvedLocation("openalex",x["pdf_url"],4,{"is_oa":x.get("is_oa")}))
        s2=get("semantic_scholar",f"https://api.semanticscholar.org/graph/v1/paper/DOI:{d}?fields=isOpenAccess,openAccessPdf")
        if (s2.get("openAccessPdf") or {}).get("url"):loc.append(ResolvedLocation("semantic_scholar",s2["openAccessPdf"]["url"],5))
        cr=get("crossref",f"https://api.crossref.org/works/{d}")
        for x in (cr.get("message") or {}).get("link",[]):
            if x.get("content-type")=="application/pdf" and x.get("URL"):loc.append(ResolvedLocation("crossref",x["URL"],9))
        seen=set();out=[]
        for x in sorted(loc,key=lambda z:z.priority):
            if x.url not in seen:seen.add(x.url);out.append(x)
        return out,events
