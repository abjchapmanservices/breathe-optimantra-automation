import unittest
from datetime import date
from src.daily_export_plan import completed_day_exports, planned_export_names


class DailyExportPlanTests(unittest.TestCase):
    def test_excludes_current_day_and_has_seven_distinct_dates(self):
        days = completed_day_exports(date(2026, 10, 11))
        self.assertEqual(days, [
            "2026-10-04", "2026-10-05", "2026-10-06",
            "2026-10-07", "2026-10-08", "2026-10-09",
            "2026-10-10",
        ])
        self.assertEqual(len(set(days)), 7)

    def test_original_file_names_are_separate(self):
        names = planned_export_names(date(2026, 10, 11))
        self.assertEqual(len(names), 7)
        self.assertEqual(names[1], "optimantra-financials-2026-10-05.csv")


if __name__ == "__main__":
    unittest.main()
