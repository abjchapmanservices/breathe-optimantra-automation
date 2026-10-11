import unittest
from src.login_smoke import validate_config

class DateFilterGuardTests(unittest.TestCase):
    def test_requires_prior_steps(self):
        with self.assertRaisesRegex(RuntimeError, "requires report selection"):
            validate_config({"DATE_FILTER_SMOKE_ENABLED": "true"})
    def test_does_not_bypass_login(self):
        with self.assertRaisesRegex(RuntimeError, "not enabled"):
            validate_config({"DATE_FILTER_SMOKE_ENABLED": "true", "REPORT_SELECTION_SMOKE_ENABLED": "true", "NAVIGATION_SMOKE_ENABLED": "true"})

if __name__ == "__main__":
    unittest.main()
