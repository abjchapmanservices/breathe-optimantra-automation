import unittest
from src.login_smoke import validate_config


class ExportDialogGuardTests(unittest.TestCase):
    def test_dialog_requires_report_run(self):
        with self.assertRaisesRegex(RuntimeError, "requires report run"):
            validate_config({"EXPORT_DIALOG_SMOKE_ENABLED": "true"})

    def test_report_run_requires_date_fill(self):
        with self.assertRaisesRegex(RuntimeError, "requires verified date fill"):
            validate_config({
                "EXPORT_DIALOG_SMOKE_ENABLED": "true",
                "REPORT_RUN_SMOKE_ENABLED": "true"
            })


if __name__ == "__main__":
    unittest.main()
