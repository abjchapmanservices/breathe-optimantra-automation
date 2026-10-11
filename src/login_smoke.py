"""OptiMantra login-only smoke test with non-sensitive stage diagnostics.

No reports, patient records, screenshots, HTML, URLs, credentials, or
Playwright exception strings are logged. One login attempt only.
"""
import os
from urllib.parse import urlparse
from src.optimantra_login import LOGIN_URL

def validate_config(env):
    if env.get("LOGIN_SMOKE_ENABLED") != "true":
        raise RuntimeError("Login test is not enabled")
    if env.get("OPTIMANTRA_TERMS_APPROVED") != "true":
        raise RuntimeError("Account owner must approve login terms before testing")
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
            context = browser.new_context(accept_downloads=False, service_workers="block")
            page = context.new_page()
            page.set_default_timeout(8000)
            stage = "open_login"
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            if urlparse(page.url).hostname != "www.optimantra.com":
                raise RuntimeError("Unexpected origin")
            stage = "select_practitioner_login"
            practitioner = page.get_by_role("button", name="Practitioner login")
            if practitioner.count() == 1 and practitioner.is_visible():
                practitioner.click()
            stage = "locate_login_fields"
            # The page includes hidden password-reset forms with duplicate Email\n            # and Password fields. Restrict matching to the visible login form.\n            email = page.locator("input[type=email]:visible")\n            if email.count() != 1:\n                email = page.get_by_role("textbox", name="Email").filter(visible=True)\n            password = page.locator("input[type=password]:visible")\n            if email.count() != 1 or password.count() != 1:\n                raise RuntimeError("Visible login fields not unique")
            stage = "fill_credentials"
            email.fill(os.environ["OPTIMANTRA_USERNAME"])
            password.fill(os.environ["OPTIMANTRA_PASSWORD"])
            stage = "locate_agreement"
            agreement = page.get_by_role("checkbox").filter(visible=True)
            if agreement.count() != 1:
                raise RuntimeError("Agreement not unique")
            stage = "confirm_agreement"
            agreement.check()
            stage = "locate_submit"
            submit = page.get_by_role("button", name="Log in", exact=True).filter(visible=True)
            if submit.count() != 1:
                raise RuntimeError("Submit not unique")
            stage = "submit_login"
            submit.click(timeout=8000)
            stage = "verify_authentication"
            page.get_by_text("Analytics", exact=True).first.wait_for(state="visible", timeout=15000)
            if "/public/login" in urlparse(page.url).path:
                raise RuntimeError("Login did not navigate")
            print("PASS: Authentication UI confirmed; no reports accessed.", flush=True)
    except Exception:
        # Never print upstream error text, page content, credentials, or URL.
        raise RuntimeError(f"Login smoke test failed at stage: {stage}") from None
    finally:
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass

if __name__ == "__main__":
    run()
