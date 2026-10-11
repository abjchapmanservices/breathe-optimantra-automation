"""Process synthetic OptiMantra-format CSV data into daily category summaries.

This prototype uses only the Python standard library and makes no network calls.
"""
import argparse
import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED = ("Charge Type", "Item Sub-Type", "Total Charges",
            "Total Discount", "Charges Minus Discount")

def to_money(value):
    try:
        return Decimal(str(value).replace("$", "").replace(",", "").strip()).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Invalid monetary value") from exc

def aggregate(rows):
    totals = defaultdict(lambda: [Decimal("0.00"), Decimal("0.00"), Decimal("0.00")])
    count = 0
    for count, row in enumerate(rows, 1):
        if any(k not in row for k in REQUIRED):
            raise ValueError("Missing required report column")
        category = (row["Charge Type"] or "").strip()
        subtype = (row["Item Sub-Type"] or "").strip()
        if not category:
            raise ValueError(f"Blank charge type in row {count}")
        gross, discount, net = [to_money(row[k]) for k in REQUIRED[2:]]
        if gross - discount != net:
            raise ValueError(f"Row {count} does not reconcile")
        bucket = totals[(category, subtype)]
        for i, amount in enumerate((gross, discount, net)):
            bucket[i] += amount
    if count == 0:
        raise ValueError("Report contains no rows")
    result = []
    for (category, subtype), (gross, discount, net) in sorted(totals.items()):
        result.append({"Charge Type": category, "Item Sub-Type": subtype,
                       "Gross Charges": str(gross), "Discount": str(discount),
                       "Discount Line (QBO)": str(-discount), "Net Revenue": str(net)})
    return result

def process(input_path, output_path):
    with Path(input_path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or any(k not in reader.fieldnames for k in REQUIRED):
            raise ValueError("Missing required CSV headers")
        result = aggregate(reader)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = process(args.input, args.output)
    print(f"Created synthetic summary with {len(result)} groups")
