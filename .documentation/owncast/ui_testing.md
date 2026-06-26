## Owncast — UI regression test run (2026-07-02)

### Scope
Two scenarios as requested: (1) startup with the default URL (public homepage), (2) admin login at
`{default_url}/admin` with the app credentials.

### Discovered
- Public homepage: no auth required. Page title "New Owncast Server" (Owncast's default
  server-name placeholder on a fresh instance), `<h1>New Owncast Server</h1>` landmark.
- `/admin` is protected by **HTTP Basic Auth**, not an in-page login form — confirmed by an
  unauthenticated request to `/admin` failing outright (`net::ERR_INVALID_AUTH_CREDENTIALS`) and
  succeeding once Basic Auth credentials were supplied. Modeled via the `http_credentials` fixture
  override (existing "Every page returns 401 Unauthorized" pattern in troubleshooting.md), not a
  page-object login flow.
- Admin panel confirmation: page title "Owncast Admin", `<h1>Owncast Admin</h1>`.
- First-run configuration page: none observed — admin panel loads straight to its dashboard.
- Note: during manual exploration I initially tested Basic Auth by embedding credentials in the
  navigation URL (`https://user:pass@host/admin`), which triggers browser-side `fetch()` errors in
  Owncast's own JS ("Request cannot be constructed from a URL that includes credentials") because
  that's a spec restriction on the Fetch API, not an app or test-suite issue. The generated tests
  use Playwright's `http_credentials` context option instead (proper `Authorization` header, no
  URL credentials), which doesn't hit this — confirmed by the full suite passing.

### Created
- Page objects: `pages/owncast/owncast_home_page.py`, `owncast_admin_page.py`
- Tests: `test_owncast_startup`, `test_owncast_admin_login`
- `conftest.py` overrides `http_credentials` with `Owncast Admin Username` / `Owncast Admin Password`

### Notes / issues
- Credential keys used: `Owncast Admin Username`, `Owncast Admin Password` (file also has
  `Sudo Username`, `Sudo Password`, unused by these tests).
- Full suite (2 tests) passed against the freshly deployed VM. Confirmed that setting
  `http_credentials` on the shared context doesn't break the unauthenticated homepage test — the
  browser only sends the Authorization header when challenged.
