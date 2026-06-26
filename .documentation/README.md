# `.documentation/` — per-app working notes (mount point)

This directory is the **mount point** for per-app working material produced by the pipeline
skills. It is symlinked into your `marketplace-apps` checkout (see the
[setup instructions](../README.md#setup-one-time-per-teammate)) so the notes are visible and
accessible while working in that repo.

Each app gets a subdirectory, owned phase-by-phase by the skills:

```
.documentation/<app>/
├── STATE.md                    # handoff file — every skill reads/writes this
├── architecture_decisions.md   # phase 1 (/backport-start or /newapp-start)
├── manual_install.md           # phase 2 (/app-manual-install)
├── e2e_testing.md              # phase 4 (/app-deploy)
├── validation_findings.md      # phase 5 (/review:validate-config)
└── pr_description.md           # phase 6 (/app-pr)
```

**Only this README and the empty mount point are committed.** Everything else inside is
gitignored and stays local — these notes routinely contain box IPs, generated credentials, and
other deploy-time material that must never be synced to the team repo.
