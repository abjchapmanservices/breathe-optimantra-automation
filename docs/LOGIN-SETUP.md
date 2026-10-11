# OptiMantra login details

Verified public login URL:
https://www.optimantra.com/optimus/om/public/login

Public page shows practitioner/patient login toggle, Email and Password fields,
a required agreement checkbox, and a Log in button. The page also mentions 2FA,
though not all accounts necessarily use it.

The repository includes a URL validator and a **deliberately disabled**
login adapter. The adapter does not sign into any real account.

Before enabling:
1. Obtain OptiMantra's approval/terms for automated report access.
2. Confirm permitted HIPAA-appropriate runtime and storage controls.
3. Verify actual login selectors in an approved environment using a test account.
4. Review the EULA and agreement checkbox with the account owner.
5. Never log secrets or upload HTML, screenshots, traces, browser profiles,
   downloads, or patient-level CSVs to GitHub.
6. Confirm the exact report navigation and minimal non-PHI output fields.
7. Add credential management only after the execution environment is approved.
