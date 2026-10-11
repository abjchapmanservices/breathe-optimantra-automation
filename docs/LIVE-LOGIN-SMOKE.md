# Live login-only smoke test

This is an **opt-in, single execution only**. It does not download files,
open patient records, or write to QuickBooks. The login is intentionally not
enabled in the synthetic job or automatic scheduler.

## Prerequisites
- Vendor permission and Google Cloud BAA / security approval confirmed.
- Breathe account owner has reviewed and accepted the *current* login agreement.
- Existing dedicated Secret Manager secrets with runtime-only access.
- Validate the login fields and non-patient post-login navigation for the actual practitioner interface.

## Deployment design
- `Dockerfile.login` builds a Playwright Chromium environment.
- `src/login_smoke.py` checks an authenticated Analytics navigation label and exits.
- The code does not log credentials, cookies, screenshots, downloaded files or page bodies.
- Login script requires `LOGIN_SMOKE_ENABLED=true` and `OPTIMANTRA_TERMS_APPROVED=true`.
- Use a distinct Cloud Run job `breathe-login-smoke`; NEVER replace the
  synthetic `breathe-optimantra-reporting` job.
- Never schedule this job or set retries until after a reviewed successful login.

## Review before execution
The input selectors and sign-in consent layout are not verified against the
live authenticated UI. Depending on the actual page, the first attempt may
safely fail. The test will not attempt report access after login. Keep Cloud Run
logs and access restricted and ensure no broad network or trace capture.

The GitHub workflow builds and publishes code-only container images. Actual
runtime execution stays entirely inside approved GCP. GitHub workflows never
receive OptiMantra credential values.
