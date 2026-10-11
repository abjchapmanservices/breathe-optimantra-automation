# Breathe OptiMantra Reporting Prototype

This is a **synthetic-only, non-PHI** proof of concept. No login to OptiMantra, Gmail, or QuickBooks is performed.

## Testing

Run `python -m unittest discover -s tests -v` to validate the aggregation logic.

Run `python -m src.process_report --input tests/fixtures/synthetic_daily.csv --output /tmp/breathe-summary.csv` to generate an example category-level summary.

The GitHub Actions workflow runs only against invented financial records. Do not commit real OptiMantra exports, patient data, secrets, browser sessions, or generated real reports.

## Later

After approval of the security and OptiMantra access model, implement secure collection, controlled email distribution, and separate QuickBooks integrations. Nothing here posts financial entries or sends emails.
