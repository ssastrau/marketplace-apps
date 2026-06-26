## Nextcloud (AIO) — UI regression test run (2026-07-01)

### Scope
1. Startup — capture the one-time Nextcloud AIO setup passphrase.
2. Log in to the AIO interface using the captured passphrase.

A third scenario (submit a domain, start containers, wait until all reach "Running") was
attempted and then **dropped** — see Notes/issues below.

### Discovered
- App is Nextcloud **All-in-One** (docker-based): mastercontainer serves the AIO admin interface
  on port 8443 (`/setup` → `/login` → `/containers`), separate from the actual Nextcloud instance
  that becomes available afterward.
- The `/setup` page shows a plaintext passphrase **exactly once** per instance — it is generated
  lazily on first HTTP request (not present in `docker logs` or any file on disk beforehand), and
  disappears permanently once a domain is submitted on `/containers`. There is no SSH-based way to
  retrieve it after the fact.
- Login form: single password field (`#master-password`), no username.
- Once Nextcloud's containers are fully up, `/login` **permanently blocks further logins**
  ("The login is blocked since Nextcloud is running") — so login is only repeatable up until
  containers finish starting, not indefinitely.
- Domain submission (`/containers`) is **one-time and irreversible** per the page's own warning
  ("you will not be able to change it afterwards"). Domain validation is disabled for this app
  (`SKIP_DOMAIN_VALIDATION=true`).
- After "Download and start containers" is clicked, the page shows a live pull/start log. It does
  **not** reliably refresh itself to the final "Containers Running" list — confirmed by checking
  actual container health via SSH (`docker ps`) while a `Playwright expect(...).to_be_visible()`
  with a 600000ms timeout was still waiting: containers were healthy in ~1-2 minutes, but the
  in-browser assertion still hadn't seen the heading after the full 10 minutes.
- First-run configuration page: yes — the entire `/setup` → `/login` → `/containers` flow **is**
  the first-run flow, and most of it cannot be repeated on an already-provisioned VM.

### Created
- Page objects: `pages/nextcloud/nextcloud_aio_setup_page.py`,
  `pages/nextcloud/nextcloud_aio_login_page.py`, `pages/nextcloud/nextcloud_aio_containers_page.py`
  (now trimmed to just the one locator `test_nextcloud_login` needs)
- Fixtures: `aio_passphrase` (session-scoped, captures the one-time passphrase using its own page
  from the shared `browser` fixture rather than the per-test `context` fixture)
- Tests: `test_nextcloud_startup`, `test_nextcloud_login` — both **confirmed passing** on a
  freshly deployed VM (172.237.132.67).

### Notes / issues
- **Container-provisioning scenario was dropped.** Multiple fresh VMs were used trying to get a
  reliable wait for "all containers Running": Playwright's own auto-retrying `expect()` alone
  doesn't work here (the page doesn't self-refresh — see Discovered above), and an explicit
  `page.reload()`-based loop repeatedly hit `page.reload()`'s own 30s timeout while the page was
  busy pulling multi-GB container images. Rather than keep chasing it across more VMs, this
  scenario was cut — the suite now only covers startup + login.
- Every VM used for exploring or testing this app's setup flow becomes unusable afterward: the
  passphrase (`/setup`) and domain submission (`/containers`) are both one-time, and login itself
  becomes permanently blocked once containers finish starting. Expect to burn one fresh VM per
  real validation attempt of anything past login.
- This matches the existing "First-run configuration page never appears" entry in
  `troubleshooting.md` — no new entry was needed there. A new general note about
  reload-vs-`expect()` tradeoffs for slow, non-self-refreshing pages was added to the skill's
  `SKILL.md` Code rules instead, since that's a reusable lesson for other apps, not a Nextcloud-
  specific troubleshooting fix.
- The `NextcloudAioSetupPage.read_passphrase()` selector parses the page's rendered text
  (splitting on "Passphrase" / "Open Nextcloud AIO login") rather than a precise DOM locator,
  since only an accessibility-tree snapshot (not raw HTML) was captured for that one-time page —
  worth re-verifying against raw HTML if it ever needs adjustment.
