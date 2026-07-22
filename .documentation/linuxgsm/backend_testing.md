# LinuxGSM — backend regression testing

## LinuxGSM — backend regression test run (2026-07-23)

### Scope
Standalone run (no STATE.md). LinuxGSM is a **CLI/framework game-server manager**, not a service —
no daemon, no port, no web UI. The deploy left `GAMESERVERNAME` empty, so **no specific game server
is installed**, only the base LinuxGSM tooling. Operator scope call → **install-smoke** (like
crewai/hermes): verify the LinuxGSM CLI is up & working and can fetch/list the game-server catalog.
Installing an actual game server (SteamCMD, multi-GB, needs a `GAMESERVERNAME` redeploy) was
explicitly out of scope.

### Deploy (operator-deployed)
- Box handed over by the operator at `172.236.104.248` (fresh deploy), probed and tested against.
  No self-driven deploy this run.

### Discovered
- Install shape: role creates a `linuxgsm` user (uid 1001, in `sudo`) and drops
  `/home/linuxgsm/linuxgsm.sh` (mode 0755); running it bootstraps `/home/linuxgsm/lgsm/` (the
  `lgsm/data/` dir with `serverlist.csv`). No game-server script present (GAMESERVERNAME empty).
- `./linuxgsm.sh` (run as the `linuxgsm` user, chdir `/home/linuxgsm`) → prints usage + a stable
  `Installer - Linux Game Server Managers - Version v26.2.0` line, exit 0.
- `./linuxgsm.sh list` → fetches `serverlist.csv` from GitHub and lists the full catalog (141 lines;
  `acserver`, `arkserver`, `arma3server`, …), exit 0. This is the real functional check for a
  *manager*: it can reach LinuxGSM's distribution and parse the server list.
- No app service/port: only sshd (`:22`) and `systemd-resolve` on loopback listen — no App URL in
  the MOTD (headless, as expected). Credentials file `/home/admin/.credentials` records
  `Sudo Username` / `Sudo Password` / `LinuxGSM User` / `LinuxGSM User Password` (not needed for
  these read-only CLI checks — the probes run as the `linuxgsm` user via `runuser`).

### Created
- Service object: `services/linuxgsm/linuxgsm_service.py` (`LinuxGSMService` — SSH/CLI actions, no
  assertions): `version` (`./linuxgsm.sh`), `list_servers` (`./linuxgsm.sh list`), both run as the
  `linuxgsm` user.
- Tests (2): `test_linuxgsm_up` (first — CLI runs and reports "Linux Game Server Managers" + a
  version) and `test_linuxgsm_list_servers` (catalog fetch/list returns a known server,
  `arma3server`).
- No app `conftest.py` (SSH-only; no `base_url`, no app credentials needed — same shape as docker).
- Shared infra already present from earlier backend runs (nothing added).

### Verified
- Box (operator-deployed, id/IP): `172.236.104.248`.
- Suite type: **idempotent-only** (read-only CLI checks). 2/2 passing twice on the fresh
  operator-provided box; treated as the Step 7 clean-deploy pass.

### Notes / issues
- Same category as crewai/hermes: a framework/CLI app whose real product (a running game server) is
  gated behind a heavy, opt-in install (`GAMESERVERNAME`) — so the suite is install-smoke by design.
- Version assertion is on the stable `Version v` prefix (not the exact `v26.2.0`), since LinuxGSM
  self-updates upstream; the exact version is recorded here for reference, not asserted.
- No troubleshooting entries added (the probe/test steps were clean).
