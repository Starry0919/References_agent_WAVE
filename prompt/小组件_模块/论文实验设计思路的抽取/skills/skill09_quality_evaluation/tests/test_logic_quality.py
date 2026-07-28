import unittest
from helpers import request
from skill import execute
class TestLogic(unittest.TestCase):
    def test_missing_hypothesis_reduces_logic(self):
        full = execute(request(), logger=lambda _: None)
        partial = execute(request(unknown={"hypothesis"}), logger=lambda _: None)
        a = full["output"]["evaluation_report"]["dimensions"]["experimental_logic"]["score"]
        b = partial["output"]["evaluation_report"]["dimensions"]["experimental_logic"]["score"]
        self.assertEqual(a - b, 20)
if __name__ == "__main__": unittest.main()
