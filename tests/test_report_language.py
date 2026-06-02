# -*- coding: utf-8 -*-
"""Unit tests for report language helpers."""

import unittest

from src.report_language import (
    get_bias_status_emoji,
    get_localized_stock_name,
    get_report_labels,
    get_sentiment_label,
    get_signal_level,
    infer_decision_type_from_advice,
    localize_operation_advice,
    localize_trend_prediction,
    localize_bias_status,
)
from src.notification import NotificationService


class ReportLanguageTestCase(unittest.TestCase):
    def test_get_signal_level_handles_compound_sell_advice(self) -> None:
        signal_text, emoji, signal_tag = get_signal_level("卖出/观望", 60, "zh")

        self.assertEqual(signal_text, "卖出")
        self.assertEqual(emoji, "🔴")
        self.assertEqual(signal_tag, "sell")

    def test_get_signal_level_handles_compound_buy_advice_in_english(self) -> None:
        signal_text, emoji, signal_tag = get_signal_level("Buy / Watch", 40, "en")

        self.assertEqual(signal_text, "Buy")
        self.assertEqual(emoji, "🟢")
        self.assertEqual(signal_tag, "buy")

    def test_get_localized_stock_name_replaces_placeholder_for_english(self) -> None:
        self.assertEqual(
            get_localized_stock_name("股票AAPL", "AAPL", "en"),
            "Unnamed Stock",
        )

    def test_get_sentiment_label_preserves_higher_band_thresholds(self) -> None:
        self.assertEqual(get_sentiment_label(80, "en"), "Very Bullish")
        self.assertEqual(get_sentiment_label(60, "en"), "Bullish")
        self.assertEqual(get_sentiment_label(40, "zh"), "中性")
        self.assertEqual(get_sentiment_label(20, "zh"), "悲观")

    def test_localize_trend_prediction_preserves_fine_grain_zh_states(self) -> None:
        self.assertEqual(localize_trend_prediction("多头排列", "zh"), "多头排列")
        self.assertEqual(localize_trend_prediction("弱势空头", "zh"), "弱势空头")

    def test_localize_trend_prediction_still_translates_english_input_for_zh(self) -> None:
        self.assertEqual(localize_trend_prediction("bullish", "zh"), "看多")
        self.assertEqual(localize_trend_prediction("very bearish", "zh"), "强烈看空")

    def test_bias_status_helpers_support_english_values(self) -> None:
        self.assertEqual(localize_bias_status("Safe", "en"), "Safe")
        self.assertEqual(localize_bias_status("警戒", "en"), "Caution")
        self.assertEqual(get_bias_status_emoji("Safe"), "✅")
        self.assertEqual(get_bias_status_emoji("Caution"), "⚠️")

    def test_infer_decision_type_from_advice_matches_chinese_phrases(self) -> None:
        self.assertEqual(infer_decision_type_from_advice("建议买入"), "buy")
        self.assertEqual(infer_decision_type_from_advice("建议持有"), "hold")
        self.assertEqual(infer_decision_type_from_advice("建议减仓"), "sell")
        self.assertEqual(infer_decision_type_from_advice("继续持有"), "hold")
        self.assertEqual(infer_decision_type_from_advice("建议洗盘观察"), "hold")
        self.assertEqual(infer_decision_type_from_advice("洗盘观察", default=""), "hold")
        self.assertEqual(infer_decision_type_from_advice("观察", default=""), "hold")
        self.assertEqual(infer_decision_type_from_advice("不建议买入"), "hold")
        self.assertEqual(
            infer_decision_type_from_advice("当前不跌破支撑位继续持有"),
            "hold",
        )
        self.assertEqual(
            infer_decision_type_from_advice("不破支撑后仍可持有"),
            "hold",
        )


class KoreanReportPolishTestCase(unittest.TestCase):
    def test_korean_report_labels_do_not_use_chinese_mixed_text(self) -> None:
        labels = get_report_labels("ko")

        self.assertEqual(labels["dashboard_title"], "의사결정 대시보드")
        self.assertEqual(labels["info_heading"], "핵심 정보 요약")
        self.assertEqual(labels["risk_alerts_label"], "리스크 알림")
        self.assertEqual(labels["one_sentence_label"], "한 줄 결론")
        self.assertEqual(labels["no_position_label"], "미보유")
        self.assertEqual(labels["battle_plan_heading"], "대응 계획")

        joined = "\n".join(labels.values())
        for forbidden in ("警报", "速览", "一句话", "时效", "空仓", "作战", "清单", "只股票"):
            self.assertNotIn(forbidden, joined)

    def test_korean_localizers_translate_common_chinese_ai_values(self) -> None:
        self.assertEqual(localize_operation_advice("持有", "ko"), "보유")
        self.assertEqual(localize_operation_advice("观望", "ko"), "관망")
        self.assertEqual(localize_trend_prediction("震荡", "ko"), "흔들림")
        self.assertEqual(localize_trend_prediction("看多", "ko"), "낙관")
        self.assertEqual(localize_bias_status("危险", "ko"), "위험")

    def test_korean_report_text_filter_replaces_common_chinese_terms(self) -> None:
        text = NotificationService._clean_report_text(
            "风险点1：动态PER高，韩元目标价，强势多头排列，空仓者严禁追高",
            "ko",
        )

        self.assertIn("리스크1", text)
        self.assertIn("동적 PER", text)
        self.assertIn("원", text)
        self.assertIn("강한 상승 배열", text)
        self.assertIn("미보유자는", text)
        for forbidden in ("风险", "韩元", "强势多头", "空仓者", "追高"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
