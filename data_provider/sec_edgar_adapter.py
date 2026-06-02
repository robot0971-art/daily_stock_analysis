# -*- coding: utf-8 -*-
"""SEC EDGAR public data adapter for US stocks.

Uses the official data.sec.gov JSON APIs, which do not require API keys.
Only public submissions and XBRL company facts are read.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

_SEC_BASE_URL = "https://data.sec.gov"
_SEC_ARCHIVES_BASE_URL = "https://www.sec.gov/Archives/edgar/data"
_TICKER_CIK_URL = "https://www.sec.gov/files/company_tickers.json"
_DEFAULT_USER_AGENT = "daily-stock-analysis/1.0 contact@example.com"
_CACHE_TTL_SECONDS = 24 * 60 * 60


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result:
        return None
    return result


def _latest_fact_value(facts: Dict[str, Any], concept: str, unit: str = "USD") -> Optional[Dict[str, Any]]:
    concept_data = facts.get("us-gaap", {}).get(concept, {})
    unit_items = concept_data.get("units", {}).get(unit, [])
    if not isinstance(unit_items, list):
        return None
    candidates = [
        item for item in unit_items
        if isinstance(item, dict) and item.get("val") is not None and item.get("fy") is not None
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda item: (str(item.get("end") or ""), str(item.get("filed") or "")), reverse=True)
    item = candidates[0]
    return {
        "value": _safe_float(item.get("val")),
        "fy": item.get("fy"),
        "fp": item.get("fp"),
        "form": item.get("form"),
        "filed": item.get("filed"),
        "end": item.get("end"),
        "accn": item.get("accn"),
    }


class SecEdgarAdapter:
    """Fetch recent SEC filings and XBRL facts for US tickers."""

    def __init__(self) -> None:
        self.user_agent = (os.getenv("SEC_USER_AGENT") or _DEFAULT_USER_AGENT).strip()
        self.timeout = float(os.getenv("SEC_TIMEOUT_SECONDS", "10"))
        self.cache_path = Path(os.getenv("SEC_TICKER_CIK_CACHE_PATH", ".sec_ticker_cik_cache.json"))
        self._ticker_map: Optional[Dict[str, str]] = None

    def get_sec_bundle(self, ticker: str, *, recent_limit: int = 8) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "status": "not_supported",
            "filings": [],
            "companyfacts": {},
            "source_chain": [],
            "errors": [],
        }
        symbol = self._normalize_ticker(ticker)
        if not symbol:
            result["errors"].append("empty_ticker")
            return result

        try:
            cik = self.get_cik_for_ticker(symbol)
        except Exception as exc:
            result["errors"].append(f"cik_lookup:{type(exc).__name__}:{exc}")
            return result
        if not cik:
            result["errors"].append("cik_not_found")
            return result

        padded_cik = cik.zfill(10)
        try:
            submissions = self._get_json(f"{_SEC_BASE_URL}/submissions/CIK{padded_cik}.json")
            result["filings"] = self._parse_recent_filings(submissions, cik, recent_limit)
            result["source_chain"].append("sec.submissions")
        except Exception as exc:
            result["errors"].append(f"submissions:{type(exc).__name__}:{exc}")

        try:
            facts = self._get_json(f"{_SEC_BASE_URL}/api/xbrl/companyfacts/CIK{padded_cik}.json")
            result["companyfacts"] = self._parse_companyfacts(facts)
            result["source_chain"].append("sec.companyfacts")
        except Exception as exc:
            result["errors"].append(f"companyfacts:{type(exc).__name__}:{exc}")

        if result["filings"] or result["companyfacts"]:
            result["status"] = "ok" if result["filings"] and result["companyfacts"] else "partial"
        elif result["errors"]:
            result["status"] = "failed"
        return result

    def get_cik_for_ticker(self, ticker: str) -> Optional[str]:
        symbol = self._normalize_ticker(ticker)
        if not symbol:
            return None
        ticker_map = self._load_ticker_map()
        return ticker_map.get(symbol)

    def _normalize_ticker(self, ticker: str) -> str:
        symbol = (ticker or "").strip().upper()
        if symbol.endswith(".US"):
            symbol = symbol[:-3]
        return symbol.replace(".", "-")

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "",
        }

    def _get_json(self, url: str) -> Dict[str, Any]:
        headers = self._headers()
        headers.pop("Host", None)
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("SEC response is not a JSON object")
        return data

    def _load_ticker_map(self) -> Dict[str, str]:
        if self._ticker_map is not None:
            return self._ticker_map

        cached = self._read_ticker_cache()
        if cached:
            self._ticker_map = cached
            return cached

        data = self._get_json(_TICKER_CIK_URL)
        mapping: Dict[str, str] = {}
        for item in data.values():
            if not isinstance(item, dict):
                continue
            ticker = str(item.get("ticker") or "").upper()
            cik = item.get("cik_str")
            if ticker and cik is not None:
                mapping[ticker] = str(cik)

        self._ticker_map = mapping
        self._write_ticker_cache(mapping)
        return mapping

    def _read_ticker_cache(self) -> Optional[Dict[str, str]]:
        try:
            if not self.cache_path.exists():
                return None
            payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
            if time.time() - float(payload.get("ts", 0)) > _CACHE_TTL_SECONDS:
                return None
            mapping = payload.get("mapping")
            if isinstance(mapping, dict):
                return {str(k).upper(): str(v) for k, v in mapping.items()}
        except Exception as exc:
            logger.debug("SEC ticker cache read failed: %s", exc)
        return None

    def _write_ticker_cache(self, mapping: Dict[str, str]) -> None:
        try:
            payload = {"ts": time.time(), "mapping": mapping}
            self.cache_path.write_text(json.dumps(payload), encoding="utf-8")
        except Exception as exc:
            logger.debug("SEC ticker cache write failed: %s", exc)

    def _parse_recent_filings(self, submissions: Dict[str, Any], cik: str, limit: int) -> List[Dict[str, Any]]:
        recent = submissions.get("filings", {}).get("recent", {})
        if not isinstance(recent, dict):
            return []
        forms = recent.get("form") or []
        accession_numbers = recent.get("accessionNumber") or []
        filing_dates = recent.get("filingDate") or []
        report_dates = recent.get("reportDate") or []
        primary_docs = recent.get("primaryDocument") or []
        descriptions = recent.get("primaryDocDescription") or []
        accepted = recent.get("acceptanceDateTime") or []

        rows: List[Dict[str, Any]] = []
        wanted_forms = {"10-K", "10-Q", "8-K", "20-F", "40-F", "6-K"}
        for idx, form in enumerate(forms):
            form_name = str(form or "")
            if form_name not in wanted_forms:
                continue
            accn = self._pick(accession_numbers, idx)
            primary_doc = self._pick(primary_docs, idx)
            accession_path = str(accn or "").replace("-", "")
            url = None
            if accn and primary_doc:
                url = f"{_SEC_ARCHIVES_BASE_URL}/{int(cik)}/{accession_path}/{primary_doc}"
            rows.append({
                "form": form_name,
                "filing_date": self._pick(filing_dates, idx),
                "report_date": self._pick(report_dates, idx),
                "accepted_at": self._pick(accepted, idx),
                "accession_number": accn,
                "description": self._pick(descriptions, idx),
                "url": url,
            })
            if len(rows) >= limit:
                break
        return rows

    def _parse_companyfacts(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        facts = payload.get("facts") or {}
        parsed = {
            "entity_name": payload.get("entityName"),
            "cik": payload.get("cik"),
            "revenue": _latest_fact_value(facts, "Revenues") or _latest_fact_value(facts, "RevenueFromContractWithCustomerExcludingAssessedTax"),
            "net_income": _latest_fact_value(facts, "NetIncomeLoss"),
            "operating_cash_flow": _latest_fact_value(facts, "NetCashProvidedByUsedInOperatingActivities"),
            "assets": _latest_fact_value(facts, "Assets"),
            "liabilities": _latest_fact_value(facts, "Liabilities"),
            "equity": _latest_fact_value(facts, "StockholdersEquity"),
            "shares": _latest_fact_value(facts, "CommonStocksIncludingAdditionalPaidInCapital", "shares"),
        }
        return {key: value for key, value in parsed.items() if value is not None}

    @staticmethod
    def _pick(values: Any, idx: int) -> Any:
        if isinstance(values, list) and idx < len(values):
            return values[idx]
        return None
