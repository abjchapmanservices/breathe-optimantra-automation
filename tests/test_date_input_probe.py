import unittest
from src.login_smoke import validate_config

class DateInputProbeGuardTests(unittest.TestCase):
    def test_probe_requires_filter(self):
        with self.assertRaisesRegex(RuntimeError, "requires date-filter"):
            validate_config({"DATE_INPUT_PROBE_ENABLED": "true"})
    def test_probe_does_not_bypass_login(self):
        with self.assertRaisesRegex(RuntimeError, "not enabled"):
            validate_config({
                "DATE_INPUT_PROBE_ENABLED": "true",
                "DATE_FILTER_SMOKE_ENABLED": "true",
                "REPORT_SELECTION_SMOKE_ENABLED": "true",
                "NAVIGATION_SMOKE_ENABLED": "true"
            })

if __name__ == "__main__":
    unittest.main()
