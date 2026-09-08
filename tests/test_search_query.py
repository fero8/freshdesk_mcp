import unittest

from freshdesk_mcp.server import (
    clamp_freshdesk_search_page,
    conversation_write_payload,
    normalize_freshdesk_search_query,
)


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


class TestClampFreshdeskSearchPage(unittest.TestCase):
    def test_keeps_valid_page(self):
        self.assertEqual(clamp_freshdesk_search_page(1), 1)
        self.assertEqual(clamp_freshdesk_search_page(4), 4)
        self.assertEqual(clamp_freshdesk_search_page(10), 10)

    def test_clamps_below_one(self):
        self.assertEqual(clamp_freshdesk_search_page(0), 1)
        self.assertEqual(clamp_freshdesk_search_page(-3), 1)

    def test_clamps_above_ten(self):
        self.assertEqual(clamp_freshdesk_search_page(11), 10)
        self.assertEqual(clamp_freshdesk_search_page(99), 10)


class TestConversationWritePayload(unittest.TestCase):
    def test_body_only_omits_optional_keys(self):
        self.assertEqual(conversation_write_payload("hello"), {"body": "hello"})

    def test_includes_provided_optional_fields(self):
        self.assertEqual(
            conversation_write_payload(
                "hello",
                cc_emails=["a@b.com"],
                user_id=9,
                extra={"private": True},
            ),
            {
                "body": "hello",
                "cc_emails": ["a@b.com"],
                "user_id": 9,
                "private": True,
            },
        )


if __name__ == "__main__":
    unittest.main()
