"""Cloud Run Secret Manager injection smoke test.

This module never calls OptiMantra, exports reports, or outputs credentials.
It verifies that required variables are provided to a dedicated GCP test job.
"""
import os

REQUIRED = ("OPTIMANTRA_USERNAME", "OPTIMANTRA_PASSWORD")

def verify_environment(environ=None):
    environment = os.environ if environ is None else environ
    if environment.get("LIVE_MODE", "false").lower() != "false":
        raise RuntimeError("Credential smoke test requires LIVE_MODE=false")
    if any(not environment.get(name, "").strip() for name in REQUIRED):
        raise RuntimeError("One or more credential variables are unavailable")
    return True

def main():
    verify_environment()
    print("PASS: Credential variables present in approved runtime. Values not displayed.")

if __name__ == "__main__":
    main()
