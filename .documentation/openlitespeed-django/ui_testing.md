## OpenLiteSpeed Django — UI regression test run (2026-07-02)

### Scope
Same scenarios as the plain `django` app: admin startup, admin login, "View site" navigating to
the public sample site. No coverage added for the separate OpenLiteSpeed web admin panel (port
7080) since it wasn't requested and is a distinct app/login.

### Discovered
- Login flow: standard Django admin login form (`#id_username`, `#id_password`,
  `input[type='submit']`), identical to the plain `django` app.
- Page title(s): "Log in | Django site admin" (login), "Site administration | Django site admin"
  (dashboard).
- Public sample site is a bare `<body>Hello, world!</body>` with no `<title>` and no heading
  element — used `get_by_text("Hello, world!")` instead of a heading role locator.
- First-run configuration page: none.
- `/etc/motd`'s `App URL:` key is blank for this app — the real URLs (OpenLiteSpeed web admin,
  sample Django site, Django admin page) are listed as separate bullets instead. Used the "sample
  Django admin page" bullet's path (`/admin`) for `base_url`.

### Created
- Page objects: `pages/openlitespeed_django/openlitespeed_django_login_page.py`,
  `openlitespeed_django_dashboard_page.py`, `openlitespeed_django_site_page.py`
- Tests: `test_openlitespeed_django_admin_startup`, `test_openlitespeed_django_admin_login`,
  `test_openlitespeed_django_view_site`

### Notes / issues
- Credential keys used: `Django admin user`, `Django admin password` (file also contains
  `OpenLiteSpeed admin password`, `Sudo Username`, `Sudo Password`, unused by these tests).
- Troubleshooting entries added this session: "`App URL:` key is present but blank, with real URLs
  listed on separate bullet lines" — confirmed to recur on `openlitespeed-wordpress` too (same
  motd.j2 pattern).
- Full suite (3 tests) passed against the freshly deployed VM.
