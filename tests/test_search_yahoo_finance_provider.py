# -*- coding: utf-8 -*-
"""Tests for Yahoo Finance no-key news fallback."""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from src.search_service import YahooFinanceNewsProvider


class _FakeResponse:
    status_code = 200

    def json(self):
        published_at = int(datetime.now(timezone.utc).timestamp())
        return {
            "news": [
                {
                    "title": "Apple WWDC news",
                    "link": "https://finance.yahoo.com/news/apple-wwdc",
                    "publisher": "Yahoo Finance",
                    "providerPublishTime": published_at,
                }
            ]
        }


class YahooFinanceNewsProviderTestCase(unittest.TestCase):
    def test_search_parses_finance_news(self) -> None:
        provider = YahooFinanceNewsProvider()

        with patch("src.search_service._get_with_retry", return_value=_FakeResponse()) as mock_get:
            response = provider.search("Apple Inc. AAPL stock latest news", max_results=3, days=3)

        self.assertTrue(response.success)
        self.assertEqual(response.provider, "YahooFinance")
        self.assertEqual([item.title for item in response.results], ["Apple WWDC news"])
        self.assertEqual(response.results[0].source, "Yahoo Finance")
        self.assertRegex(response.results[0].published_date or "", r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(mock_get.call_args.kwargs["params"]["q"], "AAPL")


if __name__ == "__main__":
    unittest.main()
