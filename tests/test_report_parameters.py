import unittest
from datetime import date, datetime, timezone
from src.report_parameters import report_dates, reporting_date, previous_calendar_day

class ReportParametersTests(unittest.TestCase):
    def test_dates_match(self):
        self.assertEqual(report_dates(date(2026, 10, 5)), ("10/05/2026", "10/05/2026"))
    def test_reject_malformed(self):
        with self.assertRaises(ValueError):
            reporting_date("10/05/26")
    def test_previous_day_in_chicago(self):
        now = datetime(2026, 10, 11, 3, 30, tzinfo=timezone.utc)
        self.assertEqual(previous_calendar_day(now), date(2026, 10, 9))
