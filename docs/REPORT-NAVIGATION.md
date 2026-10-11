# Report selection: observed UI

From the user-provided screenshot, the OptiMantra **Report List** shows the following expanded hierarchy:

1. Financials by Category
2. Summary of Category (Type/Subtype) Charges and Payments
3. + With Patient, Provider, and Date of Payment

The main report screen also shows a **Change Date Filter** link, a **PAGE-BY Practitioner** control, and report toolbar icons. The screenshot alone does not establish how date controls and CSV export operate, or which toolbar icon corresponds to CSV.

## Implemented

`src/report_navigation.py` stores the hierarchy and a **disabled** draft locator routine. It is not connected to the login adapter or GitHub Actions production workflows.

## Still needed

- A screenshot with the target report selected and the Report List closed.
- The **Change Date Filter** dialog, without sensitive information, to understand the two date prompts.
- The CSV export menu after clicking the appropriate export control, with sensitive information obscured.
- Confirmation of OptiMantra permission for automation and a HIPAA-appropriate execution environment.

**Privacy:** The selected report can include patient-level fields. Do not upload the raw exported CSV, browser screenshots/traces, or patient information into GitHub.
