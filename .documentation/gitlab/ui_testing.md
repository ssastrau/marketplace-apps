## GitLab — UI regression test run (2026-06-26)

### Scope
3 scenarios: startup (login page renders), login (valid credentials + first-run wizard skip), create project and verify it appears.

### Discovered
- Login flow: navigating to `base_url` redirects server-side to `/users/sign_in`. Inputs: `data-testid="username-field"`, `data-testid="password-field"`, submit: `data-testid="sign-in-button"`. Page title: `"Sign in · GitLab"`.
- First-run wizard (fresh VM only): after the first successful admin login, GitLab redirects to `/admin/registrations/groups/new` (title: `"Create your first project · GitLab"`). The wizard has two steps — group+project creation and profile setup — both skippable via a `link "Skip"`. Step 1 skip goes to `/admin/registrations/profile/new`; step 2 skip uses `data-testid="skip-button"`. The wizard does not reappear on subsequent logins. Tests handle it with `skip_setup_if_present()` that checks the current URL before acting.
- Post-login landmark: `button "Create new…"` in the top nav header — present on any authenticated GitLab page, absent on login and wizard pages.
- New project creation: navigate to `/projects/new`, click `a[href="#blank_project"]` to open the blank project form, fill `textbox "Project name Project name"`, click `button "Pick a group or namespace"` to open the namespace dropdown, select `option "root"` for the root user's personal namespace, click `button "Create project"`. After creation URL becomes `/root/{project-slug}` and page title matches `{project-name}`.
- General settings URL format: `/root/{project-slug}/edit` (not `/-/settings/general`).
- Credential keys: `Gitlab User`, `Gitlab Password`.

### Created
- Page objects: `pages/gitlab/gitlab_login_page.py`, `pages/gitlab/gitlab_setup_page.py`, `pages/gitlab/gitlab_home_page.py`, `pages/gitlab/gitlab_new_project_page.py`
- Tests: `test_gitlab_startup`, `test_gitlab_login`, `test_gitlab_create_project`

### Notes / issues
- All 3 tests passed on the second run in 17.96 s after cleanup.
- `test-automation-new-project` was created during the first test run and had to be deleted before the second run via `gitlab-rails runner` (project settings URL uses `/edit` not `/-/settings/general`, and the Delete button requires expanding an Advanced section the browser couldn't reach easily).
- Cleanup command: `gitlab-rails runner 'p = Project.find_by_full_path("root/test-automation-new-project"); p.destroy if p'`
- Exploration artifacts left on VM: `explore-group/explore-project` and `root/explore-new-project` (do not conflict with test-named resources).
- Troubleshooting entries added this session: none.
