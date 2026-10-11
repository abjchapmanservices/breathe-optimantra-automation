import unittest
from src.login_smoke import validate_config

class ReportSelectionConfigTests(unittest.TestCase):
    def test_selection_requires_navigation(self):
        with self.assertRaisesRegex(RuntimeError, "requires navigation"):
            validate_config({"REPORT_SELECTION_SMOKE_ENABLED": "true"})
    def test_selection_does_not_bypass_login(self):
        with self.assertRaisesRegex(RuntimeError, "not enabled"):
            validate_config({
                "REPORT_SELECTION_SMOKE_ENABLED": "true",
                "NAVIGATION_SMOKE_ENABLED": "true"
            })

if __name__ == "__main__":
    unittest.main()
