"""Bounded common-port exposure check for a single target."""

from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any


COMMON_PORTS: dict[int, tuple[str, str, str]] = {
    21: ("FTP", "medium", "FTP is often unnecessary on public web hosts and may expose an older file-transfer service."),
    22: ("SSH", "medium", "SSH administration is reachable from the internet. This is normal only when access is tightly restricted."),
    23: ("Telnet", "high", "Telnet transmits credentials and administration traffic without modern transport security."),
    25: ("SMTP", "medium", "An SMTP service is reachable. Confirm it is intentional and protected against relay abuse."),
    53: ("DNS", "medium", "A DNS service is reachable. Confirm recursive queries are not exposed publicly."),
    80: ("HTTP", "info", "HTTP is expected for many websites, but should redirect visitors to HTTPS."),
    110: ("POP3", "medium", "A POP3 mail service is reachable. Confirm it is required and uses encrypted authentication."),
    143: ("IMAP", "medium", "An IMAP mail service is reachable. Confirm it is required and uses encrypted authentication."),
    443: ("HTTPS", "info", "HTTPS is expected for a website and is inspected separately by the TLS check."),
    445: ("SMB", "high", "Windows file sharing should rarely be exposed directly to the public internet."),
    3306: ("MySQL", "high", "A MySQL database service is reachable. Public database exposure increases attack surface."),
    3389: ("RDP", "high", "Remote Desktop is reachable. Restrict it with a VPN or strict source allowlist."),
    5432: ("PostgreSQL", "high", "A PostgreSQL database service is reachable. Public database exposure increases attack surface."),
    6379: ("Redis", "critical", "Redis is reachable. Public Redis exposure can lead to data loss or host compromise if unauthenticated."),
    8080: ("HTTP alternate", "medium", "An alternate HTTP service is reachable. Confirm it is intentionally public and securely configured."),
}


def _probe(hostname: str, port: int, timeout: float) -> tuple[int, bool]:
    try:
        with socket.create_connection((hostname, port), timeout=timeout):
            return port, True
    except OSError:
        return port, False


def check_ports(hostname: str, timeout: float = 1.2, workers: int = 16) -> list[dict[str, Any]]:
    """Probe a small fixed list of commonly exposed ports; no range scan is performed."""

    findings: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(workers, len(COMMON_PORTS))) as executor:
        futures = [executor.submit(_probe, hostname, port, timeout) for port in COMMON_PORTS]
        for future in as_completed(futures):
            port, is_open = future.result()
            if not is_open:
                continue
            service, severity, explanation = COMMON_PORTS[port]
            findings.append(
                {
                    "check": "Common ports",
                    "severity": severity,
                    "status": "pass" if severity == "info" else "finding",
                    "title": f"Port {port} open — {service}",
                    "summary": explanation,
                    "remediation": (
                        "Keep the service documented and continue to protect it with current TLS and access-control settings."
                        if severity == "info"
                        else "Verify the service is required. If it is not, close the port; otherwise limit network access and apply current patches."
                    ),
                    "evidence": {"port": port, "service": service},
                }
            )
    return sorted(findings, key=lambda finding: finding["evidence"]["port"])
