import uuid

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import create_app


def test_request_id_generated_when_absent(client):
    resp = client.get("/api/v1/health/live")
    rid = resp.headers.get("X-Request-ID")
    assert rid
    # Generated value is a valid uuid4.
    uuid.UUID(rid)


def test_request_id_echoed_when_present(client):
    sent = "test-request-id-123"
    resp = client.get("/api/v1/health/live", headers={"X-Request-ID": sent})
    assert resp.headers.get("X-Request-ID") == sent


def test_unhandled_exception_returns_500_envelope_without_stack_trace(make_client):
    app = create_app()

    @app.get("/boom")
    def boom():
        raise ValueError("super secret internal detail")

    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/boom")
    assert resp.status_code == 500
    body = resp.json()
    assert body["error"]["code"] == "internal_error"
    assert body["error"]["message"] == "Internal server error"
    assert body["error"]["request_id"]
    # The exception detail must never leak into the response body.
    assert "super secret internal detail" not in resp.text
    assert "Traceback" not in resp.text


def test_http_exception_uses_error_envelope(make_client):
    from fastapi import HTTPException

    app = create_app()

    @app.get("/notfound")
    def notfound():
        raise HTTPException(status_code=404, detail="nope")

    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/notfound")
    assert resp.status_code == 404
    body = resp.json()
    assert "error" in body
    assert body["error"]["message"] == "nope"
    assert body["error"]["request_id"]


def test_docs_enabled_in_development(monkeypatch):
    monkeypatch.setattr(settings, "environment", "development")
    app = create_app()
    client = TestClient(app)
    assert client.get("/docs").status_code == 200


def test_docs_disabled_in_production(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")
    app = create_app()
    client = TestClient(app)
    assert client.get("/docs").status_code == 404
