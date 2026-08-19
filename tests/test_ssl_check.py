from backend.checks.ssl_check import check_ssl


def test_ssl_check_returns_actionable_finding_when_tls_connection_fails():
    findings = check_ssl("invalid.example.test", timeout=0.01)
    assert len(findings) == 1
    assert findings[0]["severity"] == "high"
    assert "could not establish" in findings[0]["title"].lower()
