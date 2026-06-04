def test_health_live_ok(client):
    resp = client.get("/api/v1/health/live")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_ready_ok(make_client):
    client = make_client(fail=False)
    resp = client.get("/api/v1/health/ready")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_ready_db_failure_returns_503_envelope(make_client):
    client = make_client(fail=True)
    resp = client.get("/api/v1/health/ready")
    assert resp.status_code == 503
    body = resp.json()
    assert body["error"]["code"] == "not_ready"
    assert "request_id" in body["error"]
    assert body["error"]["request_id"]
