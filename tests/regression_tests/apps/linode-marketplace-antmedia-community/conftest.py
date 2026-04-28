import os

import pytest

@pytest.fixture(scope="session")
def credentials_file_path():
    return "../home/ssastrau/.credentials"

@pytest.fixture(scope="session")
def base_url():
    linode_host = os.environ.get("LINODE_IPV4").replace(".", "-")
    return f"https://{linode_host}.ip.linodeusercontent.com:5443"
