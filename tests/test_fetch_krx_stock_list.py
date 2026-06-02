# -*- coding: utf-8 -*-
"""Tests for scripts.fetch_krx_stock_list."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

fetch_krx_stock_list = importlib.import_module("fetch_krx_stock_list")


def _response(payload):
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


def test_fetch_krx_stock_list_builds_ks_and_kq_rows():
    payloads = {
        "KOSPI": {
            "totalCount": 1,
            "stocks": [{
                "itemCode": "005930",
                "stockName": "삼성전자",
                "stockType": "domestic",
                "stockEndType": "stock",
            }],
        },
        "KOSDAQ": {
            "totalCount": 1,
            "stocks": [{
                "itemCode": "086520",
                "stockName": "에코프로",
                "stockType": "domestic",
                "stockEndType": "stock",
            }],
        },
    }

    session = MagicMock()
    session.get.side_effect = lambda url, params, timeout: _response(
        payloads[url.rsplit("/", 1)[-1]]
    )

    with patch.object(fetch_krx_stock_list.requests, "Session", return_value=session):
        rows = fetch_krx_stock_list.fetch_krx_stock_list(page_size=100)

    assert rows == [
        {"ts_code": "005930.KS", "symbol": "005930", "name": "삼성전자", "market": "KOSPI"},
        {"ts_code": "086520.KQ", "symbol": "086520", "name": "에코프로", "market": "KOSDAQ"},
    ]


def test_write_csv_uses_expected_columns(tmp_path):
    output_path = tmp_path / "stock_list_kr.csv"
    rows = [{"ts_code": "005930.KS", "symbol": "005930", "name": "삼성전자", "market": "KOSPI"}]

    fetch_krx_stock_list.write_csv(rows, output_path)

    text = output_path.read_text(encoding="utf-8-sig")
    assert "ts_code,symbol,name,market" in text
    assert "005930.KS,005930,삼성전자,KOSPI" in text
