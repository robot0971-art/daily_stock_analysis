# -*- coding: utf-8 -*-
"""Helpers for report output language selection and localization."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

SUPPORTED_REPORT_LANGUAGES = ("ko", "en", "zh")

_REPORT_LANGUAGE_ALIASES = {
    "english": "en",
    "en-us": "en",
    "en_us": "en",
    "en-gb": "en",
    "en_gb": "en",
    "kr": "ko",
    "ko-kr": "ko",
    "ko_kr": "ko",
    "korean": "ko",
    "cn": "zh",
    "zh-cn": "zh",
    "zh_cn": "zh",
    "chinese": "zh",
}

_OPERATION_ADVICE_CANONICAL_MAP = {
    "강력매수": "strong_buy",
    "强烈买入": "strong_buy",
    "strong buy": "strong_buy",
    "strong_buy": "strong_buy",
    "매수": "buy",
    "买入": "buy",
    "加仓": "buy",
    "buy": "buy",
    "비중 확대": "buy",
    "accumulate": "buy",
    "add position": "buy",
    "보유": "hold",
    "持有": "hold",
    "持有观察": "hold",
    "세탁관찰": "hold",
    "관찰": "hold",
    "hold": "hold",
    "관망": "watch",
    "观望": "watch",
    "watch": "watch",
    "wait": "watch",
    "wait and see": "watch",
    "비중 축소": "reduce",
    "减仓": "reduce",
    "reduce": "reduce",
    "trim": "reduce",
    "매도": "sell",
    "卖出": "sell",
    "sell": "sell",
    "강력매도": "strong_sell",
    "强烈卖出": "strong_sell",
    "strong sell": "strong_sell",
    "strong_sell": "strong_sell",
}

_OPERATION_ADVICE_TRANSLATIONS = {
    "strong_buy": {"en": "Strong Buy"},
    "buy": {"en": "Buy"},
    "hold": {"en": "Hold"},
    "watch": {"en": "Watch"},
    "reduce": {"en": "Reduce"},
    "sell": {"en": "Sell"},
    "strong_sell": {"en": "Strong Sell"},
}

_TREND_PREDICTION_CANONICAL_MAP = {
    "강한하락세": "strong_bearish",
    "강력낙관": "strong_bullish",
    "强烈看多": "strong_bullish",
    "strong bullish": "strong_bullish",
    "very bullish": "strong_bullish",
    "강한상승세": "strong_bullish",
    "상승세정렬": "bullish",
    "看多": "bullish",
    "多头排列": "bullish",
    "强势多头": "bullish",
    "하락세정렬": "bearish",
    "약한상승세": "bullish",
    "약한하락세": "bearish",
    "낙관": "bullish",
    "횡보": "sideways",
    "震荡": "sideways",
    "震荡观望": "sideways",
    "bullish": "bullish",
    "uptrend": "bullish",
    "흔들림": "sideways",
    "neutral": "sideways",
    "sideways": "sideways",
    "range-bound": "sideways",
    "비관": "bearish",
    "看空": "bearish",
    "bearish": "bearish",
    "downtrend": "bearish",
    "강력비관": "strong_bearish",
    "强烈看空": "strong_bearish",
    "strong bearish": "strong_bearish",
    "very bearish": "strong_bearish",
}

_TREND_PREDICTION_TRANSLATIONS = {
    "strong_bullish": {"en": "Strong Bullish"},
    "bullish": {"en": "Bullish"},
    "sideways": {"en": "Sideways"},
    "bearish": {"en": "Bearish"},
    "strong_bearish": {"en": "Strong Bearish"},
}

_CONFIDENCE_LEVEL_CANONICAL_MAP = {
    "고": "high",
    "high": "high",
    "중": "medium",
    "medium": "medium",
    "med": "medium",
    "저": "low",
    "low": "low",
}

_CONFIDENCE_LEVEL_TRANSLATIONS = {
    "high": {"en": "High"},
    "medium": {"en": "Medium"},
    "low": {"en": "Low"},
}

_CHIP_HEALTH_CANONICAL_MAP = {
    "건전": "healthy",
    "healthy": "healthy",
    "일반": "average",
    "average": "average",
    "경계": "caution",
    "caution": "caution",
}

_CHIP_HEALTH_TRANSLATIONS = {
    "healthy": {"en": "Healthy"},
    "average": {"en": "Average"},
    "caution": {"en": "Caution"},
}

_BIAS_STATUS_CANONICAL_MAP = {
    "안전": "safe",
    "safe": "safe",
    "警戒": "caution",
    "경계": "caution",
    "caution": "caution",
    "危险": "danger",
    "위험": "danger",
    "risk": "danger",
    "danger": "danger",
}

_BIAS_STATUS_TRANSLATIONS = {
    "safe": {"en": "Safe"},
    "caution": {"en": "Caution"},
    "danger": {"en": "Danger"},
}

_PLACEHOLDER_BY_LANGUAGE = {
    "en": "TBD",
}

_UNKNOWN_BY_LANGUAGE = {
    "en": "Unknown",
}

_NO_DATA_BY_LANGUAGE = {
    "en": "Data unavailable",
}

_CHIP_UNAVAILABLE_BY_LANGUAGE = {
    "en": "Chip distribution is disabled or temporarily unavailable; chip signals were not used.",
}

_CHIP_PLACEHOLDER_EXACT = {
    "",
    "n/a",
    "na",
    "none",
    "null",
    "unknown",
    "tbd",
    "데이터누락",
    "알수없음",
    "없음",
    "추가예정",
    "数据缺失",
    "数据缺失，无法判断",
    "未知",
    "待补充",
}

_CHIP_PLACEHOLDER_HINTS = (
    "데이터누락",
    "판단불가",
    "data unavailable",
    "unavailable",
    "not available",
    "missing",
    "not supported",
    "无法判断",
)

_CHIP_METRIC_KEYS = ("profit_ratio", "avg_cost", "concentration")
_CHIP_UNAVAILABLE_REASON_KEYS = (
    "chip_unavailable_reason",
    "unavailable_reason",
    "chip_unavailable",
)

_GENERIC_STOCK_NAME_BY_LANGUAGE = {
    "en": "Unnamed Stock",
}

_REPORT_LABELS: Dict[str, Dict[str, str]] = {
    "en": {
        "dashboard_title": "Decision Dashboard",
        "brief_title": "Decision Brief",
        "analyzed_prefix": "Analyzed",
        "stock_unit": "stocks",
        "stock_unit_compact": "stocks",
        "buy_label": "Buy",
        "watch_label": "Watch",
        "sell_label": "Sell",
        "summary_heading": "Summary",
        "info_heading": "Key Updates",
        "sentiment_summary_label": "Sentiment",
        "earnings_outlook_label": "Earnings Outlook",
        "risk_alerts_label": "Risk Alerts",
        "evidence_heading": "Evidence",
        "counter_evidence_heading": "Counter Evidence",
        "confidence_heading": "Confidence",
        "confidence_reason_label": "Confidence Rationale",
        "data_limitations_heading": "Data Limitations",
        "thesis_tracking_heading": "Changes Since Previous Analysis",
        "thesis_status_label": "Thesis Status",
        "current_thesis_label": "Current Thesis",
        "previous_thesis_label": "Previous Thesis",
        "key_changes_label": "Key Changes",
        "evidence_graph_heading": "Evidence Graph",
        "evidence_graph_summary_label": "Graph Summary",
        "stale_evidence_label": "Stale/Limited Nodes",
        "risk_engine_heading": "Risk Engine",
        "risk_level_label": "Risk Level",
        "risk_score_label": "Risk Score",
        "volatility_label": "Annualized Volatility",
        "max_drawdown_label": "Max Drawdown",
        "position_caution_label": "Position Caution",
        "positive_catalysts_label": "Positive Catalysts",
        "latest_news_label": "Latest News",
        "core_conclusion_heading": "Core Conclusion",
        "one_sentence_label": "One-line Decision",
        "time_sensitivity_label": "Time Sensitivity",
        "default_time_sensitivity": "This week",
        "position_status_label": "Position",
        "action_advice_label": "Action",
        "no_position_label": "No Position",
        "has_position_label": "Holding",
        "continue_holding": "Continue holding",
        "market_snapshot_heading": "Market Snapshot",
        "close_label": "Close",
        "prev_close_label": "Prev Close",
        "open_label": "Open",
        "high_label": "High",
        "low_label": "Low",
        "change_pct_label": "Change %",
        "change_amount_label": "Change",
        "amplitude_label": "Amplitude",
        "volume_label": "Volume",
        "amount_label": "Turnover",
        "current_price_label": "Price",
        "volume_ratio_label": "Volume Ratio",
        "turnover_rate_label": "Turnover Rate",
        "source_label": "Source",
        "data_perspective_heading": "Data View",
        "ma_alignment_label": "MA Alignment",
        "bullish_alignment_label": "Bullish Alignment",
        "yes_label": "Yes",
        "no_label": "No",
        "trend_strength_label": "Trend Strength",
        "price_metrics_label": "Price Metrics",
        "ma5_label": "MA5",
        "ma10_label": "MA10",
        "ma20_label": "MA20",
        "bias_ma5_label": "Bias (MA5)",
        "support_level_label": "Support",
        "resistance_level_label": "Resistance",
        "chip_label": "Chip Structure",
        "battle_plan_heading": "Battle Plan",
        "ideal_buy_label": "Ideal Entry",
        "secondary_buy_label": "Secondary Entry",
        "stop_loss_label": "Stop Loss",
        "take_profit_label": "Target",
        "suggested_position_label": "Position Size",
        "entry_plan_label": "Entry Plan",
        "risk_control_label": "Risk Control",
        "checklist_heading": "Checklist",
        "failed_checks_heading": "Failed Checks",
        "history_compare_heading": "Historical Signal Comparison",
        "time_label": "Time",
        "score_label": "Score",
        "advice_label": "Advice",
        "trend_label": "Trend",
        "generated_at_label": "Generated At",
        "report_time_label": "Generated",
        "no_results": "No analysis results",
        "report_title": "Stock Analysis Report",
        "avg_score_label": "Avg Score",
        "action_points_heading": "Action Levels",
        "position_advice_heading": "Position Advice",
        "analysis_model_label": "Model",
        "not_investment_advice": "AI-generated content for reference only. Not investment advice.",
        "details_report_hint": "See detailed report:",
        "financial_summary_heading": "Financial Summary",
        "report_date_label": "Report Date",
        "revenue_label": "Revenue",
        "net_profit_label": "Net Profit (Parent)",
        "operating_cash_flow_label": "Operating Cash Flow",
        "roe_label": "ROE",
        "revenue_yoy_label": "Revenue YoY",
        "net_profit_yoy_label": "Net Profit YoY",
        "gross_margin_label": "Gross Margin",
        "shareholder_return_heading": "Shareholder Return",
        "ttm_cash_dividend_label": "TTM Cash Dividend / Share (Pre-tax)",
        "ttm_event_count_label": "TTM Dividend Events",
        "ttm_dividend_yield_label": "TTM Dividend Yield",
        "latest_ex_dividend_label": "Latest Ex-dividend Date",
        "related_boards_heading": "Related Boards",
        "board_name_label": "Board",
        "board_type_label": "Type",
        "board_status_label": "Status",
        "board_change_pct_label": "Change %",
        "leading_board_label": "Leading",
        "lagging_board_label": "Lagging",
    },
    "ko": {
        "dashboard_title": "의사결정 대시보드",
        "brief_title": "의사결정 요약",
        "analyzed_prefix": "분석 종목",
        "stock_unit": "개",
        "stock_unit_compact": "개",
        "summary_heading": "분석 결과 요약",
        "info_heading": "핵심 정보 요약",
        "risk_alerts_label": "리스크 알림",
        "evidence_heading": "분석 근거",
        "counter_evidence_heading": "반대 근거",
        "confidence_heading": "신뢰도",
        "confidence_reason_label": "신뢰도 판단 이유",
        "data_limitations_heading": "데이터 한계",
        "thesis_tracking_heading": "이전 분석 대비 변화",
        "thesis_status_label": "투자 가설 상태",
        "current_thesis_label": "현재 투자 가설",
        "previous_thesis_label": "이전 투자 가설",
        "key_changes_label": "핵심 변화",
        "evidence_graph_heading": "근거 연결도",
        "evidence_graph_summary_label": "근거 요약",
        "stale_evidence_label": "시효가 지난 근거",
        "risk_engine_heading": "리스크 엔진",
        "risk_level_label": "리스크 수준",
        "risk_score_label": "리스크 점수",
        "volatility_label": "연환산 변동성",
        "max_drawdown_label": "최대 낙폭",
        "position_caution_label": "포지션 주의사항",
        "positive_catalysts_label": "긍정 촉매",
        "latest_news_label": "최신 동향",
        "one_sentence_label": "한 줄 결론",
        "time_sensitivity_label": "대응 시점",
        "default_time_sensitivity": "이번 주 안",
        "position_status_label": "현재 상태",
        "action_advice_label": "대응 방법",
        "no_position_label": "미보유",
        "has_position_label": "보유 중",
        "continue_holding": "계속 보유",
        "data_perspective_heading": "데이터 관점",
        "ma_alignment_label": "이동평균 배열",
        "bullish_alignment_label": "상승 배열 여부",
        "yes_label": "예",
        "no_label": "아니오",
        "trend_strength_label": "추세 강도",
        "chip_label": "매물대",
        "battle_plan_heading": "대응 계획",
        "ideal_buy_label": "1차 매수 구간",
        "secondary_buy_label": "2차 매수 구간",
        "stop_loss_label": "손절 기준",
        "take_profit_label": "목표 구간",
        "checklist_heading": "확인 체크리스트",
        "failed_checks_heading": "미충족 항목",
        "generated_at_label": "리포트 생성 시간",
        "no_results": "분석 결과 없음",
        "avg_score_label": "평균 점수",
        "action_points_heading": "가격 대응 구간",
        "not_investment_advice": "AI가 생성한 참고용 정보이며 투자 조언이 아닙니다.",
        "details_report_hint": "상세 리포트",
        "operating_cash_flow_label": "영업현금흐름",
        "revenue_yoy_label": "매출 전년비",
        "net_profit_yoy_label": "순이익 전년비",
        "gross_margin_label": "매출총이익률",
        "shareholder_return_heading": "주주환원",
        "ttm_cash_dividend_label": "최근 12개월 주당 현금배당(세전)",
        "ttm_event_count_label": "최근 12개월 배당 횟수",
        "ttm_dividend_yield_label": "TTM 배당수익률",
        "latest_ex_dividend_label": "최근 배당락일",
    },
}

_REPORT_LABELS["zh"] = {
    "dashboard_title": "决策仪表盘",
    "brief_title": "决策简报",
    "analyzed_prefix": "分析股票",
    "stock_unit": "只",
    "stock_unit_compact": "只",
    "buy_label": "买入",
    "watch_label": "观察",
    "sell_label": "卖出",
    "summary_heading": "分析结果摘要",
    "info_heading": "核心信息摘要",
    "sentiment_summary_label": "情绪",
    "earnings_outlook_label": "盈利展望",
    "risk_alerts_label": "风险提示",
    "evidence_heading": "分析依据",
    "counter_evidence_heading": "反向依据",
    "confidence_heading": "置信度",
    "confidence_reason_label": "置信度理由",
    "data_limitations_heading": "数据局限",
    "thesis_tracking_heading": "上次分析以来的变化",
    "thesis_status_label": "投资假设状态",
    "current_thesis_label": "当前投资假设",
    "previous_thesis_label": "上次投资假设",
    "key_changes_label": "关键变化",
    "evidence_graph_heading": "依据关系图",
    "evidence_graph_summary_label": "依据摘要",
    "stale_evidence_label": "过期/受限依据",
    "risk_engine_heading": "风险引擎",
    "risk_level_label": "风险等级",
    "risk_score_label": "风险分数",
    "volatility_label": "年化波动率",
    "max_drawdown_label": "最大回撤",
    "position_caution_label": "仓位提示",
    "positive_catalysts_label": "积极催化",
    "latest_news_label": "最新动态",
    "core_conclusion_heading": "核心结论",
    "one_sentence_label": "一句话结论",
    "time_sensitivity_label": "应对时点",
    "default_time_sensitivity": "本周内",
    "position_status_label": "当前状态",
    "action_advice_label": "操作建议",
    "no_position_label": "未持仓",
    "has_position_label": "持仓中",
    "continue_holding": "继续持有",
    "market_snapshot_heading": "市场快照",
    "close_label": "收盘",
    "prev_close_label": "昨收",
    "open_label": "开盘",
    "high_label": "最高",
    "low_label": "最低",
    "change_pct_label": "涨跌幅",
    "change_amount_label": "涨跌额",
    "amplitude_label": "振幅",
    "volume_label": "成交量",
    "amount_label": "成交额",
    "current_price_label": "价格",
    "volume_ratio_label": "量比",
    "turnover_rate_label": "换手率",
    "source_label": "来源",
    "data_perspective_heading": "数据视角",
    "ma_alignment_label": "均线排列",
    "bullish_alignment_label": "多头排列",
    "yes_label": "是",
    "no_label": "否",
    "trend_strength_label": "趋势强度",
    "price_metrics_label": "价格指标",
    "ma5_label": "MA5",
    "ma10_label": "MA10",
    "ma20_label": "MA20",
    "bias_ma5_label": "偏离(MA5)",
    "support_level_label": "支撑",
    "resistance_level_label": "压力",
    "chip_label": "筹码",
    "battle_plan_heading": "作战计划",
    "ideal_buy_label": "理想买点",
    "secondary_buy_label": "次级买点",
    "stop_loss_label": "止损",
    "take_profit_label": "目标",
    "suggested_position_label": "建议仓位",
    "entry_plan_label": "入场计划",
    "risk_control_label": "风控",
    "checklist_heading": "检查清单",
    "failed_checks_heading": "未通过项",
    "history_compare_heading": "历史信号对比",
    "time_label": "时间",
    "score_label": "分数",
    "advice_label": "建议",
    "trend_label": "趋势",
    "generated_at_label": "报告生成时间",
    "report_time_label": "生成时间",
    "no_results": "暂无分析结果",
    "report_title": "股票分析报告",
    "avg_score_label": "平均分",
    "action_points_heading": "操作价位",
    "position_advice_heading": "仓位建议",
    "analysis_model_label": "分析模型",
    "not_investment_advice": "AI生成内容仅供参考，不构成投资建议。",
    "details_report_hint": "查看详细报告",
    "financial_summary_heading": "财务摘要",
    "report_date_label": "报告期",
    "revenue_label": "营业收入",
    "net_profit_label": "归母净利润",
    "operating_cash_flow_label": "经营现金流",
    "roe_label": "ROE",
    "revenue_yoy_label": "营收同比",
    "net_profit_yoy_label": "净利润同比",
    "gross_margin_label": "毛利率",
    "shareholder_return_heading": "股东回报",
    "ttm_cash_dividend_label": "近12个月每股现金分红(税前)",
    "ttm_event_count_label": "近12个月分红次数",
    "ttm_dividend_yield_label": "TTM股息率",
    "latest_ex_dividend_label": "最近除权日",
    "related_boards_heading": "相关板块",
    "board_name_label": "板块",
    "board_type_label": "类型",
    "board_status_label": "状态",
    "board_change_pct_label": "涨跌幅",
    "leading_board_label": "领涨",
    "lagging_board_label": "领跌",
}

_PLACEHOLDER_BY_LANGUAGE.update({"ko": "추가예정"})
_UNKNOWN_BY_LANGUAGE.update({"ko": "알수없음"})
_NO_DATA_BY_LANGUAGE.update({"ko": "데이터누락"})
_CHIP_UNAVAILABLE_BY_LANGUAGE.update(
    {
        "ko": "매물대 데이터가 없거나 일시적으로 사용할 수 없어 판단에 반영하지 않았습니다.",
    }
)
_GENERIC_STOCK_NAME_BY_LANGUAGE.update({"ko": "확인필요종목"})
_PLACEHOLDER_BY_LANGUAGE.update({"zh": "待补充"})
_UNKNOWN_BY_LANGUAGE.update({"zh": "未知"})
_NO_DATA_BY_LANGUAGE.update({"zh": "数据缺失"})
_CHIP_UNAVAILABLE_BY_LANGUAGE.update(
    {
        "zh": "筹码分布未启用或数据源暂不可用，未纳入筹码判断。",
    }
)
_GENERIC_STOCK_NAME_BY_LANGUAGE.update({"zh": "未知股票"})
_CHIP_PLACEHOLDER_EXACT.update(
    {"데이터누락", "데이터누락，판단불가", "추가예정", "알수없음"}
)
_CHIP_PLACEHOLDER_HINTS = _CHIP_PLACEHOLDER_HINTS + ("데이터누락", "판단불가")

for _translation_table in (
    _OPERATION_ADVICE_TRANSLATIONS,
    _TREND_PREDICTION_TRANSLATIONS,
    _CONFIDENCE_LEVEL_TRANSLATIONS,
    _CHIP_HEALTH_TRANSLATIONS,
    _BIAS_STATUS_TRANSLATIONS,
):
    for _values in _translation_table.values():
        _values.setdefault("ko", _values.get("en", ""))

_OPERATION_ADVICE_CANONICAL_MAP.update(
    {
        "강력매수": "strong_buy",
        "매수": "buy",
        "보유": "hold",
        "관망": "watch",
        "비중축소": "reduce",
        "매도": "sell",
        "강력매도": "strong_sell",
    }
)
_OPERATION_ADVICE_CANONICAL_MAP.update(
    {
        "hold and watch": "watch",
        "hold/watch": "watch",
        "hold & watch": "watch",
        "\uad00\ub9dd/\ubcf4\uc720": "watch",
    }
)
_OPERATION_ADVICE_TRANSLATIONS["strong_buy"]["ko"] = "\uac15\ub825 \ub9e4\uc218"
_OPERATION_ADVICE_TRANSLATIONS["buy"]["ko"] = "\ub9e4\uc218"
_OPERATION_ADVICE_TRANSLATIONS["hold"]["ko"] = "\ubcf4\uc720"
_OPERATION_ADVICE_TRANSLATIONS["watch"]["ko"] = "\uad00\ub9dd"
_OPERATION_ADVICE_TRANSLATIONS["reduce"]["ko"] = "\ube44\uc911 \ucd95\uc18c"
_OPERATION_ADVICE_TRANSLATIONS["sell"]["ko"] = "\ub9e4\ub3c4"
_OPERATION_ADVICE_TRANSLATIONS["strong_sell"]["ko"] = "\uac15\ub825 \ub9e4\ub3c4"
_OPERATION_ADVICE_TRANSLATIONS["strong_buy"]["zh"] = "强烈买入"
_OPERATION_ADVICE_TRANSLATIONS["buy"]["zh"] = "买入"
_OPERATION_ADVICE_TRANSLATIONS["hold"]["zh"] = "持有"
_OPERATION_ADVICE_TRANSLATIONS["watch"]["zh"] = "观望"
_OPERATION_ADVICE_TRANSLATIONS["reduce"]["zh"] = "减仓"
_OPERATION_ADVICE_TRANSLATIONS["sell"]["zh"] = "卖出"
_OPERATION_ADVICE_TRANSLATIONS["strong_sell"]["zh"] = "强烈卖出"
_TREND_PREDICTION_CANONICAL_MAP.update(
    {
        "강력낙관": "strong_bullish",
        "낙관": "bullish",
        "흔들림": "sideways",
        "비관": "bearish",
        "강력비관": "strong_bearish",
    }
)
_TREND_PREDICTION_TRANSLATIONS["strong_bullish"].update({"ko": "강력낙관", "zh": "强烈看多"})
_TREND_PREDICTION_TRANSLATIONS["bullish"].update({"ko": "낙관", "zh": "看多"})
_TREND_PREDICTION_TRANSLATIONS["sideways"].update({"ko": "흔들림", "zh": "震荡"})
_TREND_PREDICTION_TRANSLATIONS["bearish"].update({"ko": "비관", "zh": "看空"})
_TREND_PREDICTION_TRANSLATIONS["strong_bearish"].update({"ko": "강력비관", "zh": "强烈看空"})
_CONFIDENCE_LEVEL_TRANSLATIONS["high"].update({"ko": "고", "zh": "高"})
_CONFIDENCE_LEVEL_TRANSLATIONS["medium"].update({"ko": "중", "zh": "中"})
_CONFIDENCE_LEVEL_TRANSLATIONS["low"].update({"ko": "저", "zh": "低"})
_CHIP_HEALTH_TRANSLATIONS["healthy"].update({"ko": "건전", "zh": "健康"})
_CHIP_HEALTH_TRANSLATIONS["average"].update({"ko": "일반", "zh": "一般"})
_CHIP_HEALTH_TRANSLATIONS["caution"].update({"ko": "경계", "zh": "警戒"})
_BIAS_STATUS_TRANSLATIONS["safe"].update({"ko": "안전", "zh": "安全"})
_BIAS_STATUS_TRANSLATIONS["caution"].update({"ko": "경계", "zh": "警戒"})
_BIAS_STATUS_TRANSLATIONS["danger"].update({"ko": "위험", "zh": "危险"})
_CONFIDENCE_LEVEL_CANONICAL_MAP.update({"고": "high", "중": "medium", "저": "low"})
_OPERATION_ADVICE_CANONICAL_MAP.update({"洗盘观察": "hold", "观察": "hold"})

_DECISION_INTENT_NEGATIONS = (
    "없음",
    "아님",
    "no ",
    "not ",
    " never",
)

_DECISION_INTENT_NEGATION_SCOPE_BREAK_CHARS = "，,。；;:!?！？"
_DECISION_INTENT_NEGATION_CONNECTORS = (
    "제안",
    "계속",
)


def _strip_decision_negation_connectors(text: str) -> str:
    """Remove common advisory connectors between a negation token and decision word."""
    suffix = text.strip()
    changed = True
    while changed:
        changed = False
        for connector in _DECISION_INTENT_NEGATION_CONNECTORS:
            if suffix.startswith(connector):
                suffix = suffix[len(connector):].strip()
                changed = True
                break
    return suffix


def normalize_report_language(value: Optional[str], default: str = "ko") -> str:
    """Normalize report language to a supported short code."""
    candidate = (value or default).strip().lower().replace(" ", "_")
    candidate = _REPORT_LANGUAGE_ALIASES.get(candidate, candidate)
    if candidate in SUPPORTED_REPORT_LANGUAGES:
        return candidate
    return default


def is_supported_report_language_value(value: Optional[str]) -> bool:
    """Return whether the raw value is a supported language code or alias."""
    candidate = (value or "").strip().lower().replace(" ", "_")
    if not candidate:
        return False
    return candidate in SUPPORTED_REPORT_LANGUAGES or candidate in _REPORT_LANGUAGE_ALIASES


def get_report_labels(language: Optional[str]) -> Dict[str, str]:
    """Return UI copy for the selected report language with English fallback for missing keys."""
    normalized = normalize_report_language(language)
    labels = _REPORT_LABELS.get(normalized, {})
    if normalized != "en":
        en_labels = _REPORT_LABELS.get("en", {})
        merged = dict(en_labels)
        merged.update(labels)
        return merged
    return labels


def get_placeholder_text(language: Optional[str]) -> str:
    """Return placeholder text for missing localized content."""
    return _PLACEHOLDER_BY_LANGUAGE[normalize_report_language(language)]


def get_unknown_text(language: Optional[str]) -> str:
    """Return localized unknown text."""
    return _UNKNOWN_BY_LANGUAGE[normalize_report_language(language)]


def get_no_data_text(language: Optional[str]) -> str:
    """Return localized data unavailable text."""
    return _NO_DATA_BY_LANGUAGE[normalize_report_language(language)]


def get_chip_unavailable_text(language: Optional[str]) -> str:
    """Return the localized one-line chip distribution fallback text."""
    return _CHIP_UNAVAILABLE_BY_LANGUAGE[normalize_report_language(language)]


def _normalize_lookup_key(value: Any) -> str:
    return str(value or "").strip().lower().replace("_", " ").replace("-", " ")


def _iter_lookup_candidates(value: Any) -> list[str]:
    raw_text = str(value or "").strip()
    if not raw_text:
        return []

    candidates = [raw_text]
    for part in re.split(r"[/|,，、]+", raw_text):
        normalized = part.strip()
        if normalized and normalized not in candidates:
            candidates.append(normalized)
    return candidates


def _canonicalize_lookup_value(value: Any, canonical_map: Dict[str, str]) -> Optional[str]:
    for candidate in _iter_lookup_candidates(value):
        canonical = canonical_map.get(_normalize_lookup_key(candidate))
        if canonical:
            return canonical
    return None


def _first_non_negated_position(text: str, token: str) -> Optional[int]:
    if not text or not token:
        return None

    normalized_text = text.lower().strip()
    if any(ch in normalized_text for ch in "abcdefghijklmnopqrstuvwxyz"):
        matches = list(re.finditer(rf"(?<![a-z0-9_]){re.escape(token)}(?![a-z0-9_])", normalized_text))
    else:
        matches = list(re.finditer(re.escape(token), normalized_text))

    for match in matches:
        prefix = normalized_text[: match.start()]
        if any(prefix.rstrip().endswith(neg) for neg in _DECISION_INTENT_NEGATIONS):
            continue
        lookback = prefix[-12:]
        negated = False
        for neg in _DECISION_INTENT_NEGATIONS:
            if not neg:
                continue
            neg_idx = lookback.rfind(neg)
            if neg_idx < 0:
                continue
            suffix = lookback[neg_idx + len(neg):]
            if not suffix:
                negated = True
                break
            if any(ch in suffix for ch in _DECISION_INTENT_NEGATION_SCOPE_BREAK_CHARS):
                continue
            normalized_suffix = _strip_decision_negation_connectors(suffix)
            if not normalized_suffix:
                negated = True
                break
            if any(ch in normalized_suffix for ch in _DECISION_INTENT_NEGATION_SCOPE_BREAK_CHARS):
                continue
            if len(normalized_suffix) > 6 and token not in normalized_suffix:
                continue
            if normalized_suffix.startswith(token):
                negated = True
                break
        if negated:
            continue
        else:
            return match.start()
    return None


def _is_placeholder_stock_name(value: Any, code: Any = None) -> bool:
    text = str(value or "").strip()
    if not text:
        return True

    lowered = text.lower()
    if lowered in {"n/a", "na", "none", "null", "unknown"}:
        return True
    if text in {"-", "—", "알수없음", "추가예정"}:
        return True

    code_text = str(code or "").strip()
    if code_text and lowered == code_text.lower():
        return True

    return text.startswith("주식") or text.startswith("股票")


def _translate_from_map(
    value: Any,
    language: Optional[str],
    *,
    canonical_map: Dict[str, str],
    translations: Dict[str, Dict[str, str]],
) -> str:
    normalized_language = normalize_report_language(language)
    raw_text = str(value or "").strip()
    if not raw_text:
        return raw_text

    canonical = _canonicalize_lookup_value(raw_text, canonical_map)
    if canonical:
        return translations[canonical][normalized_language]
    return raw_text


def localize_operation_advice(value: Any, language: Optional[str]) -> str:
    """Translate operation advice between Chinese and English when recognized."""
    return _translate_from_map(
        value,
        language,
        canonical_map=_OPERATION_ADVICE_CANONICAL_MAP,
        translations=_OPERATION_ADVICE_TRANSLATIONS,
    )


def localize_trend_prediction(value: Any, language: Optional[str]) -> str:
    """Translate trend prediction between Chinese and English when recognized."""
    raw_text = str(value or "").strip()
    if normalize_report_language(language) == "zh" and raw_text in {"多头排列", "弱势空头"}:
        return raw_text
    return _translate_from_map(
        value,
        language,
        canonical_map=_TREND_PREDICTION_CANONICAL_MAP,
        translations=_TREND_PREDICTION_TRANSLATIONS,
    )


def localize_confidence_level(value: Any, language: Optional[str]) -> str:
    """Translate confidence level between Chinese and English when recognized."""
    return _translate_from_map(
        value,
        language,
        canonical_map=_CONFIDENCE_LEVEL_CANONICAL_MAP,
        translations=_CONFIDENCE_LEVEL_TRANSLATIONS,
    )


def localize_chip_health(value: Any, language: Optional[str]) -> str:
    """Translate chip health labels between Chinese and English when recognized."""
    return _translate_from_map(
        value,
        language,
        canonical_map=_CHIP_HEALTH_CANONICAL_MAP,
        translations=_CHIP_HEALTH_TRANSLATIONS,
    )


def is_chip_placeholder_value(value: Any) -> bool:
    """Return True for chip fields filled with empty or no-data placeholders."""
    if value is None:
        return True
    if isinstance(value, (int, float)) and value == 0:
        return True
    text = str(value).strip()
    lowered = text.lower()
    if lowered in _CHIP_PLACEHOLDER_EXACT:
        return True
    return any(hint in lowered for hint in _CHIP_PLACEHOLDER_HINTS)


def is_chip_structure_unavailable(chip_data: Any) -> bool:
    """Detect chip_structure blocks that contain only unavailable placeholders."""
    if not isinstance(chip_data, dict) or not chip_data:
        return False
    for key in _CHIP_UNAVAILABLE_REASON_KEYS:
        raw = chip_data.get(key)
        if isinstance(raw, bool):
            if raw:
                return True
            continue
        if str(raw or "").strip():
            return True
    if any(key in chip_data for key in _CHIP_METRIC_KEYS):
        return all(is_chip_placeholder_value(chip_data.get(key)) for key in _CHIP_METRIC_KEYS)
    return all(is_chip_placeholder_value(value) for value in chip_data.values())


def get_chip_unavailable_reason(value: Any, language: Optional[str]) -> str:
    """Return the explicit or default chip unavailable reason for rendering."""
    if not isinstance(value, dict) or not value:
        return ""
    for key in _CHIP_UNAVAILABLE_REASON_KEYS:
        raw = value.get(key)
        if isinstance(raw, bool):
            if raw:
                return get_chip_unavailable_text(language)
            continue
        text = str(raw or "").strip()
        if text:
            return text
    if is_chip_structure_unavailable(value):
        return get_chip_unavailable_text(language)
    return ""


def localize_bias_status(value: Any, language: Optional[str]) -> str:
    """Translate price bias status labels between Chinese and English when recognized."""
    return _translate_from_map(
        value,
        language,
        canonical_map=_BIAS_STATUS_CANONICAL_MAP,
        translations=_BIAS_STATUS_TRANSLATIONS,
    )


def get_bias_status_emoji(value: Any) -> str:
    """Return the stable alert emoji for a localized or canonical bias status."""
    canonical = _canonicalize_lookup_value(value, _BIAS_STATUS_CANONICAL_MAP)
    if canonical == "safe":
        return "✅"
    if canonical == "caution":
        return "⚠️"
    return "🚨"


def infer_decision_type_from_advice(value: Any, default: str = "hold") -> str:
    """Infer buy/hold/sell from human-readable operation advice."""
    canonical = _canonicalize_lookup_value(value, _OPERATION_ADVICE_CANONICAL_MAP)
    if canonical in {"strong_buy", "buy"}:
        return "buy"
    if canonical in {"reduce", "sell", "strong_sell"}:
        return "sell"
    if canonical in {"hold", "watch"}:
        return "hold"

    normalized_text = _normalize_lookup_key(value)
    if "不建议买入" in normalized_text:
        return "hold"
    best_position: Optional[int] = None
    best_canonical: Optional[str] = None
    for option, canonical in _OPERATION_ADVICE_CANONICAL_MAP.items():
        option_norm = _normalize_lookup_key(option)
        pos = _first_non_negated_position(normalized_text, option_norm)
        if pos is None:
            continue
        if best_position is None or pos < best_position:
            best_position = pos
            best_canonical = canonical

    if best_canonical in {"strong_buy", "buy"}:
        return "buy"
    if best_canonical in {"reduce", "sell", "strong_sell"}:
        return "sell"
    if best_canonical in {"hold", "watch"}:
        return "hold"

    return default


def get_signal_level(advice: Any, score: Any, language: Optional[str]) -> tuple[str, str, str]:
    """Return localized signal text, emoji, and stable color tag."""
    normalized_language = normalize_report_language(language)
    canonical = _canonicalize_lookup_value(advice, _OPERATION_ADVICE_CANONICAL_MAP)
    if canonical == "strong_buy":
        return (_OPERATION_ADVICE_TRANSLATIONS["strong_buy"][normalized_language], "💚", "strong_buy")
    if canonical == "buy":
        return (_OPERATION_ADVICE_TRANSLATIONS["buy"][normalized_language], "🟢", "buy")
    if canonical == "hold":
        return (_OPERATION_ADVICE_TRANSLATIONS["hold"][normalized_language], "🟡", "hold")
    if canonical == "watch":
        return (_OPERATION_ADVICE_TRANSLATIONS["watch"][normalized_language], "⚪", "watch")
    if canonical == "reduce":
        return (_OPERATION_ADVICE_TRANSLATIONS["reduce"][normalized_language], "🟠", "reduce")
    if canonical in {"sell", "strong_sell"}:
        return (_OPERATION_ADVICE_TRANSLATIONS["sell"][normalized_language], "🔴", "sell")

    try:
        numeric_score = int(float(score))
    except (TypeError, ValueError):
        numeric_score = 50

    if numeric_score >= 80:
        return (_OPERATION_ADVICE_TRANSLATIONS["strong_buy"][normalized_language], "💚", "strong_buy")
    if numeric_score >= 65:
        return (_OPERATION_ADVICE_TRANSLATIONS["buy"][normalized_language], "🟢", "buy")
    if numeric_score >= 55:
        return (_OPERATION_ADVICE_TRANSLATIONS["hold"][normalized_language], "🟡", "hold")
    if numeric_score >= 45:
        return (_OPERATION_ADVICE_TRANSLATIONS["watch"][normalized_language], "⚪", "watch")
    if numeric_score >= 35:
        return (_OPERATION_ADVICE_TRANSLATIONS["reduce"][normalized_language], "🟠", "reduce")
    return (_OPERATION_ADVICE_TRANSLATIONS["sell"][normalized_language], "🔴", "sell")


def get_localized_stock_name(value: Any, code: Any, language: Optional[str]) -> str:
    """Return a localized stock name placeholder when the original name is missing."""
    raw_text = str(value or "").strip()
    if not _is_placeholder_stock_name(raw_text, code):
        return raw_text
    return _GENERIC_STOCK_NAME_BY_LANGUAGE[normalize_report_language(language)]


def get_sentiment_label(score: int, language: Optional[str]) -> str:
    """Return localized sentiment label by score band."""
    normalized = normalize_report_language(language)
    if normalized == "en":
        if score >= 80:
            return "Very Bullish"
        if score >= 60:
            return "Bullish"
        if score >= 40:
            return "Neutral"
        if score >= 20:
            return "Bearish"
        return "Very Bearish"
    if normalized == "zh":
        if score >= 80:
            return "极度乐观"
        if score >= 60:
            return "乐观"
        if score >= 40:
            return "中性"
        if score >= 20:
            return "悲观"
        return "极度悲观"

    if score >= 80:
        return "매우 낙관적"
    if score >= 60:
        return "낙관적"
    if score >= 40:
        return "중립"
    if score >= 20:
        return "비관적"
    return "매우 비관적"
