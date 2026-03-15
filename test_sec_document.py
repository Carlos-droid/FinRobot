import unittest
from finrobot.data_source.filings_src.prepline_sec_filings.sec_document import is_item_title, ITEM_TITLE_RE, SECDocument
from unstructured.documents.elements import Title, Text

class TestSECDocument(unittest.TestCase):
    def test_item_title_regex(self):
        # 10-K item titles
        self.assertTrue(bool(ITEM_TITLE_RE.match("Item 1.")))
        self.assertTrue(bool(ITEM_TITLE_RE.match("Item 1A.")))
        self.assertTrue(bool(ITEM_TITLE_RE.match("Item 1B.")))
        self.assertTrue(bool(ITEM_TITLE_RE.match("Item  1A.")))
        self.assertTrue(bool(ITEM_TITLE_RE.match("Item 15.")))
        self.assertTrue(bool(ITEM_TITLE_RE.match("Item 5(a)")))
        self.assertTrue(bool(ITEM_TITLE_RE.match("Part I")))
        self.assertTrue(bool(ITEM_TITLE_RE.match("Part   II")))
        self.assertTrue(bool(ITEM_TITLE_RE.match("Part IV.")))

        # negative cases
        self.assertFalse(bool(ITEM_TITLE_RE.match("Item")))
        self.assertFalse(bool(ITEM_TITLE_RE.match("Part ")))
        self.assertFalse(bool(ITEM_TITLE_RE.match("Risk Factors")))

    def test_is_item_title(self):
        self.assertTrue(is_item_title("Item 1A.", "10-K"))
        self.assertTrue(is_item_title("Part   II", "10-Q"))
        self.assertTrue(is_item_title("RISK FACTORS", "S-1"))
        self.assertFalse(is_item_title("Risk factors", "S-1")) # S1 title should be uppercase
        self.assertFalse(is_item_title("Risk factors", "10-K"))

if __name__ == "__main__":
    unittest.main()
