#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch Korean stock names for the Web autocomplete index.

The source is Naver Finance's public mobile stock-list JSON endpoint. The
result is stored as ``data/stock_list_kr.csv`` and consumed by
``scripts/generate_index_from_csv.py``.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "data" / "stock_list_kr.csv"
NAVER_MARKET_VALUE_URL = "https://m.stock.naver.com/api/stocks/marketValue/{market}"
MARKETS = {
    "KOSPI": "KS",
    "KOSDAQ": "KQ",
}


def _request_json(session: requests.Session, market: str, page: int, page_size: int) -> Dict[str, Any]:
    response = session.get(
        NAVER_MARKET_VALUE_URL.format(market=market),
        params={"page": page, "pageSize": page_size},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"Naver stock list response is not an object: {market} page {page}")
    return payload


def _iter_market_rows(session: requests.Session, market: str, suffix: str, page_size: int) -> Iterable[Dict[str, str]]:
    first_page = _request_json(session, market, 1, page_size)
    total_count = int(first_page.get("totalCount") or 0)
    page_count = max(1, math.ceil(total_count / page_size))

    for page in range(1, page_count + 1):
        payload = first_page if page == 1 else _request_json(session, market, page, page_size)
        for item in payload.get("stocks") or []:
            if not isinstance(item, dict):
                continue
            code = str(item.get("itemCode") or "").strip()
            name = str(item.get("stockName") or "").strip()
            stock_type = str(item.get("stockType") or "").strip().lower()
            stock_end_type = str(item.get("stockEndType") or "").strip().lower()

            if not code or not name:
                continue
            if not code.isdigit() or len(code) != 6:
                continue
            if stock_type and stock_type != "domestic":
                continue
            if stock_end_type and stock_end_type != "stock":
                continue

            yield {
                "ts_code": f"{code}.{suffix}",
                "symbol": code,
                "name": name,
                "market": market,
            }


def fetch_krx_stock_list(page_size: int = 100) -> List[Dict[str, str]]:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })

    rows: List[Dict[str, str]] = []
    seen_codes = set()
    for market, suffix in MARKETS.items():
        for row in _iter_market_rows(session, market, suffix, page_size):
            if row["symbol"] in seen_codes:
                continue
            seen_codes.add(row["symbol"])
            rows.append(row)
    return rows


def write_csv(rows: Sequence[Dict[str, str]], output_path: Path = OUTPUT_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ts_code", "symbol", "name", "market"])
        writer.writeheader()
        writer.writerows(rows)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch KRX/KOSDAQ stock names for autocomplete")
    parser.add_argument("--page-size", type=int, default=100, help="Naver API page size")
    args = parser.parse_args(argv)

    try:
        rows = fetch_krx_stock_list(page_size=args.page_size)
        if not rows:
            print("[fetch_krx_stock_list] ERROR: no Korean stock rows fetched", file=sys.stderr)
            return 1
        write_csv(rows)
    except Exception as exc:
        print(f"[fetch_krx_stock_list] ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"[fetch_krx_stock_list] wrote {len(rows)} rows to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
