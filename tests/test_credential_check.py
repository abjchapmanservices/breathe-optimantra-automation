import unittest
from src.credential_check import verify_environment

class CredentialCheckTests(unittest.TestCase):
    def test_with_mock_values(self):
        self.assertTrue(verify_environment({
            "LIVE_MODE": "false",
            "OPTIMANTRA_USERNAME": "invented@example.invalid",
            "OPTIMANTRA_PASSWORD": "synthetic-only"
        }))

    def test_missing_value(self):
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            verify_environment({"LIVE_MODE": "false", "OPTIMANTRA_USERNAME": "invented"})

    def test_live_mode_fails(self):
        with self.assertRaisesRegex(RuntimeError, "LIVE_MODE=false"):
            verify_environment({
                "LIVE_MODE": "true",
                "OPTIMANTRA_USERNAME": "invented",
                "OPTIMANTRA_PASSWORD": "invented",
            })
