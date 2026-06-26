## Mastodon — UI regression test run (2026-06-30)

### Scope
Startup, login, and write post — verify the Mastodon instance is running, admin login works,
and a post can be created and appears on the home feed.

### Discovered
- Login flow: navigate to `/auth/sign_in`; fields `E-mail address` + `Password`; submit `Log in`
  button; credentials keys: `Owner Email`, `Owner Password`
- Page titles: `"Trending - Mastodon"` (public landing/explore), `"Log in - Mastodon"` (login),
  `"Home - Mastodon"` (authenticated home feed)
- First-run page: yes — first login redirects to `/start` (Profile setup, 2-step wizard: profile
  details → follow people). The compose box is already visible on `/start`, so login confirmation
  does not require completing setup. The write-post test navigates directly to `/home` after login,
  bypassing the wizard entirely.
- Home feed: `region "Home"` contains a `feed` with `article` elements; post text is immediately
  visible after clicking `Post` without a page reload

### Created
- Page objects: `pages/mastodon/mastodon_landing_page.py`,
  `pages/mastodon/mastodon_login_page.py`,
  `pages/mastodon/mastodon_home_page.py`
- Tests: `test_mastodon_startup`, `test_mastodon_login`, `test_mastodon_write_post`

### Notes / issues
- Login and write-post tests navigate to sub-paths (`/auth/sign_in`, `/home`) via `f"{base_url}/..."`
  rather than `base_url` alone, since the root redirects to the public `/explore` page
- Profile setup wizard is a one-time server-side state; on a freshly deployed VM, every login
  redirects to `/start` until setup is saved — write-post test bypasses this by navigating directly
  to `/home` after login
- Troubleshooting entries added this session: none
