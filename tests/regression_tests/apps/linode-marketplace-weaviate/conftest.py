import pytest


@pytest.fixture(scope="session")
def credentials_file_path() -> str:
    """
    Returns the absolute path to the credentials file on the remote server.
    """
    return "/home/admin/.credentials"


@pytest.fixture(scope="session")
def base_url(ssh_credentials) -> str:
    """
    Returns the nginx vhost URL for the API.

    The MOTD carries no App URL, so this rebuilds the same default domain the deploy
    script derives from the instance IP.
    """
    host, _, _ = ssh_credentials
    return f"https://{host.replace('.', '-')}.ip.linodeusercontent.com"
