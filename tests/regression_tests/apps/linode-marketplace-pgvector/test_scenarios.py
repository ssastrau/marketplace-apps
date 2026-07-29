import uuid

from regression_tests.services.pgvector.pgvector_service import PgvectorService


def test_pgvector_up(remote_exec, app_credentials):
    # Verifies that the Postgres cluster is running and answers an authenticated query.
    service = PgvectorService(remote_exec)
    unit, active, sub = service.cluster_unit_state()
    assert unit, "no postgresql@<version>-main cluster unit was found"
    assert active == "active", f"{unit} is not active: {active}"
    assert sub == "running", f"{unit} is not running: {sub}"

    ready, code = service.is_ready()
    assert code == 0, f"pg_isready reported the cluster not accepting connections: {ready}"

    out, err, code = service.query(
        app_credentials["Postgres Admin User"], app_credentials["Postgres Admin Password"], "SELECT 1;"
    )
    assert code == 0, f"SELECT 1 failed (exit {code}): {err or out}"
    assert out == "1", f"unexpected result from SELECT 1: {out}"


def test_pgvector_listens_on_loopback(remote_exec):
    # Verifies that Postgres listens on 5432 and stays bound to loopback only.
    service = PgvectorService(remote_exec)
    listener = service.port_listener()
    assert "127.0.0.1:5432" in listener, f"postgres is not listening on loopback 5432: {listener}"
    assert "0.0.0.0:5432" not in listener, f"postgres is exposed on all interfaces: {listener}"


def test_pgvector_extension_enabled(remote_exec, app_credentials):
    # Verifies that the vector extension is registered in the application database.
    service = PgvectorService(remote_exec)
    out, err, code = service.query(
        app_credentials["Postgres Admin User"],
        app_credentials["Postgres Admin Password"],
        "SELECT extname FROM pg_extension WHERE extname = 'vector';",
    )
    assert code == 0, f"querying pg_extension failed (exit {code}): {err or out}"
    assert out == "vector", f"the vector extension is not enabled in the app database: {out!r}"


def test_pgvector_similarity_roundtrip(remote_exec, app_credentials):
    # Verifies that stored vectors are returned intact and ranked correctly by L2 distance.
    service = PgvectorService(remote_exec)
    user = app_credentials["Postgres Admin User"]
    password = app_credentials["Postgres Admin Password"]
    table = f"smoke_{uuid.uuid4().hex[:12]}"

    out, err, code = service.query(
        user,
        password,
        f"CREATE TABLE {table} (id text PRIMARY KEY, embedding vector(3));"
        f"INSERT INTO {table} (id, embedding) VALUES "
        f"('x-axis', '[1,0,0]'), ('y-axis', '[0,1,0]'), ('z-axis', '[0,0,1]');",
    )
    assert code == 0, f"seeding the vector table failed (exit {code}): {err or out}"

    out, err, code = service.query(
        user, password, f"SELECT id FROM {table} ORDER BY embedding <-> '[0.9,0.1,0]' LIMIT 1;"
    )
    assert code == 0, f"nearest-neighbour query failed (exit {code}): {err or out}"
    assert out == "x-axis", f"nearest neighbour to [0.9,0.1,0] should be x-axis, got {out!r}"

    out, err, code = service.query(
        user, password, f"SELECT embedding FROM {table} WHERE id = 'x-axis';"
    )
    assert code == 0, f"reading the stored vector failed (exit {code}): {err or out}"
    assert out == "[1,0,0]", f"stored vector did not round-trip: {out!r}"

    service.query(user, password, f"DROP TABLE {table};")


def test_pgvector_distance_operator(remote_exec, app_credentials):
    # Verifies that the L2 distance operator computes the exact expected value.
    service = PgvectorService(remote_exec)
    out, err, code = service.query(
        app_credentials["Postgres Admin User"],
        app_credentials["Postgres Admin Password"],
        "SELECT round(('[1,0,0]'::vector <-> '[0,1,0]'::vector)::numeric, 6);",
    )
    assert code == 0, f"distance query failed (exit {code}): {err or out}"
    assert out == "1.414214", f"L2 distance between orthogonal unit vectors was wrong: {out!r}"
