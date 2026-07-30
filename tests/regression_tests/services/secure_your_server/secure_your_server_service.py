import shlex
import socket

from regression_tests.utils.ssh import run_remote_command


class SecureYourServerService:
    """
    Host-hardening actions for the Secure Your Server Marketplace app.
    """

    SSH_PORT = 22
    JAIL = "sshd"
    NFT_BAN_SET = "inet f2b-table addr-set-sshd"
    LISTENER_PATTERN = "[p]ython3 -m http.server"

    def __init__(self, remote_exec, host):
        self._run = remote_exec
        self._host = host

    def start_listener(self, port, timeout=30):
        return self._run(
            f"nohup python3 -m http.server {port} --bind 0.0.0.0 "
            f">/tmp/listener-{port}.log 2>&1 & sleep 2",
            timeout=timeout,
        )

    def listener_bound(self, port):
        out, _, _ = self._run(f"ss -tlnH 'sport = :{port}'")
        return out

    def stop_listener(self):
        return self._run(f"pkill -f '{self.LISTENER_PATTERN}'")

    def tcp_connect(self, port, timeout=5):
        sock = socket.socket()
        sock.settimeout(timeout)
        try:
            sock.connect((self._host, port))
            return True, ""
        except OSError as error:
            return False, type(error).__name__
        finally:
            sock.close()

    def ban_ip(self, ip):
        return self._run(f"fail2ban-client set {self.JAIL} banip {shlex.quote(ip)}")

    def unban_ip(self, ip):
        return self._run(f"fail2ban-client set {self.JAIL} unbanip {shlex.quote(ip)}")

    def jail_banned_ips(self):
        out, _, _ = self._run(
            f"fail2ban-client status {self.JAIL} | awk -F':' '/Banned IP list/{{print $2}}'"
        )
        return out.split()

    def nft_ban_set(self):
        out, _, _ = self._run(f"nft list set {self.NFT_BAN_SET}")
        return out

    def ssh_password_auth(self, user, password, command, timeout=30):
        return run_remote_command(
            self._host, user, password, command,
            timeout=timeout, look_for_keys=False, allow_agent=False,
        )

    def sudo_command(self, user, password, command, timeout=30):
        return self.ssh_password_auth(
            user, password,
            f"echo {shlex.quote(password)} | sudo -S {command} 2>/dev/null",
            timeout=timeout,
        )
