"""Fail-closed Cloud Run Jobs entrypoint.

Runs a synthetic-only report validation. Do not use patient exports in this
stage. LIVE_MODE is explicitly blocked until security and integration review.
"""
import os
import tempfile
from pathlib import Path
from src.process_report import process

def main():
    if os.environ.get("LIVE_MODE", "false").lower() != "false":
        raise RuntimeError("Live mode disabled pending approved implementation")
    if os.environ.get("REPORT_MODE", "synthetic") != "synthetic":
        raise RuntimeError("Only synthetic report mode is enabled")
    with tempfile.TemporaryDirectory() as work:
        result = process("tests/fixtures/synthetic_daily.csv",
                         str(Path(work) / "summary.csv"))
        if len(result) != 3:
            raise RuntimeError("Synthetic report validation failed")
    print("Synthetic validation succeeded. No external login, email, or QBO access.")

if __name__ == "__main__":
    main()
