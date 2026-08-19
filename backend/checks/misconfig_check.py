"""Low-impact deterministic probes for common public web exposures."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import requests


PROBES: tuple[tuple[str, str, str, str, str], ...] = (
    ("/.git/HEAD", "critical", "Public Git metadata detected", "A reachable .git/HEAD response can expose repository history and secrets.", "Remove the .git directory from the web root and block dot-directories at the web server."),
    ("/.env", "critical", "Public environment file detected", "A reachable .env response can expose application secrets and deployment configuration.", "Remove .env files from the web root, rotate any exposed secrets, and block dot-files at the web server."),
    ("/admin", "medium", "Public administration route detected", "An administration route responded successfully. It may be legitimate, but should be strongly protected.", "Confirm the route requires strong authentication, MFA where possible, rate limiting, and appropriate network access controls."),
)


def _finding(severity: str, title: str, summary: str, remediation: str, *, status: str = "finding", evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "check": "Web exposure",
        "severity": severity,
        "status": status,
        "title": title,
        "summary": summary,
        "remediation": remediation,
        "evidence": evidence or {},
    }


def _looks_like_directory_listing(response: requests.Response) -> bool:
    if "text/html" not in response.headers.get("content-type", "").lower():
        return False
    body = response.text[:4_000].lower()
    return "<title>index of" in body or "directory listing for" in body


def check_misconfigurations(base_url: str, timeout: float = 6.0, session: requests.Session | None = None) -> list[dict[str, Any]]:
    """Run fixed, non-destructive path probes and an invalid-route error-page check."""

    requester = session or requests.Session()
    findings: list[dict[str, Any]] = []
    request_headers = {"User-Agent": "SiteSentry/0.1 local security inspection"}

    for path, severity, title, summary, remediation in PROBES:
        probe_url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        try:
            response = requester.get(probe_url, timeout=timeout, allow_redirects=False, headers=request_headers)
        except requests.RequestException as exc:
            findings.append(
                _finding(
                    "low",
                    f"Could not inspect {path}",
                    "The probe did not receive a response within the configured timeout.",
                    "Review the endpoint manually if it is relevant to your deployment.",
                    evidence={"path": path, "error_type": exc.__class__.__name__},
                )
            )
            continue

        if response.status_code == 200:
            findings.append(_finding(severity, title, summary, remediation, evidence={"path": path, "status_code": response.status_code}))
        else:
            findings.append(
                _finding(
                    "info",
                    f"{path} was not publicly served",
                    f"The probe returned HTTP {response.status_code}.",
                    "Keep deployment files outside the public web root and preserve explicit server deny rules.",
                    status="pass",
                    evidence={"path": path, "status_code": response.status_code},
                )
            )

    listing_url = urljoin(base_url.rstrip("/") + "/", "__sitesentry_directory_probe__/" )
    try:
        listing_response = requester.get(listing_url, timeout=timeout, allow_redirects=False, headers=request_headers)
        if _looks_like_directory_listing(listing_response):
            findings.append(
                _finding(
                    "medium",
                    "Directory listing markers detected",
                    "The invalid route returned a response that looks like a directory listing.",
                    "Disable auto-indexing/directory listing in the web server and serve explicit index files only.",
                    evidence={"path": "/__sitesentry_directory_probe__/", "status_code": listing_response.status_code},
                )
            )
        else:
            findings.append(
                _finding(
                    "info",
                    "No directory-listing marker found",
                    "The bounded directory-listing probe did not expose a typical index page.",
                    "Continue to disable auto-indexing explicitly in production web-server configuration.",
                    status="pass",
                    evidence={"path": "/__sitesentry_directory_probe__/", "status_code": listing_response.status_code},
                )
            )
    except requests.RequestException as exc:
        findings.append(
            _finding(
                "low",
                "Directory-listing probe could not be completed",
                "The bounded invalid-route probe did not receive a response within the configured timeout.",
                "Review web-server directory-listing configuration manually.",
                evidence={"error_type": exc.__class__.__name__},
            )
        )

    error_url = urljoin(base_url.rstrip("/") + "/", "__sitesentry_nonexistent_route_9d0b3/")
    try:
        error_response = requester.get(error_url, timeout=timeout, allow_redirects=False, headers=request_headers)
        error_markers = ("traceback", "stack trace", "exception at", "debugger", "werkzeug debugger")
        body = error_response.text[:8_000].lower()
        if error_response.status_code >= 500 and any(marker in body for marker in error_markers):
            findings.append(
                _finding(
                    "medium",
                    "Verbose error response detected",
                    "A deliberately invalid route produced an error response containing a common debugging marker.",
                    "Disable production debug mode and configure generic public error pages without stack traces.",
                    evidence={"status_code": error_response.status_code},
                )
            )
        else:
            findings.append(
                _finding(
                    "info",
                    "No verbose error marker found",
                    "The bounded invalid-route probe did not return a common debugging marker in an error response.",
                    "Keep production debug mode disabled and review errors through protected server logs only.",
                    status="pass",
                    evidence={"status_code": error_response.status_code},
                )
            )
    except requests.RequestException as exc:
        findings.append(
            _finding(
                "low",
                "Verbose-error probe could not be completed",
                "The bounded invalid-route probe did not receive a response within the configured timeout.",
                "Confirm production error handling manually if the endpoint is protected or unavailable.",
                evidence={"error_type": exc.__class__.__name__},
            )
        )
    return findings
