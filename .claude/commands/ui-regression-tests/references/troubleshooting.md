# Troubleshooting

Recurring failure modes for Marketplace-app regression tests, with confirmed fixes. When a test
fails at Step 5, find the matching symptom here and apply the fix before guessing.

This file is **append-only knowledge**: add a new entry only when you hit a failure that isn't
already covered AND you've confirmed the fix (the test passed afterwards). See Step 6 in `SKILL.md`
for the capture rules. Keep the `Symptom → Cause → Fix` shape so entries stay scannable.

---

## SSL / certificate errors (`net::ERR_CERT_AUTHORITY_INVALID`, `SEC_ERROR_*`)

- **Symptom:** Navigation fails with a certificate / SSL error before the page loads.
- **Cause:** `*.ip.linodeusercontent.com` hosts use self-signed certs. The global `context` fixture
  already sets `ignore_https_errors=True` (`conftest.py`), so this only appears when the page was
  **not** created through the `context` fixture — e.g. a raw `browser.new_page()` or a second tab
  opened without inheriting the context options.
- **Fix:** Use the `context` fixture as the page in every test. If you need a second tab, open it
  from the same context (`context.context.new_page()` / `BasePage.open_new_tab`) so it inherits
  `ignore_https_errors`.

---

## Every page returns `401 Unauthorized`

- **Symptom:** The app loads nothing; the browser shows a native Basic Auth prompt or all requests
  return 401.
- **Cause:** The app sits behind HTTP Basic Auth (e.g. htpasswd) and no credentials were supplied
  to the browser context. The global `http_credentials` fixture returns `None` by default.
- **Fix:** Override `http_credentials` in the app's `conftest.py` (see the "HTTP Basic Auth"
  template in `references/templates.md`). The global `context` fixture forwards it to
  `new_context(http_credentials=...)` automatically — no test changes needed.

---

## First-run configuration page never appears

- **Symptom:** A test that expects the first-run setup/onboarding page lands on the normal
  dashboard instead, and its assertions fail.
- **Cause:** The first-run configuration page shows **once** per instance. A previous run already
  completed it on this VM, so it's gone for good.
- **Fix:** Re-run against a freshly deployed VM for the first-run scenario, or assert the
  post-configuration state (the dashboard the app shows after setup) instead of the setup page.
  Don't write tests that depend on the first-run page being present on a re-used VM.

---

## `SSHException: Host key verification failed`

- **Symptom:** Reading the MOTD or credentials (Step 2) raises
  `Host key verification failed for <host>. The server's host key does not match the expected key.`
- **Cause:** The SSH helper pins the host key on first contact (TOFU, `utils/ssh.py`). The VM was
  rebuilt/redeployed, so it now presents a different host key than the pinned one.
- **Fix:** Expected after a redeploy — there is no stale `known_hosts` to clear (the key is pinned
  per-process). Just re-run against the current VM. If it persists on a stable VM, you're pointing
  at the wrong `LINODE_IPV4`.

---

## `KeyError` on `app_credentials["..."]`

- **Symptom:** A test raises `KeyError` when reading a credential key.
- **Cause:** `app_credentials` parses the credentials file verbatim as `Key: Value` pairs
  (`utils/ssh.py`). The key string in the test doesn't match the file exactly (wrong casing, extra
  space, renamed field).
- **Fix:** Re-read the credentials file (Step 2b) and copy the key name exactly as printed, then
  use it verbatim in the test.

---

## `App URL` or `Credentials File` missing from `/etc/motd`

- **Symptom:** Step 2a returns `None` for `App URL` or `Credentials File` — the MOTD exists but
  doesn't contain one or both of those keys.
- **Cause:** Some apps (e.g. CyberPanel, which uses LiteSpeed's own setup scripts) write
  deployment information to the interactive shell welcome message instead of, or in addition to,
  `/etc/motd`. The standard MOTD parser never sees it.
- **Fix:** Open an interactive SSH shell session and capture the welcome output printed on first
  login — it typically contains the app URL, admin panel path, and instructions for retrieving
  credentials. Use that output to determine `base_url` and the credentials file path before
  proceeding with Step 2b.

