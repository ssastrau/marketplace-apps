## Peppermint — UI regression test run (2026-07-02)

### Scope
Three scenarios as requested: (1) startup, (2) admin login, (3) create an issue and verify it's
listed.

### Discovered
- Login flow: `#email` / `#password` inputs, "Sign In" button, at `/auth/login` (root redirects
  there). Page title is just "Peppermint" on every route — the SPA doesn't vary `<title>` per page,
  so headings/URLs matter more than title checks past the login page.
- First-run configuration page: after the very first successful login, the app redirects to
  `/onboarding` — a one-time welcome screen ("Welcome to Peppermint! A fully open sourced ticket
  management system.") with a single "To Dashboard" button. Clicking it lands on the normal
  dashboard; it never reappears for that instance afterward. Modeled as
  `PeppermintOnboardingPage.complete_if_present()` (same pattern as the OpenVPN license-agreement
  handling from a previous run), so the login/create-issue tests work whether or not the target VM
  has already consumed the one-time screen.
- Post-login confirmation: an "admin" account-menu button in the top bar (from the seeded default
  admin user).
- Create Issue flow: sidebar "New Issue" button opens a dialog with `title`/`name`/`email` inputs
  plus a ProseMirror rich-text description editor (`.ProseMirror[contenteditable='true']`) and a
  "Create Ticket" button. Submitting redirects to `/issues`, where the new ticket appears as a link
  whose accessible name includes the issue number, title, date, tag, status, and priority (matched
  via substring on the title).
- Credentials file has a non-flat, indented structure (Sudo / PostgreSQL Database / Peppermint Web
  Interface sections) — the existing `Key: Value` parser (`utils/ssh.py`) still extracts the right
  flat keys correctly since header lines like `PostgreSQL Database:` have no `": "` and are silently
  skipped, leaving `Admin Email` / `Admin Password` (web interface) distinct from `Username` /
  `Password` (Postgres). No parser changes needed.

### Created
- Page objects: `pages/peppermint/peppermint_login_page.py`, `peppermint_onboarding_page.py`,
  `peppermint_dashboard_page.py`, `peppermint_create_issue_page.py`, `peppermint_issues_page.py`
- Tests: `test_peppermint_startup`, `test_peppermint_login`, `test_peppermint_create_issue`

### Notes / issues
- Credential keys used: `Admin Email`, `Admin Password` (file also has `Sudo Username`,
  `Sudo Password`, and the Postgres `Username`/`Password`/`Database`, unused by these tests).
- First run against the exploration box surfaced a real bug (not a state issue):
  `PeppermintDashboardPage.account_menu_button` used `get_by_role("button", name="admin")`, which
  matched both the sidebar "Admin" nav button and the actual account-menu button (substring
  matching). Fixed with `exact=True`. Logged in `troubleshooting.md` as a new, recurring-likely
  pattern (distinct from the existing "duplicate content from VM reuse" entry).
- Re-running the full suite against the *same* (now non-fresh) exploration box correctly reproduced
  a strict-mode violation on `test_peppermint_create_issue` (multiple same-titled issues from
  repeated runs) — expected per the existing "create content" troubleshooting entry, not a bug.
- Full suite (3 tests) passed cleanly against a genuinely fresh VM, confirming both the onboarding
  handling and the `account_menu_button` fix hold up on first login.
