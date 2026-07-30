import pytest


@pytest.fixture(scope="session")
def credentials_file_path() -> str:
    """
    Returns the absolute path to the credentials file on the remote server.
    """
    return "/home/admin/.credentials"


@pytest.fixture(scope="session")
def sudo_user_credentials(app_credentials) -> tuple[str, str]:
    """
    Returns the (username, valkey password) pair for the sudo user's Valkey account.
    The credentials file names that key after the user, e.g. "admin Valkey User Password".
    """
    username = app_credentials["Sudo Username"]
    return username, app_credentials[f"{username} Valkey User Password"]
