import csv
import tempfile
import unittest
from pathlib import Path
from src.export_adapter import summarize

COLUMNS = ["Date", "Date Of Payment", "Patient", "", "Super Bill",
           "Charge Type", "Charge Desc", "Item Sub-Type", "Svc Sub-Type",
           "Metrics", "Total Charges", "Total Discount", "Charges - Discount",
           "Calculated Payment (Line)", "Calculated Payment (Line) Adjusted",
           "Total Payment On Superbill"]

def fake(date, category, subtype, gross, discount, net):
    row = dict.fromkeys(COLUMNS, "")
    row.update({"Date": date, "Charge Type": category, "Item Sub-Type": subtype,
                "Total Charges": gross, "Total Discount": discount,
                "Charges - Discount": net})
    return row

class AdapterTests(unittest.TestCase):
    def write_test_data(self, target, records):
        with target.open("w", newline="", encoding="utf-16") as fh:
            writer = csv.DictWriter(fh, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(records)

    def test_export_and_total(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "mock.csv"
            self.write_test_data(path, [
                fake("10/5/26", "SUPPLIES", "Designs for Health", "$500.00", "$75.00", "425.00"),
                fake("10/5/26", "SUPPLIES", "Designs for Health", "$292.19", "$43.79", "248.40"),
                fake("Total", "", "", "$792.19", "$118.79", "673.40"),
            ])
            result = summarize(path)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["Gross Charges"], "792.19")
            self.assertEqual(result[0]["Discount Line (QBO)"], "-118.79")
            self.assertEqual(result[0]["Net Revenue"], "673.40")
            self.assertNotIn("Patient", result[0])

    def test_bad_totals(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "mock.csv"
            self.write_test_data(path, [
                fake("10/5/26", "LABS", "", "10", "0", "10"),
                fake("Total", "", "", "11", "0", "11"),
            ])
            with self.assertRaisesRegex(ValueError, "totals do not reconcile"):
                summarize(path)

    def test_bad_row(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "mock.csv"
            self.write_test_data(path, [fake("10/5/26", "LABS", "", "10", "2", "9")])
            with self.assertRaisesRegex(ValueError, "Mismatch"):
                summarize(path)

if __name__ == "__main__":
    unittest.main()
