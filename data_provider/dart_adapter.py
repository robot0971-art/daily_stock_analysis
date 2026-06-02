# -*- coding: utf-8 -*-
"""OpenDART adapter for Korean disclosure and financial statement data."""

from __future__ import annotations

import json
import logging
import os
import time
import zipfile
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

import requests

logger = logging.getLogger(__name__)

_DART_BASE_URL = "https://opendart.fss.or.kr/api"
_CACHE_TTL_SECONDS = 7 * 24 * 60 * 60


def _normalize_kr_symbol(stock_code: str) -> str:
    code = (stock_code or "").strip().upper()
    if "." in code:
        base, suffix = code.rsplit(".", 1)
        if suffix in {"KS", "KQ"} and base.isdigit() and len(base) == 6:
            return base
    if code.startswith(("KR", "KS", "KQ")) and code[2:].isdigit() and len(code[2:]) == 6:
        return code[2:]
    if code.isdigit() and len(code) == 6:
        return code
    return code


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).replace(",", "").strip()
    if not text or text in {"-", "N/A"}:
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    if result != result:
        return None
    return result


class DartAdapter:
    """Fetch Korean company disclosures and single-company financial accounts."""

    def __init__(self) -> None:
        self.api_key = (os.getenv("DART_API_KEY") or os.getenv("OPENDART_API_KEY") or "").strip()
        self.timeout = float(os.getenv("DART_TIMEOUT_SECONDS", "10"))
        self.corp_cache_path = Path(os.getenv("DART_CORP_CODE_CACHE_PATH", ".dart_corp_code_cache.json"))
        self._corp_map: Optional[Dict[str, Dict[str, str]]] = None

    def is_available(self) -> bool:
        return bool(self.api_key)

    def get_dart_bundle(self, stock_code: str, *, recent_limit: int = 8) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "status": "not_supported",
            "disclosures": [],
            "financial_report": {},
            "source_chain": [],
            "errors": [],
        }
        if not self.is_available():
            result["errors"].append("dart api key missing")
            return result

        symbol = _normalize_kr_symbol(stock_code)
        try:
            corp = self.get_corp_by_stock_code(symbol)
        except Exception as exc:
            result["errors"].append(f"corp_lookup:{type(exc).__name__}:{exc}")
            return result
        if not corp:
            result["errors"].append("corp_code_not_found")
            return result

        corp_code = corp["corp_code"]
        try:
            disclosures = self.get_recent_disclosures(corp_code, limit=recent_limit)
            result["disclosures"] = disclosures
            result["source_chain"].append("dart.list")
        except Exception as exc:
            result["errors"].append(f"list:{type(exc).__name__}:{exc}")

        try:
            financial_report = self.get_latest_financial_report(corp_code)
            result["financial_report"] = financial_report
            result["source_chain"].append("dart.fnlttSinglAcnt")
        except Exception as exc:
            result["errors"].append(f"financial:{type(exc).__name__}:{exc}")

        if result["disclosures"] or result["financial_report"]:
            result["status"] = "ok" if result["disclosures"] and result["financial_report"] else "partial"
        elif result["errors"]:
            result["status"] = "failed"
        return result

    def get_corp_by_stock_code(self, stock_code: str) -> Optional[Dict[str, str]]:
        symbol = _normalize_kr_symbol(stock_code)
        if not symbol:
            return None
        return self._load_corp_map().get(symbol)

    def get_recent_disclosures(self, corp_code: str, *, limit: int = 8) -> List[Dict[str, Any]]:
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=int(os.getenv("DART_DISCLOSURE_LOOKBACK_DAYS", "365")))).strftime("%Y%m%d")
        data = self._get_json(
            "list.json",
            {
                "corp_code": corp_code,
                "bgn_de": start_date,
                "end_de": end_date,
                "page_count": min(max(limit, 1), 100),
                "sort": "date",
                "sort_mth": "desc",
            },
        )
        rows = data.get("list") or []
        if not isinstance(rows, list):
            return []
        result: List[Dict[str, Any]] = []
        for item in rows[:limit]:
            if not isinstance(item, dict):
                continue
            rcept_no = item.get("rcept_no")
            result.append(
                {
                    "corp_code": item.get("corp_code"),
                    "corp_name": item.get("corp_name"),
                    "stock_code": item.get("stock_code"),
                    "report_name": item.get("report_nm"),
                    "received_date": item.get("rcept_dt"),
                    "report_code": rcept_no,
                    "url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}" if rcept_no else None,
                }
            )
        return result

    def get_latest_financial_report(self, corp_code: str) -> Dict[str, Any]:
        year = int(os.getenv("DART_REPORT_YEAR") or time.strftime("%Y"))
        errors: List[str] = []
        for bsns_year in (year - 1, year):
            for reprt_code in ("11011", "11014", "11012", "11013"):
                try:
                    report = self.get_financial_report(corp_code, str(bsns_year), reprt_code)
                    if report:
                        return report
                except Exception as exc:
                    errors.append(f"{bsns_year}/{reprt_code}:{exc}")
        if errors:
            raise RuntimeError("; ".join(errors[-3:]))
        return {}

    def get_financial_report(self, corp_code: str, bsns_year: str, reprt_code: str) -> Dict[str, Any]:
        data = self._get_json(
            "fnlttSinglAcnt.json",
            {
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": reprt_code,
                "fs_div": "CFS",
            },
        )
        rows = data.get("list") or []
        if not isinstance(rows, list) or not rows:
            return {}

        account_map = {
            "매출액": "revenue",
            "영업수익": "revenue",
            "영업이익": "operating_profit",
            "당기순이익": "net_profit",
            "당기순이익(손실)": "net_profit",
            "자산총계": "assets",
            "부채총계": "liabilities",
            "자본총계": "equity",
        }
        parsed: Dict[str, Any] = {
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
            "currency": "KRW",
            "source": "dart.fnlttSinglAcnt",
        }
        for row in rows:
            if not isinstance(row, dict):
                continue
            account_name = str(row.get("account_nm") or "").strip()
            key = account_map.get(account_name)
            if key and key not in parsed:
                parsed[key] = _safe_float(row.get("thstrm_amount"))
            if not parsed.get("report_date") and row.get("thstrm_dt"):
                parsed["report_date"] = row.get("thstrm_dt")
        return {key: value for key, value in parsed.items() if value is not None}

    def _get_json(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        query = {"crtfc_key": self.api_key, **params}
        response = requests.get(f"{_DART_BASE_URL}/{endpoint}", params=query, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("OpenDART response is not a JSON object")
        status = str(data.get("status") or "")
        if status and status not in {"000"}:
            message = data.get("message") or status
            raise RuntimeError(f"OpenDART API error {status}: {message}")
        return data

    def _load_corp_map(self) -> Dict[str, Dict[str, str]]:
        if self._corp_map is not None:
            return self._corp_map
        cached = self._read_corp_cache()
        if cached is not None:
            self._corp_map = cached
            return cached

        response = requests.get(
            f"{_DART_BASE_URL}/corpCode.xml",
            params={"crtfc_key": self.api_key},
            timeout=self.timeout,
        )
        response.raise_for_status()
        with zipfile.ZipFile(BytesIO(response.content)) as zf:
            xml_names = [name for name in zf.namelist() if name.lower().endswith(".xml")]
            if not xml_names:
                raise ValueError("corpCode.xml zip has no xml file")
            xml_data = zf.read(xml_names[0])
        root = ElementTree.fromstring(xml_data)
        mapping: Dict[str, Dict[str, str]] = {}
        for item in root.findall("list"):
            stock_code = (item.findtext("stock_code") or "").strip()
            if not stock_code:
                continue
            mapping[stock_code] = {
                "corp_code": (item.findtext("corp_code") or "").strip(),
                "corp_name": (item.findtext("corp_name") or "").strip(),
                "stock_code": stock_code,
                "modify_date": (item.findtext("modify_date") or "").strip(),
            }
        self._corp_map = mapping
        self._write_corp_cache(mapping)
        return mapping

    def _read_corp_cache(self) -> Optional[Dict[str, Dict[str, str]]]:
        try:
            if not self.corp_cache_path.exists():
                return None
            payload = json.loads(self.corp_cache_path.read_text(encoding="utf-8"))
            if time.time() - float(payload.get("ts", 0)) > _CACHE_TTL_SECONDS:
                return None
            mapping = payload.get("mapping")
            if isinstance(mapping, dict):
                return {str(k): dict(v) for k, v in mapping.items() if isinstance(v, dict)}
        except Exception as exc:
            logger.debug("DART corp cache read failed: %s", exc)
        return None

    def _write_corp_cache(self, mapping: Dict[str, Dict[str, str]]) -> None:
        try:
            self.corp_cache_path.write_text(json.dumps({"ts": time.time(), "mapping": mapping}), encoding="utf-8")
        except Exception as exc:
            logger.debug("DART corp cache write failed: %s", exc)
