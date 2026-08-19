from backend.checks.headers_check import check_headers


class Response:
    url = "https://example.com/"
    status_code = 200
    headers = {
        "Content-Security-Policy": "default-src 'self'",
        "Strict-Transport-Security": "max-age=31536000",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }


class Session:
    def get(self, *args, **kwargs):
        return Response()


def test_headers_mark_all_baselines_as_passes():
    findings = check_headers("https://example.com", session=Session())
    assert len(findings) == 5
    assert all(finding["status"] == "pass" for finding in findings)


def test_headers_flag_missing_csp():
    response = Response()
    response.headers = {"Strict-Transport-Security": "max-age=31536000"}

    class MissingSession:
        def get(self, *args, **kwargs):
            return response

    findings = check_headers("https://example.com", session=MissingSession())
    csp = next(finding for finding in findings if finding["title"] == "Missing Content-Security-Policy")
    assert csp["severity"] == "medium"
