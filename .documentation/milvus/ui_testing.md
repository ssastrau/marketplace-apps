## Milvus — UI regression test run (2026-06-30)

### Scope
MinIO Console startup, login, and bucket creation — verify MinIO is running, admin login works,
the license dialog is acknowledged, and a new bucket can be created.

### Discovered
- MOTD uses `Minio Admin Dashboard` key instead of `App URL`; `base_url` is derived from the VM
  host in the standard way (no port or path suffix needed)
- Login flow: navigate to root (redirects to `/login`); fields `Username` + `Password`;
  submit `Login` button; credentials keys: `Minio Username`, `Minio Password`
- Page title: `"MinIO Console"` throughout (login, browser, all states)
- First-run page: yes — a license acknowledgment dialog (`button "Acknowledge"`) appears after
  every login on a fresh browser session (session-based, stored in browser localStorage, NOT
  server-side). The dialog overlays the UI and blocks pointer events to the sidebar until dismissed.
  Both `test_milvus_minio_login` and `test_milvus_create_bucket` must acknowledge it.
- Post-login URL: `/browser/<first-bucket>` (redirects to the first existing bucket)
- Bucket creation: `button "Create Bucket"` (sidebar, `.first`) opens a drawer; `textbox "Bucket
  Name*"` + submit `#create-bucket`; on success redirects to `/browser/<bucket-name>` and
  `heading "<bucket-name>"` (h1) appears in main area
- Bucket name uses `uuid.uuid4().hex[:8]` suffix to avoid conflicts on repeated runs

### Created
- Page objects: `pages/milvus/milvus_login_page.py`, `pages/milvus/milvus_browser_page.py`
- Tests: `test_milvus_startup`, `test_milvus_minio_login`, `test_milvus_create_bucket`

### Notes / issues
- License acknowledgment dialog is session-based: every fresh Playwright context (new cookies /
  localStorage) triggers it again regardless of server state. Both login and create-bucket tests
  must explicitly expect and click the Acknowledge button after login.
- Troubleshooting entries added this session: none (failure was Milvus-specific, not a recurring
  pattern worth adding to the shared troubleshooting.md)
