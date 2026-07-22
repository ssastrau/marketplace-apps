# Backend Testing — pgvector

## 2026-07-29

### Scope

Standalone run (`/backend-regression-tests pgvector`). The invocation passed the full directory name
`linode-marketplace-pgvector`; the skill expects the suffix, so it was normalised to `pgvector`.
No prior `.documentation/pgvector/` artifacts existed and no `--scenarios` was given, so the scenario
list was proposed from the playbook and the archetype table and confirmed by the operator.

Scenarios tested:

1. Service liveness — the Postgres cluster unit is running, `pg_isready` accepts connections, and an
   authenticated `SELECT 1` succeeds as the admin user.
2. Listener posture — bound on 5432, loopback only.
3. The `vector` extension is registered in the application database.
4. Vector similarity round-trip — insert three explicit unit vectors, confirm the nearest neighbour
   to `[0.9,0.1,0]` is the `x-axis` row, and confirm the stored vector reads back as `[1,0,0]`.
5. Distance operator — `'[1,0,0]'::vector <-> '[0,1,0]'::vector` equals `1.414214`.

Determinism note: the test supplies literal vectors rather than embedding text, so the expected
nearest neighbour and the distance are fixed arithmetic and cannot drift with a model version.

### Discovered on the live box

- **The umbrella unit is a trap.** `postgresql.service` is a oneshot that reports
  `active (exited)` and stays that way even if the cluster dies; `postgresql@16-main.service` is the
  unit that is genuinely `active (running)`. Asserting on `postgresql` alone would pass against a
  dead database. The service object resolves the cluster unit by glob
  (`systemctl list-units --type=service --all 'postgresql@*'`) so it does not hardcode the major
  version, and the test asserts both the `active` and `running` columns, backed by `pg_isready`.
- **Versions:** PostgreSQL 16.14 (Ubuntu 24.04), pgvector extension 0.6.0.
- **Bind posture:** `127.0.0.1:5432` and `[::1]:5432` only; UFW active with 22/tcp alone. Loopback is
  the intended posture, so the client runs on the box via `remote_exec` and the test asserts loopback
  while explicitly asserting the port is *not* on `0.0.0.0`.
- **Credential keys** (`/home/admin/.credentials`, mode 600): `Sudo Username`, `Sudo Password`,
  `Postgres Password` (the `postgres` superuser), `Postgres Admin User`, `Postgres Admin Password`.
  Tests authenticate as the admin user, not the superuser.
- **Application database** is `appname` and the admin user `postadmin` — both `test-vars.sh` defaults
  (`POSTGRESQL_APP_DB`, `POSTGRESQL_ADMIN_USER`). The DB name is a constant on the service object;
  the user comes from `app_credentials`.
- **MOTD** carries `Credentials File:` but no `App URL` — correct for this app; no `base_url`.
- **Root SSH** stays enabled (`DISABLE_ROOT=No`).

### Issue hit while writing the tests

`psql -c` with several statements prints a **command tag per statement on stdout**
(`CREATE TABLE`, `INSERT 0 3`, …) ahead of the final result, so an assertion comparing stdout to the
expected value fails with the tags prepended. Fixed by splitting the DDL/DML setup into its own call
so each assertion reads a query whose stdout is only its own result. This was the single test failure
of the run, fixed on the first attempt. It is recorded in `troubleshooting.md` as a recurring-likely
failure mode for any CLI client that echoes per-statement status.

### Files created

- `tests/regression_tests/services/pgvector/__init__.py`
- `tests/regression_tests/services/pgvector/pgvector_service.py` — `PgvectorService`; no assertions.
- `tests/regression_tests/apps/linode-marketplace-pgvector/conftest.py` — `credentials_file_path` only.
- `tests/regression_tests/apps/linode-marketplace-pgvector/test_scenarios.py` — 5 tests.

Shared infra (`remote_exec`, `http_session`, `utils/ssh.run_remote_command`, `services/__init__.py`)
already existed and was **reused untouched**.

### Boxes deployed

- `101680151` — exploration box; probing and the first green suite run.
- `101681593` — fresh verification box; carried the final green run.

Both provisioned from `linode-config.sh` values (`us-ord`, `g6-dedicated-4`, `linode/ubuntu24.04`)
and deployed by replicating `.github/scripts/app-installation.sh` — repo cloned on the box, then
`. ./test-vars.sh` and `./pgvector-deploy.sh` from `akamai-compute-marketplace/main`, with generated
root passwords. No private IP; this app does not need one.

### Issues

- The suite is idempotent-only: every check is read-only apart from the round-trip table, which uses
  a uuid-suffixed name and drops itself. 7a and 7b therefore converge; the fresh-deploy run was still
  done for parity.
- No app defects found. Unlike the other apps tested this session, pgvector deployed and behaved
  correctly on the first attempt.
