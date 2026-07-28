import unittest
from helpers import request
from skill import execute
class LanguageTest(unittest.TestCase):
    def test_zh_en_labels(self):
        zh=execute(request("zh"),logger=lambda _:None)["output"]["expanded_view"]["labels"]
        en=execute(request("en"),logger=lambda _:None)["output"]["expanded_view"]["labels"]
        self.assertEqual(zh["what"],"是什么");self.assertEqual(en["what"],"What")
    def test_invalid_language(self):
        self.assertEqual(execute(request("fr"),logger=lambda _:None)["errors"][0]["code"],"UI004")
if __name__=="__main__":unittest.main()
