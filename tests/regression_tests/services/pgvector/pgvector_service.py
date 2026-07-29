import shlex


class PgvectorService:
    """
    Client actions for the pgvector Marketplace app over SSH.
    """

    HOST = "127.0.0.1"
    PORT = 5432
    APP_DB = "appname"

    def __init__(self, remote_exec):
        self._run = remote_exec

    def cluster_unit_state(self):
        out, _, _ = self._run(
            "systemctl list-units --type=service --all 'postgresql@*' --no-legend --plain"
        )
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 4:
                return parts[0], parts[2], parts[3]
        return None, None, None

    def is_ready(self):
        out, _, code = self._run(f"pg_isready -h {self.HOST}")
        return out, code

    def port_listener(self):
        out, _, _ = self._run(f"ss -tlnH 'sport = :{self.PORT}'")
        return out

    def query(self, user, password, sql, database=None, timeout=30):
        cmd = (
            f"PGPASSWORD={shlex.quote(password)} psql -h {self.HOST} "
            f"-U {shlex.quote(user)} -d {shlex.quote(database or self.APP_DB)} "
            f"-tAc {shlex.quote(sql)}"
        )
        return self._run(cmd, timeout=timeout)
