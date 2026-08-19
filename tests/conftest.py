from pathlib import Path

import pytest

from backend.app import create_app
from backend.auth import LocalAuthStore


@pytest.fixture()
def app(tmp_path: Path):
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret", "AUTH_STORE": LocalAuthStore(tmp_path / "sitesentry.db")})
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
