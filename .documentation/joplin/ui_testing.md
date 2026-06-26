## Joplin — UI regression test run (2026-06-29)

### Scope
Startup (login page verification) and login (admin credentials → admin dashboard).

### Discovered
- Login flow: email + password form at `/login`; redirects to `/admin/dashboard` on success
- Page title (login): "Joplin Server - Login"; heading: "Log in to Joplin Server" (h1)
- Page title (dashboard): "Joplin Server - Admin dashboard"; heading: "Joplin Server admin dashboard" (h2)
- Email input resolved to `input[name="email"]`; password input to `input[name="password"]` — stable name-attribute selectors
- Login button: role button "Login"
- Dashboard confirmation: "Joplin Server admin dashboard" heading + "Logout" button
- First-run configuration page: none observed; lands directly on dashboard after login
- Credential keys used: `"Joplin Login"` (email), `"Joplin Password"`
- Note: default `admin` password triggers a security warning banner on the dashboard — does not affect test flow

### Created
- Page objects: `pages/joplin/joplin_login_page.py`, `pages/joplin/joplin_dashboard_page.py`
- Tests: `test_joplin_startup`, `test_joplin_login`

### Notes / issues
- Troubleshooting entries added this session: none
