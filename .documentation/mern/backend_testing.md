# MERN — backend regression testing

## MERN — backend regression test run (2026-07-23)

### Scope
Standalone run (no STATE.md). Operator asked to **deploy and investigate smoke tests**. MERN is a
full-stack **starter**: nginx serves a built React SPA at `/` and proxies `/api/` to an Express
service, backed by MongoDB. This is a **split** app — the React SPA at `/` is a browser surface
(that's `/ui-regression-tests`' job); this run covers only the **data/service plane**: the Express
API and MongoDB.

### Deploy (skill-deployed)
- Empty `linode/ubuntu24.04` box via the Linode MCP (generated root pass + operator pubkey), then
  `test-vars.sh` + `mern-deploy.sh` run as CI does (`akamai-compute-marketplace` / `main`, no
  fork/branch). Two-play deploy (`provision.yml` ok=7, `site.yml` ok=60 failed=0),
  `Installation Complete`. `express`, `mongod`, `nginx` all came up active.

### Discovered
- Units (all active): `express` (systemd, `/var/www/<host>/backend/server.js`), `mongod`, `nginx`.
- Ports / firewall posture (UFW allows `22` + `80`; TLS `443` also reachable via the nginx SSL
  addon):
  - `nginx` `0.0.0.0:80` → **http→https 301**; TLS `443` serves the SPA and proxies the API. Public.
  - `express` `*:5000` — bound on all interfaces but **firewalled** (from the runner → `000`);
    reachable only on the box / via the nginx proxy.
  - `mongod` `127.0.0.1:27017` — **loopback-only** (correct DB posture) + auth enabled.
- Express API (Express `server.js`): `GET /` → `Hello from the Express backend!`,
  `GET /api` → `{"message":"API is running!"}`. Through nginx over TLS the working public path is
  **`/api/`** (200 JSON); `/api` (no trailing slash) → 301 → `/api/`. nginx keys its vhost on
  `server_name <host>.ip.linodeusercontent.com`, so requests with a `localhost` Host hit the default
  server and 404 — probe/assert against the real host (the `base_url` fixture builds it).
- MongoDB: admin creds in `/home/admin/.credentials` as `MongoDB Admin User` /
  `MongoDB Admin Password`. Client `mongosh` at `/usr/bin/mongosh`. Authenticated `ping` → `1`;
  insert+find round-trip → `42`; an unauthenticated privileged command → `requires authentication`
  (auth is enforced).

### Created
- Service object: `services/mern/mern_service.py` (`MernService` — two-vantage actions, no
  assertions): SSH via `remote_exec` (`unit_active`, `listening_ports`, `mongo_eval`,
  `mongo_eval_unauthenticated`) and HTTP via `http_session` (`api_get`). Same combined-vantage shape
  as `ChromaService`.
- App `conftest.py`: `credentials_file_path` (`/home/admin/.credentials`) + `base_url`
  (`https://<host>.ip.linodeusercontent.com`, self-signed → `http_session` uses `verify=False`).
- Tests (5): `test_mern_api_up` (first — express active AND the public `/api/` returns
  `{"message":"API is running!"}`), `test_mern_mongodb_up` (mongod active + authenticated ping),
  `test_mern_mongodb_loopback` (27017 bound to loopback), `test_mern_mongodb_roundtrip` (insert→find
  a doc keyed by a per-run `uuid`, assert `42`), `test_mern_mongodb_auth_enforced` (unauth privileged
  command is rejected).
- Shared infra already present from earlier backend runs (nothing added). Exercises both fixtures —
  `remote_exec` (Mongo/units) and `http_session` (public API).

### Verified
- Box (skill-deployed, id/IP): `101197170` / `45.79.151.47`.
- Suite type: effectively **idempotent-only** — the round-trip writes to a unique per-run collection,
  so it re-runs cleanly. 5/5 passing twice on the fresh deploy; treated as the Step 7 clean-deploy
  pass.

### Notes / issues
- Split app: only the backend plane is tested here. A full browser suite for the React SPA at `/`
  (and its live API interaction) belongs to `/ui-regression-tests`.
- No troubleshooting entries added — the probe/test steps were clean. The nginx `server_name`
  matching and `/api`→`/api/` redirect are app-config behaviors captured in the tests (assert against
  the real host + `/api/`), not failure modes.
