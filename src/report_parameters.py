"""Validate a single payment date for the OptiMantra daily report.

No web access or patient data is involved.
"""
from datetime import date, datetime
from zoneinfo import ZoneInfo

REPORT_TIMEZONE = "America/Chicago"

def reporting_date(value: str) -> date:
    """Accept ISO calendar date only; never a date range."""
    try:
        selected = date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("REPORT_DATE must be YYYY-MM-DD") from exc
    if selected.isoformat() != value:
        raise ValueError("REPORT_DATE must be YYYY-MM-DD")
    return selected

def previous_calendar_day(now=None) -> date:
    """Default one calendar day before execution in clinic timezone."""
    current = now or datetime.now(ZoneInfo(REPORT_TIMEZONE))
    return current.astimezone(ZoneInfo(REPORT_TIMEZONE)).date().fromordinal(
        current.astimezone(ZoneInfo(REPORT_TIMEZONE)).date().toordinal() - 1
    )

def report_dates(selected: date) -> tuple[str, str]:
    """Both OptiMantra prompts must use the same date, as shown in the SOP."""
    value = selected.strftime("%m/%d/%Y")
    return (value, value)
