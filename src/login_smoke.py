"""Single OptiMantra login attempt with stage-only diagnostic messages.

No patient data or reports accessed. Never output secrets, URLs, DOM,
screenshots, trace files, cookies or raw Playwright errors.
"""
import os
from urllib.parse import urlparse

from src.optimantra_login import LOGIN_URL


def validate_config(env):
    if env.get("DATE_FIELD_MAPPING_PROBE_ENABLED") == "true" and env.get("DATE_FILTER_SMOKE_ENABLED") != "true":
        raise RuntimeError("Date field mapping requires date-filter smoke")
    if env.get("DATE_INPUT_PROBE_ENABLED") == "true" and env.get("DATE_FILTER_SMOKE_ENABLED") != "true":
        raise RuntimeError("Date input probe requires date-filter smoke")
    if env.get("DATE_FILTER_SMOKE_ENABLED") == "true" and (env.get("NAVIGATION_SMOKE_ENABLED") != "true" or env.get("REPORT_SELECTION_SMOKE_ENABLED") != "true"):
        raise RuntimeError("Date filter smoke requires report selection and navigation")
    if env.get("REPORT_SELECTION_SMOKE_ENABLED") == "true" and env.get("NAVIGATION_SMOKE_ENABLED") != "true":
        raise RuntimeError("Report selection requires navigation")
    if env.get("LOGIN_SMOKE_ENABLED") != "true":
        raise RuntimeError("Login test is not enabled")
    if env.get("OPTIMANTRA_TERMS_APPROVED") != "true":
        raise RuntimeError("Login terms approval required")
    if not env.get("OPTIMANTRA_USERNAME") or not env.get("OPTIMANTRA_PASSWORD"):
        raise RuntimeError("Credentials are not available")


def wait_for_prompt_in_frames(page, fragment, timeout_ms=20000):
    """Look for a visible report prompt in main page or embedded report frames.

    Never logs frame URLs, labels, HTML, patient information, or screenshots.
    """
    import time
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                locator = frame.get_by_text(fragment, exact=False).first
                if locator.count() and locator.is_visible():
                    return
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise RuntimeError("Report prompt not visible")


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
                if os.environ.get("REPORT_SELECTION_SMOKE_ENABLED") == "true":
                    stage = "locate_report_family"
                    category = page.get_by_text("Financials by Category", exact=True).first
                    family = page.get_by_text(
                        "Summary of Category (Type/Subtype) Charges and Payments", exact=True
                    ).first
                    if not family.is_visible():
                        stage = "expand_report_category"
                        category.click()
                        family.wait_for(state="visible", timeout=10000)
                    stage = "expand_report_family"
                    target = page.get_by_text(
                        "+ With Patient, Provider, and Date of Payment", exact=True
                    ).first
                    if not target.is_visible():
                        family.click()
                        target.wait_for(state="visible", timeout=10000)
                    stage = "select_report"
                    target.click()
                    # Selecting the report should expose filter controls,
                    # but do not click Run Report or export anything.
                    stage = "verify_report_filter"
                    page.get_by_text("Change Date Filter", exact=True).first.wait_for(
                        state="visible", timeout=15000
                    )
                    if os.environ.get("DATE_FILTER_SMOKE_ENABLED") == "true":
                        stage = "open_date_filter"
                        page.get_by_text("Change Date Filter", exact=True).first.click()
                        stage = "verify_start_date_prompt"
                        wait_for_prompt_in_frames(page, "Starting Date for Period")
                        stage = "verify_end_date_prompt"
                        wait_for_prompt_in_frames(page, "Ending Date for Period")
                        if os.environ.get("DATE_FIELD_MAPPING_PROBE_ENABLED") == "true":
                            stage = "map_date_field_candidates"
                            for label_name, phrase in (
                                ("start", "Starting Date for Period"),
                                ("end", "Ending Date for Period"),
                            ):
                                prompt_frames = 0
                                candidates = 0
                                visible = 0
                                input_types = {"text": 0, "date": 0, "other": 0}
                                for frame in page.frames:
                                    try:
                                        prompts = frame.get_by_text(phrase, exact=False)
                                        if not prompts.count():
                                            continue
                                        prompt_frames += 1
                                        for idx in range(min(prompts.count(), 3)):
                                            candidate = prompts.nth(idx).locator(
                                                "xpath=following::input[1]"
                                            )
                                            if candidate.count() != 1:
                                                continue
                                            candidates += 1
                                            kind = (candidate.get_attribute("type") or "text").lower()
                                            input_types[kind if kind in ("text", "date") else "other"] += 1
                                            if candidate.is_visible():
                                                visible += 1
                                    except Exception:
                                        continue
                                print(
                                    f"DATE_FIELD_MAPPING: label={label_name}; "
                                    f"frames={prompt_frames}; "
                                    f"candidate_inputs={candidates}; "
                                    f"visible_candidates={visible}; "
                                    f"text={input_types['text']}; "
                                    f"date={input_types['date']}; "
                                    f"other={input_types['other']}. "
                                    "No values inspected or changed.",
                                    flush=True,
                                )
                            print("PASS: Date field mapping probe complete. No report run.", flush=True)
                        elif os.environ.get("DATE_INPUT_PROBE_ENABLED") == "true":
                            stage = "inspect_date_input_structure"
                            # Probe metadata only. Do not read input values,
                            # page text, HTML, identifiers or frame URLs.
                            import time
                            totals = {"date": 0, "text": 0, "other": 0}
                            frame_count = 0
                            deadline = time.monotonic() + 12
                            while time.monotonic() < deadline:
                                totals = {"date": 0, "text": 0, "other": 0}
                                frame_count = 0
                                for frame in page.frames:
                                    try:
                                        fields = frame.locator("input:visible")
                                        n = fields.count()
                                        if not n:
                                            continue
                                        frame_count += 1
                                        for i in range(min(n, 30)):
                                            kind = (fields.nth(i).get_attribute("type") or "text").lower()
                                            if kind == "date":
                                                totals["date"] += 1
                                            elif kind in ("text", "search"):
                                                totals["text"] += 1
                                            else:
                                                totals["other"] += 1
                                    except Exception:
                                        continue
                                if sum(totals.values()) > 0:
                                    break
                                page.wait_for_timeout(400)
                            print(
                                "DATE_INPUT_STRUCTURE: "
                                f"frames_with_inputs={frame_count}; "
                                f"visible_date_inputs={totals['date']}; "
                                f"visible_text_inputs={totals['text']}; "
                                f"visible_other_inputs={totals['other']}. "
                                "No values inspected.",
                                flush=True,
                            )
                            if sum(totals.values()) == 0:
                                print("DIAGNOSTIC: No standard visible input elements detected. "
                                      "Custom controls require selector inspection.", flush=True)
                            else:
                                print("PASS: Input metadata collected; no report run.", flush=True)
                        else:
                            print("PASS: Date filter prompts visible. No report run or exported.", flush=True)
                    else:
                        print("PASS: Financial report selected. No report run or exported.", flush=True)
                else:
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
