from backend.checks.misconfig_check import check_misconfigurations


class Response:
    def __init__(self, status_code, text="", content_type="text/html"):
        self.status_code = status_code
        self.text = text
        self.headers = {"content-type": content_type}


class Session:
    def get(self, url, *args, **kwargs):
        if url.endswith("/.env"):
            return Response(200, "SECRET_KEY=test")
        if "directory_probe" in url:
            return Response(404, "Not found")
        if "nonexistent_route" in url:
            return Response(500, "Generic error")
        return Response(404, "Not found")


def test_misconfiguration_check_flags_public_env_file():
    findings = check_misconfigurations("https://example.com", session=Session())
    env_finding = next(finding for finding in findings if finding["evidence"].get("path") == "/.env")
    assert env_finding["severity"] == "critical"
    assert env_finding["status"] == "finding"


def test_misconfiguration_check_marks_nonserved_git_as_pass():
    findings = check_misconfigurations("https://example.com", session=Session())
    git_finding = next(finding for finding in findings if finding["evidence"].get("path") == "/.git/HEAD")
    assert git_finding["status"] == "pass"
