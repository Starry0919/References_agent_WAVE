import tempfile,unittest
from helpers import executors,request
from paper_experimental_design_extraction import execute
class Recovery(unittest.TestCase):
 def test_resume_after_failure(self):
  calls=[];ex=executors(fail_once="skill08_evidence_binding",calls=calls);q=request("resume-task")
  with tempfile.TemporaryDirectory() as d:
   first=execute(q,{"executors":ex,"state_dir":d});self.assertEqual(first["status"],"FAILED")
   before=calls.count("skill07_experiment_extraction")
   second=execute(q,{"executors":ex,"state_dir":d,"resume":True})
   self.assertEqual(second["status"],"COMPLETED")
   self.assertEqual(calls.count("skill07_experiment_extraction"),before)
if __name__=="__main__":unittest.main()
