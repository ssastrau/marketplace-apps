## OpenLiteSpeed WordPress — UI regression test run (2026-07-02)

### Scope
Three scenarios as requested: (1) startup via the admin login page, (2) login to admin, (3) check
the public site page. No coverage added for phpMyAdmin or the separate LiteSpeed web admin panel
(port 7080) — out of scope for this run.

### Discovered
- Login flow: standard WordPress login form (`#user_login`, `#user_pass`, `#wp-submit`) at
  `/wp-login.php`; submitting redirects to `/wp-admin/` on success.
- Page title(s): "Log In ‹ My WP Site — WordPress" (login), "My WP Site" (public site homepage).
- Post-login confirmation: "Dashboard" `<h1>` on `/wp-admin/`.
- Public site confirmation: "Blog" `<h1>` on the homepage (default Twenty Twenty-Five theme index).
- First-run configuration page: none — WordPress was already fully installed with a default post
  ("Hello world!") and page ("Sample Page") on first load.
- `/etc/motd`'s `App URL:` key is blank here too, same as `openlitespeed-django` — confirms the
  troubleshooting entry "`App URL:` key is present but blank, with real URLs listed on separate
  bullet lines" recurs across OpenLiteSpeed-based apps. No new entry needed.

### Created
- Page objects: `pages/openlitespeed_wordpress/openlitespeed_wordpress_login_page.py`,
  `openlitespeed_wordpress_dashboard_page.py`, `openlitespeed_wordpress_site_page.py`
- Tests: `test_openlitespeed_wordpress_admin_startup`, `test_openlitespeed_wordpress_admin_login`,
  `test_openlitespeed_wordpress_site_page`

### Notes / issues
- Credential keys used: `Wordpress admin user`, `Wordpress admin password` (file also contains
  `Sudo Username`, `Sudo Password`, MySQL/phpMyAdmin/LiteSpeed passwords, unused by these tests).
- Full suite (3 tests) passed against the freshly deployed VM.
