"""Deterministic HTTP response-header inspection."""

from __future__ import annotations

from typing import Any

import requests


RULES: tuple[tuple[str, str, str, str], ...] = (
    (
        "Content-Security-Policy",
        "medium",
        "Missing Content-Security-Policy",
        "Add a restrictive Content-Security-Policy and tune it for the scripts, styles, frames, and connections your site actually needs.",
    ),
    (
        "Strict-Transport-Security",
        "medium",
        "Missing Strict-Transport-Security",
        "After verifying all traffic works over HTTPS, set Strict-Transport-Security with a long max-age and consider includeSubDomains.",
    ),
    (
        "X-Frame-Options",
        "medium",
        "Missing X-Frame-Options",
        "Set X-Frame-Options to DENY or SAMEORIGIN unless the page is intentionally embedded elsewhere.",
    ),
    (
        "X-Content-Type-Options",
        "low",
        "Missing X-Content-Type-Options",
        "Set X-Content-Type-Options: nosniff to reduce MIME-type sniffing.",
    ),
    (
        "Referrer-Policy",
        "low",
        "Missing Referrer-Policy",
        "Set a Referrer-Policy such as strict-origin-when-cross-origin after validating your analytics and login flows.",
    ),
)


def _finding(severity: str, title: str, summary: str, remediation: str, *, status: str = "finding", evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "check": "HTTP headers",
        "severity": severity,
        "status": status,
        "title": title,
        "summary": summary,
        "remediation": remediation,
        "evidence": evidence or {},
    }


def check_headers(url: str, timeout: float = 8.0, session: requests.Session | None = None) -> list[dict[str, Any]]:
    """Inspect the final response after a bounded redirect chain."""

    requester = session or requests.Session()
    try:
        response = requester.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "SiteSentry/0.1 local security inspection"},
        )
    except requests.RequestException as exc:
        return [
            _finding(
                "high",
                "HTTP response could not be inspected",
                "SiteSentry could not retrieve the target URL within the configured timeout.",
                "Confirm the URL is reachable from this machine and does not require an interactive login to load its main page.",
                evidence={"error_type": exc.__class__.__name__},
            )
        ]

    findings: list[dict[str, Any]] = []
    headers = {key.lower(): value for key, value in response.headers.items()}
    final_scheme = response.url.split(":", 1)[0].lower()

    for header, severity, title, remediation in RULES:
        header_value = headers.get(header.lower())
        if header == "Strict-Transport-Security" and final_scheme != "https":
            findings.append(
                _finding(
                    "high",
                    "Target does not finish on HTTPS",
                    f"The inspected page resolved to {response.url}, so HSTS cannot protect the final response.",
                    "Redirect HTTP traffic to HTTPS and serve the final page over HTTPS before enabling HSTS.",
                    evidence={"final_url": response.url, "status_code": response.status_code},
                )
            )
        elif not header_value:
            findings.append(
                _finding(
                    severity,
                    title,
                    f"The final response from {response.url} does not include the {header} header.",
                    remediation,
                    evidence={"final_url": response.url, "status_code": response.status_code, "header": header},
                )
            )
        elif header == "X-Content-Type-Options" and header_value.lower().strip() != "nosniff":
            findings.append(
                _finding(
                    "low",
                    "X-Content-Type-Options is not set to nosniff",
                    f"The target sends X-Content-Type-Options: {header_value}.",
                    "Set X-Content-Type-Options: nosniff on HTML and static asset responses.",
                    evidence={"header": header, "value": header_value},
                )
            )
        else:
            findings.append(
                _finding(
                    "info",
                    f"{header} is present",
                    f"The final response includes {header}.",
                    "Review the policy value during scheduled security configuration reviews.",
                    status="pass",
                    evidence={"header": header, "value": header_value},
                )
            )
    return findings
