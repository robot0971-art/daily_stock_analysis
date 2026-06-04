# -*- coding: utf-8 -*-
"""
Market context detection for LLM prompts.

Detects the market (KR, US, HK, CN) from a stock code and returns
market-specific role descriptions so prompts are not hardcoded to a
single market.

Fixes: https://github.com/ZhuLinsen/daily_stock_analysis/issues/644
"""

import re
from typing import Optional

KNOWN_BARE_KR_CODES = {"000660", "005930"}


def detect_market(stock_code: Optional[str]) -> str:
    """Detect market from stock code.

    Returns:
        One of 'kr', 'us', 'hk', 'cn', or 'kr' as fallback.
    """
    if not stock_code:
        return "cn"

    code = stock_code.strip().upper()

    if code.endswith((".KS", ".KQ")):
        return "kr"
    if code.startswith(("KR", "KS", "KQ")) and code[2:].isdigit() and len(code[2:]) == 6:
        return "kr"
    if code in KNOWN_BARE_KR_CODES:
        return "kr"

    # HK stocks: HK00700, 00700.HK, or 5-digit pure numbers
    if code.startswith("HK") or code.endswith(".HK"):
        return "hk"
    lower = code.lower()
    if lower.endswith(".hk"):
        return "hk"
    # 5-digit pure numbers are HK (A-shares are 6-digit)
    if code.isdigit() and len(code) == 5:
        return "hk"

    # US stocks: 1-5 uppercase letters (AAPL, TSLA, GOOGL)
    # Also handles suffixed forms like BRK.B
    if re.match(r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$', code):
        return "us"

    return "cn"


# -- Market-specific role descriptions --

_MARKET_ROLES = {
    "cn": {
        "ko": "China A-shares",
        "en": "China A-shares",
    },
    "hk": {
        "ko": "Hong Kong stock",
        "en": "Hong Kong stock",
    },
    "us": {
        "ko": "US stock",
        "en": "US stock",
    },
    "kr": {
        "ko": "Korean stock",
        "en": "Korean stock",
    },
}

_MARKET_GUIDELINES = {
    "cn": {
        "ko": (
            "- This analysis covers a **China A-share** (listed on Shanghai/Shenzhen exchanges).\n"
            "- Consider A-share-specific rules: daily price limits (±10%/±20%/±30%), T+1 settlement, and PRC policy factors."
        ),
        "en": (
            "- This analysis covers a **China A-share** (listed on Shanghai/Shenzhen exchanges).\n"
            "- Consider A-share-specific rules: daily price limits (±10%/±20%/±30%), T+1 settlement, and PRC policy factors."
        ),
    },
    "hk": {
        "ko": (
            "- This analysis covers a **Hong Kong stock** (listed on HKEX).\n"
            "- HK stocks have no daily price limits, allow T+0 trading. Consider HKD FX, Southbound/Northbound flows, and HKEX-specific rules."
        ),
        "en": (
            "- This analysis covers a **Hong Kong stock** (listed on HKEX).\n"
            "- HK stocks have no daily price limits, allow T+0 trading. Consider HKD FX, Southbound/Northbound flows, and HKEX-specific rules."
        ),
    },
    "us": {
        "ko": (
            "- This analysis covers a **US stock** (listed on NYSE/NASDAQ).\n"
            "- US stocks have no daily price limits (but have circuit breakers), allow T+0 and pre/after-market trading. Consider USD FX, Fed policy, and SEC regulations."
        ),
        "en": (
            "- This analysis covers a **US stock** (listed on NYSE/NASDAQ).\n"
            "- US stocks have no daily price limits (but have circuit breakers), allow T+0 and pre/after-market trading. Consider USD FX, Fed policy, and SEC regulations."
        ),
    },
    "kr": {
        "ko": (
            "- This analysis covers a **Korean stock** listed on KRX/KOSDAQ.\n"
            "- Consider KRW FX, Bank of Korea policy, export cycles, company disclosures, and foreign investor flow. Do not apply China A-share price-limit or T+1 assumptions."
        ),
        "en": (
            "- This analysis covers a **Korean stock** listed on KRX/KOSDAQ.\n"
            "- Consider KRW FX, Bank of Korea policy, export cycles, company disclosures, and foreign investor flow. Do not apply China A-share price-limit or T+1 assumptions."
        ),
    },
}


def get_market_role(stock_code: Optional[str], lang: str = "ko") -> str:
    """Return market-specific role description for LLM prompt.

    Args:
        stock_code: The stock code being analyzed.
        lang: 'en' or 'ko'.

    Returns:
        Role string like 'China A-shares' or 'US stock investment analysis'.
    """
    market = detect_market(stock_code)
    lang_key = "en" if lang == "en" else "ko"
    return _MARKET_ROLES.get(market, _MARKET_ROLES["cn"])[lang_key]


def get_market_guidelines(stock_code: Optional[str], lang: str = "ko") -> str:
    """Return market-specific analysis guidelines for LLM prompt.

    Args:
        stock_code: The stock code being analyzed.
        lang: 'en' or 'ko'.

    Returns:
        Multi-line string with market-specific guidelines.
    """
    market = detect_market(stock_code)
    lang_key = "en" if lang == "en" else "ko"
    return _MARKET_GUIDELINES.get(market, _MARKET_GUIDELINES["cn"])[lang_key]
