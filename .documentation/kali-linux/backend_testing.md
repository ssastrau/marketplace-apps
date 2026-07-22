# Kali Linux — backend regression testing

## Kali Linux — backend regression test run (2026-07-23)

### Scope
Standalone run (no STATE.md). Operator scope call → **install-smoke**: verify the installed Kali
version and that Kali is up and running. Deployed with `VNC=No`, so there is no VNC/web surface —
the box is a headless Kali workstation reachable only over SSH.

### Deploy history (operator-deployed)
- The automated deploy is a **hard stop** for this skill: a from-scratch deploy failed at
  `TASK [kali : Install Kali Linux]` when Kali rolling's `base-files_2026.3.0` pre-install script
  returned exit 2 on the Ubuntu 24.04 base image (`dpkg` error, 0 kali packages installed). Fixing
  the deployment is the operator's job, not this skill's.
- The operator resolved the deploy and handed over a **fresh, working box** at `172.236.104.57`,
  which this run probed and tested against. (Separate, still-worth-fixing repo issue: the kali
  `test-vars.sh` is zsh, not bash — `#!/bin/zsh`, `typeset -A`, `${(@k)...}` — unlike every other
  app, so the standard bash source of the deploy vars fails on it.)

### Discovered
- OS: `/etc/os-release` → `ID=kali`, `PRETTY_NAME="Kali GNU/Linux Rolling"`, `VERSION_ID="2026.3"`,
  `VERSION_CODENAME=kali-rolling`. `/etc/kali_version` → `kali-rolling`.
- Kernel: `7.0.12+kali-amd64` (the Kali kernel, not the Ubuntu base kernel) — confirms the box was
  actually converted to Kali, not just labeled.
- Running state: `systemctl is-system-running` → `running`; no failed units.
- Package set: `kali-linux-default 2026.3.0` installed (alongside `kali-linux-core` and
  `kali-linux-headless`); 11 `kali-*` packages total. Real tools present and runnable — `nmap 7.99`,
  `metasploit-framework`, `hydra`, `sqlmap` (nmap runs as the `admin` user too).
- MOTD advertises `App URL: https://172.236.104.57` and `Credentials File: /home/admin/.credentials`,
  but with `VNC=No` **nothing serves that URL** — only sshd (`:22`) is listening. The credentials
  file records `Username` / `Password` / `Sudo Credentials` and a
  `Kali Linux Package Installed: kali-linux-default` line.

### Created
- Service object: `services/kali_linux/kali_linux_service.py` (`KaliLinuxService` — SSH/OS actions,
  no assertions): `os_release`, `system_running_state`, `kernel`, `default_metapackage_version`.
- Tests (2): `test_kali_up` (first — box is Kali via `/etc/os-release` + Kali kernel, and
  `systemctl is-system-running` == `running`) and `test_kali_version_installed` (a `VERSION_ID` is
  reported and the `kali-linux-default` metapackage is installed).
- No app `conftest.py` (SSH-only; no `base_url`, no app credentials needed — same shape as docker).
- Shared infra already present from earlier backend runs (nothing added).

### Verified
- Box (operator-deployed, id/IP): `172.236.104.57`, Kali `2026.3`.
- Suite type: **idempotent-only** (read-only OS/package checks). 2/2 passing twice on the fresh
  operator-provided box; treated as the Step 7 clean-deploy pass (a self-driven redeploy isn't
  possible here — the automated deploy is the operator's hard-stop).

### Notes / issues
- No troubleshooting entries added — the probe/test steps were clean. The two deploy-material issues
  (zsh `test-vars.sh`; Kali-rolling `base-files` conflict on the Ubuntu base image) are deploy
  failures, out of scope for `troubleshooting.md`, and were surfaced to the operator.
