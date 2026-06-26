## Grav — UI regression test run (2026-06-25)

### Scope
Startup of admin login page, admin login, and creating a page that's verified by navigating to its
public URL and checking the body text.

### Discovered
- Login flow: `input[name="data[username]"]` / `input[name="data[password]"]`, "Login" button.
  Redirects to `Dashboard | Grav` on success.
- Page title(s): "Grav Admin Login | Grav" (login), "Dashboard | Grav" (dashboard).
- Add Page flow: "Add" button on `/admin/pages` opens a modal (Page Title + auto-derived Folder
  Name); "Continue" lands on the page editor. Body content is a CodeMirror editor over a hidden
  textarea — Playwright can't type into it directly; set the value via the CodeMirror instance API
  (`el.CodeMirror.setValue(text)`) instead.
- The created page's folder name becomes its public URL slug (e.g. "Test Automation Page" →
  `/test-automation-page`), auto-derived from the title.
- First-run configuration page: none — login goes straight to the dashboard.

### Created
- Page objects: `pages/grav/grav_login_page.py`, `pages/grav/grav_pages_list_page.py`,
  `pages/grav/grav_page_editor_page.py`, `pages/grav/grav_published_page.py`
- Tests: `test_grav_startup`, `test_grav_login`, `test_grav_create_page`

### Notes / issues
- The "Add" button's accessible name has a leading space/hidden icon character (` Add`, not exactly
  `Add`), so `get_by_role("button", name="Add", exact=True)` times out with zero matches. Fixed by
  dropping `exact=True` for non-exact (whitespace-tolerant) matching.
- Unlike Drupal/Gitea, re-running "create page" against the same folder name in Grav overwrites the
  existing page in place rather than creating a duplicate — confirmed no duplicate-content cleanup
  was needed here even after multiple repeated test runs during debugging.
- All 3 tests pass against a freshly deployed instance.
- Troubleshooting entries added this session: none (the "Add" button issue is app-specific, not a
  recurring pattern worth generalizing).
