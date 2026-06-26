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
  template in `templates/test-file-templates.md`). The global `context` fixture forwards it to
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

## Strict-mode locator violation on a "create content" scenario (duplicate items found)

- **Symptom:** A test that creates content (article, post, menu item, etc.) and then asserts it
  appears fails with a Playwright strict-mode violation — the locator resolves to 2+ elements with
  the same name/title, even though the test only created one.
- **Cause:** Exploration (Step 3) submitted the same create-content form to learn the resulting page
  shape, and/or the test was re-run against the same VM without redeploying. Each run adds another
  item with the same fixture title, so the box no longer matches the single-item state a genuinely
  fresh deploy would have.
- **Fix:** Don't paper over this with `.first` or similar — that masks a real regression if the app
  ever actually creates duplicates. Instead, delete the content created during exploration (and any
  extra items from repeated test runs) via the app's admin UI before considering the test final, so
  the box returns to the state a fresh deploy would be in. Then re-run the full suite once, end to
  end, to confirm it passes cleanly with exactly one matching item. Treat "exploring a create-content
  scenario" as mutating shared state that you're responsible for cleaning up — same caution as the
  first-run page above, but for ordinary content instead of a one-time wizard.

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

---

## SPA login form not found within the default assertion timeout

- **Symptom:** `test_{slug}_startup` fails with `<element(s) not found>` on the username input locator
  even though the page title assertion (`to_have_title`) passes and the page URL is already at the
  login path (e.g. `/signin`). Error shows `timeout 5000ms`.
- **Cause:** Single-page applications (SPAs) route client-side — `page.goto("/signin")` resolves
  once the HTML shell loads, but the login form is rendered asynchronously by the JS framework
  (React, Vue, etc.). The default Playwright assertion timeout (5 s) expires before the form
  elements are injected into the DOM.
- **Fix:** Add `timeout=30000` to the `to_be_visible()` assertion on the login form element in
  `test_{slug}_startup`. This gives the SPA up to 30 s to render the form, which is consistent with
  how the suite already handles other slow operations. Also ensure you navigate directly to the
  login path (e.g. `{base_url}/signin`) rather than the SPA root (`base_url`) — the root adds an
  extra client-side redirect that further delays rendering.

