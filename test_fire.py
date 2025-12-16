import unittest

from fire import _parse_git_log_to_ticker


class ParseGitLogToTickerTests(unittest.TestCase):
    def test_no_output_returns_none(self) -> None:
        self.assertIsNone(_parse_git_log_to_ticker(""))
        self.assertIsNone(_parse_git_log_to_ticker("\n\n"))

    def test_single_commit_parses_message_and_meta(self) -> None:
        log = "abcd1234\tAlice\t3 days ago\tInitial commit"
        result = _parse_git_log_to_ticker(log)
        self.assertIsNotNone(result)
        message_text, meta_text = result  # type: ignore[misc]

        self.assertIn("Initial commit", message_text)
        self.assertIn("by Alice 3 days ago", meta_text)
        self.assertGreaterEqual(len(message_text), len("Initial commit"))
        self.assertGreaterEqual(len(meta_text), len("by Alice 3 days ago"))

    def test_multiple_commits_all_appear_in_order(self) -> None:
        log = """abcd1234\tAlice\t3 days ago\tInitial commit
        efgh5678\tBob\t2 weeks ago\tAdd feature X
        ijkl9012\tCarol\t1 year ago\tRefactor module Y
        """
        result = _parse_git_log_to_ticker(log)
        self.assertIsNotNone(result)
        message_text, meta_text = result  # type: ignore[misc]

        # Messages should all be present in the combined ticker string.
        self.assertIn("Initial commit", message_text)
        self.assertIn("Add feature X", message_text)
        self.assertIn("Refactor module Y", message_text)

        # Meta lines should all be present as well.
        self.assertIn("by Alice 3 days ago", meta_text)
        self.assertIn("by Bob 2 weeks ago", meta_text)
        self.assertIn("by Carol 1 year ago", meta_text)

        # Order should match git log order (Alice -> Bob -> Carol).
        self.assertLess(
            message_text.index("Initial commit"), message_text.index("Add feature X")
        )
        self.assertLess(
            message_text.index("Add feature X"), message_text.index("Refactor module Y")
        )


if __name__ == "__main__":
    unittest.main()
