"""Single OptiMantra login attempt with stage-only diagnostic messages.

No patient data or reports accessed. Never output secrets, URLs, DOM,
screenshots, trace files, cookies or raw Playwright errors.
"""
import os
from urllib.parse import urlparse

from src.optimantra_login import LOGIN_URL


def validate_config(env):
    if env.get("LOGIN_SMOKE_ENABLED") != "true":
        raise RuntimeError("Login test is not enabled")
    if env.get("OPTIMANTRA_TERMS_APPROVED") != "true":
        raise RuntimeError("Login agreement approval required")
    if not env.get("OPTIMANTRA_USERNAME") or not env.get("OPTIMANTRA_PASSWORD"):
        raise RuntimeError("Credentials are not available")


def run():
    validate_config(os.environ)
    from playwright.sync_api import sync_playwright

    stage = "browser_start"
    browser = None
    try:
        with sync_playwright() as playwright:
            stage = "browser_launch"
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_context(
                accept_downloads=False, service_workers="block"
            ).new_page()
            page.set_default_timeout(8000)

            stage = "open_login"
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            if urlparse(page.url).hostname != "www.optimantra.com":
                raise RuntimeError("Unexpected origin")

            stage = "select_practitioner_login"
            # Practitioner is selected by default in the observed screenshot.
            # Do not click an unverified control.

            stage = "locate_login_fields"
            email = page.locator('input[type="email"]:visible')
            if email.count() != 1:
                email = page.locator('input[type="text"]:visible')
            password = page.locator('input[type="password"]:visible')
            if email.count() != 1 or password.count() != 1:
                raise RuntimeError("Visible login fields not unique")

            stage = "fill_credentials"
            email.fill(os.environ["OPTIMANTRA_USERNAME"])
            password.fill(os.environ["OPTIMANTRA_PASSWORD"])

            stage = "locate_agreement"
            agreement = page.locator('input[type="checkbox"]:visible')
            if agreement.count() != 1:
                raise RuntimeError("Visible agreement checkbox not unique")
            stage = "confirm_agreement"
            agreement.check()

            stage = "locate_submit"
            submit = page.get_by_role("button", name="Log in", exact=True)
            if submit.count() != 1 or not submit.is_visible():
                raise RuntimeError("Login button not unique")

            stage = "submit_login"
            submit.click(timeout=8000)

            stage = "verify_authentication"
            page.get_by_text("Analytics", exact=True).first.wait_for(
                state="visible", timeout=15000
            )
            if "/public/login" in urlparse(page.url).path:
                raise RuntimeError("Still on login page")
            if os.environ.get("NAVIGATION_SMOKE_ENABLED") == "true":
                stage = "open_analytics"
                page.get_by_text("Analytics", exact=True).first.click()
                stage = "open_report_list"
                report_list = page.get_by_text("List of Reports", exact=True).first
                report_list.wait_for(state="visible", timeout=15000)
                report_list.click()
                stage = "locate_financial_report_category"
                page.get_by_text("Financials by Category", exact=True).first.wait_for(
                    state="visible", timeout=15000
                )
                print("PASS: Report list visible. No report opened.", flush=True)
            else:
                print("PASS: Authenticated UI confirmed; no reports accessed.", flush=True)
    except Exception:
        raise RuntimeError(f"Login smoke test failed at stage: {stage}") from None
    finally:
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass


if __name__ == "__main__":
    run()
