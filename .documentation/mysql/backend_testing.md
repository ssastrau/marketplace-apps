# Backend Testing — mysql

## 2026-07-29

### Scope

Standalone run (`/backend-regression-tests mysql --scenarios "cover smoke scenarios including
writing and reading data"`). No prior `.documentation/mysql/` artifacts existed, so scenarios came
from the operator, not from pipeline phase documents.

The app's `DATABASE` UDF selects the engine and `test-vars.sh` defaults to `mariadb`, not `mysql`.
The operator chose to deploy and test the **CI default (`mariadb`)**, since that is what a default
Marketplace deploy produces. The `mysql` variant of the UDF is not covered by this suite.

Scenarios tested:

1. Service liveness — unit active plus an authenticated `SELECT 1`.
2. Port posture — server listening on 3306, loopback-only.
3. Write/read round-trip — create a database + table, insert a row, read the value back.
4. Auth rejection — a wrong password is refused.

Deliberately out of scope, as beyond smoke: a restart-durability check and a deploy-hardening check
(anonymous accounts / default `test` database removed). Both were written and passing, then dropped
at the operator's call — the restart test also mutated the box, which no other test does.

### Discovered on the live box

- **Engine / unit:** MariaDB 10.11.14 under the `mariadb` systemd unit (not `mysql`), installed by
  the shared `linode_helpers/roles/database` helper via `mariadb.yml`.
- **Bind posture:** `bind-address = 127.0.0.1` in `/etc/mysql/`; `ss -tlnH 'sport = :3306'` reports
  `LISTEN 0 80 127.0.0.1:3306 0.0.0.0:*`. UFW is active and allows **only** 22/tcp. This is the
  intended posture — the suite asserts loopback-only and explicitly asserts the port is *not* bound
  on `0.0.0.0`.
- **Vantage:** all checks run on the box through `remote_exec`. There is no HTTP surface; the
  `App URL` line in `/etc/motd` is vestigial for this app, so the app conftest defines no `base_url`.
- **Client:** `/usr/bin/mysql`. Invoked as
  `MYSQL_PWD=<pass> mysql --protocol=TCP -h 127.0.0.1 -u root -N -B -e '<sql>'`.
  `--protocol=TCP` forces the TCP path (MariaDB would otherwise resolve `127.0.0.1` back to
  `localhost` and could match the socket account); `-N -B` strips headers and formatting so
  assertions compare raw values.
- **Credential keys** (`/home/admin/.credentials`): `Sudo Username`, `Sudo Password`,
  `MySQL Root Password`. Tests read the last one via `app_credentials`.
- **Auth behaviour:** a wrong password exits non-zero with `Access denied` on stderr — the assertion
  reads stderr, not stdout.
- **Root SSH:** `test-vars.sh` leaves `DISABLE_ROOT=No`, so the securessh tasks skip and password
  root login stays available; the pytest run needs no `LINODE_ROOT_USER` override.

### Files created

- `tests/regression_tests/services/mysql/__init__.py`
- `tests/regression_tests/services/mysql/mysql_service.py` — `MysqlService` (`unit_active`,
  `port_listener`, `query`); no assertions.
- `tests/regression_tests/apps/linode-marketplace-mysql/conftest.py` — `credentials_file_path` only.
- `tests/regression_tests/apps/linode-marketplace-mysql/test_scenarios.py` — 4 tests.

Shared infra (`remote_exec`, `http_session`, `utils/ssh.run_remote_command`,
`services/__init__.py`) already existed from earlier backend runs and was **reused untouched** — no
shared file was modified by this run.

### Boxes deployed

- `101672112` — exploration box; probing and the first suite run (6/6 passed).
- `101672552` — fresh verification box; carried the final green run.

Both were deployed CI-style (bare `linode/ubuntu24.04`, then `test-vars.sh` + `mysql-deploy.sh` from
`akamai-compute-marketplace/main`) with generated root passwords. Teardown is a manual operator step.

### Issues

None blocking. Notes worth carrying forward:

- The `mysql` app deploying MariaDB by default is a genuine trap for test authoring — a suite written
  against a `mysql` unit name would fail on every default deploy.
- The deploy's first `PLAY RECAP` comes from `provision.yml`, well before the app is installed;
  monitoring must wait on `Installation Complete`, not on `PLAY RECAP`.
- No new `troubleshooting.md` entries: the suite passed on its first run against both boxes, so no
  failure mode was encountered to confirm and record.
