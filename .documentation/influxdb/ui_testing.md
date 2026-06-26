## InfluxDB — UI regression test run (2026-06-26)

### Scope
3 scenarios: startup (login page renders), login (valid credentials), create bucket and verify it appears in the list.

### Discovered
- Login flow: navigate to `{base_url}/signin` (direct path required — navigating to `base_url` adds a client-side redirect that delays form rendering). Inputs use `data-testid`: `username`, `password`, `button`.
- Page title(s): `"InfluxDB"` on `/signin`; `"Get Started | InfluxDB | InfluxDB"` post-login.
- Post-login landmark: `heading "Get Started"` (level 1). URL after login contains the org ID: `/orgs/{orgId}` — extracted via regex for use in subsequent navigation.
- Buckets page: `data-testid="Create Bucket"`, `data-testid="bucket-form-name"`, `data-testid="bucket-form-submit"`. Created bucket name appears as visible text in the list.
- Credential keys: username `admin` (literal, from credentials file structure); password key `admin Password`.
- First-run configuration page: none.

### Created
- Page objects: `pages/influxdb/influxdb_login_page.py`, `pages/influxdb/influxdb_home_page.py`, `pages/influxdb/influxdb_buckets_page.py`
- Tests: `test_influxdb_startup`, `test_influxdb_login`, `test_influxdb_create_bucket`

### Notes / issues
- The startup test required `timeout=30000` on `to_be_visible()` for the login form — InfluxDB's React SPA renders asynchronously after navigation even when targeting `/signin` directly.
- The `test_influxdb_create_bucket` test extracts the org ID from `context.url` after waiting for the "Get Started" heading. Using `page.wait_for_url()` with a glob pattern was unreliable; waiting for the post-login heading is the correct approach.
- `test-automation-bucket` was created during exploration and deleted via the UI before the test run so the VM was in fresh-deploy state.
- Troubleshooting entries added this session: "SPA login form not found within the default assertion timeout".
