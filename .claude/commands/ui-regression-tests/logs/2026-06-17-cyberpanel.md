# CyberPanel — generation session log (2026-06-17)

### Scope
Startup, login, and create-website regression tests for linode-marketplace-cyberpanel.

### Discovered
- **Login flow**: `input[name="username"]` → `input[name="password"]` → `button.btn-login`;
  confirmed by `a.menu-item.active` with text "Dashboard" appearing after login.
- **Page titles**: `"Login - CyberPanel"` (login page), `"Dashboard - CyberPanel"` (post-login),
  `"Create New Website - CyberPanel"` (create website form).
- **Base URL**: not present as `App URL:` in `/etc/motd`. Found in the SSH shell welcome banner
  printed by LiteSpeed's `per-instance.sh` script on first login. Constructed using the standard
  `host.replace(".", "-")` pattern: `https://{linode_host}.ip.linodeusercontent.com:8090`.
- **Admin credentials**: not in `/home/admin/.credentials` (that file holds only OS sudo
  credentials in the standard `Key: Value` format). CyberPanel admin password lives at
  `/root/.litespeed_password` in `key=value` format (`admin_pass=<password>`). Admin username is
  always `admin`.
- **Credential file format mismatch**: `get_credentials_via_ssh` previously only parsed
  `Key: Value` (colon-space). Updated the shared utility (`utils/ssh.py`) to also handle
  `key=value` (equals-sign) lines, so `credentials_file_path = "/root/.litespeed_password"` and
  `app_credentials["admin_pass"]` now work without any app-specific fixture override.
- **Create website form**: requires Package select (`select[ng-model="packageForWebsite"]`), Owner
  select (`select[ng-model="websiteOwner"]`), domain input (`input[name="dom"]`), email input
  (`input[name="email"]`), and PHP version select (`select[ng-model="phpSelection"]`). Omitting
  any required field returns `Error message: '<fieldname>'` in `.alert.alert-danger`.
- **Success indicator**: `.alert.alert-success` — starts hidden (`ng-hide` class present); after
  ~20 s the AngularJS controller removes `ng-hide` and the element becomes visible. Test uses
  `timeout=60000` to accommodate the async backend operation.
- **First-run configuration page**: none — app goes straight to the login page on first access.

### Created
- Page objects:
  - `pages/cyberpanel/cyberpanel_login_page.py`
  - `pages/cyberpanel/cyberpanel_dashboard_page.py`
  - `pages/cyberpanel/cyberpanel_create_website_page.py`
- Tests: `test_cyberpanel_startup`, `test_cyberpanel_login`, `test_cyberpanel_create_website`

### Notes / issues
- **`App URL` / `Credentials File` not in MOTD**: `/etc/motd` existed but contained neither key.
  The actual app URL and credential instructions were printed in the interactive shell welcome
  message on first SSH login (output by LiteSpeed's `per-instance.sh`). If Step 2a returns `None`
  for either key, open an interactive shell session and capture the welcome output — it is the
  authoritative source for this app.
- **`utils/ssh.py` parser extended**: `get_credentials_via_ssh` now handles both `Key: Value` and
  `key=value` delimiters. This is a shared utility change that benefits any future app whose
  credentials file uses `=` as a separator.
- **Unique domain per run**: `test_cyberpanel_create_website` generates a timestamp-based domain
  (`testsite-<epoch>.example.com`) so the test is safe to re-run on the same VM without hitting a
  "domain already exists" error.
- Troubleshooting entries added this session: `App URL / Credentials File missing from /etc/motd`
