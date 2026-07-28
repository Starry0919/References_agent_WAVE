from urllib.parse import quote
from .base import BinaryTransport,JsonTransport
class SemanticScholarDownloader:
    source_type="semantic_scholar_oa"
    def __init__(self,metadata_transport=None,binary_transport=None):
        self.metadata=metadata_transport or JsonTransport();self.binary=binary_transport or BinaryTransport()
    def fetch(self,candidate,url=None):
        doi=candidate.get("identifiers",{}).get("doi")
        endpoint=f"https://api.semanticscholar.org/graph/v1/paper/DOI:{quote(doi,safe='')}?fields=isOpenAccess,openAccessPdf"
        data=self.metadata.get_json(endpoint,{"Accept":"application/json"})
        if not data.get("isOpenAccess"):raise ValueError("Semantic Scholar does not mark the work open access")
        target=(data.get("openAccessPdf") or {}).get("url")
        if not target:raise ValueError("Semantic Scholar has no OA PDF URL")
        result=self.binary.get(target,{"Accept":"application/pdf"})
        return {**result,"source_url":target,"source_type":self.source_type,"metadata_url":endpoint}
