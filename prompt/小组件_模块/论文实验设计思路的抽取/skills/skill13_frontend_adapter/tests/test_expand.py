import unittest
from helpers import request
from skill import execute
class ExpandTest(unittest.TestCase):
    def test_expand_has_what_why_how_and_same_steps(self):
        r=execute(request(),logger=lambda _:None);o=r["output"]
        self.assertTrue(all({"what","why","how"}.issubset(x) for x in o["detail_panels"]))
        self.assertEqual(len(o["collapsed_view"]["steps"]),len(o["expanded_view"]["detail_panels"]))
        self.assertTrue(r["self_check"]["passed"])
if __name__=="__main__":unittest.main()
