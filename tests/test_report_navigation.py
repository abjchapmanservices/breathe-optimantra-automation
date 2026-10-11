import unittest
from src.report_navigation import REPORT_HIERARCHY, select_report_from_open_list

class ReportNavigationTests(unittest.TestCase):
    def test_screenshot_hierarchy(self):
        self.assertEqual(REPORT_HIERARCHY, (
            "Financials by Category",
            "Summary of Category (Type/Subtype) Charges and Payments",
            "+ With Patient, Provider, and Date of Payment",
        ))

    def test_live_navigation_disabled(self):
        with self.assertRaisesRegex(RuntimeError, "disabled"):
            select_report_from_open_list(None)

if __name__ == "__main__":
    unittest.main()
