import tempfile,unittest
from pathlib import Path
from helpers import CANDIDATE,VALID_PDF,fixed_clock
from downloader import OpenAlexDownloader
from skill import PdfAcquisitionSkill
class Metadata:
 def get_json(self,url,headers=None):
  return {"open_access":{"is_oa":True},"best_oa_location":{"is_oa":True,"pdf_url":"https://oa.example/paper.pdf","license":"cc-by"},"locations":[]}
class Binary:
 def get(self,url,headers=None):
  return {"data":VALID_PDF,"content_type":"application/pdf","final_url":url}
class OpenAlexTest(unittest.TestCase):
 def test_openalex_oa_artifact_and_license_audit(self):
  downloader=OpenAlexDownloader(Metadata(),Binary(),api_key="test")
  with tempfile.TemporaryDirectory() as d:
   r=PdfAcquisitionSkill(artifact_root=Path(d),downloaders=[downloader],logger=lambda _:None,clock=fixed_clock).execute({"accepted_candidates":[CANDIDATE]})
  self.assertEqual(r["status"],"succeeded")
  item=r["output"]["paper_artifacts"][0]
  self.assertEqual(item["source_information"]["source_type"],"openalex_oa")
  self.assertEqual(item["download_attempts"][0]["license"],"cc-by")
 def test_small_batch_defers_remaining(self):
  candidates=[dict(CANDIDATE,paper_id=f"p{i}") for i in range(3)]
  downloader=OpenAlexDownloader(Metadata(),Binary(),api_key="test")
  with tempfile.TemporaryDirectory() as d:
   r=PdfAcquisitionSkill(artifact_root=Path(d),downloaders=[downloader],logger=lambda _:None,clock=fixed_clock).execute(
      {"accepted_candidates":candidates,"download_policy":{"max_candidates":1}})
  self.assertEqual(len(r["output"]["paper_artifacts"]),1)
  self.assertEqual(len(r["output"]["deferred_items"]),2)
if __name__=="__main__":unittest.main()
