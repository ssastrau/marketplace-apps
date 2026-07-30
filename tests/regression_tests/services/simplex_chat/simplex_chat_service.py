import socket


class SimplexChatService:
    """
    Container and protocol actions for the SimpleX Chat servers over SSH.
    """

    SMP_CONTAINER = "simplex-smp-1"
    XFTP_CONTAINER = "simplex-xftp-1"
    SMP_PORT = 5223
    XFTP_PORT = 443
    FINGERPRINT_FILE = "/etc/opt/simplex/fingerprint"

    def __init__(self, remote_exec, host):
        self._run = remote_exec
        self._host = host

    def container_status(self, name):
        out, _, _ = self._run(f"docker inspect -f '{{{{.State.Status}}}}' {name}")
        return out

    def fingerprint(self):
        out, _, _ = self._run(f"cat {self.FINGERPRINT_FILE}")
        return out

    def advertised_address(self):
        out, _, _ = self._run(
            f"docker logs {self.SMP_CONTAINER} 2>&1 | grep -m1 'Server address:'",
            timeout=60,
        )
        return out

    def tcp_connect(self, port, timeout=8):
        sock = socket.socket()
        sock.settimeout(timeout)
        try:
            sock.connect((self._host, port))
            return True, ""
        except OSError as error:
            return False, type(error).__name__
        finally:
            sock.close()
