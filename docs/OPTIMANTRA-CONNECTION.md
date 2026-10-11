# OptiMantra connectivity checklist

## Current state
- Only a synthetic/offline browser smoke test is implemented.
- **No production login, credentials, report retrieval, scheduling, or emailing is enabled.**
- Do not enter OptiMantra credentials into repository files, issues, chat, screenshots, or logs.

## Before connecting a real account
1. Confirm the official OptiMantra login URL and whether browser automation is allowed.
2. Identify the stable UI route / labels for the report named in the SOP:
   **Daily Financials by Category/Summary of Category (Type/Subtype) Charges and Payments/+With Patient, Provider, and Date of Payment**.
3. Confirm permitted hosting and a HIPAA-appropriate arrangement for processing patient-level CSV exports.
4. Decide where raw report files may be stored, and which approved employee recipients may receive de-identified summaries.
5. Define the date timezone, failure alerts, and duplicate-run handling.
6. Keep actions manually triggered until an approved data flow and validation rules exist.

## SOP reporting fields
- Charge Type
- Item Sub-Type
- Total Charges
- Total Discount
- Charges Minus Discount

The prototype groups these fields and creates net revenue and negative discount preview columns. It does not create QuickBooks records.

## Security principles
- No patient-level reports, browser traces/screenshots, session state, or CSV attachments may be uploaded as GitHub artifacts or checked into GitHub.
- A private repository and GitHub Secrets do not by themselves establish HIPAA compliance.
- Use a security-reviewed, approved processing host before running PHI-bearing workflows.
