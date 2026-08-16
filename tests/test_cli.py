import json
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
            relative_html = Path("2026/08/market-summary-2026-08-15.html")
            relative_json = Path("2026/08/market-summary-2026-08-15.json")
            relative_manifest = Path("2026/08/run-manifest-2026-08-15.json")
            expected = Path(first, relative_html).read_bytes()
            self.assertEqual(expected, Path(second, relative_html).read_bytes())
            self.assertEqual(expected, Path(first, "latest.html").read_bytes())
            self.assertEqual(expected, Path(first, "index.html").read_bytes())
            self.assertIn("KOSPI", expected.decode())
            data = json.loads(Path(first, relative_json).read_text(encoding="utf-8"))
            self.assertEqual(data["report_date"], "2026-08-15")
            self.assertEqual(data["provider"], "fixture")
            self.assertTrue(data["indicators"])
            manifest = json.loads(Path(first, relative_manifest).read_text(encoding="utf-8"))
            self.assertEqual(manifest["html"], relative_html.as_posix())
            self.assertEqual(manifest["json"], relative_json.as_posix())


if __name__ == "__main__":
    unittest.main()
