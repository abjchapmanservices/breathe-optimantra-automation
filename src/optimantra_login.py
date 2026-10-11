"""OptiMantra practitioner login adapter, deliberately disabled in automation.

Do not run against real accounts before approved hosting, provider permission,
and a PHI-safe reporting plan are confirmed. No credentials stored here.
"""
from urllib.parse import urlparse

LOGIN_URL = "https://www.optimantra.com/optimus/om/public/login"

def validate_login_url(url: str = LOGIN_URL) -> str:
    parsed = urlparse(url)
    if (parsed.scheme, parsed.hostname, parsed.path) != (
        "https", "www.optimantra.com", "/optimus/om/public/login"
    ) or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Unexpected OptiMantra login URL")
    return url

def login(page, username: str, password: str, *, live_enabled: bool = False):
    """Draft selector workflow. Disabled by default; not yet validated live.

    Call only in an approved runtime, and only after verifying provider terms.
    """
    if not live_enabled:
        raise RuntimeError("Live OptiMantra login is not enabled")
    if not username or not password:
        raise ValueError("Credentials are required")
    page.goto(validate_login_url(), wait_until="domcontentloaded")
    page.get_by_role("button", name="Practitioner login").click()
    page.get_by_role("textbox", name="Email").fill(username)
    page.get_by_label("Password", exact=True).fill(password)
    # Consent is not automated. Review any legally binding agreement with
    # the account owner before implementing a live acceptance step.
    raise RuntimeError("Live sign-in requires verified consent and selector review")
