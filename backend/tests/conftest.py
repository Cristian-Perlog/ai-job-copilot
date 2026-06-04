import os

# Provide a DATABASE_URL before any app import so Settings() and the
# module-level engine in app.core.db can be constructed without a real
# .env file or a running database. Engine creation is lazy-connecting,
# so this URL is never actually dialed except through overridden deps.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_nodb")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.db import get_db  # noqa: E402
from app.main import create_app  # noqa: E402


class StubSession:
    """Minimal stand-in for a SQLAlchemy Session used in tests."""

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    def execute(self, *args, **kwargs):
        if self.fail:
            raise RuntimeError("database unavailable")
        return None


@pytest.fixture
def make_client():
    """Build a TestClient whose get_db dependency yields a stub session.

    Pass fail=True to simulate a database that errors on execute().
    raise_server_errors=False lets us assert on 500 response bodies
    produced by the exception handlers rather than re-raising.
    """

    def _make(*, fail: bool = False) -> TestClient:
        app = create_app()

        def _override_get_db():
            yield StubSession(fail=fail)

        app.dependency_overrides[get_db] = _override_get_db
        return TestClient(app, raise_server_exceptions=False)

    return _make


@pytest.fixture
def client(make_client):
    return make_client()
