import unittest
from src.login_smoke import validate_config

class DateFillGuardTests(unittest.TestCase):
    def test_requires_prerequisites(self):
        with self.assertRaisesRegex(RuntimeError, "Date fill requires"):
            validate_config({"DATE_FILL_SMOKE_ENABLED": "true", "REPORT_DATE": "2026-10-05"})

    def test_requires_valid_date(self):
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            validate_config({
                "DATE_FILL_SMOKE_ENABLED": "true",
                "DATE_FILTER_SMOKE_ENABLED": "true",
                "NAVIGATION_SMOKE_ENABLED": "true",
                "REPORT_SELECTION_SMOKE_ENABLED": "true",
                "REPORT_DATE": "10/05/2026"
            })

    def test_does_not_bypass_login(self):
        with self.assertRaisesRegex(RuntimeError, "not enabled"):
            validate_config({
                "DATE_FILL_SMOKE_ENABLED": "true",
                "DATE_FILTER_SMOKE_ENABLED": "true",
                "NAVIGATION_SMOKE_ENABLED": "true",
                "REPORT_SELECTION_SMOKE_ENABLED": "true",
                "REPORT_DATE": "2026-10-05"
            })
