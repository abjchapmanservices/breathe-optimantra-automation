"""Construct a seven-day OptiMantra backfill plan without accessing PHI.

The reporting window is seven completed calendar days in America/Chicago.
Each day must be exported separately, without altering the report layout.
"""
from datetime import date, timedelta
from src.report_parameters import reporting_date, previous_calendar_day


def completed_day_exports(today=None):
    """Return seven ISO dates, oldest first, excluding the current clinic day."""
    last_day = (today - timedelta(days=1)) if today is not None else previous_calendar_day()
    return [(last_day - timedelta(days=offset)).isoformat() for offset in range(6, -1, -1)]


def planned_export_names(today=None):
    """Filenames only, never raw reports or patient data."""
    return [f"optimantra-financials-{day}.csv" for day in completed_day_exports(today)]
