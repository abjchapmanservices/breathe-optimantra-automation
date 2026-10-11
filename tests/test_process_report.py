import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from src.process_report import aggregate, process

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_daily.csv"

class SyntheticReportTests(unittest.TestCase):
    def test_category_aggregation(self):
        with tempfile.TemporaryDirectory() as dirname:
            output = Path(dirname) / "summary.csv"
            result = process(FIXTURE, output)
            self.assertEqual(len(result), 3)
            self.assertTrue(output.exists())
            supplement = next(x for x in result if x["Item Sub-Type"] == "Designs for Health")
            self.assertEqual(supplement["Gross Charges"], "792.19")
            self.assertEqual(supplement["Discount"], "118.79")
            self.assertEqual(supplement["Discount Line (QBO)"], "-118.79")
            self.assertEqual(supplement["Net Revenue"], "673.40")
            self.assertEqual(sum(Decimal(r["Net Revenue"]) for r in result), Decimal("1013.40"))

    def test_inconsistent_row_is_rejected(self):
        row = {"Charge Type": "Labs", "Item Sub-Type": "",
               "Total Charges": "100.00", "Total Discount": "10.00",
               "Charges Minus Discount": "95.00"}
        with self.assertRaisesRegex(ValueError, "does not reconcile"):
            aggregate([row])

    def test_empty_report_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "no rows"):
            aggregate([])

if __name__ == "__main__":
    unittest.main()
