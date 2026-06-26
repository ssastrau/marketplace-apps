## Django — UI regression test run (2026-06-25)

### Scope
Startup of admin login page, admin login, and "View site" link confirming the public site loads.

### Discovered
- Login flow: `#id_username` / `#id_password` inputs, `input[type='submit']` ("Log in"), redirects to `/admin/` on success
- Page title(s): "Log in | Django site admin" (login), "Site administration | Django site admin" (dashboard), "The install worked successfully! Congratulations!" (public site, since no app URLs are configured yet on a fresh deploy)
- First-run configuration page: none — admin login goes straight to the dashboard

### Created
- Page objects: `pages/django/django_login_page.py`, `pages/django/django_dashboard_page.py`, `pages/django/django_site_page.py`
- Tests: `test_django_admin_startup`, `test_django_admin_login`, `test_django_view_site`

### Notes / issues
- All 3 tests pass against a freshly deployed instance.
- Public site page shown by "View site" is Django's default `DEBUG=True` placeholder page (no project URLs configured) — expected on a fresh marketplace deploy.
- Troubleshooting entries added this session: none
