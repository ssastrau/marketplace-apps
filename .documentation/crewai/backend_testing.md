# CrewAI — backend regression testing

## CrewAI — backend regression test run (2026-07-22)

### Scope
Standalone run (no STATE.md). CrewAI is a **library-only** install — no service, port, API, or
datastore — so the standard backend suite (service-active / port posture / data round-trip) has no
target. Raised the scope call with the operator; the chosen functional check is the CLI project
scaffold. Single test.

### Discovered
- Install shape: `pip install crewai` into venvs at `/root/.env` and `/home/<user>/.env`, plus a
  `PATH` line in `.bashrc`. **No systemd unit, container, port, web/API surface, or app credentials**
  (creds file is just `Sudo Username`/`Sudo Password`; MOTD has no `App URL`). UDFs are only
  `user_name` / `disable_root`.
- crewai version `1.15.5`; `import crewai` succeeds in the venv.
- `crewai create crew <name>` is an **interactive wizard** (prompts for tools, step-by-step
  planning, and per-agent role/goal) — it aborts under non-interactive SSH. The non-interactive path
  is `crewai create crew <name> --classic --skip_provider </dev/null`, which emits the classic
  Python/YAML project and prints `Crew <name> created successfully!`.
- Classic scaffold produces: `pyproject.toml`, `src/<name>/crew.py`, `src/<name>/main.py`,
  `src/<name>/config/agents.yaml`, `src/<name>/config/tasks.yaml` (plus README, tools/, knowledge/).

### Created
- Service object: `services/crewai/crewai_service.py` (`CrewAIService` — SSH/CLI actions, no
  assertions). No app `conftest.py` needed (no `base_url`, no app credentials — only `remote_exec`).
- Tests (2): `test_crewai_up` (first — verifies the app is up and working: the CLI runs and reports
  a version) and `test_crewai_create_crew_scaffold` (scaffolds a classic crew in a unique `/tmp`
  workdir, asserts exit 0 + "created successfully" + the key project files exist, then cleans up).
- Shared infra already present from the chroma run (nothing added).

### Verified
- Box deployed (id only): `101130796` (empty box → `test-vars.sh` + `crewai-deploy.sh`).
- Suite type: **idempotent-only** (unique per-run project name + temp workdir, cleaned up). 2/2
  passing twice on the fresh deploy `101130796`; treated as the Step 7b clean-deploy pass (no
  separate redeploy, consistent with the idempotent-only clause).

### Notes / issues
- CrewAI sits at the edge of this skill's scope — it's a framework, not a service. The scaffold test
  proves the framework + CLI installed and function; there is deliberately no service/port/API test
  because none exist. A real crew run (`.kickoff()`) needs an LLM API key the app doesn't provision,
  so it's out of scope.
- Prefer the CLI's own non-interactive flags over piping fake answers: `yes N | crewai create …`
  technically scaffolds but produces garbage (an agent literally named "n") in the newer JSON layout.
- Troubleshooting entry added: "A CLI generator/scaffold hangs or Aborted!s under remote_exec".
