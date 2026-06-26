## LiveSwitch — UI regression test run (2026-06-30)

### Scope
Startup only — verify the LiveSwitch admin console is running and serving the initialization wizard.

### Discovered
- Login flow: none on first run — app redirects to a 4-step first-run setup wizard (`#/initialize`)
  rather than a login form; the wizard collects License Key, User Account, and Application config
- Page title: "LiveSwitch Console"
- App URL path: `/admin` (included in `base_url`; MOTD reports the full `/admin` path)
- Stable landmarks on the setup wizard: logo image ("LiveSwitch Configuration Console") and
  "Next" button
- Credentials file contains only infra-level keys: `Sudo Username`, `Sudo Password`,
  `Postgres Password`, `RabbitMQ User`, `RabbitMQ Password` — no app admin credentials

### Created
- Page objects: `pages/liveswitch/liveswitch_home_page.py`
- Tests: `test_liveswitch_startup`

### Notes / issues
- `base_url` includes `/admin` path (not just root host) to match the MOTD-reported App URL
- `app_credentials` fixture is not used by any test; `credentials_file_path` is defined in conftest
  for suite consistency
- No login test — first-run wizard requires a license key from Frozen Mountain that is not
  available in the credentials file
- Troubleshooting entries added this session: none
