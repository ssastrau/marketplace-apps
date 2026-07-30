import shlex


class ValkeyService:
    """
    Client and CLI actions for the Valkey datastore over SSH.
    """

    UNIT = "valkey"
    TLS_PORT = 6379
    CA_CERT = "/etc/valkey/ssl/ca/ca.crt"
    CLIENT_CERT = "/etc/valkey/ssl/certs/client1.crt"
    CLIENT_KEY = "/etc/valkey/ssl/keys/client1.key.pem"

    def __init__(self, remote_exec):
        self._run = remote_exec

    def unit_state(self):
        out, _, _ = self._run(f"systemctl is-active {self.UNIT}")
        return out

    def cli(self, user, password, args, tls=True):
        tls_flags = ""
        if tls:
            tls_flags = (
                f"--tls --cacert {self.CA_CERT} "
                f"--cert {self.CLIENT_CERT} --key {self.CLIENT_KEY} "
            )
        return self._run(
            f"valkey-cli {tls_flags}"
            f"--user {shlex.quote(user)} --pass {shlex.quote(password)} "
            f"--no-auth-warning {args}"
        )

    def listening_sockets(self):
        out, _, _ = self._run(f"ss -tlnH 'sport = :{self.TLS_PORT}'")
        return out

    def firewall_rules(self):
        out, _, _ = self._run("ufw status")
        return out
