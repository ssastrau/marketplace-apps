## Jaeger — UI regression test run (2026-06-26)

### Scope
One combined startup + login scenario: verify the app is running and accessible with valid credentials.

### Discovered
- Auth mechanism: HTTP Basic Auth (no in-page login form). Credentials sourced from `Jaeger Username` / `Jaeger Password` keys in the credentials file. The `http_credentials` conftest fixture overrides the global default so the browser context carries the auth header automatically.
- Page title: "Jaeger UI" (used in `to_have_title()`)
- Post-auth landmark: `menuitem "Search"` in the top navigation bar — confirms the app loaded and auth succeeded.
- First-run configuration page: none.
- Note: during exploration, embedding credentials in the navigation URL (`https://user:pass@host`) caused Jaeger's SPA router to double-append the URL on each navigation. This is a browser MCP exploration quirk only; tests are unaffected because the `http_credentials` fixture properly injects auth into the Playwright context before `navigate(base_url)`.

### Created
- Page objects: `pages/jaeger/jaeger_home_page.py`
- Tests: `test_jaeger_startup_and_login`

### Notes / issues
- Test passed on first run in 6.99 s.
- Credential keys used: `Jaeger Username`, `Jaeger Password`.
- Troubleshooting entries added this session: none (HTTP Basic Auth pattern already covered in troubleshooting.md).
