import unittest

from freshdesk_mcp.server import normalize_freshdesk_search_query


class TestNormalizeFreshdeskSearchQuery(unittest.TestCase):
    def test_wraps_bare_query(self):
        self.assertEqual(normalize_freshdesk_search_query("status:2"), '"status:2"')

    def test_leaves_already_quoted(self):
        self.assertEqual(
            normalize_freshdesk_search_query('"status:2"'),
            '"status:2"',
        )

    def test_strips_whitespace_then_wraps(self):
        self.assertEqual(
            normalize_freshdesk_search_query("  status:2 AND priority:1  "),
            '"status:2 AND priority:1"',
        )

    def test_compound_with_parens(self):
        self.assertEqual(
            normalize_freshdesk_search_query("(status:2 OR status:3)"),
            '"(status:2 OR status:3)"',
        )


if __name__ == "__main__":
    unittest.main()
