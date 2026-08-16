import os
import unittest
from datetime import date

from finance_briefing.providers import FinanceDataReaderProvider


@unittest.skipUnless(os.getenv("RUN_FDR_INTEGRATION") == "1", "live test is opt-in")
class FinanceDataReaderIntegrationTest(unittest.TestCase):
    def test_fetches_at_least_one_indicator(self):
        indicators = FinanceDataReaderProvider().fetch(date.today())
        self.assertEqual(len(indicators), 4)
        self.assertTrue(any(item.value is not None for item in indicators))


if __name__ == "__main__":
    unittest.main()
