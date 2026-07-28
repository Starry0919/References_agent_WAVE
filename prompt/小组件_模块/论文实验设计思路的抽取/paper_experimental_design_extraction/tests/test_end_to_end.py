import tempfile,unittest
from helpers import executors,request
from paper_experimental_design_extraction import execute
class E2E(unittest.TestCase):
 def test_complete_module(self):
  with tempfile.TemporaryDirectory() as d:
   r=execute(request(),{"executors":executors(),"state_dir":d})
   self.assertEqual(r["status"],"COMPLETED");self.assertTrue(r["frontend_view"])
   self.assertEqual(r["skill_states"]["skill13_frontend_adapter"],"SUCCESS")
if __name__=="__main__":unittest.main()
