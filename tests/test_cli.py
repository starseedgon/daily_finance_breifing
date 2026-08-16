import tempfile
import unittest
from pathlib import Path

from finance_briefing.cli import main


class CliTest(unittest.TestCase):
    def test_fixture_output_is_repeatable_and_creates_aliases(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            args = ["--provider", "fixture", "--date", "2026-08-15"]
            self.assertEqual(main([*args, "--output-dir", first]), 0)
            self.assertEqual(main([*args, "--output-dir", second]), 0)
            expected = Path(first, "2026-08-15.html").read_bytes()
            self.assertEqual(expected, Path(second, "2026-08-15.html").read_bytes())
            self.assertEqual(expected, Path(first, "latest.html").read_bytes())
            self.assertEqual(expected, Path(first, "index.html").read_bytes())
            self.assertIn("KOSPI", expected.decode())


if __name__ == "__main__":
    unittest.main()
