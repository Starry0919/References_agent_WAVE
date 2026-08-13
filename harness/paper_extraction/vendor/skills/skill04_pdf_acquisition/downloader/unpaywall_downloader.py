import os
from urllib.parse import quote
from .base import BinaryTransport,JsonTransport
class UnpaywallDownloader:
    source_type="unpaywall_oa"
    def __init__(self,metadata_transport=None,binary_transport=None,email=None):
        self.metadata=metadata_transport or JsonTransport();self.binary=binary_transport or BinaryTransport()
        self.email=email if email is not None else os.getenv("UNPAYWALL_EMAIL")
    def fetch(self,candidate,url=None):
        if not self.email:raise ValueError("UNPAYWALL_EMAIL is not configured")
        doi=candidate.get("identifiers",{}).get("doi")
        endpoint=f"https://api.unpaywall.org/v2/{quote(doi,safe='')}?email={quote(self.email,safe='')}"
        data=self.metadata.get_json(endpoint,{"Accept":"application/json"})
        locations=[data.get("best_oa_location"),*(data.get("oa_locations") or [])]
        target=next((x.get("url_for_pdf") for x in locations if isinstance(x,dict) and x.get("url_for_pdf")),None)
        if not target:raise ValueError("Unpaywall has no OA PDF URL")
        result=self.binary.get(target,{"Accept":"application/pdf"})
        return {**result,"source_url":target,"source_type":self.source_type,"metadata_url":endpoint,
                "license":(data.get("best_oa_location") or {}).get("license")}
