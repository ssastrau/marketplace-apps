# Backend Testing — netfoundry-edge-router

## 2026-07-29

### Scope — read this before trusting the suite

Standalone run (`/backend-regression-tests netfoundry-edge-router --scenarios "some smoke
scenarios"`). No prior `.documentation/netfoundry-edge-router/` artifacts existed, so scenarios came
from the operator.

**This suite covers the unregistered (staged) state only.** The app's whole purpose is to register
an edge router against a NetFoundry network, which requires a `REGISTRATION_KEY` from a NetFoundry
console account. `test-vars.sh` defaults it to `none`, and the operator chose to deploy with that
default. In that state there is **no router service to probe**: no `ziti` unit exists, `salt-minion`
is installed but deliberately stopped and disabled, and the app binds no port. The suite therefore
asserts the staged install, not a working router.

**These assertions will be wrong for a registered router.** `test_netfoundry_salt_minion_staged_for_registration`
and `test_netfoundry_exposes_no_service_port` assert the *pre-registration* posture by design — a box
deployed with a real key starts salt-minion and installs the ziti router, and both tests would
correctly fail. Anyone adding key-based coverage should split the suite rather than loosen these.

Scenarios tested:

1. Registration entrypoint installed and executes (`router-registration --help`).
2. Bootstrap tools present and executable (`router-registration`, `zt-upgrade`, `vm-support-bundle`).
3. `salt-minion` installed at the pinned 3006 major, stopped, disabled, with no `minion_id`.
4. NetFoundry login help script installed for interactive shells.
5. UFW active, inbound denied by default, SSH allowed.
6. No listening TCP port beyond SSH and the local resolver.

### App bug found — invalid registration key yields a "successful" deploy

Deploying with the CI default `REGISTRATION_KEY=none` **does not fail the deploy**, contrary to what
the playbook's guard implies. `roles/edge-router/tasks/main.yml` skips registration only when the key
equals the literal `"paste key here"`, so the default `none` passes the guard and the task runs:

```
cmd: ["/opt/netfoundry/router-registration", "none"]
rc: 0
stderr: "... ERROR-Unable to determine registration path using key length for key none"
```

`router-registration` reports a hard error on **stderr but exits 0**, so Ansible records the task as
`changed`, the play recap is `failed=0`, and the deploy prints `Installation Complete` — leaving a
completely unregistered, non-functional edge router that looks like a healthy deploy. Two separate
issues worth raising with the app owner:

- the guard sentinel (`"paste key here"`) does not match the `test-vars.sh` default (`none`), so the
  no-key path attempts registration instead of skipping it;
- `router-registration` exits 0 on a fatal registration error, so no caller can detect the failure.

### Discovered on the live box

- **No app unit.** `systemctl list-units --all` matches nothing for `ziti`/`netfoundry`.
  `systemctl is-active ziti-router` returns `inactive` because the unit does not exist.
- **salt-minion:** `salt-minion 3006.27 (Sulfur)`, `is-active` → `inactive` (exit 3), `is-enabled` →
  `disabled` (exit 1). Because both commands exit non-zero in this state, the service object reads
  **stdout**, never the exit code.
- **Install dir** `/opt/netfoundry`: `router-registration`, `zt-upgrade`, `vm-support-bundle` all
  mode `755` root-owned, plus the hidden `.router_registration` real binary and the two login-readme
  files.
- **Firewall / ports:** UFW active, default deny inbound, only 22/tcp allowed. Listening TCP is SSH
  and `systemd-resolve` on 53 only.
- **Credential keys** (`/home/admin/.credentials`, mode 600): `Sudo Username`, `Sudo Password`. There
  is no app-level credential — the router has no local auth surface before registration.
- **MOTD** carries `Credentials File:` but **no `App URL`** — correct for this app; the app conftest
  defines no `base_url`.
- **Root SSH** stays enabled (`DISABLE_ROOT=No`), so no `LINODE_ROOT_USER` override is needed.
- `zt-upgrade --help` downloads ~18 MB before printing usage — avoided in the tests to keep the run
  fast; `zt-upgrade` is covered by presence/permission only.

### Files created

- `tests/regression_tests/services/netfoundry_edge_router/__init__.py`
- `tests/regression_tests/services/netfoundry_edge_router/netfoundry_edge_router_service.py` —
  `NetFoundryEdgeRouterService`; no assertions.
- `tests/regression_tests/apps/linode-marketplace-netfoundry-edge-router/conftest.py` —
  `credentials_file_path` only. Currently unused: no remaining test requests `app_credentials`, so
  this fixture is dead weight until credential coverage is added back.
- `tests/regression_tests/apps/linode-marketplace-netfoundry-edge-router/test_scenarios.py` — 6 tests.

Shared infra (`remote_exec`, `http_session`, `utils/ssh.run_remote_command`,
`services/__init__.py`) already existed and was **reused untouched**.

### Boxes deployed

- `101673989` — exploration box; probing and the first suite run.
- `101674842` — fresh verification box; carried the final green run.

Both deployed CI-style (bare `linode/ubuntu24.04`, then `test-vars.sh` +
`netfoundry-edge-router-deploy.sh` from `akamai-compute-marketplace/main`) with generated root
passwords. Teardown is a manual operator step.

### Issues

- The registration bug above is the headline finding; the suite cannot detect it, because from the
  box's perspective the staged state is indistinguishable from a deliberate no-key deploy.
- The suite is entirely idempotent (read-only inspection), so 7a and 7b converge; the fresh-deploy
  run was still done for parity.
- No new `troubleshooting.md` entries: no test failure occurred, so there was no fix to confirm.
