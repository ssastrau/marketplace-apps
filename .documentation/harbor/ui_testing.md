## Harbor — UI regression test run (2026-06-26)

### Scope
3 scenarios: startup (login page renders), login (valid credentials), create project and verify it appears in the list.

### Discovered
- Login flow: navigating to `base_url` redirects server-side to `/account/sign-in`. Inputs resolved via `get_by_role("textbox", name="Username")` and `get_by_role("textbox", name="Password")`; submit via `get_by_role("button", name="LOG IN")`. Button is disabled until both fields are filled (no action needed — `fill()` enables it).
- Page title(s): `"Harbor"` (same on both login page and post-login — URL distinguishes the state, not the title).
- Post-login landmark: `heading "Projects" [level=2]` on `/harbor/projects`.
- Project creation: "New Project" button opens a dialog; project name input has `id="create_project_name"`; submit via `get_by_role("button", name="OK")`. Created project appears immediately as a `link` in the grid table. Verification: `get_by_role("link", name=project_name, exact=True)`.
- Checkbox row selection in the grid uses a `<label>` that intercepts pointer events — direct Playwright click fails; `page.evaluate()` with `label.click()` is required for bulk-select/delete flows. Not needed for test scenarios (create + link check only).
- First-run configuration page: none.
- Credential keys: `Harbor user`, `Harbor admin password`.

### Created
- Page objects: `pages/harbor/harbor_login_page.py`, `pages/harbor/harbor_projects_page.py`
- Tests: `test_harbor_startup`, `test_harbor_login`, `test_harbor_create_project`

### Notes / issues
- All 3 tests passed on the first run in 16.71 s — no fixes needed.
- `test-automation-project` was created during exploration and deleted via the UI (JS click on `label[for="clr-dg-row-cb3"]` + ACTION → Delete → DELETE confirm) before the test run.
- Troubleshooting entries added this session: none.
