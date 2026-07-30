class WireGuardClientService:
    """
    Interface and key actions for the WireGuard client over SSH.
    """

    UNIT = "wg-quick@wg0"
    INTERFACE = "wg0"
    CONFIG = "/etc/wireguard/wg0.conf"

    def __init__(self, remote_exec):
        self._run = remote_exec

    def unit_state(self):
        out, _, _ = self._run(f"systemctl is-active {self.UNIT}")
        return out

    def unit_enabled(self):
        out, _, _ = self._run(f"systemctl is-enabled {self.UNIT}")
        return out

    def config_value(self, field):
        if field.lower() == "privatekey":
            raise ValueError("refusing to read PrivateKey out of the config")
        out, _, _ = self._run(
            f"grep -m1 '^{field}' {self.CONFIG} | cut -d= -f2- | tr -d ' '"
        )
        return out

    def interface_public_key(self):
        out, _, _ = self._run(f"wg show {self.INTERFACE} public-key")
        return out

    def interface_address(self):
        out, _, _ = self._run(f"ip -brief addr show {self.INTERFACE} | awk '{{print $3}}'")
        return out

    def link_flags(self):
        out, _, _ = self._run(f"ip -brief link show {self.INTERFACE} | awk '{{print $3}}'")
        return out

    def peers(self):
        out, _, _ = self._run(f"wg show {self.INTERFACE} peers")
        return out.splitlines()

    def peer_endpoint(self):
        out, _, _ = self._run(f"wg show {self.INTERFACE} endpoints | cut -f2")
        return out

    def peer_allowed_ips(self):
        out, _, _ = self._run(f"wg show {self.INTERFACE} allowed-ips | cut -f2")
        return out
