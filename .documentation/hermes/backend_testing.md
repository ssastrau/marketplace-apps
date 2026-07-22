# Hermes — backend regression testing

## Hermes — backend regression test run (2026-07-22)

### Scope
Standalone run (no STATE.md). Hermes is an AI-agent platform, but on a **fresh deploy it is
installed-but-not-running**: the `hermes-gateway` service and web dashboard only come up after an
interactive `hermes gateway setup` onboarding wizard that needs an LLM API key (not provisioned).
Operator scope call → **install-smoke** suite (like crewai): verify the CLI runs and the install
layout is present. No service/port/dashboard tests (nothing runs until onboarding).

### Deploy history (see below — required a playbook fix)
- Deploys from `akamai-compute-marketplace/main` failed at the `npx playwright install-deps chromium`
  task (`rc 127, playwright: not found`), twice, deterministically.
- Root cause (investigated live): the role clones `NousResearch/hermes-agent` at **unpinned `main`**.
  A working run on 2026-07-19 succeeded only because `npx playwright` **auto-installed** `playwright@1.61.1`
  on demand; by 2026-07-22 upstream `main` had changed into a private `workspaces` monorepo (built
  around `agent-browser`) where `npx` no longer auto-installs playwright. Node/npm were identical
  (v22.23.1) across both runs — the only variable was the drifting upstream clone.
- Fix (applied to the playbook, `roles/hermes/tasks/hermes_setup.yml`): add an explicit
  `Install Playwright npm package` task before the `install-deps`/`install chromium` tasks, so the
  deploy no longer relies on npx's implicit auto-install. Verified live, then deployed clean from
  `ssastrau/marketplace-apps@backend-tests-batch-1`.
- Durable safeguard still recommended (not done here): pin the `git … version:` to a known-good ref
  instead of `main`, and make the browser step non-fatal (upstream treats it as a warning).

### Discovered
- Install shape: hermes-agent (Python via `uv` + Node.js) cloned into `/opt/hermes-agent`; CLI at
  `/opt/hermes-agent/.venv/bin/hermes`, symlinked to `/home/hermes/.local/bin/hermes`. No systemd
  unit, port, web/API surface, or app credentials on a fresh deploy (creds file is just `Sudo …`;
  MOTD has no `App URL`).
- `hermes --version` → `Hermes Agent v0.19.0 (2026.7.20)` (non-interactive, exit 0). `hermes --help`
  is also non-interactive. Node.js `v22.23.1`.
- Per the app guide's "Confirm Hermes and Gateway Statuses" step: `hermes gateway status` (run as the
  hermes user) → `✗ Gateway is not running` (exit 0) on a fresh, non-onboarded deploy — deterministic.
  Note the guide's `hermes agent status` command does **not** exist in v0.19.0 (`invalid choice: 'agent'`),
  so only `gateway status` is used.

### Created
- Service object: `services/hermes/hermes_service.py` (`HermesService` — SSH/CLI actions, no
  assertions). No app `conftest.py` (no `base_url`, no app credentials — only `remote_exec`).
- Tests (2): `test_hermes_up` (first — CLI runs and reports "Hermes Agent" + version) and
  `test_hermes_gateway_status` (the app guide's verification step — `hermes gateway status` as the
  hermes user reports `Gateway is not running` on a fresh deploy).
- Shared infra already present from earlier backend runs (nothing added).

### Verified
- Box deployed (id only): `101138827` — empty box → `test-vars.sh` + `hermes-deploy.sh` with
  `GH_USER=ssastrau BRANCH=backend-tests-batch-1` (the fixed branch). `PLAY RECAP: ok=52 failed=0`,
  Installation Complete.
- Suite type: **idempotent-only** (read-only CLI/layout checks). 2/2 passing twice on the fresh
  deploy `101138827`; treated as the Step 7b clean-deploy pass.

### Notes / issues
- Same category as crewai: a framework/CLI app whose real service surface is gated behind interactive,
  API-key-requiring onboarding — so the suite is install-smoke only, by design.
- A full gateway/dashboard test would require supplying an LLM API key and driving the onboarding
  wizard non-interactively — out of scope for this run.
- No troubleshooting entries added (deploy failures are out of scope for that file; the test steps
  were clean).
