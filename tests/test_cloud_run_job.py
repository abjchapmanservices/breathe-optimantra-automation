import os
import unittest
from unittest.mock import patch
from src.cloud_run_job import main

class CloudRunJobTests(unittest.TestCase):
    def test_synthetic_mode(self):
        with patch.dict(os.environ, {"LIVE_MODE": "false", "REPORT_MODE": "synthetic"}):
            main()

    def test_live_mode_fails_closed(self):
        with patch.dict(os.environ, {"LIVE_MODE": "true", "REPORT_MODE": "synthetic"}):
            with self.assertRaisesRegex(RuntimeError, "Live mode disabled"):
                main()

    def test_unapproved_mode_fails_closed(self):
        with patch.dict(os.environ, {"LIVE_MODE": "false", "REPORT_MODE": "production"}):
            with self.assertRaisesRegex(RuntimeError, "Only synthetic"):
                main()
