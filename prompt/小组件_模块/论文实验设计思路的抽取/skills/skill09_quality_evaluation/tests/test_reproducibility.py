import unittest
from helpers import request
from skill import execute
class TestReproducibility(unittest.TestCase):
    def test_missing_replicate_reduces_score(self):
        full = execute(request(), logger=lambda _: None)
        partial = execute(request(unknown={"replicates"}), logger=lambda _: None)
        a = full["output"]["evaluation_report"]["dimensions"]["reproducibility"]["score"]
        b = partial["output"]["evaluation_report"]["dimensions"]["reproducibility"]["score"]
        self.assertEqual(a - b, 20)
if __name__ == "__main__": unittest.main()
