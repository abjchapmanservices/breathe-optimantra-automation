import unittest
from src.login_smoke import validate_config

class LoginSmokeConfigTests(unittest.TestCase):
    def test_requires_explicit_enable(self):
        with self.assertRaisesRegex(RuntimeError, "not enabled"):
            validate_config({})
    def test_requires_terms_approval(self):
        with self.assertRaisesRegex(RuntimeError, "terms"):
            validate_config({"LOGIN_SMOKE_ENABLED": "true"})
    def test_requires_secrets(self):
        with self.assertRaisesRegex(RuntimeError, "Credentials"):
            validate_config({"LOGIN_SMOKE_ENABLED": "true", "OPTIMANTRA_TERMS_APPROVED": "true"})
