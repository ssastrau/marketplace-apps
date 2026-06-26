## JupyterLab — UI regression test run (2026-06-29)

### Scope
Startup (login page verification), login (token → workspace), and running a Python notebook
(`print("hello")` in a new Python 3 notebook with output verification).

### Discovered
- Login flow: token-only (no username/password); token input at `/login?next=%2Flab%3F`; redirects
  to `/lab` on success
- Page title (login): "Jupyter Server"; page title (workspace): "JupyterLab"
- Token input: `textbox "Password or token:"`; login button: `button "Log in"` (exact match needed
  to avoid matching "Log Out")
- Workspace confirmation: `menuitem "File"` in the top menubar — stable indicator that the
  JupyterLab UI fully loaded
- Notebook creation: `button "New Launcher (⇧ ⌘ L)"` opens a launcher tab; the Launcher panel
  exposes two `get_by_title("Python 3 (ipykernel)")` elements (Notebook section first, Console
  section second) — use `.first()` to target the Notebook creator
- Notebook cell input: `get_by_role("region", name="notebook content").get_by_role("textbox").first()`
- Run button: `button "Run this cell and advance"` in the notebook toolbar
- Output verification: `expect(region "notebook content").to_contain_text("hello")` — output renders
  inside the same "notebook content" region immediately after the kernel executes the cell
- Kernel status indicator in status bar: "Python 3 (ipykernel) | Idle" confirms kernel is ready;
  no explicit wait needed — notebook cell auto-waits for the element to be interactable
- Credential key used: `"Jupyter Token"`

### Created
- Page objects: `pages/jupyterlab/jupyterlab_login_page.py`,
  `pages/jupyterlab/jupyterlab_lab_page.py`, `pages/jupyterlab/jupyterlab_notebook_page.py`
- Tests: `test_jupyterlab_startup`, `test_jupyterlab_login`, `test_jupyterlab_run_notebook`

### Notes / issues
- Troubleshooting entries added this session: none
- A Jupyter news notification dialog appears on first load but does not block interaction
- Title check for startup uses `"Jupyter Server"` (not `"JupyterLab"`) — the login page is served
  by Jupyter Server before the lab UI is initialized
