## Moodle — UI regression test run (2026-07-01)

### Scope
Startup, admin login, and course creation (create a course + verify it's created).

### Discovered
- Login flow: `#username` / `#password` text inputs, `#loginbtn` submit button. Successful login redirects to `/my/` (Dashboard).
- Page title(s): "Log in to the site | moodle" (login page); post-login dashboard confirmed via heading "Dashboard" (h1, no stable id/class beyond generic `h2 mb-0`, so role-based locator used).
- Course creation reachable directly at `/course/edit.php?category=1` ("Add a new course"). Fields: `#id_fullname`, `#id_shortname`, submit via `#id_saveanddisplay`. On save, redirects to `/course/view.php?id=<n>` with page title `Course: <fullname> | moodle` and an h1 heading matching the course fullname.
- Course creation verified two ways: (1) heading on the new course's own page, (2) course appears in `/course/management.php?search=<fullname>` results list as a role="link" with the course name.
- First-run configuration page: none — first login goes straight to the normal Dashboard.

### Created
- Page objects: `pages/moodle/moodle_login_page.py`, `pages/moodle/moodle_dashboard_page.py`, `pages/moodle/moodle_create_course_page.py`, `pages/moodle/moodle_course_page.py`, `pages/moodle/moodle_course_management_page.py`
- Tests: `test_moodle_startup`, `test_moodle_login`, `test_moodle_create_course`

### Notes / issues
- Course shortname must be unique per Moodle instance; the test uses a fixed shortname (`qa-regression-course`) which is fine for a freshly deployed VM but will collide if the suite is re-run against the same, already-tested instance.
- Troubleshooting entries added this session: none (no novel failure modes hit — all steps worked on the first pass).
