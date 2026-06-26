## Odoo — UI regression test run (2026-07-01)

### Scope
1. Startup — verify the one-time database-creation form renders.
2. Create the Odoo database using test data from a fixture (database name, admin email/password,
   phone, language, country, demo data).
3. Log in with the fixture's admin credentials and confirm the dashboard (Apps page) loads.

### Discovered
- Landing page for a never-configured instance is `/web/database/selector`: a one-time database
  creation form (Master Password, Database Name, Email, Password, Phone Number, Language, Country,
  Demo Data checkbox, "Create database" button). Page title: "Odoo".
- The Master Password field is pre-filled by the app itself with a freshly generated,
  instance-specific value on load — left untouched by the test, matching how the suite already
  handles Nextcloud AIO's one-time setup passphrase.
- Submitting the form provisions the database (installs base modules) and **auto-logs in**,
  redirecting to `/odoo/apps` (title "Apps") — no separate first-login step is needed.
- Once a database exists, `/web/database/selector` **permanently** stops showing the creation form
  (redirects to a simple "choose your database" link instead) — one-time, like Nextcloud AIO.
- Standalone login form: `/web/login`, with an `Email` textbox and a `Password` textbox, "Log in"
  button. Successful login also redirects to `/odoo/apps`.
- First-run configuration page: yes — the database-creation form at `/web/database/selector` is the
  first-run flow; it cannot be repeated once a database has been created on that VM.
- The credentials file (`/home/admin/.credentials`) does **not** contain an Odoo admin login —
  only the Linux sudo credentials, the intended Postgres/Odoo database name, and the Postgres
  password. The admin email/password are supplied by the test's own fixture, not read from the box.

### Created
- Page objects: `pages/odoo/odoo_database_creation_page.py`, `pages/odoo/odoo_login_page.py`,
  `pages/odoo/odoo_apps_page.py`
- Fixtures: `db_test_data` (session-scoped plain dict — database name, admin email/password, phone,
  language, country, demo data flag)
- Tests: `test_odoo_startup`, `test_odoo_create_database`, `test_odoo_login` — all **confirmed
  passing** on a freshly deployed VM.

### Notes / issues
- **Locator drift between exploration and pytest.** During exploration, the login page's Email
  field had an accessible name of "Email Choose a user" (an extra "Choose a user" chooser button
  folded into the name) — but this only appeared because the Playwright MCP browser carried
  saved-login state across multiple prior app explorations in the same long session. Under
  pytest's per-test fresh `browser.new_context()`, the same field is simply named "Email". The
  page object was updated to use the shorter, generic name — confirmed working against a second
  fresh VM. A general version of this lesson was added to `troubleshooting.md` ("Locator captured
  during exploration includes extra accessible-name text not present in pytest's run").
- Database provisioning (installing base modules) takes under a minute; `test_odoo_create_database`
  uses `timeout=180000` on its post-creation assertion as a safety margin, consistent with how the
  suite handles other slow first-run operations.
- Every VM used to explore or test this app's setup flow becomes unusable for that scenario
  afterward — the database-creation form is one-time. Two VMs were used this session: one for
  exploration (manual walkthrough matching the generated flow). On the second, `test_odoo_startup`
  and `test_odoo_create_database` passed together in one pytest run; `test_odoo_login` failed on
  the old locator in that same run, was fixed, and passed on a follow-up run against the same
  (already-provisioned) VM. All three have each individually been confirmed passing, but not yet
  in a single pytest invocation against one VM — worth doing on the next fresh deploy if a fully
  clean end-to-end run is needed.
