class NetFoundryEdgeRouterService:
    """
    Host actions for the NetFoundry Edge Router Marketplace app over SSH.
    """

    INSTALL_DIR = "/opt/netfoundry"
    REGISTRATION_TOOL = f"{INSTALL_DIR}/router-registration"
    SALT_UNIT = "salt-minion"
    LOGIN_HELP = "/etc/profile.d/nfhelp.sh"

    def __init__(self, remote_exec):
        self._run = remote_exec

    def registration_tool_help(self, timeout=120):
        return self._run(f"{self.REGISTRATION_TOOL} --help")

    def file_mode(self, path):
        out, _, _ = self._run(f"stat -c '%a' {path} 2>/dev/null")
        return out

    def unit_state(self, unit):
        active, _, _ = self._run(f"systemctl is-active {unit}")
        enabled, _, _ = self._run(f"systemctl is-enabled {unit}")
        return active, enabled

    def salt_minion_version(self):
        out, _, _ = self._run(f"{self.SALT_UNIT} --version")
        return out

    def minion_id_exists(self):
        _, _, code = self._run("test -f /etc/salt/minion_id")
        return code == 0

    def ufw_status(self):
        out, _, _ = self._run("ufw status verbose")
        return out

    def listening_tcp_ports(self):
        out, _, _ = self._run("ss -tlnH")
        return out
