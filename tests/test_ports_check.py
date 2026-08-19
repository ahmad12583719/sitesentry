from backend.checks import ports_check


def test_ports_reports_only_open_ports(monkeypatch):
    monkeypatch.setattr(ports_check, "_probe", lambda hostname, port, timeout: (port, port in {443, 3306}))
    findings = ports_check.check_ports("example.com", workers=4)
    assert [finding["evidence"]["port"] for finding in findings] == [443, 3306]
    assert next(finding for finding in findings if finding["evidence"]["port"] == 3306)["severity"] == "high"
