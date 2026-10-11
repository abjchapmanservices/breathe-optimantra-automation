"""Safe Playwright smoke test. Does not access OptiMantra or any external URL."""
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content("""
                <html><body><h1>Offline Login Test</h1>
                <label>Username<input name="username"></label>
                <label>Password<input name="password" type="password"></label>
                <button type="button">Sign in</button></body></html>
            """)
            page.locator('input[name="username"]').fill("synthetic-user")
            page.locator('input[name="password"]').fill("synthetic-password")
            assert page.get_by_role("heading", name="Offline Login Test").is_visible()
            assert page.locator('input[name="password"]').input_value() == "synthetic-password"
            print("PASS: Browser automation works using an offline synthetic login page.")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
