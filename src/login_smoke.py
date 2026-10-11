"""Single OptiMantra login attempt with stage-only diagnostic messages.

No patient data or reports accessed. Never output secrets, URLs, DOM,
screenshots, trace files, cookies or raw Playwright errors.
"""
import os
from urllib.parse import urlparse

from src.optimantra_login import LOGIN_URL


def validate_config(env):
    if env.get("EXPORT_DIALOG_SMOKE_ENABLED") == "true" and env.get("REPORT_RUN_SMOKE_ENABLED") != "true":
        raise RuntimeError("Export dialog smoke requires report run smoke")
    if env.get("REPORT_RUN_SMOKE_ENABLED") == "true" and env.get("DATE_FILL_SMOKE_ENABLED") != "true":
        raise RuntimeError("Report run smoke requires verified date fill")
    if env.get("DATE_FILL_SMOKE_ENABLED") == "true":
        if env.get("DATE_FILTER_SMOKE_ENABLED") != "true" or env.get("NAVIGATION_SMOKE_ENABLED") != "true" or env.get("REPORT_SELECTION_SMOKE_ENABLED") != "true":
            raise RuntimeError("Date fill requires date filter and report selection")
        from src.report_parameters import reporting_date
        reporting_date(env.get("REPORT_DATE"))
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


def fill_known_report_dates(page, iso_date):
    """Locate each date input by its prompt container, without dynamic IDs."""
    import sys
    from src.report_parameters import reporting_date, report_dates

    print("DATE_FILL_DIAGNOSTIC: phase=entered", file=sys.stderr, flush=True)
    formatted, _ = report_dates(reporting_date(iso_date))
    print("DATE_FILL_DIAGNOSTIC: phase=date_validated", file=sys.stderr, flush=True)
    import time
    matched = []
    for label, phrase in (
        ("start", "Starting Date for Period"),
        ("end", "Ending Date for Period"),
    ):
        deadline = time.monotonic() + 12
        candidates = []
        last_counts = (0, 0, 0, 0, 0)
        while time.monotonic() < deadline:
            candidates = []
            headings_total = headings_visible = sections_found = texts_found = radios_found = 0
            for frame in page.frames:
                try:
                    headings = frame.locator(".mstrPromptQuestionMeaning").filter(
                        has_text=phrase
                    )
                    headings_total += headings.count()
                    for index in range(min(headings.count(), 4)):
                        heading = headings.nth(index)
                        if not heading.is_visible():
                            continue
                        headings_visible += 1
                        section = heading.locator("xpath=../../../../..")
                        if section.count() != 1:
                            continue
                        sections_found += 1
                        # The prior structure test observed one text input
                        # and two radio inputs within this five-level parent.
                        text_inputs = section.locator('input[type="text"]')
                        radios = section.locator('input[type="radio"]')
                        texts_found += text_inputs.count()
                        radios_found += radios.count()
                        if text_inputs.count() == 1 and radios.count() == 2:
                            candidates.append(text_inputs.first)
                except Exception:
                    continue
            last_counts = (
                headings_total, headings_visible, sections_found,
                texts_found, radios_found
            )
            if len(candidates) == 1:
                break
            if len(candidates) > 1:
                break
            page.wait_for_timeout(400)
        print(
            f"DATE_FILL_DIAGNOSTIC: field={label}; phase=prompt_scoped_selector; "
            f"matches={len(candidates)}; headings={last_counts[0]}; "
            f"visible_headings={last_counts[1]}; sections={last_counts[2]}; "
            f"text_inputs={last_counts[3]}; radio_inputs={last_counts[4]}",
            file=sys.stderr, flush=True,
        )
        if len(candidates) != 1:
            raise RuntimeError("Date prompt does not map to one input")
        matched.append((label, candidates[0]))
    for label, control in matched:
        visible = control.is_visible()
        enabled = control.is_enabled()
        print(
            f"DATE_FILL_DIAGNOSTIC: field={label}; phase=editable; "
            f"visible={str(visible).lower()}; enabled={str(enabled).lower()}",
            file=sys.stderr, flush=True,
        )
        if not visible or not enabled:
            raise RuntimeError("Date input is not editable; selection mode must be inspected")
    for label, control in matched:
        print(
            f"DATE_FILL_DIAGNOSTIC: field={label}; phase=fill_attempt",
            file=sys.stderr, flush=True,
        )
        control.fill(formatted, timeout=8000)
        control.press("Tab", timeout=8000)
        print(
            f"DATE_FILL_DIAGNOSTIC: field={label}; phase=filled",
            file=sys.stderr, flush=True,
        )
    for label, control in matched:
        correct = control.input_value().strip() == formatted
        print(
            f"DATE_FILL_DIAGNOSTIC: field={label}; phase=verify; "
            f"matches_expected={str(correct).lower()}",
            file=sys.stderr, flush=True,
        )
        if not correct:
            raise RuntimeError("Date input verification failed")
    return True

def run_report_smoke(page):
    """Submit the already-verified date filter; do not export or log results."""
    import sys
    buttons = []
    for frame in page.frames:
        try:
            query = frame.locator('input[type="button"][value="Run Report"], input[type="submit"][value="Run Report"], button:has-text("Run Report")')
            for i in range(min(query.count(), 5)):
                item = query.nth(i)
                if item.is_visible() and item.is_enabled():
                    buttons.append(item)
        except Exception:
            continue
    print(f"REPORT_RUN_DIAGNOSTIC: visible_button_matches={len(buttons)}",
          file=sys.stderr, flush=True)
    if len(buttons) != 1:
        raise RuntimeError("Run Report control requires inspection")
    unique = buttons
    unique[0].click(timeout=8000)
    print("REPORT_RUN_DIAGNOSTIC: submitted=true; export_attempted=false",
          file=sys.stderr, flush=True)
    # No patient-data content read or logged. A later gated stage will validate
    # report completion and the export toolbar.
    return True


def open_export_dialog_smoke(page):
    """Open export settings only, without clicking final Export or downloading."""
    import sys
    import time
    deadline = time.monotonic() + 120
    controls = []
    while time.monotonic() < deadline:
        controls = []
        for tab in page.context.pages:
            for frame in tab.frames:
                try:
                    export_icon = frame.locator("#tbExport")
                    if export_icon.count() == 1 and export_icon.is_visible():
                        controls.append(export_icon)
                except Exception:
                    continue
        if len(controls) == 1:
            break
        if len(controls) > 1:
            break
        page.wait_for_timeout(1000)
    print(
        f"EXPORT_DIALOG_DIAGNOSTIC: phase=toolbar; matches={len(controls)}",
        file=sys.stderr, flush=True,
    )
    if len(controls) != 1:
        raise RuntimeError("Export toolbar control not unique or not ready")
    # The inspected HTML places the Export span inside a clickable
    # mstrToolbarButton anchor. Click the anchor rather than its child span.
    parent = controls[0].locator("xpath=..")
    is_anchor = parent.count() == 1 and parent.evaluate(
        "(e) => e.tagName.toLowerCase() === 'a'"
    )
    print(
        "EXPORT_DIALOG_DIAGNOSTIC: phase=click_attempt; "
        f"parent_anchor={str(is_anchor).lower()}",
        file=sys.stderr, flush=True,
    )
    if not is_anchor:
        raise RuntimeError("Export toolbar anchor not found")
    previous_pages = set(page.context.pages)
    print(
        "EXPORT_DIALOG_DIAGNOSTIC: phase=click_start",
        file=sys.stderr, flush=True,
    )
    # The provided HTML installs its onclick handler directly on #tbExport,
    # not on the enclosing anchor. Dispatch to that specific icon rather than
    # asking Playwright to find a hit-testable point on a toolbar overlay.
    # This only opens settings, never submits a download.
    try:
        controls[0].dispatch_event("click", timeout=5000)
    except Exception:
        print(
            "EXPORT_DIALOG_DIAGNOSTIC: phase=icon_dispatch_failed",
            file=sys.stderr, flush=True,
        )
        raise RuntimeError("Export icon click handler did not complete") from None
    print(
        "EXPORT_DIALOG_DIAGNOSTIC: phase=icon_dispatch_returned",
        file=sys.stderr, flush=True,
    )
    deadline = time.monotonic() + 35
    dialog_frames = []
    while time.monotonic() < deadline:
        dialog_frames = []
        for tab in page.context.pages:
            for frame in tab.frames:
                try:
                    whole = frame.get_by_text("Whole report", exact=True)
                    csv_format = frame.get_by_text("CSV file format", exact=True)
                    if whole.count() and csv_format.count():
                        dialog_frames.append(frame)
                except Exception:
                    continue
        if len(dialog_frames) != 0:
            break
        page.wait_for_timeout(400)
    print(
        "EXPORT_DIALOG_DIAGNOSTIC: phase=tab_and_dialog_scan; "
        f"new_pages={len(set(page.context.pages)-previous_pages)}; "
        f"matching_frames={len(dialog_frames)}",
        file=sys.stderr, flush=True,
    )
    print(
        f"EXPORT_DIALOG_DIAGNOSTIC: phase=dialog; matching_frames={len(dialog_frames)}",
        file=sys.stderr, flush=True,
    )
    if len(dialog_frames) != 1:
        raise RuntimeError("Export dialog default choices not uniquely found")
    print(
        "PASS: Export dialog opened; expected Whole report and CSV options visible. "
        "No final export or download attempted.",
        flush=True,
    )


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
                        if os.environ.get("DATE_FILL_SMOKE_ENABLED") == "true":
                            stage = "fill_date_fields"
                            fill_known_report_dates(page, os.environ["REPORT_DATE"])
                            if os.environ.get("REPORT_RUN_SMOKE_ENABLED") == "true":
                                stage = "submit_report"
                                run_report_smoke(page)
                                if os.environ.get("EXPORT_DIALOG_SMOKE_ENABLED") == "true":
                                    stage = "open_export_dialog"
                                    open_export_dialog_smoke(page)
                                else:
                                    print("PASS: Report submitted. No export or download attempted.", flush=True)
                            else:
                                print("PASS: Both reporting dates entered and verified. Report not run.", flush=True)
                        elif os.environ.get("DATE_FIELD_MAPPING_PROBE_ENABLED") == "true":
                            stage = "map_date_field_candidates"
                            # Structural metadata only. No values, IDs, names,
                            # page HTML, URLs, or patient information collected.
                            for frame_index, frame in enumerate(page.frames):
                                try:
                                    start_count = frame.get_by_text(
                                        "Starting Date for Period", exact=False
                                    ).count()
                                    end_count = frame.get_by_text(
                                        "Ending Date for Period", exact=False
                                    ).count()
                                    if not (start_count or end_count):
                                        continue
                                    type_counts = {}
                                    inputs = frame.locator("input")
                                    for i in range(min(inputs.count(), 50)):
                                        field = inputs.nth(i)
                                        kind = (field.get_attribute("type") or "text").lower()
                                        visible = "visible" if field.is_visible() else "hidden"
                                        key = kind + "_" + visible
                                        type_counts[key] = type_counts.get(key, 0) + 1
                                    summary = ",".join(
                                        f"{kind}:{count}" for kind, count in sorted(type_counts.items())
                                    ) or "none"
                                    print(
                                        f"DATE_FRAME_STRUCTURE: frame_index={frame_index}; "
                                        f"start_label_matches={start_count}; "
                                        f"end_label_matches={end_count}; "
                                        f"input_types={summary}. Values not inspected.",
                                        flush=True,
                                    )
                                except Exception:
                                    continue
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
