# Memgraph — backend regression testing

## Memgraph — backend regression test run (2026-07-23)

### Scope
Standalone run (no STATE.md). Operator asked to **deploy and investigate a smoke pack**. Memgraph is
a headless in-memory transactional **graph database** (Bolt protocol + Cypher via `mgconsole`); no
web UI in the role (no Memgraph Lab, no nginx). DB archetype → smoke pack = up-and-serving,
port-listening, and a data round-trip.

### Deploy (skill-deployed)
- Empty `linode/ubuntu24.04` box created via the Linode MCP (generated root pass + operator pubkey),
  then `test-vars.sh` + `memgraph-deploy.sh` copied and run as CI does (`akamai-compute-marketplace`
  / `main`, no fork/branch). Two-play deploy (`provision.yml` ok=7, then `site.yml` ok=33 failed=0),
  `Installation Complete`. `memgraph.service` came up active.

### Discovered
- Version: Memgraph `3.12.0` (playbook installs the latest GitHub release deb).
- Unit: `memgraph` — `systemctl is-active` → `active`.
- Ports (all `0.0.0.0`): `7687` Bolt, `7444`, `9091` (monitoring). **Firewall posture:** UFW is
  active and allows **only `22/tcp`** — Bolt (7687) is bound on all interfaces but firewalled, so it
  is **not reachable from the runner** (confirmed: closed from outside). The `MEMGRAPH_BOLT_ALLOW`
  UDF was empty, so no Bolt allow-rule was added. → **vantage = client on the box** (`mgconsole` via
  `remote_exec`), not direct from the runner.
- Client: `mgconsole` at `/usr/bin/mgconsole`. **Bolt requires SSL** (`ssl.yml` enables
  `--bolt-cert-file`/`--bolt-key-file` and flips bind to `0.0.0.0`) — the client needs
  `--use-ssl=true`; without it the handshake is closed by the server. CSV output via
  `--output-format=csv` gives clean, assertable rows (`"ok"` / `"1"`).
- Auth: user/password required; keys in `/home/admin/.credentials` are `Memgraph User` /
  `Memgraph Password` (also `Sudo Username` / `Sudo Password`).
- Round-trip probed live: `CREATE (n:SmokeTest {id: <uuid>, val: 42});` then
  `MATCH (n:SmokeTest {id: <uuid>}) RETURN n.val;` → `"42"`.

### Created
- Service object: `services/memgraph/memgraph_service.py` (`MemgraphService` — SSH/`mgconsole`
  actions, no assertions): `unit_active`, `bolt_listener` (`ss` on :7687), `cypher(user, password,
  query)` (SSL + CSV, newline-terminated via `printf '%s\n'`).
- App `conftest.py`: `credentials_file_path` → `/home/admin/.credentials` (no `base_url` — Bolt is
  not HTTP and is firewalled; the global `app_credentials` fixture parses the creds).
- Tests (3): `test_memgraph_up` (first — unit active AND an authenticated `RETURN 1` answers `1`),
  `test_memgraph_bolt_listening` (listener present on 7687), `test_memgraph_data_roundtrip`
  (CREATE→MATCH a node keyed by a per-run `uuid`, assert the property round-trips as `42`).
- Shared infra already present from earlier backend runs (nothing added).

### Verified
- Box (skill-deployed, id/IP): `101195383` / `45.33.85.231`.
- Suite type: effectively **idempotent-only** — the round-trip writes with a unique `uuid` per run,
  so it re-runs cleanly on a fresh **or** reused box. 3/3 passing twice on the fresh deploy; treated
  as the Step 7 clean-deploy pass.

### Notes / issues
- **New troubleshooting entry** (confirmed on this run): a stdin-fed query client returns empty
  output when the piped query lacks a trailing newline. The first cut used `printf '%s'` and both
  Cypher tests returned `""` at exit 0; switching to `printf '%s\n'` fixed it (mgconsole executes on
  the line terminator). Added as a sibling to the existing "exit 0 but stdout empty" entry.
- Bolt is deliberately SSL-only and, by default, firewalled to SSH — a correct posture for a
  datastore; the tests assert the on-box reachable service, not public reachability.
