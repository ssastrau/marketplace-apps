import shlex


class MysqlService:
    """
    Client actions for the MySQL Marketplace app over SSH
    """

    UNIT = "mariadb"
    HOST = "127.0.0.1"
    PORT = 3306
    DB_USER = "root"

    def __init__(self, remote_exec):
        self._run = remote_exec

    def unit_active(self):
        out, _, _ = self._run(f"systemctl is-active {self.UNIT}")
        return out

    def port_listener(self):
        out, _, _ = self._run(f"ss -tlnH 'sport = :{self.PORT}'")
        return out

    def query(self, password, sql, timeout=30):
        cmd = (
            f"MYSQL_PWD={shlex.quote(password)} mysql --protocol=TCP "
            f"-h {self.HOST} -u {self.DB_USER} -N -B -e {shlex.quote(sql)}"
        )
        return self._run(cmd, timeout=timeout)
