---
description: Optional QA step (post-deploy) — generate Playwright + Pytest UI regression tests for a deployed Marketplace app by exploring the live app with a real browser first, then producing Page Object Model test files that match the suite's existing conventions. User-invoked only.
disable-model-invocation: true
arguments: [app, slug, scenarios]
---

# UI Regression Tests (Optional QA — Generate Live-Explored Browser Tests)

Generate Playwright + Pytest tests for a Linode Marketplace app by exploring the **live deployed
app** first, then producing real-locator Page Object Model (POM) test files that match the existing
`tests/regression_tests/` suite conventions.

Outside the core pipeline (like `/app-docs`): it needs a **freshly deployed box** — exactly what
`/app-deploy` leaves running — but does not require the rest of the pipeline to have produced it.
Run it after `/app-deploy` when an app needs UI regression coverage.

## Usage
```
/ui-regression-tests <app> [--slug <slug>] [--scenarios "<free text>"]
```
Parse `--slug` and `--scenarios` from `$ARGUMENTS`; `$app` is the first positional. If `--slug` or
`--scenarios` is omitted, ask the operator once (all missing inputs in one message — see Step 1).
Connection details (box IP, SSH user, root password) come from the environment when set; otherwise
the skill asks the operator for them (see Step 1).

## Arguments
- `<app>`: the full Marketplace directory suffix under `apps/`, **hyphenated**, exactly as deployed
  (e.g. `apache-airflow`, `hashicorp-nomad`). Used for
  `tests/regression_tests/apps/linode-marketplace-<app>/`.
- `--slug <slug>`: the Python package name under `pages/` — short, lowercase, **underscores** (a
  valid Python identifier). **Not** mechanically derived from `<app>`; choose it by hand and reuse
  an existing folder if one exists (`apache-airflow` → `airflow`; `hashicorp-nomad` →
  `hashicorp_nomad`).
- `--scenarios "<free text>"`: plain-language description of what to test beyond startup + login.

## Grounding contract (non-negotiable)
Tests are written from what the live app actually shows — never from memory or guesswork:
- Every selector, page title, and login flow comes from a real `browser_snapshot` of the deployed
  app (Step 3). A guessed locator is a test that fails on first run.
- `base_url` and the app's login credentials come from the box's `/etc/motd` + credentials file
  (Step 2), read over SSH — never hardcoded into a test. (The *SSH connection* details are a separate
  thing: taken from the environment, or asked of the operator when unset — see Step 1.)
- If the live app can't be reached, or a required selector / credential can't be observed, **STOP
  and ask the operator.** Do not fabricate a test against an imagined UI.

## Flow overview

```
1. Check prerequisites  →  Playwright MCP connected? Inputs + env vars present?
2. SSH into VM          →  Read /etc/motd (base_url) + credentials file (user + password)
3. Explore with browser →  Navigate live app, capture real selectors
4. Generate test files  →  POM page classes + test_scenarios.py + conftest.py
5. Run tests            →  Check troubleshooting.md on failure; ask operator if stuck after 2 attempts
6. Record failure modes →  Append confirmed, novel issues to troubleshooting.md
7. Record artifact      →  Summarize the run (no sensitive data) in .documentation/<app>/ui_testing.md
```

## On any error — check `troubleshooting.md` first (standing rule)

**This applies at _every_ step, not just the test run.** The moment any command fails — an SSH
error in Step 2, a cert/auth/navigation error in Step 3, a `KeyError` parsing credentials, a pytest
failure in Step 5 — **read `troubleshooting.md` and look for the matching symptom before improvising
a fix.** Its entries deliberately span the whole flow: SSH host-key (`SSHException`), `KeyError` on
`app_credentials`, and missing `/etc/motd` keys all fire in **Step 2**; SSL/cert errors and `401`
Basic-Auth fire in **Step 3**; the first-run-page mismatch fires in **Step 5**. If the symptom is
listed, apply the documented fix; only if it isn't do you diagnose from scratch. New, confirmed,
novel failures get appended back per Step 6.

## Test suite conventions

Understanding these upfront avoids generating code that doesn't fit the project.

**Placeholders used throughout this skill:**
- `{app}` — see `<app>` above (hyphenated directory suffix).
- `{slug}` — see `--slug` above (underscored Python package name).
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

## Process

### Step 1 — Check prerequisites

**Optional STATE.md discovery (if the pipeline produced it).** If
`.documentation/<app>/STATE.md` exists, read it to pre-fill the app name and the live box IP
(`fresh_deploy_box.ip`) instead of asking. Treat it as a convenience — this skill works standalone
against any deployed box, so a missing `STATE.md` is fine.

**Playwright MCP.** Verify Playwright MCP tools are available (`browser_navigate`,
`browser_snapshot`, `browser_click`, `browser_type`).

If **not available** → stop and tell the operator:

> Playwright MCP is not connected. Add it to Claude Code, then restart this chat:
> ```bash
> claude mcp add playwright -- npx @playwright/mcp@latest
> ```
> (Or add a `playwright` server to a project `.mcp.json` or your user-scope `~/.claude.json`,
> mirroring how the team wires the `linode-team` MCP — see `.claude/README.md`.) Then restart the
> chat and try again.

Do not fall back to Python scripts or any other method. Stop and wait.

**Connection details — prefer the environment, otherwise ask the operator.** The SSH helper and
pytest read these from the environment at runtime:

| Env var | Description |
|---|---|
| `LINODE_IPV4` | Public IP of the VM |
| `LINODE_ROOT_USER` | SSH user (optional, defaults to `root`) |
| `LINODE_ROOT_PASS` | Root SSH password |

**Check whether they're already set.** Each command runs in a fresh shell, so variables the operator
`export`ed in their own terminal may not carry over to this session:

```bash
printenv LINODE_IPV4 LINODE_ROOT_PASS >/dev/null && echo OK || echo MISSING
```
(Output is redirected so the values — including the password — are never printed to the chat.)

If this prints `MISSING` → **ask the operator for the connection details** (box IP and root SSH
password; the SSH user defaults to `root`). If `STATE.md` was found above, offer its
`fresh_deploy_box.ip` as the IP so they only need to confirm it and supply the password.

> **Interim:** asking for the password in chat is a temporary convenience — a later refactor will
> move this back to env-only / key-based auth. Until then, once the operator provides the values,
> pass them to each command as inline env-var prefixes, e.g.
> `LINODE_IPV4=<ip> LINODE_ROOT_PASS=<pass> python3 ...` (don't echo the password back to the chat).

**Also ask the operator for any missing inputs (fold into the same message):**
- `{app}` and `{slug}` — see Arguments / the naming glossary above (e.g. app `apache-airflow`,
  slug `airflow`)
- Scenarios — plain-language description of what to test

### Step 2 — SSH into VM: get base URL and credentials

> **If anything here errors** (`SSHException: Host key verification failed`, a `KeyError` reading a
> credential key, or `App URL`/`Credentials File` missing from `/etc/motd`) → **check
> `troubleshooting.md` first** — each of these has a documented fix.

Every Marketplace app writes two things into `/etc/motd` at deploy time:
- `App URL:` — the full URL where the app is running → use this as `base_url` in tests
- `Credentials File:` — the absolute path to the app credentials file on the VM

Use the project's own SSH helper (`regression_tests.utils.ssh`) for both reads — it pins the host
key (TOFU) and parses `Key: Value` files into a dict. Run from the repo root with the suite on the
path. Both snippets read connection details from the environment; if the operator supplied them in
chat (Step 1), set them as inline env-var prefixes on these commands
(`LINODE_IPV4=<ip> LINODE_ROOT_PASS=<pass> PYTHONPATH=tests python3 ...`) and don't echo the
password back to the chat:

#### 2a — Read the MOTD

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

Example `/etc/motd` contents (the banner line varies per app — current branding is
`Akamai Connected Cloud <App> Quick Deploy App`; **only the `App URL:` and `Credentials File:` keys
matter for parsing**):

```
Akamai Connected Cloud <App> Quick Deploy App
App URL: https://172-233-219-65.ip.linodeusercontent.com:3000/ui/panel
Credentials File: /home/admin/.credentials
Documentation: https://www.linode.com/marketplace/apps/...
```

- `App URL` value → this is `base_url`
- `Credentials File` value → this is `credentials_file_path`

**Edge case:** `App URL` or `Credentials File` not present → see `troubleshooting.md`
(some apps write deploy info to the interactive shell welcome instead), or ask the operator.

#### 2b — Read the credentials file

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
- Credentials file not found or empty → ask the operator to provide credentials manually
- App has no login (public app) → skip credentials and skip the login test

### Step 3 — Explore the app with Playwright MCP

Real selectors from a live app produce tests that actually work. Guessed selectors produce
tests that fail on first run.

> **If navigation errors** (`net::ERR_CERT_AUTHORITY_INVALID` / `SEC_ERROR_*` SSL errors, or every
> request returning `401 Unauthorized`) → **check `troubleshooting.md` first** — both have a
> documented fix (self-signed cert handling; HTTP Basic Auth via `http_credentials`).

> **Tests run on freshly deployed VMs.** Every exploration happens on a first-run,
> never-configured instance — so watch for a first-run configuration page (see below).

**Landing page**
- `browser_navigate` → `base_url`
- `browser_snapshot` → record:
  - Exact page `<title>` for `to_have_title()`
  - Login form element selectors (inputs, labels, submit button)
  - Any stable visible landmark elements

**First-run configuration page detection.** Some apps require a one-time configuration the first
time you open them — creating an admin account, naming a resource, setting a domain, finishing an
install step, etc. It is **not always labelled "setup" or "wizard"**; it's simply a page (or short
sequence of pages) you complete once. After it's done and you log in again it disappears forever and
the app goes straight to its normal dashboard. Because tests run on freshly deployed VMs, this
first-run state IS what CI hits — so it must be captured during exploration and driven by the tests.

If the app shows a first-run configuration page (often right after the first login):
- Record all input selectors and button locators for every step
- Complete each step to advance, recording as you go (you only get one chance per instance)
- Note what confirms completion (redirect to dashboard, created entity visible, etc.)
- Generate a page object for it like any other feature page, named for **what it does** rather than
  generically — e.g. `{slug}_setup_page.py`, `{slug}_onboarding_page.py`,
  `{slug}_create_station_page.py`.

**Login flow**
- Fill username → fill password → click submit
- `browser_snapshot` post-login → record a stable element that confirms successful login
  (heading, nav item, unique dashboard element)

**Per-scenario pages.** For each scenario beyond startup/login:
- Navigate to the relevant section
- `browser_snapshot` → record selectors for elements the scenario interacts with

**Locator priority.** Prefer stable, semantic selectors. Dynamic class names (e.g. `css-1a2b3c`)
break when the app updates — avoid them entirely.

```
#id  →  [aria-label]  →  get_by_role(name=)  →  [name=]  →  XPath (last resort)
```

### Step 4 — Generate and save test files

See `${CLAUDE_SKILL_DIR}/templates/test-file-templates.md` for exact code templates to use for each file type.

**Files to create:**

```
tests/regression_tests/pages/{slug}/__init__.py          (empty)
tests/regression_tests/pages/{slug}/{slug}_login_page.py
tests/regression_tests/pages/{slug}/{slug}_{feature}_page.py    (one per feature/scenario)
tests/regression_tests/apps/linode-marketplace-{app}/conftest.py    (no __init__.py — app dirs don't use one)
tests/regression_tests/apps/linode-marketplace-{app}/test_scenarios.py
```

A first-run configuration page (see Step 3) is just another `{slug}_{feature}_page.py` — name it
for what it does. Use the generic "Page class" template for it; there's no separate template.

**Code rules** — these keep tests independent, readable, and consistent with the rest of the suite:

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

### Step 5 — Run the tests

pytest reads `LINODE_IPV4`, `LINODE_ROOT_PASS` (and optionally `LINODE_ROOT_USER`) from the
environment. If they're already exported (Step 1), run it plain; if the operator supplied them in
chat, prefix the command with inline env-var assignments:

```bash
# already exported:
python3 -m pytest tests/regression_tests/apps/linode-marketplace-{app}/ -v
# supplied in chat:
LINODE_IPV4=<ip> LINODE_ROOT_PASS=<pass> python3 -m pytest tests/regression_tests/apps/linode-marketplace-{app}/ -v
```

- Tests pass → done ✅ → go to Step 6
- Tests fail → **first check `troubleshooting.md`** for the symptom; if it's listed,
  apply the documented fix. Otherwise inspect the error and fix selectors/titles/locators, re-run.
- Still failing after 2 attempts → stop and ask the operator for help

### Step 6 — Record new failure modes

Keep `troubleshooting.md` alive so future runs don't re-solve the same problems. After
the run, append a new entry **only if all four gates pass** — otherwise add nothing:

1. **Confirmed** — the test actually passed *after* your fix. Never record a guess or an unverified
   "this might be it."
2. **Novel** — the symptom isn't already covered in `troubleshooting.md` (you read it in
   Step 5, so you already know).
3. **Recurring-likely** — it's a class of failure that could hit another app (cert/auth/wizard/SSH/
   credential-parsing/locator patterns), not a one-off typo or an app-specific selector tweak.
4. **Structured** — follow the existing `Symptom → Cause → Fix` shape, and reference the relevant
   fixture/file/template so the fix is actionable.

`troubleshooting.md` is a **tracked team file**: an edit lands in the diff and a human
reviews it in the PR before it's trusted — that review is the quality gate. When in doubt, leave it
out; a wrong entry actively misleads the next run.

### Step 7 — Record the `ui_testing.md` artifact

Record what this run did so the next person (or run) has context — this is the skill's per-app
artifact, the parallel of `e2e_testing.md` / `validation_findings.md`. Append a dated section to
`.documentation/<app>/ui_testing.md` (per-app working notes live under `.documentation/<app>/`
and are gitignored — never synced) using the artifact template in
`${CLAUDE_SKILL_DIR}/templates/test-file-templates.md`. Get the date with `date '+%Y-%m-%d'`; create
the file if it doesn't exist, append a new section if it does.

Capture: scope/scenarios, what was **discovered** (titles, login flow, first-run page), files
**created** (page objects + test functions), and any **issues** worth noting (slow ops, flaky
areas, new troubleshooting entries added in Step 6).

**No sensitive data — this is a hard rule.** Never write credentials, passwords, tokens, or
credential-file contents into the artifact, and **do not include the base URL.** Credential *key
names* are fine; their *values* are not.

## Output
- `tests/regression_tests/pages/{slug}/` — POM page classes (this command owns them).
- `tests/regression_tests/apps/linode-marketplace-{app}/` — `conftest.py` + `test_scenarios.py`.
- `troubleshooting.md` — appended only when a novel, confirmed failure mode was hit.
- `.documentation/<app>/ui_testing.md` — the per-app UI-testing artifact (no sensitive data).

## STOP — manual review (checkpoint)
Before relying on the generated tests, the operator verifies:
- [ ] Every selector / title / login flow traces to a real `browser_snapshot` of the live app — no guessed locators.
- [ ] `base_url` is derived from the VM host (not hardcoded); credentials read from the box, never pasted into chat.
- [ ] The full suite passes against a freshly deployed VM (`pytest ... -v`), including any first-run page.
- [ ] Global fixtures (`context`, `app_credentials`, `http_credentials`) are reused, not redefined in the app conftest.
- [ ] Any new `troubleshooting.md` entry passed all four gates (confirmed, novel, recurring-likely, structured).
- [ ] The `ui_testing.md` artifact contains no credential values and no base URL.

**Next:** operator reviews the generated tests + any `troubleshooting.md` diff, then commits them with the app's PR.
