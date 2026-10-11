"""OptiMantra login-only smoke test for the approved Cloud Run runtime.

No reports, downloads, screenshots, page content, or credentials are logged.
Fails closed when selectors or confirmation are ambiguous.
"""
import os
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        try:
            context = browser.new_context(accept_downloads=False, service_workers="block")
            page = context.new_page()
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            if urlparse(page.url).hostname != "www.optimantra.com":
                raise RuntimeError("Unexpected login host")
            # Visible labels come from the public login page; actual selectors
            # must be tested in the authorized environment.
            email = page.get_by_role("textbox", name="Email")
            password = page.get_by_label("Password", exact=True)
            if email.count() != 1 or password.count() != 1:
                raise RuntimeError("Login fields were not uniquely identified")
            email.fill(os.environ["OPTIMANTRA_USERNAME"])
            password.fill(os.environ["OPTIMANTRA_PASSWORD"])
            # Never auto-accept an agreement with unspecified text.
            agreement = page.get_by_role("checkbox")
            if agreement.count() != 1:
                raise RuntimeError("Agreement checkbox ambiguous")
            agreement.check()
            submit = page.get_by_role("button", name="Log in", exact=True)
            if submit.count() != 1:
                raise RuntimeError("Submit button ambiguous")
            submit.click()
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            # Require a navigation away from the public login URL AND a
            # post-login UI landmark. Do not print URL or page text.
            if "/public/login" in urlparse(page.url).path:
                raise RuntimeError("Login remained on public login page")
            landmark = page.get_by_text("Analytics", exact=True)
            if landmark.count() < 1:
                raise RuntimeError("Authenticated UI was not verified")
            print("PASS: Authenticated session confirmed. No report accessed.")
        except (PlaywrightTimeout, Exception) as exc:
            # Avoid printing exception/page content which may disclose details.
            raise RuntimeError("Login smoke test failed; inspect selectors securely") from None
        finally:
            browser.close()

if __name__ == "__main__":
    run()
