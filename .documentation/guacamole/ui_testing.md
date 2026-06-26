## Guacamole — UI regression test run (2026-06-26)

### Scope
1 startup scenario, 2 login scenarios (valid credentials, invalid credentials).

### Discovered
- Login flow: username textbox (`get_by_role("textbox", name="Username")`), password textbox (`get_by_role("textbox", name="Password")`), Login button (`get_by_role("button", name="Login")`). Successful login lands on the home dashboard. Failed login surfaces an inline "Invalid Login" paragraph above the form.
- Page title(s): "Apache Guacamole" (used in `to_have_title()`)
- First-run configuration page: none — a fresh deploy goes straight to the login dialog.
- Note: on the very first navigation the Playwright session was already authenticated (browser carried state). Logged out via the user menu → Re-login button to reach the clean login form.

### Created
- Page objects: `pages/guacamole/guacamole_login_page.py`, `pages/guacamole/guacamole_home_page.py`
- Tests: `test_guacamole_startup`, `test_guacamole_login`, `test_guacamole_login_invalid_credentials`

### Notes / issues
- All 3 tests passed on first run in 23.55 s.
- Credential keys used: `Guacamole Admin Username`, `Guacamole Admin Password`.
- Troubleshooting entries added this session: none.
