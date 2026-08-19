import pytest

from backend import app as app_module
from backend.app import normalize_target


def test_setup_login_and_logout(client):
    response = client.post("/api/auth/setup", json={"username": "operator", "password": "a-long-local-password"})
    assert response.status_code == 201
    assert client.get("/api/auth/status").get_json()["authenticated"] is True
    assert client.post("/api/auth/logout").status_code == 200
    assert client.post("/api/auth/login", json={"username": "operator", "password": "a-long-local-password"}).status_code == 200


def test_normalize_target_rejects_localhost():
    with pytest.raises(ValueError, match="Local"):
        normalize_target("localhost")


def test_scan_requires_authorization(client):
    client.post("/api/auth/setup", json={"username": "operator", "password": "a-long-local-password"})
    response = client.post("/api/scan", json={"target": "example.com", "authorized": False})
    assert response.status_code == 400


def test_scan_uses_isolated_check_modules(client, monkeypatch):
    client.post("/api/auth/setup", json={"username": "operator", "password": "a-long-local-password"})
    monkeypatch.setattr(app_module, "normalize_target", lambda target: {"hostname": "example.com", "url": "https://example.com/"})
    sample = [{"check": "Test", "severity": "info", "status": "pass", "title": "Pass", "summary": "ok", "remediation": "keep", "evidence": {}}]
    monkeypatch.setattr(app_module, "check_ssl", lambda host: sample)
    monkeypatch.setattr(app_module, "check_headers", lambda url: sample)
    monkeypatch.setattr(app_module, "check_ports", lambda host: sample)
    monkeypatch.setattr(app_module, "check_misconfigurations", lambda url: sample)
    response = client.post("/api/scan", json={"target": "example.com", "authorized": True})
    assert response.status_code == 200
    assert response.get_json()["score"]["grade"] == "A"
