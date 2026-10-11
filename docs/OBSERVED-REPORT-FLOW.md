# Observed report steps

The supplied screenshots show:

1. Analytics > List of Reports.
2. Financials by Category > Summary of Category (Type/Subtype) Charges and Payments > + With Patient, Provider, and Date of Payment.
3. Change Date Filter: choose **Your selection** for Starting Date for Period and Ending Date for Period. Use the same reporting date for both.
4. Leave the other required/identifier prompts unchanged; click **Run Report**.
5. In the results table, remove the **Practitioner** page-by grouping by clicking its X.
6. Open export options using the spreadsheet/export toolbar icon.
7. Choose **Whole report** and **CSV file format**, then **Export**.
8. The resulting CSV is UTF-16; the final Date=Total row is a grand total, not a sale.

The provided report contains sensitive records. Source files and screenshots are not checked into this repository.

The current adapter only parses local files and is not wired to remote authentication, browser downloads or employee email.
