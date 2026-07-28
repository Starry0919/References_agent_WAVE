import tempfile,unittest
from helpers import executors,request,result
from paper_experimental_design_extraction import execute
class MissingUpstream(unittest.TestCase):
 def test_no_pdf_blocks_next_stage_for_review(self):
  ex=executors()
  ex["skill04_pdf_acquisition"]=lambda req:result("skill04_pdf_acquisition",{"paper_artifacts":[],"failed_items":[{"reason":"unavailable"}]},"needs_review")
  with tempfile.TemporaryDirectory() as d:r=execute(request(),{"executors":ex,"state_dir":d})
  self.assertEqual(r["status"],"WAITING_REVIEW")
  self.assertEqual(r["skill_states"]["skill05_pdf_parser"],"BLOCKED")
  self.assertNotIn("skill10_k12_transfer",r["skill_states"])
if __name__=="__main__":unittest.main()
