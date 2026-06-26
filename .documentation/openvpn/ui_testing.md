## OpenVPN — UI regression test run (2026-07-02)

### Scope
Two scenarios as requested so far: (1) startup (admin login page loads), (2) admin login. A third
scenario was flagged by the operator as coming in a follow-up run — not yet implemented. Also asked
to capture the one-time acknowledgement pop-up shown on first login.

### Discovered
- Login flow: OpenVPN Access Server admin portal at `:943/admin`, React SPA login form
  (`getByRole("textbox", name="Username *")`, `"Password *"`, `getByRole("button", name="Sign in")`
  — the Sign In button stays disabled until both fields are filled).
- Page title(s): "Access server admin portal" (used for both the login page and the post-login
  dashboard — the SPA doesn't change `<title>` on navigation, so route/heading checks matter more
  than title checks past the login page).
- **One-time acknowledgement pop-up**: a "License Agreement" `dialog` appears once, immediately
  after the very first successful login on a fresh instance, with "Agree" / "I Do Not Accept"
  buttons. Accepting it lands on the "Status" page (`<h1>Status</h1>`); it never reappears for that
  instance afterward (consistent with the existing troubleshooting.md guidance on first-run pages).
  Modeled as `OpenVPNLicenseAgreementPage.accept_if_present()`, which waits briefly for the dialog
  and clicks "Agree" only if it shows up — so the login test works whether or not this particular
  VM has already consumed the one-time dialog.
- Post-login confirmation: "Status" `<h1>` plus an "Account menu" button showing the logged-in
  username.

### Created
- Page objects: `pages/openvpn/openvpn_login_page.py`, `openvpn_license_agreement_page.py`,
  `openvpn_status_page.py`
- Tests: `test_openvpn_startup`, `test_openvpn_admin_login`

### Notes / issues
- Credential keys used: `OpenVPN Username`, `OpenVPN Password` (file also has `Sudo Username`,
  `Sudo Password`, unused by these tests).
- Full suite (2 tests) passed against the freshly deployed VM; the License Agreement dialog had
  already been dismissed by this run's own exploration step, so `accept_if_present()`'s no-dialog
  branch was exercised rather than the accept branch — both paths were validated across this run.
- Follow-up: operator indicated a third scenario is coming in a later run.
