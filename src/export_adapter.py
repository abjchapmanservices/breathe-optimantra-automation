"""Aggregate OptiMantra financial export into category totals."""
import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

FIELDS = ("Charge Type", "Item Sub-Type", "Total Charges", "Total Discount")
NET_HEADERS = ("Charges - Discount", "Charges Minus Discount")

def cash(value):
    value = str(value or "").strip().replace(",", "").replace("$", "")
    if value.startswith("(") and value.endswith(")"):
        value = "-" + value[1:-1]
    return Decimal(value).quantize(Decimal("0.01"))

def summarize(path):
    with Path(path).open(encoding="utf-16", newline="") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        net_header = next((v for v in NET_HEADERS if v in headers), None)
        if not net_header or any(v not in headers for v in FIELDS):
            raise ValueError("Missing financial columns")
        totals = defaultdict(lambda: [Decimal("0.00")] * 3)
        detail_total = [Decimal("0.00")] * 3
        stated_total = None
        count = 0
        for line, row in enumerate(reader, start=2):
            category = (row["Charge Type"] or "").strip()
            amounts = [cash(row[name]) for name in
                       ("Total Charges", "Total Discount", net_header)]
            if (row.get("Date") or "").strip().casefold() == "total":
                if stated_total is not None:
                    raise ValueError("Duplicate totals row")
                stated_total = amounts
                continue
            if not category:
                raise ValueError(f"Missing category at row {line}")
            if amounts[0] - amounts[1] != amounts[2]:
                raise ValueError(f"Mismatch at row {line}")
            count += 1
            target = totals[(category, (row["Item Sub-Type"] or "").strip())]
            for i, val in enumerate(amounts):
                target[i] += val
                detail_total[i] += val
        if not count:
            raise ValueError("No detail records")
        if stated_total is not None and detail_total != stated_total:
            raise ValueError("Report totals do not reconcile")
    return [
        {"Charge Type": category, "Item Sub-Type": subtype,
         "Gross Charges": str(v[0]), "Discount": str(v[1]),
         "Discount Line (QBO)": str(-v[1]), "Net Revenue": str(v[2])}
        for (category, subtype), v in sorted(totals.items())
    ]
