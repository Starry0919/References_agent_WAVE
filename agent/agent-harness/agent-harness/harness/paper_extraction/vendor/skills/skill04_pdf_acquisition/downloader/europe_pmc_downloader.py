from urllib.parse import quote
from .base import BinaryTransport,JsonTransport
class EuropePmcDownloader:
    source_type="europe_pmc_oa"
    def __init__(self,metadata_transport=None,binary_transport=None):
        self.metadata=metadata_transport or JsonTransport();self.binary=binary_transport or BinaryTransport()
    def fetch(self,candidate,url=None):
        doi=candidate.get("identifiers",{}).get("doi")
        if not doi:raise ValueError("Candidate has no DOI")
        endpoint=f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{quote(doi,safe='')}&format=json"
        data=self.metadata.get_json(endpoint,{"Accept":"application/json"})
        records=(data.get("resultList") or {}).get("result") or []
        pmcid=next((x.get("pmcid") for x in records if x.get("pmcid")),None)
        if not pmcid:raise ValueError("No PMCID for DOI")
        targets=[f"https://europepmc.org/articles/{pmcid}?pdf=render",
                 f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmcid}&blobtype=pdf"]
        last=None
        for target in targets:
            try:
                result=self.binary.get(target,{"Accept":"application/pdf"})
                return {**result,"source_url":target,"source_type":self.source_type,"metadata_url":endpoint}
            except Exception as exc:last=exc
        raise last or ValueError("Europe PMC download failed")
