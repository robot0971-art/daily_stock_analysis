import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

import pandas as pd

from data_provider.kis_fetcher import KisFetcher, is_kr_stock_code, to_kis_symbol


class KisFetcherTestCase(unittest.TestCase):
    def test_kr_code_detection_and_symbol_conversion(self):
        cases = {
            "005930.KS": "005930",
            "091990.KQ": "091990",
            "KR005930": "005930",
            "KS005930": "005930",
            "KQ091990": "091990",
            "005930": "005930",
        }
        for raw, expected in cases.items():
            self.assertTrue(is_kr_stock_code(raw))
            self.assertEqual(to_kis_symbol(raw), expected)

        self.assertFalse(is_kr_stock_code("AAPL"))

    def test_token_cache_reuses_valid_cached_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = os.path.join(tmp, "kis-token.json")
            with patch.dict(
                os.environ,
                {
                    "KIS_APP_KEY": "app",
                    "KIS_APP_SECRET": "secret",
                    "KIS_API_BASE_URL": "https://example.test",
                    "KIS_TOKEN_CACHE_PATH": cache_path,
                },
                clear=False,
            ):
                fetcher = KisFetcher()
                cache_key = fetcher._cache_key()
                with open(cache_path, "w", encoding="utf-8") as fh:
                    json.dump({cache_key: {"access_token": "cached-token", "expires_at": 9999999999}}, fh)

                with patch("requests.post") as post:
                    self.assertEqual(fetcher._get_access_token(), "cached-token")
                    post.assert_not_called()

    def test_realtime_quote_parses_kis_output(self):
        with patch.dict(os.environ, {"KIS_APP_KEY": "app", "KIS_APP_SECRET": "secret"}, clear=False):
            fetcher = KisFetcher()
            fetcher._get = Mock(
                return_value={
                    "output": {
                        "hts_kor_isnm": "삼성전자",
                        "stck_prpr": "70000",
                        "prdy_ctrt": "1.25",
                        "prdy_vrss": "900",
                        "acml_vol": "12345",
                        "stck_oprc": "69000",
                        "stck_hgpr": "70500",
                        "stck_lwpr": "68800",
                        "stck_sdpr": "69100",
                        "hts_avls": "123456789",
                    }
                }
            )

            quote = fetcher.get_realtime_quote("005930.KS")

        self.assertIsNotNone(quote)
        self.assertEqual(quote.code, "005930")
        self.assertEqual(quote.name, "삼성전자")
        self.assertEqual(quote.price, 70000.0)
        self.assertEqual(quote.change_pct, 1.25)
        self.assertEqual(quote.volume, 12345)
        self.assertIsNone(quote.turnover_rate)
        self.assertEqual(quote.total_mv, 123456789.0)

    def test_daily_data_normalization(self):
        fetcher = KisFetcher()
        raw = pd.DataFrame(
            [
                {
                    "stck_bsop_date": "20260602",
                    "stck_oprc": "69000",
                    "stck_hgpr": "70500",
                    "stck_lwpr": "68800",
                    "stck_clpr": "70000",
                    "acml_vol": "12345",
                    "acml_tr_pbmn": "864150000",
                    "prdy_ctrt": "1.25",
                }
            ]
        )

        df = fetcher._normalize_data(raw, "005930.KS")

        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["close"], 70000)
        self.assertEqual(df.iloc[0]["volume"], 12345)


if __name__ == "__main__":
    unittest.main()
