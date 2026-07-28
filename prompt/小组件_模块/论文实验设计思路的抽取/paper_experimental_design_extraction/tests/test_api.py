import tempfile,time,unittest
from helpers import executors,request
from paper_experimental_design_extraction.api import TaskManager
class API(unittest.TestCase):
 def test_async_run_status_result(self):
  m=TaskManager(1)
  with tempfile.TemporaryDirectory() as d:
   q=request("api-task");accepted=m.submit(q,{"executors":executors(),"state_dir":d})
   self.assertEqual(accepted["status"],"running")
   for _ in range(100):
    if m.status("api-task")["status"]!="running":break
    time.sleep(.01)
   self.assertEqual(m.result("api-task")["status"],"COMPLETED")
if __name__=="__main__":unittest.main()
