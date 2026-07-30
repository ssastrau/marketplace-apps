class WireGuardServerService:
    """
    Interface and config actions for the WireGuard server over SSH.
    """

    UNIT = "wg-quick@wg0"
    INTERFACE = "wg0"
    CONFIG = "/etc/wireguard/wg0.conf"
    LISTEN_PORT = 51820

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

    def interface_listen_port(self):
        out, _, _ = self._run(f"wg show {self.INTERFACE} listen-port")
        return out

    def link_flags(self):
        out, _, _ = self._run(f"ip -brief link show {self.INTERFACE} | awk '{{print $3}}'")
        return out
