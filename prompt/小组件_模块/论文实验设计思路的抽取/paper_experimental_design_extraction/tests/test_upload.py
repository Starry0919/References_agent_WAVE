import tempfile,unittest
from helpers import executors,request
from paper_experimental_design_extraction import execute
class Upload(unittest.TestCase):
 def test_upload_skips_search_and_validation(self):
  calls=[]
  with tempfile.TemporaryDirectory() as d:execute(request(),{"executors":executors(calls=calls),"state_dir":d})
  self.assertNotIn("skill02_literature_retrieval",calls);self.assertNotIn("skill03_citation_validation",calls)
  self.assertIn("skill04_pdf_acquisition",calls)
if __name__=="__main__":unittest.main()
