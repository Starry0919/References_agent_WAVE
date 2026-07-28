import tempfile,unittest
from helpers import executors,request
from paper_experimental_design_extraction import execute
class Review(unittest.TestCase):
 def test_review_is_nonblocking(self):
  with tempfile.TemporaryDirectory() as d:r=execute(request(),{"executors":executors(review=True),"state_dir":d})
  self.assertEqual(r["status"],"WAITING_REVIEW")
  self.assertEqual(r["skill_states"]["skill13_frontend_adapter"],"SUCCESS")
if __name__=="__main__":unittest.main()
