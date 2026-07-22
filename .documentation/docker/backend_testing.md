# Docker — backend regression testing

## Docker — backend regression test run (2026-07-22)

### Scope
Standalone run (no STATE.md). Docker is an infrastructure-baseline app — it installs the Docker
engine and nothing else. The "app" is the Docker daemon (`docker.service`), so the suite is a
liveness check plus the canonical container-run functional check.

### Discovered
- Service: `docker.service` (systemd unit `docker`), **active**. Installed via the shared `docker`
  role (docker-ce from the official repo). `docker` binary at `/usr/bin/docker`.
- Daemon responsive: `docker version` reports client + server `29.6.2`; `docker info` server version
  `29.6.2`.
- Functional: `docker run --rm hello-world` → "Hello from Docker!" (exit 0) — proves pull + run.
- **No TCP port** — Docker listens on the unix socket `/var/run/docker.sock` only (open TCP ports are
  just 22/53), so there is no port-listening test.
- No `App URL` and no app credentials (MOTD has only `Credentials File` with `Sudo …`), so no app
  `conftest.py` is needed — tests use only the global `remote_exec`.

### Created
- Service object: `services/docker/docker_service.py` (`DockerService` — SSH/CLI actions, no
  assertions).
- Tests (2): `test_docker_up` (first — Docker unit active AND daemon responds via `docker version`)
  and `test_docker_run_hello_world` (pull + run a container, assert "Hello from Docker!").
- Shared infra already present from earlier backend runs (nothing added).

### Verified
- Box deployed (id only): `101133480` (empty box → `test-vars.sh` + `docker-deploy.sh`).
- Suite type: **idempotent-only** (`--rm` cleans up the container; image is cached; unit/version
  checks are read-only). 2/2 passing twice on the fresh deploy `101133480`; treated as the Step 7b
  clean-deploy pass (no separate redeploy, consistent with the idempotent-only clause).

### Notes / issues
- `docker run hello-world` pulls a tiny image from Docker Hub, so the functional test needs outbound
  network on the box (present on a normal deploy).
- No troubleshooting entries added — the deploy and probe were clean.
