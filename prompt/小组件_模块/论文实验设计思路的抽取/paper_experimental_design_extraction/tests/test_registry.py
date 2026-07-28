import unittest
from paper_experimental_design_extraction.skills import SkillRegistry
class Registry(unittest.TestCase):
 def test_all_13_skills_callable(self):
  items=SkillRegistry().metadata()
  self.assertEqual(len(items),13)
  self.assertTrue(all(x["status"]=="implemented" for x in items))
if __name__=="__main__":unittest.main()
