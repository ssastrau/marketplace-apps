# Backend Testing — redis

## 2026-07-29

### Scope

Standalone run (`/backend-regression-tests redis`). No prior `.documentation/redis/` artifacts
existed and no `--scenarios` was given, so the scenario list was proposed from the playbook and the
archetype table and confirmed by the operator.

Scenarios tested:

1. Service liveness — `redis-server` unit active and an authenticated TLS `PING` returns `PONG`.
2. Port posture — the TLS port is bound beyond loopback and opened by the firewall.
3. Data round-trip — `SET` a uuid-named key, `GET` it back, assert the value.

TLS-enforcement checks (plain TCP refused, connection without a client cert refused) were offered
and not selected.

### This app's security posture is the inverse of the other datastores

mysql, postgresql and pgvector all bind loopback-only with UFW opening SSH alone. Redis here is
**deliberately internet-facing**, and the port assertion had to say the opposite of theirs. From
`redis.conf.j2`, confirmed live:

- `port 0` — plain TCP is disabled entirely; `tls-port 6379` — TLS only. A non-TLS `redis-cli`
  connection returns `I/O error`.
- `tls-auth-clients yes` — mutual TLS. Every connection must present a client cert signed by the
  CA generated at deploy time.
- `bind 127.0.0.1 -::1 <default ipv4>` — live listeners were `172.x.x.x:6379`, `127.0.0.1:6379` and
  `[::1]:6379`.
- UFW opens **6379/tcp to Anywhere** (v4 and v6), unlike every other datastore tested this session.
- ACL (`/etc/redis/users.acl`): `user default on ><password> sanitize-payload ~* &* +@all` — the
  default user requires the password from the credentials file.

The port test therefore asserts loopback **plus** at least one routable bind **plus** the UFW rule —
it would fail if a future change quietly made the service loopback-only, which for this app would be
a functional regression rather than a hardening win.

### Discovered on the live box

- **Unit:** `redis-server` (not `redis`), `active running`.
- **Client invocation**, verbatim from the probe:
  `redis-cli --tls --cert /etc/redis/ssl/certs/client1.crt --key /etc/redis/ssl/keys/client1.key.pem
  --cacert /etc/redis/ssl/ca/ca.crt -h 127.0.0.1 -p 6379 -a <password> --no-auth-warning`.
  The generated filenames match what the config template references (`client1.*`, `client_count=1`).
- **Vantage:** the port is genuinely public, but the client cert/key/CA live on the box, so the
  runner cannot connect. `redis-cli` therefore runs on the box via `remote_exec` — a public port does
  not automatically mean a runner-side check.
- **The server cert has no SAN** — subject is `CN = Redis Server` only. `redis-cli` accepted both
  `-h 127.0.0.1` and `-h <public ip>`, so the tests use `127.0.0.1`: stable, and it avoids having to
  discover the box's public address at runtime.
- **`redis-cli` exits 0 even when auth fails.** A wrong password prints
  `AUTH failed: WRONGPASS ...` / `NOAUTH Authentication required.` on stdout but still returns exit
  code 0. Any future auth-rejection test for this app must assert on output, never on the exit code.
  (Not needed for the confirmed scenarios, but recorded because it is a trap.)
- **Credential keys** (`/home/admin/.credentials`, mode 600): `Sudo Username`, `Sudo Password`,
  `Redis Default User Password`, `Redis CA Password (required to generate new certs)` — note the
  parenthetical is part of the key as `app_credentials` parses it.
- **MOTD** carries `Credentials File:` plus config/SSL paths, no `App URL` — no `base_url`.
- **Root SSH** stays enabled (`DISABLE_ROOT=No`).

### Files created

- `tests/regression_tests/services/redis/__init__.py`
- `tests/regression_tests/services/redis/redis_service.py` — `RedisService`; no assertions.
- `tests/regression_tests/apps/linode-marketplace-redis/conftest.py` — `credentials_file_path` only.
- `tests/regression_tests/apps/linode-marketplace-redis/test_scenarios.py` — 3 tests.

Shared infra (`remote_exec`, `http_session`, `utils/ssh.run_remote_command`, `services/__init__.py`)
already existed and was **reused untouched**.

### Boxes deployed

- `101684191` — exploration box; probing and the first green suite run (3/3, first attempt).
- `101685252` — fresh verification box; carried the final green run.

Both provisioned from `linode-config.sh` values (`us-ord`, `g6-dedicated-4`, `linode/ubuntu24.04`)
and deployed by replicating `.github/scripts/app-installation.sh` — repo cloned on the box, then
`. ./test-vars.sh` and `./redis-deploy.sh` from `akamai-compute-marketplace/main`, with generated
root passwords.

### Issues

- No test failures during the run, and no app defects found.
- The suite is idempotent-only: the round-trip key is uuid-named and deleted at the end, everything
  else is read-only. 7a and 7b converge; the fresh-deploy run was still done for parity.
- No new `troubleshooting.md` entries. The `redis-cli` exit-code-0-on-auth-failure behaviour is
  app-specific rather than a recurring class, so it is recorded here rather than in the shared file.
