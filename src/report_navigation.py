"""Observed OptiMantra report labels and guarded navigation scaffold.

Source: user-provided screenshot of the Report List. The screenshot establishes
visible text and hierarchy, not HTML selectors. No login or network calls occur.
"""
REPORT_HIERARCHY = (
    "Financials by Category",
    "Summary of Category (Type/Subtype) Charges and Payments",
    "+ With Patient, Provider, and Date of Payment",
)

def select_report_from_open_list(page, *, enabled=False):
    """Draft Playwright navigation, requires an already open Report List.

    This is NOT wired into GitHub Actions or live login. The actual DOM,
    collapsible-row behavior, and click targets must be verified in a
    permitted test environment before enabling.
    """
    if not enabled:
        raise RuntimeError("Live report navigation is disabled")
    dialog = page.get_by_text("Report List", exact=True)
    dialog.wait_for(state="visible")
    for label in REPORT_HIERARCHY:
        item = page.get_by_text(label, exact=True)
        if item.count() != 1:
            raise RuntimeError(f"Expected exactly one report row: {label}")
        item.click()
    # Selection is not a download. Do not request patient-level data here.
    return REPORT_HIERARCHY[-1]
