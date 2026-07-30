import shlex
import socket


class ShadowsocksService:
    """
    Client actions for the Shadowsocks SOCKS5 proxy over SSH.
    """

    UNIT = "shadowsocks-libev"
    SERVER_PORT = 8000
    METHOD = "aes-256-gcm"
    CONFIG = "/etc/shadowsocks-libev/config.json"

    def __init__(self, remote_exec, host):
        self._run = remote_exec
        self._host = host

    def unit_active(self):
        out, _, _ = self._run(f"systemctl is-active {self.UNIT}")
        return out

    def transient_unit_active(self, unit):
        out, _, _ = self._run(f"systemctl is-active {shlex.quote(unit)}")
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

    def start_origin_server(self, unit, port, token, directory="/tmp/ss-probe"):
        self._run(
            f"mkdir -p {directory} && echo {shlex.quote(token)} > {directory}/token.txt"
        )
        return self._run(
            f"systemd-run --unit={shlex.quote(unit)} --quiet "
            f"--working-directory={directory} "
            f"python3 -m http.server {port} --bind 127.0.0.1"
        )

    def start_client(self, unit, local_port, password):
        return self._run(
            f"systemd-run --unit={shlex.quote(unit)} --quiet "
            f"ss-local -s {self._host} -p {self.SERVER_PORT} -l {local_port} "
            f"-k {shlex.quote(password)} -m {self.METHOD}"
        )

    def fetch_through_proxy(self, local_port, origin_port, max_time=15):
        return self._run(
            f"curl -s --max-time {max_time} --socks5 127.0.0.1:{local_port} "
            f"http://127.0.0.1:{origin_port}/token.txt",
            timeout=max_time + 20,
        )

    def stop_units(self, *units):
        for unit in units:
            quoted = shlex.quote(unit)
            self._run(
                f"systemctl stop {quoted} 2>/dev/null; "
                f"systemctl reset-failed {quoted} 2>/dev/null; true"
            )
