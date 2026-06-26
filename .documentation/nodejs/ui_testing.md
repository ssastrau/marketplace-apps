## Node.js — UI regression test run (2026-07-01)

### Scope
Startup only — verify the app responds after deploy.

### Discovered
- No login — the app serves a single static `text/plain` response at `/` (rendered by the browser as a `<pre>` block): `NodeJS App - Powered by Akamai Cloud Compute Marketplace`.
- No `<title>` on the page (plain-text response, not HTML).
- No credentials file entries beyond the VM's sudo password — no app-level login exists.
- First-run configuration page: none.

### Created
- Page objects: `pages/nodejs/nodejs_home_page.py`
- Tests: `test_nodejs_startup`

### Notes / issues
- App conftest.py omits `credentials_file_path` — no test needs `app_credentials` since there's no app login.
- Troubleshooting entries added this session: none (no novel failure modes hit).
