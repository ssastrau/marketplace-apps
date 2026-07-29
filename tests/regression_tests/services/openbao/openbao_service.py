import re
import shlex


class OpenBaoService:
    """
    Client actions for the OpenBao Marketplace app over SSH.
    """

    UNIT = "openbao"
    PORT = 8200
    CONFIG = "/etc/openbao/openbao.hcl"

    def __init__(self, remote_exec):
        self._run = remote_exec
        self._api_addr = None

    def api_address(self):
        if self._api_addr is None:
            out, _, _ = self._run(f"awk -F'\"' '/^api_addr/{{print $2}}' {self.CONFIG}")
            self._api_addr = out
        return self._api_addr

    def _bao(self, args, token=None, timeout=30):
        env = f"BAO_ADDR={shlex.quote(self.api_address())}"
        if token:
            env += f" BAO_TOKEN={shlex.quote(token)}"
        return self._run(f"{env} bao {args}", timeout=timeout)

    def unit_active(self):
        out, _, _ = self._run(f"systemctl is-active {self.UNIT}")
        return out

    def port_listener(self):
        out, _, _ = self._run(f"ss -tlnH 'sport = :{self.PORT}'")
        return out

    def status(self):
        return self._bao("status")

    def status_fields(self):
        out, _, _ = self.status()
        fields = {}
        for line in out.splitlines():
            parts = re.split(r"\s{2,}", line.strip())
            if len(parts) == 2:
                fields[parts[0]] = parts[1]
        return fields

    def unseal(self, key):
        return self._bao(f"operator unseal {shlex.quote(key)}")

    def enable_kv(self, path, token):
        return self._bao(f"secrets enable -path={shlex.quote(path)} kv-v2", token=token)

    def kv_put(self, path, token, field, value):
        return self._bao(
            f"kv put {shlex.quote(path)} {shlex.quote(field)}={shlex.quote(value)}", token=token
        )

    def kv_get_field(self, path, token, field):
        return self._bao(
            f"kv get -field={shlex.quote(field)} {shlex.quote(path)}", token=token
        )
