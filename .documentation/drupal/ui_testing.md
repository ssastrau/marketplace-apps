## Drupal — UI regression test run (2026-06-25)

### Scope
Startup of admin login page, admin login, and creating an Article that's verified on the home page.

### Discovered
- Login flow: `#edit-name` / `#edit-pass` inputs inside `#user-login-form`, submit button has a
  non-unique id (`#edit-submit` also matches the site search form) — scoped to the login form.
  Redirects to the user's profile page on success.
- Page title(s): "Log in | My Drupal Site" (login), "Home | My Drupal Site" (home page), default
  Articles use `node/add/article` with a CKEditor 5 body field (`.ck-editor__editable`).
- First-run configuration page: none — login goes straight to the user profile / dashboard.

### Created
- Page objects: `pages/drupal/drupal_login_page.py`, `pages/drupal/drupal_create_article_page.py`,
  `pages/drupal/drupal_home_page.py`
- Tests: `test_drupal_startup`, `test_drupal_login`, `test_drupal_create_article`

### Notes / issues
- All 3 tests pass against a freshly deployed instance.
- Exploration submitted the create-article form to learn the resulting page shape, which left test
  content on the box; combined with iterating on a locator fix, this produced 3 duplicate
  "Test Article Title" articles and a strict-mode Playwright failure. Cleaned up by deleting all
  test content via `/admin/content` (bulk "Delete content" action) before finalizing, then
  re-ran the full suite once against the now-clean box to confirm a single clean pass.
- Added a troubleshooting.md entry for this class of issue (create-content scenarios leaving
  duplicate items behind during exploration/iteration).
- Troubleshooting entries added this session: "Strict-mode locator violation on a 'create content'
  scenario (duplicate items found)"
