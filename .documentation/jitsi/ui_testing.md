## Jitsi — UI regression test run (2026-06-29)

### Scope
Startup (landing page verification) and start stream (enter room → pre-join screen → join → verify meeting room active).

### Discovered
- Login flow: none — Jitsi is a public app with no authentication required
- Landing page title: "Jitsi Meet"; heading: "Jitsi Meet" (h1); meeting name input: role textbox "Meeting name input"; "Start meeting" button
- Pre-join screen: heading "Join meeting" (h1); display name input: role textbox "Enter your name"; join button has `data-testid="prejoin.joinMeeting"` — more stable than role-based
- Alert "Configuring devices…" appears during WebRTC device setup; disappears once devices are ready (or timed out)
- Meeting room confirmation: heading "Toolbar" (h1) and button "Leave the meeting" — both always visible once the room loads
- Credentials file contains only sudo credentials; no app-specific credentials needed in tests
- WebRTC device setup takes 15–30 s on a fresh instance without fake devices; the pytest browser uses `--use-fake-ui-for-media-stream` and `--use-fake-device-for-media-stream` flags so this should be faster in CI — `timeout=30000` added on toolbar assertion

### Created
- Page objects: `pages/jitsi/jitsi_login_page.py`, `pages/jitsi/jitsi_prejoin_page.py`, `pages/jitsi/jitsi_meeting_page.py`
- Tests: `test_jitsi_startup`, `test_jitsi_start_stream`

### Notes / issues
- No login test generated — app is publicly accessible; `credentials_file_path` fixture returns the sudo credentials path to satisfy the global fixture dependency, but `app_credentials` is not used in any test
- `TEST_ROOM = "test-regression-room"` is a module-level constant used across tests — keep it consistent if adding future scenarios
- Troubleshooting entries added this session: none
