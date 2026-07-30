import pytest


@pytest.fixture(scope="session")
def credentials_file_path() -> str:
    """
    Returns the absolute path to the credentials file on the remote server.
    """
    return "/home/admin/.credentials"
