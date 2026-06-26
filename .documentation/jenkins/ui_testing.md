## Jenkins — UI regression test run (2026-06-29)

### Scope
Startup, full setup wizard (unlock → install plugins → skip admin → verify dashboard), and post-setup login + dummy job creation.

### Discovered
- Login flow (pre-wizard): single password field ("Administrator password"), "Continue" button — no username field
- Login flow (post-wizard): separate "Username" and "Password" fields, "Sign in" button
- Page title (both states): "Sign in - Jenkins"
- Heading distinguishes state: "Unlock Jenkins" (pre-wizard) vs "Sign in to Jenkins" (post-wizard)
- Setup wizard steps: Customize Jenkins → plugin install progress (progressbar) → Create First Admin User (in iframe) → Instance Configuration (in iframe) → Jenkins is ready
- "Skip and continue as admin" and "Save and Finish" buttons are outside their respective iframes
- Plugin installation takes 2–5 min on a fresh instance; `timeout=180000` needed on the skip-admin assertion
- "Freestyle project" radio button is overlapped by an SVG icon; must click `.jenkins-choice-list__item` container, not the radio directly
- Dashboard confirmation elements: title "Dashboard - Jenkins", heading "Welcome to Jenkins!", "admin" user link
- Credential key used: `Jenkins Admin password` (password for both unlock wizard and normal login; username is always "admin" after skipping admin creation)

### Created
- Page objects: `pages/jenkins/jenkins_unlock_page.py`, `pages/jenkins/jenkins_setup_wizard_page.py`, `pages/jenkins/jenkins_login_page.py`, `pages/jenkins/jenkins_dashboard_page.py`, `pages/jenkins/jenkins_new_item_page.py`
- Tests: `test_jenkins_startup`, `test_jenkins_setup_wizard`, `test_jenkins_dashboard_login`

### Notes / issues
- Tests must run in order on a fresh VM: scenario 1 and 2 require the wizard to be in its initial state; scenario 3 requires the wizard to be already complete (run after scenario 2)
- VPN connectivity required from the test runner machine — the `172-238-182-40.ip.linodeusercontent.com` hostname routes through Linode-internal IPs and is unreachable without it
- Troubleshooting entries added this session: none (no novel confirmed failures)
