import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from data_provider.sec_edgar_adapter import SecEdgarAdapter


class SecEdgarAdapterTestCase(unittest.TestCase):
    def test_ticker_cik_mapping_uses_sec_company_tickers_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = os.path.join(tmp, "sec-cache.json")
            with patch.dict(os.environ, {"SEC_TICKER_CIK_CACHE_PATH": cache_path}, clear=False):
                adapter = SecEdgarAdapter()
                adapter._get_json = Mock(
                    return_value={
                        "0": {"ticker": "AAPL", "cik_str": 320193},
                        "1": {"ticker": "MSFT", "cik_str": 789019},
                    }
                )

                self.assertEqual(adapter.get_cik_for_ticker("AAPL"), "320193")
                self.assertEqual(adapter.get_cik_for_ticker("aapl.us"), "320193")

    def test_recent_filings_are_filtered_and_linked(self):
        adapter = SecEdgarAdapter()
        submissions = {
            "filings": {
                "recent": {
                    "form": ["4", "10-K", "8-K"],
                    "accessionNumber": ["x", "0000320193-26-000001", "0000320193-26-000002"],
                    "filingDate": ["2026-01-01", "2026-02-01", "2026-03-01"],
                    "reportDate": ["", "2025-12-31", "2026-02-28"],
                    "primaryDocument": ["x.xml", "aapl-20251231.htm", "aapl-8k.htm"],
                    "primaryDocDescription": ["", "10-K", "8-K"],
                    "acceptanceDateTime": ["", "2026-02-01T12:00:00.000Z", "2026-03-01T12:00:00.000Z"],
                }
            }
        }

        rows = adapter._parse_recent_filings(submissions, "320193", 5)

        self.assertEqual([row["form"] for row in rows], ["10-K", "8-K"])
        self.assertIn("/320193/000032019326000001/aapl-20251231.htm", rows[0]["url"])

    def test_companyfacts_extracts_latest_core_facts(self):
        adapter = SecEdgarAdapter()
        payload = {
            "entityName": "Apple Inc.",
            "cik": 320193,
            "facts": {
                "us-gaap": {
                    "Revenues": {
                        "units": {
                            "USD": [
                                {"val": 100.0, "fy": 2024, "fp": "FY", "form": "10-K", "filed": "2024-10-01", "end": "2024-09-30"},
                                {"val": 120.0, "fy": 2025, "fp": "FY", "form": "10-K", "filed": "2025-10-01", "end": "2025-09-30"},
                            ]
                        }
                    },
                    "NetIncomeLoss": {
                        "units": {
                            "USD": [
                                {"val": 30.0, "fy": 2025, "fp": "FY", "form": "10-K", "filed": "2025-10-01", "end": "2025-09-30"}
                            ]
                        }
                    },
                }
            },
        }

        facts = adapter._parse_companyfacts(payload)

        self.assertEqual(facts["entity_name"], "Apple Inc.")
        self.assertEqual(facts["revenue"]["value"], 120.0)
        self.assertEqual(facts["net_income"]["value"], 30.0)

    def test_sec_bundle_combines_submissions_and_companyfacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = os.path.join(tmp, "sec-cache.json")
            with patch.dict(os.environ, {"SEC_TICKER_CIK_CACHE_PATH": cache_path}, clear=False):
                adapter = SecEdgarAdapter()
                adapter.get_cik_for_ticker = Mock(return_value="320193")
                adapter._get_json = Mock(
                    side_effect=[
                        {
                            "filings": {
                                "recent": {
                                    "form": ["10-Q"],
                                    "accessionNumber": ["0000320193-26-000003"],
                                    "filingDate": ["2026-05-01"],
                                    "reportDate": ["2026-03-31"],
                                    "primaryDocument": ["aapl-10q.htm"],
                                    "primaryDocDescription": ["10-Q"],
                                    "acceptanceDateTime": ["2026-05-01T12:00:00.000Z"],
                                }
                            }
                        },
                        {"entityName": "Apple Inc.", "cik": 320193, "facts": {"us-gaap": {}}},
                    ]
                )

                bundle = adapter.get_sec_bundle("AAPL")

        self.assertEqual(bundle["status"], "ok")
        self.assertEqual(bundle["filings"][0]["form"], "10-Q")
        self.assertEqual(bundle["companyfacts"]["entity_name"], "Apple Inc.")


if __name__ == "__main__":
    unittest.main()
