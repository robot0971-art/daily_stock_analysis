# -*- coding: utf-8 -*-
import os
import sys
import unittest
from unittest.mock import MagicMock

import pandas as pd

if 'fake_useragent' not in sys.modules:
    sys.modules['fake_useragent'] = MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def _make_mock_hist(close: float, prev_close: float) -> pd.DataFrame:
    return pd.DataFrame({
        'Close': [prev_close, close],
        'Open': [prev_close - 5, close - 3],
        'High': [prev_close + 10, close + 10],
        'Low': [prev_close - 10, close - 10],
        'Volume': [1000000.0, 1200000.0],
    }, index=pd.DatetimeIndex(['2026-06-10', '2026-06-11']))


def _make_mock_yf(hist_df: pd.DataFrame):
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = hist_df
    mock_yf = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    return mock_yf


class TestGetKrMainIndices(unittest.TestCase):
    def setUp(self):
        from data_provider.yfinance_fetcher import YfinanceFetcher
        self.fetcher = YfinanceFetcher()

    def test_uses_kospi_and_kosdaq_symbols(self):
        mock_yf = _make_mock_yf(pd.DataFrame())

        self.fetcher._get_kr_main_indices(mock_yf)

        ticker_calls = [call.args[0] for call in mock_yf.Ticker.call_args_list]
        self.assertEqual(ticker_calls, ['^KS11', '^KQ11'])

    def test_returns_korean_index_payload(self):
        mock_yf = _make_mock_yf(_make_mock_hist(close=2800.0, prev_close=2750.0))

        result = self.fetcher._get_kr_main_indices(mock_yf)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual({item['code'] for item in result}, {'KOSPI', 'KOSDAQ'})
        self.assertEqual({item['name'] for item in result}, {'코스피', '코스닥'})
        for item in result:
            self.assertIn('current', item)
            self.assertIn('change_pct', item)
            self.assertIn('prev_close', item)


if __name__ == '__main__':
    unittest.main()
