import unittest
from src.optimantra_login import LOGIN_URL, login, validate_login_url

class LoginConfigurationTests(unittest.TestCase):
    def test_exact_url_is_approved(self):
        self.assertEqual(validate_login_url(), LOGIN_URL)

    def test_other_hosts_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_login_url("https://fake-optimantra.example/optimus/om/public/login")

    def test_live_login_blocked_by_default(self):
        with self.assertRaisesRegex(RuntimeError, "not enabled"):
            login(None, "fake-user", "fake-password")

if __name__ == "__main__":
    unittest.main()
