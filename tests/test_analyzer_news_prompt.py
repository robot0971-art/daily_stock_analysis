# -*- coding: utf-8 -*-
"""Tests for analyzer news prompt hard constraints (Issue #697)."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

try:
    import litellm  # noqa: F401
except ModuleNotFoundError:
    from tests.litellm_stub import ensure_litellm_stub

    ensure_litellm_stub()

from src.analyzer import (
    GeminiAnalyzer,
    _BULLISH_TREND_HINTS,
    _contains_trend_hint,
    _infer_trend_direction,
    _sanitize_trend_analysis_for_prompt,
)


class AnalyzerNewsPromptTestCase(unittest.TestCase):
    def test_contains_trend_hint_treats_non_adjacent_negation_as_negated(self) -> None:
        self.assertFalse(_contains_trend_hint("尚未形成上升趋势，继续观察。", _BULLISH_TREND_HINTS))
        self.assertFalse(_contains_trend_hint("未形成上升趋势，继续观察。", _BULLISH_TREND_HINTS))
        self.assertFalse(_contains_trend_hint("并未形成上升趋势，继续观察。", _BULLISH_TREND_HINTS))
        self.assertFalse(_contains_trend_hint("没有形成多头排列，继续观察。", _BULLISH_TREND_HINTS))
        self.assertFalse(_contains_trend_hint("当前无多头排列，仍需观察。", _BULLISH_TREND_HINTS))
        self.assertFalse(_contains_trend_hint("尚不属于上升趋势，反弹仍待确认。", _BULLISH_TREND_HINTS))
        self.assertFalse(_contains_trend_hint("当前非多头排列，仍需观察。", _BULLISH_TREND_HINTS))
        self.assertFalse(_contains_trend_hint("This is not a bullish trend yet.", _BULLISH_TREND_HINTS))

    def test_contains_trend_hint_scans_later_non_negated_occurrences(self) -> None:
        self.assertTrue(
            _contains_trend_hint(
                "不是多头排列，后续放量后再次出现多头排列信号。",
                _BULLISH_TREND_HINTS,
            )
        )

    def test_contains_trend_hint_keeps_contrast_clause_target_hint(self) -> None:
        self.assertTrue(_contains_trend_hint("不是空头而是多头排列，趋势修复。", _BULLISH_TREND_HINTS))
        self.assertFalse(_contains_trend_hint("未转为上升趋势，反弹仍待确认。", _BULLISH_TREND_HINTS))

    def test_contains_trend_hint_ignores_single_character_prefixes_in_common_words(self) -> None:
        self.assertTrue(_contains_trend_hint("非常明显的多头排列，趋势仍在延续。", _BULLISH_TREND_HINTS))
        self.assertTrue(_contains_trend_hint("未来上升趋势若放量将进一步确认。", _BULLISH_TREND_HINTS))
        self.assertEqual(
            _infer_trend_direction({"trend_status": "非常明显的多头排列", "ma_alignment": "未来上升趋势逐步明确"}),
            "bullish",
        )

    def test_infer_trend_direction_recognizes_weak_bullish_and_bearish_states(self) -> None:
        self.assertEqual(
            _infer_trend_direction({"trend_status": "弱势多头", "ma_alignment": "弱势多头，MA5>MA10 但 MA10≤MA20"}),
            "bullish",
        )
        self.assertEqual(
            _infer_trend_direction({"trend_status": "弱势空头", "ma_alignment": "弱势空头，MA5<MA10 但 MA10≥MA20"}),
            "bearish",
        )

    def test_infer_trend_direction_ignores_negated_bullish_hints(self) -> None:
        self.assertEqual(
            _infer_trend_direction({"trend_status": "未形成上升趋势", "ma_alignment": "当前非多头排列"}),
            "neutral",
        )
        self.assertEqual(
            _infer_trend_direction({"trend_status": "没有形成多头排列", "ma_alignment": "当前无上升趋势"}),
            "neutral",
        )

    def test_infer_trend_direction_keeps_contrast_clause_final_direction(self) -> None:
        self.assertEqual(
            _infer_trend_direction({"trend_status": "不是空头而是多头排列", "ma_alignment": ""}),
            "bullish",
        )

    def test_analysis_prompt_resolves_shared_skill_prompt_state_by_default(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer()

        fake_state = SimpleNamespace(
            skill_instructions="### 技能 1: 波段低吸\n- 关注支撑确认",
            default_skill_policy="",
        )
        with patch("src.agent.factory.resolve_skill_prompt_state", return_value=fake_state):
            prompt = analyzer._get_analysis_system_prompt("zh", stock_code="600519")

        self.assertIn("### 技能 1: 波段低吸", prompt)
        self.assertNotIn("专注于趋势交易", prompt)

    def test_analysis_prompt_uses_injected_skill_sections_instead_of_hardcoded_trend_baseline(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer(
                skill_instructions="### 技能 1: 缠论\n- 关注中枢与背驰",
                default_skill_policy="",
            )

        prompt = analyzer._get_analysis_system_prompt("zh", stock_code="600519")

        self.assertIn("### 技能 1: 缠论", prompt)
        self.assertNotIn("专注于趋势交易", prompt)
        self.assertNotIn("多头排列：MA5 > MA10 > MA20", prompt)

    def test_analysis_prompt_keeps_injected_default_policy_for_implicit_default_run(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer(
                skill_instructions="### 技能 1: 默认多头趋势",
                default_skill_policy="## 默认技能基线（必须严格遵守）\n- **多头排列必须条件**：MA5 > MA10 > MA20",
                use_legacy_default_prompt=True,
            )

        prompt = analyzer._get_analysis_system_prompt("zh", stock_code="600519")

        self.assertIn("专注于趋势交易", prompt)
        self.assertIn("多头排列必须条件", prompt)
        self.assertIn("多头排列：MA5 > MA10 > MA20", prompt)

    def test_analysis_prompt_contains_actionability_guardrails(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer()

        prompt = analyzer._get_analysis_system_prompt("zh", stock_code="002812")

        self.assertIn("可操作性与稳定性约束", prompt)
        self.assertIn("不得仅因为单日涨跌", prompt)
        self.assertIn("支撑/压力位", prompt)
        self.assertIn("洗盘观察", prompt)

    def test_analysis_system_prompt_requires_beginner_friendly_korean_style(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer()

        prompt = analyzer._get_analysis_system_prompt("ko", stock_code="005930.KS")

        self.assertIn("초보자도 이해할 수 있는 설명 원칙", prompt)
        self.assertIn("쉬운 한국어", prompt)
        self.assertIn("지금 무슨 일이 있는지", prompt)
        self.assertIn("수익을 보장", prompt)

    def test_format_prompt_adds_beginner_decision_rules_for_korean_report(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer()

        context = {
            "code": "005930.KS",
            "stock_name": "삼성전자",
            "date": "2026-06-02",
            "today": {"close": 356500, "ma5": 350000, "ma10": 342000, "ma20": 330000},
        }

        prompt = analyzer._format_prompt(
            context,
            "삼성전자",
            news_context="Samsung Electronics stock news",
            report_language="ko",
        )

        self.assertIn("초보자용 판단 설명 규칙", prompt)
        self.assertIn("결론부터 시작", prompt)
        self.assertIn("현재 상황", prompt)
        self.assertIn("뉴스 날짜가 불명확한 경우", prompt)

    def test_analysis_system_prompt_requires_beginner_friendly_english_style(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer()

        prompt = analyzer._get_analysis_system_prompt("en", stock_code="AAPL")

        self.assertIn("Beginner-Friendly Analyst Style", prompt)
        self.assertIn("first-time investor", prompt)
        self.assertIn("what would change the view", prompt)

    def test_prompt_contains_time_constraints(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer()

        context = {
            "code": "600519",
            "stock_name": "贵州茅台",
            "date": "2026-03-16",
            "today": {},
            "fundamental_context": {
                "earnings": {
                    "data": {
                        "financial_report": {"report_date": "2025-12-31", "revenue": 1000},
                        "dividend": {"ttm_cash_dividend_per_share": 1.2, "ttm_dividend_yield_pct": 2.4},
                    }
                }
            },
        }
        fake_cfg = SimpleNamespace(
            news_max_age_days=30,
            news_strategy_profile="medium",  # 7 days
        )
        with patch("src.analyzer.get_config", return_value=fake_cfg):
            prompt = analyzer._format_prompt(context, "贵州茅台", news_context="news")

        self.assertIn("\u8fd17\u65e5\uc758\ub274\uc2a4\uac80\uc0c9\uacb0\uacfc", prompt)
        self.assertIn("\u6bcf\u4e00\u6761\u90fd\ud544\uc218\u5e26\uad6c\uccb4\uc801\ub0a0\uc9dc\uff08YYYY-MM-DD\uff09", prompt)
        self.assertIn("\u8d85\u51fa\u8fd17\u65e5\u7a97\u53e3\uc758\ub274\uc2a4\u4e00\u5f8b\u5ffd\u7565", prompt)
        self.assertIn("\uc2dc\uac04\uc54c\uc218\uc5c6\uc74c\u3001\ubd88\uac00\ud655\uc778\ubc1c\ud589\ub0a0\uc9dc\uc758\ub274\uc2a4\u4e00\u5f8b\u5ffd\u7565", prompt)
        self.assertIn("\uc7ac\ubb34\uc81c\ud45c\uc640\ubc30\ub2f9\uff08\uac00\uce58\u6295\u8d44\u53e3\u5f84\uff09", prompt)
        self.assertIn("禁止编造", prompt)

    def test_prompt_includes_capital_flow_as_operation_filter(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer()

        context = {
            "code": "002812",
            "stock_name": "恩捷股份",
            "date": "2026-04-01",
            "today": {"close": 32.8, "ma5": 31.2, "ma10": 30.5, "ma20": 29.8},
            "fundamental_context": {
                "capital_flow": {
                    "status": "ok",
                    "data": {
                        "stock_flow": {
                            "main_net_inflow": -1200000,
                            "inflow_5d": -3600000,
                            "inflow_10d": -5200000,
                        },
                        "sector_rankings": {
                            "top": [{"name": "电池"}],
                            "bottom": [{"name": "化工"}],
                        },
                    },
                }
            },
        }

        prompt = analyzer._format_prompt(context, "恩捷股份", news_context=None)

        self.assertIn("\uc8fc\uc694\uc790\uae08\u6d41\ub85c\uff08\ub9e4\ub9e4\uc81c\uc548\ud544\ud130\ub9c1\u5668\uff09", prompt)
        self.assertIn("\uc8fc\uc694\uc21c\uc720\uc785", prompt)
        self.assertIn("-1200000", prompt)
        self.assertIn("\uc811\uadfc\uc800\ud56d\ub610\ud55c\uc8fc\u529b\uc720\ucd9c\u65f6\ucd94\uaca9\ub9e4\uc218\uae08\uc9c0", prompt)
        self.assertIn("\ud754\ub4e4\ub9bc\ub610\ub294\uc138\ud0c1\uad00\ucc30", prompt)

    def test_prompt_prefers_context_news_window_days(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer()

        context = {
            "code": "600519",
            "stock_name": "贵州茅台",
            "date": "2026-03-16",
            "today": {},
            "news_window_days": 1,
        }
        fake_cfg = SimpleNamespace(
            news_max_age_days=30,
            news_strategy_profile="long",  # 30 days if fallback is used
        )
        with patch("src.analyzer.get_config", return_value=fake_cfg):
            prompt = analyzer._format_prompt(context, "贵州茅台", news_context="news")

        self.assertIn("\u8fd11\u65e5\uc758\ub274\uc2a4\uac80\uc0c9\uacb0\uacfc", prompt)
        self.assertIn("\u8d85\u51fa\u8fd11\u65e5\u7a97\u53e3\uc758\ub274\uc2a4\u4e00\u5f8b\u5ffd\u7565", prompt)

    def test_format_prompt_injects_market_phase_before_technical_data(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer()

        context = {
            "code": "600519",
            "stock_name": "贵州茅台",
            "date": "2026-03-27",
            "today": {},
            "market_phase_context": {
                "market": "cn",
                "phase": "premarket",
                "market_local_time": "2026-03-27T09:00:00+08:00",
                "effective_daily_bar_date": "2026-03-26",
                "is_partial_bar": False,
                "minutes_to_open": 30,
                "warnings": [],
            },
        }

        prompt = analyzer._format_prompt(context, "贵州茅台", news_context=None)

        phase_index = prompt.index("市场阶段上下文")
        technical_index = prompt.index("技术面数据")
        self.assertLess(phase_index, technical_index)
        self.assertIn("盘前", prompt)
        self.assertIn("不得描述“今日走势已经发生”", prompt)

    def test_format_prompt_omits_market_phase_section_without_context(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer()

        context = {
            "code": "600519",
            "stock_name": "贵州茅台",
            "date": "2026-03-27",
            "today": {},
        }

        prompt = analyzer._format_prompt(context, "贵州茅台", news_context=None)

        self.assertNotIn("市场阶段上下文", prompt)

    def test_format_prompt_omits_legacy_trend_checks_for_nondefault_skill_mode(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer(
                skill_instructions="### 技能 1: 缠论\n- 关注中枢与背驰",
                default_skill_policy="",
                use_legacy_default_prompt=False,
            )

        context = {
            "code": "600519",
            "stock_name": "贵州茅台",
            "date": "2026-03-16",
            "today": {"close": 100, "ma5": 99, "ma10": 98, "ma20": 97},
            "trend_analysis": {
                "trend_status": "震荡偏强",
                "ma_alignment": "粘合后发散",
                "trend_strength": 61,
                "bias_ma5": 1.2,
                "bias_ma10": 2.4,
                "volume_status": "平量",
                "volume_trend": "量能温和",
                "buy_signal": "观察",
                "signal_score": 58,
                "signal_reasons": ["结构待确认"],
                "risk_factors": ["无背驰确认"],
            },
        }
        prompt = analyzer._format_prompt(context, "贵州茅台", news_context=None)

        self.assertIn("\ud604\uc7ac\uad6c\uc870\uc5ec\ubd80\u6ee1\u8db3\u6fc0\u6d3b\uc2a4\ud0ac\uc758\ud575\uc2ec\ud2b8\ub9ac\uac70\uc870\uac74", prompt)
        self.assertNotIn("是否满足 MA5>MA10>MA20 多头排列", prompt)
        self.assertNotIn("超过5%必须标注\"严禁追高\"", prompt)
        self.assertNotIn("MA5>MA10>MA20为多头", prompt)

    def test_format_prompt_removes_bullish_reasons_when_final_trend_is_bearish(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer(
                skill_instructions="### 技能 1: 缠论\n- 关注中枢与背驰",
                default_skill_policy="",
                use_legacy_default_prompt=False,
            )

        context = {
            "code": "603259",
            "stock_name": "药明康德",
            "date": "2026-04-28",
            "today": {"close": 58.6, "ma5": 57.2, "ma10": 58.8, "ma20": 60.4},
            "yesterday": {"close": 57.8},
            "volume_change_ratio": 12.4,
            "trend_analysis": {
                "trend_status": "空头排列",
                "ma_alignment": "空头排列 MA5<MA10<MA20",
                "trend_strength": 34,
                "bias_ma5": 2.1,
                "bias_ma10": -0.8,
                "volume_status": "放量",
                "volume_trend": "放量震荡",
                "buy_signal": "观察",
                "signal_score": 41,
                "signal_reasons": ["多头排列，持续上涨", "事件催化存在但技术待确认"],
                "risk_factors": ["跌破MA20，趋势承压"],
            },
        }

        prompt = analyzer._format_prompt(
            context,
            "药明康德",
            news_context="2026-04-27 一季报超预期，订单增长。",
        )

        self.assertIn("空头排列 MA5<MA10<MA20", prompt)
        self.assertNotIn("多头排列，持续上涨", prompt)
        self.assertIn("事件催化存在但技术待确认", prompt)
        self.assertIn("事件先行、技术待确认", prompt)
        self.assertIn("\uac70\ub798\ub7c9\uc608\uc678\uc54c\ub9bc", prompt)
        self.assertIn("\uc77c\uce58\u6027\u7ea6\u675f", prompt)

    def test_format_prompt_removes_bearish_risks_when_final_trend_is_bullish(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer(
                skill_instructions="### 技能 1: 缠论\n- 关注中枢与背驰",
                default_skill_policy="",
                use_legacy_default_prompt=False,
            )

        context = {
            "code": "600519",
            "stock_name": "贵州茅台",
            "date": "2026-04-28",
            "today": {"close": 1688.0, "ma5": 1675.0, "ma10": 1660.0, "ma20": 1640.0},
            "trend_analysis": {
                "trend_status": "多头排列",
                "ma_alignment": "多头排列 MA5>MA10>MA20",
                "trend_strength": 78,
                "bias_ma5": 1.8,
                "bias_ma10": 3.2,
                "volume_status": "平量",
                "volume_trend": "量价配合",
                "buy_signal": "偏强",
                "signal_score": 73,
                "signal_reasons": ["多头排列，持续上涨", "空头排列，持续下跌"],
                "risk_factors": ["空头排列，持续下跌", "财报披露前波动可能放大"],
            },
        }

        prompt = analyzer._format_prompt(context, "贵州茅台", news_context=None)

        self.assertIn("多头排列 MA5>MA10>MA20", prompt)
        self.assertIn("财报披露前波动可能放大", prompt)
        self.assertNotIn("空头排列，持续下跌\n", prompt)
        self.assertNotIn("空头排列，持续下跌", prompt)
        self.assertIn("已剔除与多头主判断直接冲突的空头结构理由", prompt)
        self.assertIn("已剔除与多头主判断直接冲突的空头结构风险表述", prompt)

    def test_format_prompt_removes_bullish_reasons_when_final_trend_is_weak_bearish(self) -> None:
        with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
            analyzer = GeminiAnalyzer(
                skill_instructions="### 技能 1: 缠论\n- 关注中枢与背驰",
                default_skill_policy="",
                use_legacy_default_prompt=False,
            )

        context = {
            "code": "300750",
            "stock_name": "宁德时代",
            "date": "2026-04-28",
            "today": {"close": 178.5, "ma5": 176.0, "ma10": 180.2, "ma20": 179.9},
            "trend_analysis": {
                "trend_status": "弱势空头",
                "ma_alignment": "弱势空头，MA5<MA10 但 MA10≥MA20",
                "trend_strength": 43,
                "bias_ma5": 1.4,
                "bias_ma10": -0.9,
                "volume_status": "平量",
                "volume_trend": "量能一般",
                "buy_signal": "观察",
                "signal_score": 45,
                "signal_reasons": ["弱势多头修复", "多头排列，持续上涨", "事件催化存在但技术待确认"],
                "risk_factors": ["MA10 压制仍在"],
            },
        }

        prompt = analyzer._format_prompt(
            context,
            "宁德时代",
            news_context="2026-04-27 新产品发布，市场情绪回暖。",
        )

        self.assertIn("弱势空头，MA5<MA10 但 MA10≥MA20", prompt)
        self.assertNotIn("弱势多头修复", prompt)
        self.assertNotIn("多头排列，持续上涨", prompt)
        self.assertIn("事件催化存在但技术待确认", prompt)
        self.assertIn("已剔除与空头主判断直接冲突的看多结构理由", prompt)

    def test_sanitize_trend_analysis_for_prompt_returns_derived_copy_only(self) -> None:
        original = {
            "trend_status": "空头排列",
            "ma_alignment": "空头排列 MA5<MA10<MA20",
            "signal_reasons": ["多头排列，持续上涨", "事件催化存在但技术待确认"],
            "risk_factors": ["跌破MA20，趋势承压"],
        }

        sanitized = _sanitize_trend_analysis_for_prompt(original, volume_change_ratio=12.4)

        self.assertEqual(
            original["signal_reasons"],
            ["多头排列，持续上涨", "事件催化存在但技术待确认"],
        )
        self.assertNotIn("prompt_consistency_notes", original)
        self.assertNotIn("prompt_trend_direction", original)
        self.assertNotIn("多头排列，持续上涨", sanitized["signal_reasons"])
        self.assertEqual(sanitized["prompt_trend_direction"], "bearish")


if __name__ == "__main__":
    unittest.main()
