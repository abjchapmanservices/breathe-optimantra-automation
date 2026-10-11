# Next OptiMantra report automation milestone

The completed navigation smoke test located the Financials by Category report group but did not select the patient-level report.

The next controlled version should:
1. Select **Summary of Category (Type/Subtype) Charges and Payments** then **+ With Patient, Provider, and Date of Payment**.
2. Set both **Starting Date for Period** and **Ending Date for Period** to the same clinic-local reporting date.
3. Leave internal prompt/identifier values unchanged.
4. Run exactly one report in the approved Google Cloud environment.
5. Remove the Practitioner page-by grouping.
6. Export Whole report as CSV.
7. Validate all financial totals and strip patient-identifying fields before producing financial summaries.

Current code validates reporting dates only. It does **not** select or run the live report, and does not export files, send email, or post to QBO. DOM selectors for the report and date controls still need live validation.

For the first financial export, require an explicit date and a controlled single execution. Do not attach browser traces, raw HTML, screenshots, patient CSVs, or browser sessions to GitHub workflows or artifacts.
