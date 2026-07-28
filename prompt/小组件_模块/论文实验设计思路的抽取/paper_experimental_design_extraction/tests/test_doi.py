import tempfile,unittest
from helpers import executors,request
from paper_experimental_design_extraction import execute
class DOI(unittest.TestCase):
 def test_doi_enters_validation(self):
  calls=[];q=request(source="doi")
  with tempfile.TemporaryDirectory() as d:execute(q,{"executors":executors(calls=calls),"state_dir":d})
  self.assertNotIn("skill02_literature_retrieval",calls);self.assertIn("skill03_citation_validation",calls)
if __name__=="__main__":unittest.main()
