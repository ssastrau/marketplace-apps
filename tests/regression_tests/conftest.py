import pytest
import os
from playwright.sync_api import sync_playwright
from regression_tests.utils.ssh import get_credentials_via_ssh


@pytest.fixture(scope="session")
def app_credentials(credentials_file_path) -> dict:
    """
    Retrieves application credentials from a remote Linode server via SSH.

    This session-scoped fixture connects to the deployed Linode using
    credentials sourced from environment variables. It reads the remote
    credentials file and returns it as a dictionary to be consumed by tests.

    Args:
        credentials_file_path (str): The absolute path to the credentials file
            on the remote server (yielded by the `credentials_file_path` fixture).

    Environment Variables Required:
        LINODE_IPV4: The IP address of the deployed Linode.
        USER_NAME: The SSH username.
        LINODE_ROOT_PASS: The SSH password.

    Returns:
        dict: A dictionary mapping the credential keys to their respective values.
    """
    host = os.environ.get("LINODE_IPV4")
    username = os.environ.get("USER_NAME", "root")
    password = os.environ.get("LINODE_ROOT_PASS")

    if not host:
        raise ValueError("LINODE_IPV4 env var is required")
    if not password:
        raise ValueError("LINODE_ROOT_PASS env var is required")

    return get_credentials_via_ssh(
        host=host,
        username=username,
        password=password,
        remote_path=credentials_file_path
    )


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def context(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
