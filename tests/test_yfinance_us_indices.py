# -*- coding: utf-8 -*-
"""
data_provider/yfinance_fetcher 中美股指数获取逻辑的单元测试

使用 unittest.mock 模拟 yfinance API 响应，覆盖：
- _fetch_yf_ticker_data 单指数数据解析
- _get_us_main_indices 美股指数批量获取及异常场景
"""
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd

# 在导入 data_provider 前 mock 可能缺失的依赖，避免环境差异导致测试无法运行
if 'fake_useragent' not in sys.modules:
    sys.modules['fake_useragent'] = MagicMock()

# 确保能导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def _make_mock_hist(close: float, prev_close: float, high: float = None, low: float = None) -> pd.DataFrame:
    """构造模拟的 history DataFrame，包含计算涨跌幅所需字段"""
    high = high if high is not None else close + 1
    low = low if low is not None else close - 1
    return pd.DataFrame({
        'Close': [prev_close, close],
        'Open': [prev_close - 0.5, close - 0.3],
        'High': [prev_close + 1, high],
        'Low': [prev_close - 1, low],
        'Volume': [1000000.0, 1200000.0],
    }, index=pd.DatetimeIndex(['2025-02-16', '2025-02-17']))


def _make_mock_yf(hist_df: pd.DataFrame):
    """构造模拟的 yf 模块，Ticker().history() 返回给定 DataFrame"""
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = hist_df
    mock_yf = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    return mock_yf


class TestFetchYfTickerData(unittest.TestCase):
    """_fetch_yf_ticker_data 单指数取数逻辑测试"""

    def setUp(self):
        from data_provider.yfinance_fetcher import YfinanceFetcher
        self.fetcher = YfinanceFetcher()

    def test_returns_dict_with_correct_fields(self):
        """正常数据应返回包含 code/name/current/change_pct 等字段的字典"""
        mock_hist = _make_mock_hist(close=5100.0, prev_close=5000.0)
        mock_yf = _make_mock_yf(mock_hist)

        result = self.fetcher._fetch_yf_ticker_data(mock_yf, '^GSPC', '标普500指数', 'SPX')

        self.assertIsNotNone(result)
        self.assertEqual(result['code'], 'SPX')
        self.assertEqual(result['name'], '标普500指数')
        self.assertEqual(result['current'], 5100.0)
        self.assertEqual(result['prev_close'], 5000.0)
        self.assertEqual(result['change'], 100.0)
        self.assertAlmostEqual(result['change_pct'], 2.0)
        self.assertIn('open', result)
        self.assertIn('high', result)
        self.assertIn('low', result)
        self.assertIn('volume', result)
        self.assertIn('amount', result)
        self.assertIn('amplitude', result)

    def test_returns_none_when_history_empty(self):
        """history 为空时应返回 None"""
        mock_yf = _make_mock_yf(pd.DataFrame())

        result = self.fetcher._fetch_yf_ticker_data(mock_yf, '^GSPC', '标普500指数', 'SPX')

        self.assertIsNone(result)

    def test_single_row_history_uses_same_as_prev(self):
        """仅一行数据时 prev_close 等于 current，change_pct 为 0"""
        mock_hist = _make_mock_hist(close=5000.0, prev_close=5000.0)
        mock_hist = mock_hist.iloc[[-1]]
        mock_yf = _make_mock_yf(mock_hist)

        result = self.fetcher._fetch_yf_ticker_data(mock_yf, '^GSPC', '标普500指数', 'SPX')

        self.assertIsNotNone(result)
        self.assertEqual(result['change_pct'], 0.0)


class TestGetUsMainIndices(unittest.TestCase):
    """_get_us_main_indices 美股指数批量获取测试"""

    def setUp(self):
        from data_provider.yfinance_fetcher import YfinanceFetcher
        self.fetcher = YfinanceFetcher()

    @patch('data_provider.yfinance_fetcher.get_us_index_yf_symbol')
    def test_returns_list_when_mock_succeeds(self, mock_get_symbol):
        """当映射与取数均成功时返回指数列表"""
        def get_symbol(code):
            mapping = {
                'SPX': ('^GSPC', '标普500指数'),
                'IXIC': ('^IXIC', '纳斯达克综合指数'),
                'DJI': ('^DJI', '道琼斯工业指数'),
                'VIX': ('^VIX', 'VIX恐慌指数'),
            }
            return mapping.get(code, (None, None))

        mock_get_symbol.side_effect = get_symbol
        mock_hist = _make_mock_hist(close=5100.0, prev_close=5000.0)
        mock_yf = _make_mock_yf(mock_hist)

        result = self.fetcher._get_us_main_indices(mock_yf)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        for item in result:
            self.assertIn('code', item)
            self.assertIn('name', item)
            self.assertIn('current', item)
            self.assertIn('change_pct', item)

    @patch('data_provider.yfinance_fetcher.get_us_index_yf_symbol')
    def test_handles_empty_history_gracefully(self, mock_get_symbol):
        """部分指数 history 为空时仍返回能取到数据的指数"""
        call_count = [0]

        def get_symbol(code):
            return ('^GSPC', '标普500指数') if code == 'SPX' else (
                ('^IXIC', '纳斯达克综合指数') if code == 'IXIC' else (None, None)
            )

        def history_side_effect(period):
            call_count[0] += 1
            if call_count[0] == 1:
                return _make_mock_hist(close=5100.0, prev_close=5000.0)
            return pd.DataFrame()

        mock_get_symbol.side_effect = get_symbol
        mock_ticker = MagicMock()
        mock_ticker.history.side_effect = history_side_effect
        mock_yf = MagicMock()
        mock_yf.Ticker.return_value = mock_ticker

        result = self.fetcher._get_us_main_indices(mock_yf)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

    @patch('data_provider.yfinance_fetcher.get_us_index_yf_symbol')
    def test_returns_none_when_all_fail(self, mock_get_symbol):
        """全部取数失败时返回 None"""
        mock_get_symbol.return_value = (None, None)
        mock_yf = _make_mock_yf(pd.DataFrame())

        result = self.fetcher._get_us_main_indices(mock_yf)

        self.assertIsNone(result)

    @patch('data_provider.yfinance_fetcher.get_us_index_yf_symbol')
    def test_handles_ticker_exception(self, mock_get_symbol):
        """Ticker.history 抛异常时跳过该指数，不整体失败"""
        mock_get_symbol.return_value = ('^GSPC', '标普500指数')
        mock_ticker = MagicMock()
        mock_ticker.history.side_effect = Exception("Network error")
        mock_yf = MagicMock()
        mock_yf.Ticker.return_value = mock_ticker

        result = self.fetcher._get_us_main_indices(mock_yf)

        self.assertIsNone(result)

    @patch('data_provider.yfinance_fetcher.get_us_index_yf_symbol')
    def test_skips_unknown_index_code(self, mock_get_symbol):
        """get_us_index_yf_symbol 返回 (None, None) 的代码应被跳过"""
        def get_symbol(code):
            if code == 'SPX':
                return ('^GSPC', '标普500指数')
            return (None, None)

        mock_get_symbol.side_effect = get_symbol
        mock_hist = _make_mock_hist(close=5100.0, prev_close=5000.0)
        mock_yf = _make_mock_yf(mock_hist)

        result = self.fetcher._get_us_main_indices(mock_yf)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['code'], 'SPX')


class TestNormalizeData(unittest.TestCase):
    """Regression tests for current yfinance daily DataFrame shapes."""

    def setUp(self):
        from data_provider.yfinance_fetcher import YfinanceFetcher
        self.fetcher = YfinanceFetcher()

    def test_normalize_multiindex_with_unnamed_date_index(self):
        columns = pd.MultiIndex.from_tuples([
            ("Open", "AAPL"),
            ("High", "AAPL"),
            ("Low", "AAPL"),
            ("Close", "AAPL"),
            ("Volume", "AAPL"),
        ])
        df = pd.DataFrame(
            [
                [100.0, 105.0, 99.0, 104.0, 1000],
                [104.0, 108.0, 103.0, 107.0, 1200],
            ],
            index=pd.DatetimeIndex(["2026-05-28", "2026-05-29"]),
            columns=columns,
        )

        result = self.fetcher._normalize_data(df, "AAPL")

        self.assertIn("date", result.columns)
        self.assertEqual(result["date"].dt.strftime("%Y-%m-%d").tolist(), ["2026-05-28", "2026-05-29"])
        self.assertEqual(result["code"].tolist(), ["AAPL", "AAPL"])
        self.assertEqual(result["close"].tolist(), [104.0, 107.0])
        self.assertEqual(result["amount"].tolist(), [104000.0, 128400.0])
        self.assertAlmostEqual(result["pct_chg"].iloc[1], 2.88)


if __name__ == '__main__':
    unittest.main()
