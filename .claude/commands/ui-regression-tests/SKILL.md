---
name: ui-regression-tests
description: >
  Generates Playwright + Pytest UI regression tests for a Linode Marketplace app by exploring
  the live app with a real browser first, then producing Page Object Model test files that match
  the project's existing conventions.

  Use this skill whenever a user wants to write, generate, or create UI tests for a Marketplace
  app — even if they just say "write tests for X" or "add tests for Y" without mentioning
  Playwright, Pytest, or regression testing explicitly.
---

# UI Regression Test Generator

Generate Playwright + Pytest tests for a Linode Marketplace app by exploring the live app first,
then producing real-locator POM test files that match existing project conventions.

## Flow overview

```
1. Check prerequisites  →  Playwright MCP connected? Inputs provided?
2. SSH into VM          →  Read credentials file, get username + password
3. Explore with browser →  Navigate live app, capture real selectors
4. Generate test files  →  POM page classes + test_scenarios.py + conftest.py
5. Run tests            →  Check troubleshooting.md on failure; ask user if stuck after 2 attempts
6. Record failure modes →  Append confirmed, novel issues to troubleshooting.md
7. Write session log    →  Summarize the run (no sensitive data) in logs/{date}-{app}.md
```

---

## Test suite conventions

Understanding these upfront avoids generating code that doesn't fit the project.

**Placeholders used throughout this skill:**
- `{app}` — the full Marketplace directory suffix under `apps/`, **hyphenated**, exactly as
  deployed (e.g. `apache-airflow`, `hashicorp-nomad`).
- `{slug}` — the Python package name under `pages/`: short, lowercase, **underscores** (must be a
  valid Python identifier). It is **not** mechanically derived from `{app}` — choose it by hand and
  reuse the existing folder if one already exists. Examples:
  - `apache-airflow` → `airflow` (prefix dropped)
  - `hashicorp-nomad` → `hashicorp_nomad` (hyphens become underscores)
- `{App}` — PascalCase class prefix for page objects (e.g. `Airflow`, `ArangoDB`).
- `{Feature}` — PascalCase name of a page/scenario (e.g. `Dashboard`, `Collections`).

```
tests/regression_tests/
├── conftest.py                          # global fixtures — do NOT redefine these
├── pages/
│   └── {slug}/
│       ├── __init__.py
│       ├── {slug}_login_page.py
│       └── {slug}_{feature}_page.py
└── apps/
    └── linode-marketplace-{app}/
        ├── conftest.py                  # app-specific: credentials_file_path, base_url
        └── test_scenarios.py
```

**Global fixtures already defined — never redefine in app conftest:**
- `ssh_credentials` — reads `LINODE_IPV4`, `LINODE_ROOT_USER`, `LINODE_ROOT_PASS` from env
- `app_credentials` — SSHes into VM, parses credentials file as `Key: Value` pairs
- `context` — a fresh Playwright **`Page`** per test (it yields a `Page` despite the name). Pass it
  wherever a page is expected, e.g. `{App}LoginPage(context)`.
- `http_credentials` — returns `None` by default, which is correct for **most apps** — leave it
  alone. Only override it in the app conftest in the rare case the app sits behind HTTP Basic Auth
  (e.g. htpasswd); then the global `context` fixture passes it to `new_context(http_credentials=...)`.
  See the "HTTP Basic Auth" template. Apps with a normal in-page login form do **not** use this.

---

## Step 1 — Check prerequisites

### Playwright MCP

Verify Playwright MCP tools are available (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`).

If **not available** → stop and tell the user:

> Playwright MCP is not connected. Please set it up:
> - **PyCharm**: Settings → Tools → GitHub Copilot → MCP Servers → Add:
>   Command: `npx`, Args: `@playwright/mcp@latest`
> - **VS Code**: already configured via `.mcp.json` in the repo root — restart agent chat.
>
> Then restart the chat and try again.

Do not fall back to Python scripts or any other method. Stop and wait.

### Required inputs

**Connection details come from environment variables — never from chat.** Do not ask the user to
paste the IP, username, or password into the chat, and never put them in a command's arguments. The
SSH helper and pytest read them from the environment at runtime:

| Env var | Description |
|---|---|
| `LINODE_IPV4` | Public IP of the VM |
| `LINODE_ROOT_USER` | SSH user (optional, defaults to `root`) |
| `LINODE_ROOT_PASS` | Root SSH password |

**Verify they're visible in your shell before continuing.** Each command runs in a fresh shell, so
variables the user `export`ed in their own terminal may not carry over to this session:

```bash
printenv LINODE_IPV4 LINODE_ROOT_PASS >/dev/null && echo OK || echo MISSING
```
(Output is redirected so the values — including the password — are never printed to the chat.)

If this prints `MISSING` → **stop and ask the user to make the variables available to this session,
then wait.** Do not prompt for the values in chat. Tell them:

> I can't see `LINODE_IPV4` / `LINODE_ROOT_PASS` in my shell — each command I run starts a fresh
> shell, so an `export` in your own terminal doesn't reach me. Please make them available to this
> session (e.g. add the `export` lines to your shell profile such as `~/.zshrc` and restart, or set
> them wherever this agent's shell is launched from), then tell me to continue.

**Ask the user for these (all missing ones in one message):**
- App name `{app}` and page `{slug}` — see the naming glossary above (e.g. app `apache-airflow`,
  slug `airflow`)
- Scenarios — plain-language description of what to test

---

## Step 2 — SSH into VM: get base URL and credentials

Every Marketplace app writes two things into `/etc/motd` at deploy time:
- `App URL:` — the full URL where the app is running → use this as `base_url` in tests
- `Credentials File:` — the absolute path to the app credentials file on the VM

Use the project's own SSH helper (`regression_tests.utils.ssh`) for both reads — it pins the host
key (TOFU) and parses `Key: Value` files into a dict. Run from the repo root with the suite on the
path. Both snippets read connection details from the environment — keep credentials out of the
command line:

### 2a — Read the MOTD

`/etc/motd` is itself `Key: Value` formatted, so the same parser works:

```bash
PYTHONPATH=tests python3 -c "
import os
from regression_tests.utils.ssh import get_credentials_via_ssh
host = os.environ['LINODE_IPV4']
user = os.environ.get('LINODE_ROOT_USER', 'root')
password = os.environ['LINODE_ROOT_PASS']
motd = get_credentials_via_ssh(host, user, password, '/etc/motd')
print('App URL:', motd.get('App URL'))
print('Credentials File:', motd.get('Credentials File'))
"
```

Expected `/etc/motd` contents:

```
Akamai Connected Cloud Marketplace App
App URL: https://172-233-219-65.ip.linodeusercontent.com:3000/ui/panel
Credentials File: /home/admin/.credentials
Documentation: https://www.linode.com/marketplace/apps/linode/app
```

- `App URL` value → this is `base_url`
- `Credentials File` value → this is `credentials_file_path`

**Edge case:** `App URL` or `Credentials File` not present → ask the user to provide them directly.

### 2b — Read the credentials file

```bash
PYTHONPATH=tests python3 -c "
import os
from regression_tests.utils.ssh import get_credentials_via_ssh
host = os.environ['LINODE_IPV4']
user = os.environ.get('LINODE_ROOT_USER', 'root')
password = os.environ['LINODE_ROOT_PASS']
creds = get_credentials_via_ssh(host, user, password, 'CREDENTIALS_FILE_PATH')
print(creds)
"
```

Credentials file format:

```
App Admin Email: admin@example.com
App Admin Password: secret123
```

- Save the **exact key names** — use them verbatim as `app_credentials["..."]` in tests.
  Exact key names matter because `app_credentials` parses the file as-is at runtime.
- Identify which key is the login username and which is the password.
- Use the actual values to log in during exploration (Step 3).

**Edge cases:**
- Credentials file not found or empty → ask the user to provide credentials manually
- App has no login (public app) → skip credentials and skip the login test

---

## Step 3 — Explore the app with Playwright MCP

Real selectors from a live app produce tests that actually work. Guessed selectors produce
tests that fail on first run.

> **Tests run on freshly deployed VMs.** Every exploration happens on a first-run,
> never-configured instance — so watch for a first-run configuration page (see below).

### Landing page
- `browser_navigate` → `base_url`
- `browser_snapshot` → record:
  - Exact page `<title>` for `to_have_title()`
  - Login form element selectors (inputs, labels, submit button)
  - Any stable visible landmark elements

### First-run configuration page detection
Some apps require a one-time configuration the first time you open them — creating an admin
account, naming a resource, setting a domain, finishing an install step, etc. It is **not always
labelled "setup" or "wizard"**; it's simply a page (or short sequence of pages) you complete once.
After it's done and you log in again it disappears forever and the app goes straight to its normal
dashboard. Because tests run on freshly deployed VMs, this first-run state IS what CI hits — so it
must be captured during exploration and driven by the tests.

**If the app shows a first-run configuration page (often right after the first login):**
- Record all input selectors and button locators for every step
- Complete each step to advance, recording as you go (you only get one chance per instance)
- Note what confirms completion (redirect to dashboard, created entity visible, etc.)
- Generate a page object for it like any other feature page, named for **what it does** rather than
  generically — e.g. `{slug}_setup_page.py`, `{slug}_onboarding_page.py`,
  `{slug}_create_station_page.py`.

### Login flow
- Fill username → fill password → click submit
- `browser_snapshot` post-login → record a stable element that confirms successful login
  (heading, nav item, unique dashboard element)

### Per-scenario pages
For each scenario beyond startup/login:
- Navigate to the relevant section
- `browser_snapshot` → record selectors for elements the scenario interacts with

### Locator priority
Prefer stable, semantic selectors. Dynamic class names (e.g. `css-1a2b3c`) break when the
app updates — avoid them entirely.

```
#id  →  [aria-label]  →  get_by_role(name=)  →  [name=]  →  XPath (last resort)
```

---

## Step 4 — Generate and save test files

See `references/templates.md` for exact code templates to use for each file type.

### Files to create

```
tests/regression_tests/pages/{slug}/__init__.py          (empty)
tests/regression_tests/pages/{slug}/{slug}_login_page.py
tests/regression_tests/pages/{slug}/{slug}_{feature}_page.py    (one per feature/scenario)
tests/regression_tests/apps/linode-marketplace-{app}/conftest.py    (no __init__.py — app dirs don't use one)
tests/regression_tests/apps/linode-marketplace-{app}/test_scenarios.py
```

A first-run configuration page (see Step 3) is just another `{slug}_{feature}_page.py` — name it
for what it does. Use the generic "Page class" template for it; there's no separate template.

### Code rules

These rules exist to keep tests independent, readable, and consistent with the rest of the suite:

- **No test classes** — plain `def test_...` functions only. Classes add indirection with no benefit here.
- **Re-login per test** — each test that needs auth must log in fresh. Shared sessions cause
  flaky failures that are hard to diagnose because one test's state bleeds into another.
- **Descriptive failure messages** — every `expect()` call takes a failure message as second
  argument. Without it, a failed assertion in CI gives no context about what was being checked.
- **No assertions in page classes** — page classes contain locators and actions only. Assertions
  belong in test functions so the intent of each test is visible in one place.
- **Absolute imports** — `regression_tests.pages.{slug}.{file}` (no relative imports), consistent
  with the rest of the suite.
- **Slow operations** — add `timeout=180000` (Playwright timeouts are in **milliseconds**;
  180000 ms = 3 min) for AI responses, heavy processing, or anything that regularly takes more
  than a few seconds.

---

## Step 5 — Run the tests

With `LINODE_IPV4`, `LINODE_ROOT_PASS` (and optionally `LINODE_ROOT_USER`) already exported in the
environment from Step 1 — do not pass them on the command line:

```bash
python3 -m pytest tests/regression_tests/apps/linode-marketplace-{app}/ -v
```

- Tests pass → done ✅ → go to Step 6
- Tests fail → **first check `references/troubleshooting.md`** for the symptom; if it's listed,
  apply the documented fix. Otherwise inspect the error and fix selectors/titles/locators, re-run.
- Still failing after 2 attempts → stop and ask the user for help

---

## Step 6 — Record new failure modes

Keep `references/troubleshooting.md` alive so future runs don't re-solve the same problems. After
the run, append a new entry **only if all four gates pass** — otherwise add nothing:

1. **Confirmed** — the test actually passed *after* your fix. Never record a guess or an unverified
   "this might be it."
2. **Novel** — the symptom isn't already covered in `references/troubleshooting.md` (you read it in
   Step 5, so you already know).
3. **Recurring-likely** — it's a class of failure that could hit another app (cert/auth/wizard/SSH/
   credential-parsing/locator patterns), not a one-off typo or an app-specific selector tweak.
4. **Structured** — follow the existing `Symptom → Cause → Fix` shape, and reference the relevant
   fixture/file/template so the fix is actionable.

The entry lands in the diff, so a human reviews it in the PR before it's trusted — that review is
the quality gate. When in doubt, leave it out; a wrong entry actively misleads the next run.

---

## Step 7 — Write the session log

Record what this session did so the next person (or run) has context. Write a file to
`.claude/commands/ui-regression-tests/logs/{YYYY-MM-DD}-{app}.md` (date from `date '+%Y-%m-%d'`,
then app name — e.g. `2026-06-17-apache-airflow.md`; create `logs/` if missing) using the "Session
log" template in `references/templates.md`.

Capture: scope/scenarios, what was **discovered** (titles, login flow, first-run page), files
**created** (page objects + test functions), and any **issues** worth noting (slow ops, flaky
areas, new troubleshooting entries added in Step 6).

**No sensitive data — this is a hard rule.** Never write credentials, passwords, tokens, or
credential-file contents into the log, and **do not include the base URL.** Credential *key names*
are fine; their *values* are not.
