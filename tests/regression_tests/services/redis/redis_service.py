import shlex


class RedisService:
    """
    Client actions for the Redis Marketplace app over SSH.
    """

    UNIT = "redis-server"
    HOST = "127.0.0.1"
    PORT = 6379
    CLIENT_CERT = "/etc/redis/ssl/certs/client1.crt"
    CLIENT_KEY = "/etc/redis/ssl/keys/client1.key.pem"
    CA_CERT = "/etc/redis/ssl/ca/ca.crt"

    def __init__(self, remote_exec):
        self._run = remote_exec

    def unit_active(self):
        out, _, _ = self._run(f"systemctl is-active {self.UNIT}")
        return out

    def port_listener(self):
        out, _, _ = self._run(f"ss -tlnH 'sport = :{self.PORT}'")
        return out

    def ufw_status(self):
        out, _, _ = self._run("ufw status")
        return out

    def cli(self, password, args, timeout=30):
        cmd = (
            f"redis-cli --tls --cert {self.CLIENT_CERT} --key {self.CLIENT_KEY} "
            f"--cacert {self.CA_CERT} -h {self.HOST} -p {self.PORT} "
            f"-a {shlex.quote(password)} --no-auth-warning {args}"
        )
        return self._run(cmd, timeout=timeout)
