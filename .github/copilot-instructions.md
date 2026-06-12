# Marketplace Apps — Project Context

This repo contains Linode Marketplace app deployment scripts and a Playwright + Pytest UI
regression test suite for those apps.

## Repo structure

```
apps/                          # Ansible deployment scripts (no useful UI info here)
tests/regression_tests/        # Playwright + Pytest UI regression tests
```

## General principles

- **KISS** — simplest solution that works.
- **Don't guess** — if input is missing, ask the user directly.
- **If stuck after 2 attempts** — stop and ask the user for help.

## Skills

| Task | Instructions |
|---|---|
| Generate UI regression tests for a new app | Read `.claude/commands/ui-regression-tests/SKILL.md` and follow the steps exactly |
