# Backend Testing — openbao

## 2026-07-29

### Scope

Standalone run (`/backend-regression-tests openbao`). No prior `.documentation/openbao/` artifacts
existed. Scenarios came from two operator-supplied documents plus the app playbook:

- Akamai Marketplace guide for OpenBao — the `bao status` verification step, the credentials-file
  location, and the unseal procedure (3 shares, threshold 2, `bao operator unseal` until
  `Sealed: false`).
- `openbao.org/docs/install/` — binary-on-PATH verification (`bao -h`).

Scenarios tested:

1. Service liveness — `openbao` unit active and the API answers a seal-status request.
2. Listener posture — bound on 8200 at the configured address, explicitly **not** the wildcard.
3. Credentials file records 3 unseal keys plus the Initial Root Token.
4. Unseal at the key threshold — two of three keys yield `Sealed: false`.
5. Secret round-trip — enable a kv-v2 mount, write a secret, read the value back.

A systemd-hardening check (upstream's `MemorySwapMax=0` advice) was considered and dropped at the
operator's call as beyond smoke. See the observation below — it is a real gap, just not a test.

### Defect found — OpenBao cannot unseal without a private IP, and CI provisioned without one

The playbook derives its listen address from the box's private address:

```yaml
listen_address: "{{ (ansible_all_ipv4_addresses | select('search', '^192\\.168\\.') | list | first) | default('0.0.0.0') }}"
```

With no `192.168.x` address this falls back to `0.0.0.0`, producing
`cluster_addr = "https://0.0.0.0:8201"`. The deploy still reports success and `bao operator init`
still succeeds, but the vault can never be unsealed — the second key returns:

```
Code: 500. * cannot use unspecified IP with raft storage: 0.0.0.0:8201
```

Raft only rejects the unspecified address when it starts at unseal time, long after Ansible has
finished, so nothing in the deploy detects it.

**This was CI's actual configuration.** `.github/scripts/linode-provisioning.sh` hardcoded
`"private_ip": false`, so every CI deploy of this app produced a permanently sealed vault. The first
exploration box reproduced that faithfully; it was not a misprovisioned box, and the initial
write-up here that called it one was wrong.

**Fix applied (CI layer):** `PRIVATE_IP` is now a variable.
- `.github/scripts/linode-provisioning.sh` — `"private_ip": ${PRIVATE_IP:-false}`. The default keeps
  all other apps' behaviour byte-identical; only an app that opts in changes.
- `deployment_scripts/linode-marketplace-openbao/linode-config.sh` — sets `PRIVATE_IP="true"` and
  exports it to `$GITHUB_ENV`, with a comment explaining why.

Both branches were verified to render valid JSON (`private_ip: false` when unset, `true` when set)
and both scripts pass `bash -n`.

**Still open for the app owner:** this fixes CI, not the shipped app. A user deploying from the
Marketplace without private networking still gets a silently sealed vault. A candidate app-level fix
is changing the fallback from `0.0.0.0` to `127.0.0.1` — raft accepts a specified address, and the
cert SAN would then match the client's default `https://127.0.0.1:8200`, so the guide's `bao status`
step would work out of the box. The trade-off is that the listener becomes loopback-only in that
case, which would silently defeat the `CLIENT_IPS` firewall whitelist for anyone using it. That
fallback change was **not** tested here.

`test_openbao_listens_on_configured_address` asserts the address is not `0.0.0.0`, so this failure
mode is now caught by the suite.

### Discovered on the live box

- **Unit:** `openbao`, active. **Version:** OpenBao 2.6.1+hsm, storage type `raft`.
- **Listener:** `192.168.128.206:8200` (the private IP) once provisioned correctly. UFW allows only
  22/tcp — the rule for 8200 is gated on a `client_ips` variable that is not a UDF and is never
  defined, so 8200 is never opened. Vantage is therefore SSH on the box.
- **`bao status` exits 2 while sealed** (0 once unsealed), so the service object reads stdout and
  never trusts the exit code.
- **Status parsing:** the status table's column widths change once the vault unseals (more rows are
  added). An assertion on fixed spacing fails; `status_fields()` splits on a run of 2+ spaces
  instead. This caused the only test failure of the run, fixed on the first attempt.
- **Address env:** the playbook exports `VAULT_ADDR` in `.bashrc`; the binary honours both
  `VAULT_ADDR` and `BAO_ADDR`. A non-interactive SSH exec never sources `.bashrc`, and the default
  `127.0.0.1` fails TLS because the cert's SAN is the private IP, so the service object sets
  `BAO_ADDR` explicitly from `api_addr` in `/etc/openbao/openbao.hcl` rather than hardcoding an IP.
- **Post-deploy state:** initialized but **sealed**. Nothing unseals it automatically.
- **No kv engine is mounted by default** (only `cubbyhole/`, `identity/`, `sys/`), so the round-trip
  test enables its own uniquely-named `kv-v2` mount.
- **`bao operator unseal` is idempotent** when already unsealed — returns `Sealed false`, exit 0 —
  so the suite stays re-runnable.
- **Credential keys** (`/home/admin/.credentials`, mode 600): `Sudo username`, `Sudo password`,
  `CA Password`, `Unseal Key 1`, `Unseal Key 2`, `Unseal Key 3`, `Initial Root Token`. Note the
  lowercase `username`/`password` here, unlike other apps' `Sudo Username`.
- **MOTD** has `Credentials File:` but no `App URL` — correct for this app; no `base_url` in conftest.
- **Root SSH** stays enabled (`DISABLE_ROOT=No`).

### Observation not covered by a test

`openbao.org/docs/install/` recommends `MemorySwapMax=0` in the systemd unit so secrets cannot leak
to swap. The app's `openbao.service` template does **not** set it. It does grant `CAP_IPC_LOCK` with
`LimitMEMLOCK=infinity` (so mlock, the primary protection, works) and applies `ProtectSystem=full`,
`ProtectHome=read-only`, `NoNewPrivileges=yes`. Closing the gap is an app change, not a test change.

### Files created

- `tests/regression_tests/services/openbao/__init__.py`
- `tests/regression_tests/services/openbao/openbao_service.py` — `OpenBaoService`; no assertions.
- `tests/regression_tests/apps/linode-marketplace-openbao/conftest.py` — `credentials_file_path` only.
- `tests/regression_tests/apps/linode-marketplace-openbao/test_scenarios.py` — 5 tests.

Shared infra (`remote_exec`, `http_session`, `utils/ssh.run_remote_command`, `services/__init__.py`)
already existed and was **reused untouched**.

### Boxes deployed

- `101676715` — first exploration box, created **without** private networking (matching CI's then
  hardcoded `private_ip: false`); unsealing impossible. Deleted once the cause was understood.
- `101677525` — second exploration box (private IP); probing and the first green suite run.
- `101678278` — fresh verification box (private IP); first green run against a genuinely sealed vault.
- `101679343` — CI-parity box: provisioned from `linode-config.sh` values (`us-ord`,
  `g6-dedicated-4`, `PRIVATE_IP=true`) with CI's label, deployed by replicating
  `.github/scripts/app-installation.sh` (clone the repo on the box, `. ./test-vars.sh`, run
  `openbao-deploy.sh`), and tested with `regression-tests.sh`'s pytest invocation. Carried the final
  green run and confirmed the `PRIVATE_IP` fix end to end: `cluster_addr = https://192.168.136.27:8201`,
  no `0.0.0.0` fallback, 5/5 passed.

All deployed CI-style (bare `linode/ubuntu24.04`, then `test-vars.sh` + `openbao-deploy.sh` from
`akamai-compute-marketplace/main`) with generated root passwords.

**Deviations from CI provisioning**, recorded deliberately: boxes were created in `us-east` on
`g6-standard-2`, whereas `linode-config.sh` specifies `us-ord` / `g6-dedicated-4`. Neither affects
any assertion in this suite. Separately, `test-vars.sh` for this app does not set `CLIENT_IPS` or the
five SSL identity UDFs (`COUNTRY_NAME`, `STATE_OR_PROVINCE_NAME`, `LOCALITY_NAME`,
`ORGANIZATION_NAME`, `EMAIL_ADDRESS`) that `openbao-deploy.sh` consumes, so they landed empty in
`group_vars` and the generated cert has only `CN = openbao` with no C/ST/L/O/emailAddress. A real
Marketplace deploy supplies these. No test asserts on the cert subject, so the suite is unaffected —
but `test-vars.sh` is incomplete for this app.

### Issues

- The private-IP prerequisite above is the headline finding.
- The suite is **not** idempotent-only in spirit: the unseal test is only meaningful against a
  freshly deployed, sealed vault. It still passes on an already-unsealed box because unsealing is
  idempotent, so the fresh-box run is what actually proves it.
- No new `troubleshooting.md` entries; see the run notes for the reasoning.
