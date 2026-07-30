import pytest


@pytest.fixture(scope="session")
def credentials_file_path(app_username) -> str:
    """
    Returns the absolute path to the credentials file on the remote server.
    """
    return f"/home/{app_username}/.credentials"


@pytest.fixture(scope="session")
def app_username() -> str:
    """
    Returns the sudo username the app was deployed with (USER_NAME in test-vars.sh).
    """
    return "admin"
