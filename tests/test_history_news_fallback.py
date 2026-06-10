# -*- coding: utf-8 -*-
"""Tests for history fallback published_date hard filtering (Issue #697)."""

import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.services.history_service import HistoryService
from src.search_service import SearchResponse, SearchResult


class HistoryNewsFallbackTestCase(unittest.TestCase):
    def test_fallback_filters_by_published_date_window(self) -> None:
        now = datetime.now()
        analysis = SimpleNamespace(code="600519", created_at=now)

        # All entries are within fetched_at window; only one should pass published_date window.
        candidates = [
            SimpleNamespace(
                fetched_at=now,
                published_date=now - timedelta(days=20),  # too old
                title="old",
            ),
            SimpleNamespace(
                fetched_at=now,
                published_date=None,  # unknown -> drop
                title="unknown",
            ),
            SimpleNamespace(
                fetched_at=now,
                published_date=now - timedelta(days=1),  # valid
                title="fresh",
            ),
        ]

        mock_db = MagicMock()
        mock_db.get_analysis_history.return_value = [analysis]
        mock_db.get_recent_news.return_value = candidates

        svc = HistoryService(db_manager=mock_db)
        fake_cfg = SimpleNamespace(news_max_age_days=30, news_strategy_profile="short")
        with patch("src.services.history_service.get_config", return_value=fake_cfg):
            result = svc._fallback_news_by_analysis_context("q-1", limit=20)

        self.assertEqual([item.title for item in result], ["fresh"])

    def test_fallback_uses_analysis_date_as_window_anchor(self) -> None:
        analysis_time = datetime.now() - timedelta(days=40)
        analysis = SimpleNamespace(code="600519", created_at=analysis_time)

        candidates = [
            SimpleNamespace(
                fetched_at=analysis_time,
                published_date=analysis_time - timedelta(days=10),  # too old for short profile
                title="too_old_for_analysis_window",
            ),
            SimpleNamespace(
                fetched_at=analysis_time,
                published_date=analysis_time - timedelta(days=1),  # valid around analysis date
                title="valid_near_analysis_date",
            ),
        ]

        mock_db = MagicMock()
        mock_db.get_analysis_history.return_value = [analysis]
        mock_db.get_recent_news.return_value = candidates

        svc = HistoryService(db_manager=mock_db)
        fake_cfg = SimpleNamespace(news_max_age_days=30, news_strategy_profile="short")
        with patch("src.services.history_service.get_config", return_value=fake_cfg):
            result = svc._fallback_news_by_analysis_context("q-1", limit=20)

        self.assertEqual([item.title for item in result], ["valid_near_analysis_date"])

    def test_fallback_uses_same_stock_recent_news_when_analysis_window_has_no_match(self) -> None:
        now = datetime.now()
        analysis = SimpleNamespace(code="AAPL", created_at=now)
        recent_news = SimpleNamespace(
            fetched_at=now - timedelta(days=2),
            published_date=now - timedelta(days=1),
            title="recent apple news",
            snippet="recent snippet",
            url="https://example.com/aapl",
            source="Example",
        )

        mock_db = MagicMock()
        mock_db.get_analysis_history.return_value = [analysis]
        mock_db.get_recent_news.side_effect = [[recent_news], [recent_news]]

        svc = HistoryService(db_manager=mock_db)
        fake_cfg = SimpleNamespace(news_max_age_days=3, news_strategy_profile="short")
        with patch("src.services.history_service.get_config", return_value=fake_cfg):
            result = svc._fallback_news_by_analysis_context("q-1", limit=20)

        self.assertEqual([item.title for item in result], ["recent apple news"])
        self.assertEqual(mock_db.get_recent_news.call_args_list[1].kwargs["days"], 30)

    def test_get_news_intel_marks_same_stock_recent_fallback(self) -> None:
        now = datetime.now()
        analysis = SimpleNamespace(code="AAPL", created_at=now)
        recent_news = SimpleNamespace(
            fetched_at=now - timedelta(days=2),
            published_date=now - timedelta(days=1),
            title="recent apple news",
            snippet="recent snippet",
            url="https://example.com/aapl",
            source="Example",
        )

        mock_db = MagicMock()
        mock_db.get_news_intel_by_query_id.return_value = []
        mock_db.get_analysis_history.return_value = [analysis]
        mock_db.get_recent_news.side_effect = [[recent_news], [recent_news]]

        svc = HistoryService(db_manager=mock_db)
        fake_cfg = SimpleNamespace(news_max_age_days=3, news_strategy_profile="short")
        with patch("src.services.history_service.get_config", return_value=fake_cfg):
            result = svc.get_news_intel("q-1", limit=20)

        self.assertEqual(result[0]["title"], "recent apple news")
        self.assertTrue(result[0]["is_fallback"])
        self.assertEqual(result[0]["fallback_reason"], "same_stock_recent")
        self.assertEqual(result[0]["source"], "Example")
        self.assertRegex(result[0]["published_date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_get_news_intel_uses_live_us_news_fallback_when_no_saved_news_exists(self) -> None:
        now = datetime.now()
        analysis = SimpleNamespace(code="AAPL", name="Apple Inc.", created_at=now)
        response = SearchResponse(
            query="Apple Inc. AAPL stock latest news",
            results=[
                SearchResult(
                    title="live apple news",
                    snippet="Yahoo Finance - 2026-06-10",
                    url="https://example.com/live-aapl",
                    source="Yahoo Finance",
                    published_date="2026-06-10",
                )
            ],
            provider="YahooFinance",
            success=True,
        )
        search_service = SimpleNamespace(search_stock_news=MagicMock(return_value=response))

        mock_db = MagicMock()
        mock_db.get_news_intel_by_query_id.return_value = []
        mock_db.get_analysis_history.return_value = [analysis]
        mock_db.get_recent_news.return_value = []
        mock_db.save_news_intel.return_value = 1

        svc = HistoryService(db_manager=mock_db)
        with patch("src.search_service.get_search_service", return_value=search_service):
            result = svc.get_news_intel("q-1", limit=8)

        self.assertEqual(result[0]["title"], "live apple news")
        self.assertTrue(result[0]["is_fallback"])
        self.assertEqual(result[0]["fallback_reason"], "live_search")
        search_service.search_stock_news.assert_called_once_with("AAPL", "Apple Inc.", max_results=8)
        mock_db.save_news_intel.assert_called_once()


if __name__ == "__main__":
    unittest.main()
