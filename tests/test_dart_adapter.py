import io
import json
import os
import tempfile
import unittest
import zipfile
from unittest.mock import Mock, patch

from data_provider.dart_adapter import DartAdapter


def _corp_zip() -> bytes:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<result>
  <list>
    <corp_code>00126380</corp_code>
    <corp_name>삼성전자</corp_name>
    <stock_code>005930</stock_code>
    <modify_date>20250101</modify_date>
  </list>
</result>
"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("CORPCODE.xml", xml)
    return buf.getvalue()


class DartAdapterTestCase(unittest.TestCase):
    def test_load_corp_map_from_corp_code_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = os.path.join(tmp, "dart-cache.json")
            with patch.dict(os.environ, {"DART_API_KEY": "key", "DART_CORP_CODE_CACHE_PATH": cache_path}, clear=False):
                adapter = DartAdapter()
                response = Mock()
                response.content = _corp_zip()
                response.raise_for_status = Mock()
                with patch("requests.get", return_value=response):
                    corp = adapter.get_corp_by_stock_code("005930.KS")

        self.assertEqual(corp["corp_code"], "00126380")
        self.assertEqual(corp["corp_name"], "삼성전자")

    def test_recent_disclosures_are_normalized(self):
        with patch.dict(os.environ, {"DART_API_KEY": "key"}, clear=False):
            adapter = DartAdapter()
            adapter._get_json = Mock(
                return_value={
                    "status": "000",
                    "list": [
                        {
                            "corp_code": "00126380",
                            "corp_name": "삼성전자",
                            "stock_code": "005930",
                            "report_nm": "분기보고서",
                            "rcept_dt": "20260515",
                            "rcept_no": "20260515000001",
                        }
                    ],
                }
            )

            rows = adapter.get_recent_disclosures("00126380")

        self.assertEqual(rows[0]["report_name"], "분기보고서")
        self.assertIn("rcpNo=20260515000001", rows[0]["url"])

    def test_financial_report_extracts_core_accounts(self):
        with patch.dict(os.environ, {"DART_API_KEY": "key"}, clear=False):
            adapter = DartAdapter()
            adapter._get_json = Mock(
                return_value={
                    "status": "000",
                    "list": [
                        {"account_nm": "매출액", "thstrm_amount": "1,000", "thstrm_dt": "2025.12.31"},
                        {"account_nm": "영업이익", "thstrm_amount": "200"},
                        {"account_nm": "당기순이익", "thstrm_amount": "150"},
                        {"account_nm": "자산총계", "thstrm_amount": "5,000"},
                    ],
                }
            )

            report = adapter.get_financial_report("00126380", "2025", "11011")

        self.assertEqual(report["revenue"], 1000.0)
        self.assertEqual(report["operating_profit"], 200.0)
        self.assertEqual(report["net_profit"], 150.0)
        self.assertEqual(report["assets"], 5000.0)

    def test_bundle_combines_disclosures_and_financial_report(self):
        with patch.dict(os.environ, {"DART_API_KEY": "key"}, clear=False):
            adapter = DartAdapter()
            adapter.get_corp_by_stock_code = Mock(return_value={"corp_code": "00126380", "corp_name": "삼성전자"})
            adapter.get_recent_disclosures = Mock(return_value=[{"report_name": "사업보고서"}])
            adapter.get_latest_financial_report = Mock(return_value={"revenue": 1000.0})

            bundle = adapter.get_dart_bundle("005930.KS")

        self.assertEqual(bundle["status"], "ok")
        self.assertTrue(bundle["disclosures"])
        self.assertEqual(bundle["financial_report"]["revenue"], 1000.0)

    def test_missing_key_is_not_supported(self):
        with patch.dict(os.environ, {"DART_API_KEY": "", "OPENDART_API_KEY": ""}, clear=False):
            bundle = DartAdapter().get_dart_bundle("005930.KS")

        self.assertEqual(bundle["status"], "not_supported")
        self.assertIn("dart api key missing", bundle["errors"])


if __name__ == "__main__":
    unittest.main()
