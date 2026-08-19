"""Deterministic TLS certificate and transport inspection."""

from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone
from typing import Any

from cryptography import x509


def _finding(
    severity: str,
    title: str,
    summary: str,
    remediation: str,
    *,
    status: str = "finding",
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "check": "SSL/TLS",
        "severity": severity,
        "status": status,
        "title": title,
        "summary": summary,
        "remediation": remediation,
        "evidence": evidence or {},
    }


def _certificate_expiry(cert: x509.Certificate) -> datetime:
    value = getattr(cert, "not_valid_after_utc", None)
    if value is not None:
        return value
    return cert.not_valid_after.replace(tzinfo=timezone.utc)


def check_ssl(hostname: str, port: int = 443, timeout: float = 6.0) -> list[dict[str, Any]]:
    """Inspect a target's TLS certificate, negotiated protocol, issuer, and public key.

    The socket deliberately disables certificate verification so an expired or self-signed
    certificate can be measured and reported rather than stopping the inspection early.
    """

    findings: list[dict[str, Any]] = []
    try:
        context = ssl._create_unverified_context()
        with socket.create_connection((hostname, port), timeout=timeout) as connection:
            with context.wrap_socket(connection, server_hostname=hostname) as tls_socket:
                cert_bytes = tls_socket.getpeercert(binary_form=True)
                protocol = tls_socket.version() or "unknown"

        certificate = x509.load_der_x509_certificate(cert_bytes)
        expires_at = _certificate_expiry(certificate)
        days_remaining = (expires_at - datetime.now(timezone.utc)).days
        issuer = certificate.issuer.rfc4514_string() or "Unknown issuer"

        if days_remaining < 0:
            findings.append(
                _finding(
                    "critical",
                    "TLS certificate has expired",
                    f"The certificate expired {abs(days_remaining)} day(s) ago. Issuer: {issuer}.",
                    "Renew and deploy a valid certificate, then confirm the full certificate chain is served.",
                    evidence={"issuer": issuer, "expires_at": expires_at.isoformat(), "days_remaining": days_remaining},
                )
            )
        elif days_remaining < 14:
            findings.append(
                _finding(
                    "high",
                    "TLS certificate expires soon",
                    f"The certificate expires in {days_remaining} day(s). Issuer: {issuer}.",
                    "Renew the certificate now and verify automatic renewal before its expiry date.",
                    evidence={"issuer": issuer, "expires_at": expires_at.isoformat(), "days_remaining": days_remaining},
                )
            )
        elif days_remaining < 30:
            findings.append(
                _finding(
                    "medium",
                    "TLS certificate renewal window is approaching",
                    f"The certificate expires in {days_remaining} day(s). Issuer: {issuer}.",
                    "Confirm certificate renewal is scheduled and monitor the next deployment.",
                    evidence={"issuer": issuer, "expires_at": expires_at.isoformat(), "days_remaining": days_remaining},
                )
            )
        else:
            findings.append(
                _finding(
                    "info",
                    "TLS certificate is within its validity window",
                    f"The certificate expires in {days_remaining} day(s). Issuer: {issuer}.",
                    "Continue monitoring automated renewal and certificate-chain health.",
                    status="pass",
                    evidence={"issuer": issuer, "expires_at": expires_at.isoformat(), "days_remaining": days_remaining},
                )
            )

        if protocol in {"TLSv1", "TLSv1.1", "SSLv3", "SSLv2"}:
            findings.append(
                _finding(
                    "high",
                    "Deprecated TLS protocol negotiated",
                    f"The server negotiated {protocol}, which is no longer considered a modern transport baseline.",
                    "Disable TLS 1.0 and TLS 1.1 and configure the server to require TLS 1.2 or TLS 1.3.",
                    evidence={"protocol": protocol},
                )
            )
        else:
            findings.append(
                _finding(
                    "info",
                    "Modern TLS protocol negotiated",
                    f"The server negotiated {protocol} for this connection.",
                    "Maintain TLS 1.2 or TLS 1.3 as the minimum production baseline.",
                    status="pass",
                    evidence={"protocol": protocol},
                )
            )

        public_key = certificate.public_key()
        key_size = getattr(public_key, "key_size", None)
        key_type = public_key.__class__.__name__.replace("PublicKey", "")
        if key_size is not None and key_size < 2048:
            findings.append(
                _finding(
                    "high",
                    "TLS public key is below the 2048-bit baseline",
                    f"The certificate exposes a {key_type} public key with {key_size} bits.",
                    "Replace the certificate with one using at least a 2048-bit RSA key or a modern elliptic-curve key.",
                    evidence={"key_type": key_type, "key_size": key_size},
                )
            )
        else:
            size_label = f"{key_size}-bit" if key_size else "modern"
            findings.append(
                _finding(
                    "info",
                    "TLS public key meets the configured baseline",
                    f"The certificate exposes a {size_label} {key_type} public key.",
                    "Review certificate key algorithms during scheduled certificate rotation.",
                    status="pass",
                    evidence={"key_type": key_type, "key_size": key_size},
                )
            )
    except (OSError, ssl.SSLError, ValueError) as exc:
        findings.append(
            _finding(
                "high",
                "TLS inspection could not establish a secure connection",
                "The target did not complete a TLS handshake on port 443 within the configured timeout.",
                "Confirm HTTPS is enabled, port 443 is reachable, and the server presents a valid TLS service.",
                evidence={"error_type": exc.__class__.__name__},
            )
        )
    return findings
