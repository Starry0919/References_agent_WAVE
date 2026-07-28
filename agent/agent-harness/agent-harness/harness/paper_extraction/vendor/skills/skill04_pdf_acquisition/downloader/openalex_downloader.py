import os
from urllib.parse import quote
from .base import BinaryTransport, JsonTransport

class OpenAlexDownloader:
    source_type="openalex_oa"
    def __init__(self,metadata_transport=None,binary_transport=None,api_key=None):
        self.metadata=metadata_transport or JsonTransport();self.binary=binary_transport or BinaryTransport()
        self.api_key=api_key if api_key is not None else os.getenv("OPENALEX_API_KEY")
    def fetch(self,candidate,url=None):
        doi=candidate.get("identifiers",{}).get("doi")
        if not doi:raise ValueError("Candidate has no DOI")
        endpoint=f"https://api.openalex.org/works/doi:{quote(doi,safe='')}"
        if self.api_key:endpoint+=f"?api_key={quote(self.api_key,safe='')}"
        data=self.metadata.get_json(endpoint,{"Accept":"application/json","User-Agent":"paper-experimental-design-extraction/0.1"})
        if not (data.get("open_access") or {}).get("is_oa"):raise ValueError("OpenAlex does not mark this work open access")
        locations=[data.get("best_oa_location"),data.get("primary_location"),*(data.get("locations") or [])]
        urls=[]
        for loc in locations:
            if isinstance(loc,dict) and (loc.get("is_oa") is not False):
                candidate_url=loc.get("pdf_url")
                if candidate_url and candidate_url not in urls:urls.append(candidate_url)
        if not urls:raise ValueError("OpenAlex has no open-access PDF URL")
        last=None
        for candidate_url in urls:
            try:
                result=self.binary.get(candidate_url,{"Accept":"application/pdf"})
                return {**result,"source_url":candidate_url,"source_type":self.source_type,
                        "metadata_url":endpoint,"license":(data.get("best_oa_location") or {}).get("license")}
            except Exception as exc:last=exc
        raise last or ValueError("OpenAlex PDF download failed")
