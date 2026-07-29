import uuid

from regression_tests.services.mysql.mysql_service import MysqlService


def test_mysql_up(remote_exec, app_credentials):
    # Verifies that the database unit is active and answers an authenticated query.
    service = MysqlService(remote_exec)
    assert service.unit_active() == "active", "mariadb unit is not active"
    out, err, code = service.query(app_credentials["MySQL Root Password"], "SELECT 1;")
    assert code == 0, f"SELECT 1 failed (exit {code}): {err or out}"
    assert out == "1", f"unexpected result from SELECT 1: {out}"


def test_mysql_port_listening_on_loopback(remote_exec):
    # Verifies that the server listens on 3306 and stays bound to loopback only.
    service = MysqlService(remote_exec)
    listener = service.port_listener()
    assert "127.0.0.1:3306" in listener, f"mysql is not listening on loopback port 3306: {listener}"
    assert "0.0.0.0:3306" not in listener, f"mysql is exposed on all interfaces: {listener}"


def test_mysql_data_roundtrip(remote_exec, app_credentials):
    # Verifies that a row written to a new database can be read back with its value intact.
    service = MysqlService(remote_exec)
    password = app_credentials["MySQL Root Password"]
    suffix = uuid.uuid4().hex[:12]
    database = f"smoke_{suffix}"
    label = f"roundtrip-{suffix}"
    out, err, code = service.query(
        password,
        f"CREATE DATABASE {database};"
        f"CREATE TABLE {database}.items (id INT PRIMARY KEY, label VARCHAR(64));"
        f"INSERT INTO {database}.items (id, label) VALUES (1, '{label}');"
        f"SELECT label FROM {database}.items WHERE id = 1;",
    )
    assert code == 0, f"write/read round-trip failed (exit {code}): {err or out}"
    assert out == label, f"row did not round-trip, expected {label}: {out}"
    service.query(password, f"DROP DATABASE {database};")


def test_mysql_rejects_invalid_password(remote_exec):
    # Verifies that the database refuses a connection made with a wrong password.
    service = MysqlService(remote_exec)
    out, err, code = service.query("invalid-" + uuid.uuid4().hex, "SELECT 1;")
    assert code != 0, f"authentication with an invalid password unexpectedly succeeded: {out}"
    assert "Access denied" in err, f"unexpected error for an invalid password: {err or out}"
