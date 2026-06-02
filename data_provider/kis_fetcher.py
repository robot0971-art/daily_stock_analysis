# -*- coding: utf-8 -*-
"""Korea Investment & Securities quote-only data fetcher.

This fetcher intentionally implements only domestic stock quotation endpoints.
It does not call account, balance, or order APIs.
"""

from __future__ import annotations

import logging
import os
import time
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import requests

from .base import BaseFetcher, DataFetchError, STANDARD_COLUMNS
from .realtime_types import RealtimeSource, UnifiedRealtimeQuote, safe_float, safe_int

logger = logging.getLogger(__name__)

_REAL_BASE_URL = "https://openapi.koreainvestment.com:9443"
_PAPER_BASE_URL = "https://openapivts.koreainvestment.com:29443"


def is_kr_stock_code(stock_code: str) -> bool:
    code = (stock_code or "").strip().upper()
    if "." in code:
        base, suffix = code.rsplit(".", 1)
        return suffix in {"KS", "KQ"} and base.isdigit() and len(base) == 6
    if code.startswith(("KR", "KS", "KQ")) and code[2:].isdigit() and len(code[2:]) == 6:
        return True
    return code.isdigit() and len(code) == 6


def to_kis_symbol(stock_code: str) -> str:
    code = (stock_code or "").strip().upper()
    if "." in code:
        base, suffix = code.rsplit(".", 1)
        if suffix in {"KS", "KQ"} and base.isdigit() and len(base) == 6:
            return base
    if code.startswith(("KR", "KS", "KQ")) and code[2:].isdigit() and len(code[2:]) == 6:
        return code[2:]
    if code.isdigit() and len(code) == 6:
        return code
    raise DataFetchError(f"KIS only supports Korean 6-digit stock codes: {stock_code}")


class KisFetcher(BaseFetcher):
    """KIS Open API fetcher for Korean domestic stock quotations."""

    name = "KisFetcher"
    priority = int(os.getenv("KIS_PRIORITY", "0"))

    def __init__(self) -> None:
        self.app_key = (os.getenv("KIS_APP_KEY") or "").strip()
        self.app_secret = (os.getenv("KIS_APP_SECRET") or "").strip()
        self.env = (os.getenv("KIS_ENV") or "real").strip().lower()
        configured_base = (os.getenv("KIS_API_BASE_URL") or "").strip().rstrip("/")
        self.base_url = configured_base or (_PAPER_BASE_URL if self.env in {"paper", "mock", "vts"} else _REAL_BASE_URL)
        self.timeout = float(os.getenv("KIS_TIMEOUT_SECONDS", "10"))
        self._access_token: Optional[str] = None
        self._token_expires_at = 0.0
        self._token_cache_path = Path(os.getenv("KIS_TOKEN_CACHE_PATH", ".kis_token_cache.json"))

    def is_available_for(self, capability: str = "") -> bool:
        return bool(self.app_key and self.app_secret)

    def _get_access_token(self) -> str:
        now = time.time()
        if self._access_token and now < self._token_expires_at - 60:
            return self._access_token

        cached = self._load_cached_token(now)
        if cached:
            return cached

        try:
            response = requests.post(
                f"{self.base_url}/oauth2/tokenP",
                headers={"content-type": "application/json; charset=utf-8"},
                json={
                    "grant_type": "client_credentials",
                    "appkey": self.app_key,
                    "appsecret": self.app_secret,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise DataFetchError(f"KIS access token request failed: {exc}") from exc

        token = data.get("access_token")
        if not token:
            raise DataFetchError(f"KIS access token missing: {data.get('msg1') or data.get('message') or 'unknown'}")

        expires_in = safe_int(data.get("expires_in"), 24 * 60 * 60) or (24 * 60 * 60)
        self._access_token = str(token)
        self._token_expires_at = now + max(60, expires_in)
        self._save_cached_token()
        return self._access_token

    def _cache_key(self) -> str:
        raw = f"{self.base_url}|{self.app_key}|{self.app_secret}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _load_cached_token(self, now: float) -> Optional[str]:
        try:
            if not self._token_cache_path.exists():
                return None
            data = json.loads(self._token_cache_path.read_text(encoding="utf-8"))
            item = data.get(self._cache_key()) if isinstance(data, dict) else None
            if not isinstance(item, dict):
                return None
            token = item.get("access_token")
            expires_at = float(item.get("expires_at") or 0)
            if token and now < expires_at - 60:
                self._access_token = str(token)
                self._token_expires_at = expires_at
                return self._access_token
        except Exception as exc:
            logger.debug("KIS token cache read failed: %s", exc)
        return None

    def _save_cached_token(self) -> None:
        if not self._access_token:
            return
        try:
            data: Dict[str, Any] = {}
            if self._token_cache_path.exists():
                loaded = json.loads(self._token_cache_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    data = loaded
            data[self._cache_key()] = {
                "access_token": self._access_token,
                "expires_at": self._token_expires_at,
            }
            self._token_cache_path.write_text(json.dumps(data), encoding="utf-8")
        except Exception as exc:
            logger.debug("KIS token cache write failed: %s", exc)

    def _headers(self, tr_id: str) -> Dict[str, str]:
        return {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self._get_access_token()}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": tr_id,
            "custtype": "P",
        }

    def _get(self, path: str, tr_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.get(
                f"{self.base_url}{path}",
                headers=self._headers(tr_id),
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise DataFetchError(f"KIS request failed: {path}: {exc}") from exc

        if str(data.get("rt_cd", "")) not in {"", "0"}:
            raise DataFetchError(f"KIS API error: {data.get('msg1') or data.get('msg_cd') or 'unknown'}")
        return data

    def get_realtime_quote(self, stock_code: str) -> Optional[UnifiedRealtimeQuote]:
        if not is_kr_stock_code(stock_code):
            return None

        symbol = to_kis_symbol(stock_code)
        data = self._get(
            "/uapi/domestic-stock/v1/quotations/inquire-price",
            "FHKST01010100",
            {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": symbol},
        )
        output = data.get("output") or {}
        if not isinstance(output, dict):
            return None

        return UnifiedRealtimeQuote(
            code=symbol,
            name=str(output.get("hts_kor_isnm") or ""),
            source=RealtimeSource.KIS,
            price=safe_float(output.get("stck_prpr")),
            change_pct=safe_float(output.get("prdy_ctrt")),
            change_amount=safe_float(output.get("prdy_vrss")),
            volume=safe_int(output.get("acml_vol")),
            amount=safe_float(output.get("acml_tr_pbmn")),
            volume_ratio=safe_float(output.get("vol_tnrt")),
            turnover_rate=safe_float(output.get("hts_avls")),
            open_price=safe_float(output.get("stck_oprc")),
            high=safe_float(output.get("stck_hgpr")),
            low=safe_float(output.get("stck_lwpr")),
            pre_close=safe_float(output.get("stck_sdpr")),
            pe_ratio=safe_float(output.get("per")),
            pb_ratio=safe_float(output.get("pbr")),
            total_mv=safe_float(output.get("hts_avls")),
        )

    def _fetch_raw_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        if not is_kr_stock_code(stock_code):
            raise DataFetchError(f"KIS only supports Korean stocks: {stock_code}")

        data = self._get(
            "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            "FHKST03010100",
            {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": to_kis_symbol(stock_code),
                "FID_INPUT_DATE_1": start_date.replace("-", ""),
                "FID_INPUT_DATE_2": end_date.replace("-", ""),
                "FID_PERIOD_DIV_CODE": "D",
                "FID_ORG_ADJ_PRC": "0",
            },
        )
        rows = data.get("output2") or []
        if not isinstance(rows, list) or not rows:
            raise DataFetchError(f"KIS returned no daily data for {stock_code}")
        return pd.DataFrame(rows)

    def _normalize_data(self, df: pd.DataFrame, stock_code: str) -> pd.DataFrame:
        if df is None or df.empty:
            raise DataFetchError(f"KIS returned empty daily data for {stock_code}")

        normalized = pd.DataFrame(
            {
                "date": pd.to_datetime(df.get("stck_bsop_date"), format="%Y%m%d", errors="coerce"),
                "open": pd.to_numeric(df.get("stck_oprc"), errors="coerce"),
                "high": pd.to_numeric(df.get("stck_hgpr"), errors="coerce"),
                "low": pd.to_numeric(df.get("stck_lwpr"), errors="coerce"),
                "close": pd.to_numeric(df.get("stck_clpr"), errors="coerce"),
                "volume": pd.to_numeric(df.get("acml_vol"), errors="coerce"),
                "amount": pd.to_numeric(df.get("acml_tr_pbmn"), errors="coerce"),
                "pct_chg": pd.to_numeric(df.get("prdy_ctrt"), errors="coerce"),
            }
        )
        normalized = normalized.dropna(subset=["date", "close"]).sort_values("date").reset_index(drop=True)
        for col in STANDARD_COLUMNS:
            if col not in normalized.columns:
                normalized[col] = None
        return normalized[STANDARD_COLUMNS]
