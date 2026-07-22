# Chroma — backend regression testing

## Chroma — backend regression test run (2026-07-22)

### Scope
Standalone run (no STATE.md). Operator-confirmed scenarios: container/nginx liveness + port
posture (baseline), loopback heartbeat, public HTTP Basic Auth gate (401/200), and an authenticated
collection create-and-read roundtrip. First backend app in the suite — added the shared
`remote_exec` / `http_session` / `run_remote_command` / `services/__init__.py` infra.

### Discovered
- Service shape: docker-compose container (image `chromadb/chroma`), **no systemd unit**. Liveness
  via `docker ps` (container name filter `compose-server`). nginx is a normal systemd unit.
- Bind / firewall posture: Chroma API on `127.0.0.1:8000` (loopback-only, via docker-proxy); nginx
  public on `0.0.0.0:80` and `0.0.0.0:443`. ufw active, allows 22/80/443 only (8000 firewalled).
  Loopback-only bind is the intended posture — asserted as correct.
- Auth model: nginx HTTP Basic Auth (htpasswd) in front of the API. Credential keys (exact):
  `Chroma Username`, `Chroma Password` (also `Sudo Username` / `Sudo Password`) in the creds file.
- API endpoints (paths only): `/api/v2/heartbeat`, `/api/v2/version`, and collections under
  `/api/v2/tenants/default_tenant/databases/default_database/collections` — GET list, POST create
  `{"name": ...}`, POST `{id}/add` `{ids, embeddings, documents, metadatas}` (returns 201), POST
  `{id}/query` `{query_embeddings, n_results}` (returns ids/documents/distances, nearest-first), GET
  `{id}/count`. Chroma API version reported `1.0.0`. Explicit embeddings are supplied in tests, so
  no server-side embedding model is needed and nearest-neighbour retrieval is deterministic.
- Vantage split confirmed empirically: the public URL probed **from the box** returned `000`
  (NAT hairpin); the same request from the **runner** returned 401 (unauth) / 200 (authed). So the
  public API is tested via `http_session` (runner), the loopback API via `remote_exec` (on box).
- Let's Encrypt cert issued successfully (public HTTPS valid without `-k`).

### Created
- Shared infra (first backend app): `services/__init__.py`, `run_remote_command` in `utils/ssh.py`,
  `remote_exec` + `http_session` fixtures in the global `conftest.py`.
- Service object: `services/chroma/chroma_service.py` (`ChromaService` — SSH + HTTP actions, no
  assertions).
- App files: `apps/linode-marketplace-chroma/conftest.py` (`credentials_file_path`, `base_url`) and
  `test_scenarios.py`.
- Tests (6): `test_chroma_service_active`, `test_chroma_port_posture`, `test_chroma_local_heartbeat`,
  `test_chroma_public_requires_auth`, `test_chroma_public_authenticated_heartbeat`, and
  `test_chroma_collection_roundtrip` — the end-to-end vector-store check (create → confirm listed →
  add records → count == 2 → similarity query returns the expected nearest neighbour + document,
  distances ordered nearest-first).

### Verified
- Boxes deployed (ids only): `101126180` (StackScript-deploy attempt — failed, torn down by
  operator); `101126729` (empty box → manual `test-vars.sh` + deploy script → **the green box**).
- Suite type: **idempotent-only** (read-only checks + a uniquely-named collection per run). 6/6
  passing on the fresh deploy `101126729`; operator accepted that as the Step 7b clean-deploy pass
  (no separate redeploy needed).

### Notes / issues
- Deploy method: the StackScript path (box `101126180`) failed; the working path was an **empty box
  + `source test-vars.sh && bash chroma-deploy.sh`** (clones `akamai-compute-marketplace/main`).
- StackScript-deploy gotcha (deploy-side, not a test issue): the `add_ons` UDF `manyOf` list has a
  leading-space ` none` and `default="none"`, so passing `add_ons: "none"` via `stackscript_data`
  is rejected by the API; omitting it (use the default) or the deploy-script path avoids it.
- `http_session` uses `verify=False` (global default for self-signed backend apps; Chroma's cert is
  actually valid). The urllib3 `InsecureRequestWarning` is silenced via `filterwarnings` in
  `pytest.ini`, so the run output is clean.
- Troubleshooting entries added this session: "Public endpoint returns `000` when probed from the
  box" (NAT hairpin / vantage).
