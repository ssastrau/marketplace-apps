# Backend Testing — postgresql

## 2026-07-29

### Scope

Standalone run (`/backend-regression-tests postgresql`). The invocation passed the full directory
name `linode-marketplace-postgresql`; the skill expects the suffix, so it was normalised to
`postgresql`. No prior `.documentation/postgresql/` artifacts existed and no `--scenarios` was given,
so the scenario list was proposed from the playbook and the archetype table and confirmed by the
operator.

Scenarios tested:

1. Service liveness — the Postgres cluster unit is running, `pg_isready` accepts connections, and an
   authenticated `SELECT 1` succeeds as the `postgres` superuser over TCP.
2. Listener posture — bound on 5432, loopback only.
3. Data round-trip — create a uuid-named table, `INSERT` a row, `SELECT` the value back.

An auth-rejection check (wrong password refused) was offered and not selected.

### How this app differs from pgvector

Both apps import the same shared `database` helper, but this one is far thinner. It runs only
`database` with `database: postgresql`, which installs stock `postgresql` and sets a password on the
`postgres` superuser. There is **no application database and no admin role** — pgvector creates
`postadmin` and the `appname` DB on top of the same helper. Consequences for the tests:

- Tests authenticate as `postgres` against the default `postgres` database, not an app-specific role.
- The credential key is **`Postgresql Password`** — note the spelling, which differs from pgvector's
  `Postgres Password`. `app_credentials` parses the file verbatim, so the wrong spelling is a
  `KeyError` rather than a silent mismatch.

### Discovered on the live box

- **The umbrella unit is a trap**, same as pgvector: `postgresql.service` reports `active (exited)`
  and stays that way even if the cluster dies; `postgresql@16-main.service` is the unit genuinely
  `active (running)`. The service object resolves the cluster unit by glob so it does not hardcode
  the major version, and the test asserts both the `active` and `running` columns plus `pg_isready`.
- **Version:** PostgreSQL 16.14 (Ubuntu 24.04).
- **Auth:** `/etc/postgresql/16/main/pg_hba.conf` ships `local all postgres peer` but also
  `host all all 127.0.0.1/32 scram-sha-256`, so password auth over TCP works without the playbook
  touching `pg_hba`. This was verified before writing the tests rather than assumed — had only
  `peer` been present, the tests would have had to run psql as the `postgres` OS user instead.
- **Bind posture:** `127.0.0.1:5432` and `[::1]:5432` only; UFW active with 22/tcp alone. Loopback is
  the intended posture, so the client runs on the box via `remote_exec`, and the test asserts
  loopback while explicitly asserting the port is *not* on `0.0.0.0`.
- **Credential keys** (`/home/admin/.credentials`, mode 600): `Sudo Username`, `Sudo Password`,
  `Postgresql Password`.
- **MOTD** carries `Credentials File:` but no `App URL` — correct for this app; no `base_url`.
- **Root SSH** stays enabled (`DISABLE_ROOT=No`).
- psql prints a command tag per statement on stdout, so the round-trip test keeps its DDL/DML setup
  in a separate call from the `SELECT` it asserts on. This is the failure mode recorded in
  `troubleshooting.md` during the pgvector run; applying it up front meant the suite passed on its
  first run here.

### Files created

- `tests/regression_tests/services/postgresql/__init__.py`
- `tests/regression_tests/services/postgresql/postgresql_service.py` — `PostgresqlService`;
  no assertions.
- `tests/regression_tests/apps/linode-marketplace-postgresql/conftest.py` — `credentials_file_path`
  only.
- `tests/regression_tests/apps/linode-marketplace-postgresql/test_scenarios.py` — 3 tests.

Shared infra (`remote_exec`, `http_session`, `utils/ssh.run_remote_command`, `services/__init__.py`)
already existed and was **reused untouched**.

`PostgresqlService` deliberately duplicates the shape of `PgvectorService` rather than sharing a base
class: the suite convention is one service package per app, and the two apps' auth models differ
(superuser vs. app admin role). If a third Postgres-derived app appears, factoring out a shared base
is worth revisiting.

### Boxes deployed

- `101682703` — exploration box; probing and the first green suite run (3/3, first attempt).
- `101683116` — fresh verification box; carried the final green run.

Both provisioned from `linode-config.sh` values (`us-ord`, `g6-dedicated-4`, `linode/ubuntu24.04`)
and deployed by replicating `.github/scripts/app-installation.sh` — repo cloned on the box, then
`. ./test-vars.sh` and `./postgresql-deploy.sh` from `akamai-compute-marketplace/main`, with
generated root passwords.

### Issues

- No test failures during the run, and no app defects found.
- The suite is idempotent-only: every check is read-only apart from the round-trip table, which uses
  a uuid-suffixed name and drops itself. 7a and 7b therefore converge; the fresh-deploy run was still
  done for parity.
- No new `troubleshooting.md` entries — the one failure mode this app could have hit was already
  recorded during the pgvector run.
