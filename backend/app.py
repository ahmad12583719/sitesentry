"""SiteSentry's local-only Flask server and deterministic scan orchestration."""

from __future__ import annotations

import html
import ipaddress
import json
import os
import socket
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, Response, jsonify, request, send_from_directory, session
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.auth import LocalAuthStore
from backend.checks.headers_check import check_headers
from backend.checks.misconfig_check import check_misconfigurations
from backend.checks.ports_check import check_ports
from backend.checks.ssl_check import check_ssl
from backend.scoring import score_findings


FRONTEND_DIR = ROOT_DIR / "frontend"
MAX_REPORTS = 20
REPORTS: dict[str, dict] = {}
REPORT_LOCK = threading.Lock()


def create_app(test_config: dict | None = None) -> Flask:
    """Create the local server. No third-party service is contacted by this application."""

    application = Flask(__name__, static_folder=None)
    configuration = test_config or {}
    auth_store = configuration.get("AUTH_STORE") or LocalAuthStore(configuration.get("DATABASE_PATH"))
    application.config.update(
        SECRET_KEY=configuration.get("SECRET_KEY") or os.environ.get("SITESENTRY_SESSION_SECRET") or auth_store.session_secret(),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        MAX_CONTENT_LENGTH=32 * 1024,
    )
    application.extensions["sitesentry_auth_store"] = auth_store

    @application.after_request
    def add_local_security_headers(response: Response) -> Response:
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @application.get("/")
    def index() -> Response:
        return send_from_directory(FRONTEND_DIR, "index.html")

    @application.get("/<path:asset_path>")
    def frontend_assets(asset_path: str) -> Response:
        if asset_path.startswith("api/"):
            return jsonify({"error": "Endpoint not found"}), 404
        return send_from_directory(FRONTEND_DIR, asset_path)

    @application.get("/api/auth/status")
    def auth_status() -> Response:
        return jsonify({
            "configured": auth_store.configured(),
            "authenticated": bool(session.get("authenticated")),
            "username": session.get("username"),
        })

    @application.post("/api/auth/setup")
    def setup() -> Response:
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))
        if not 3 <= len(username) <= 64:
            return jsonify({"error": "Choose a username between 3 and 64 characters."}), 400
        if len(password) < 12:
            return jsonify({"error": "Choose a password with at least 12 characters."}), 400
        if not auth_store.setup(username, password):
            return jsonify({"error": "Local credentials are already configured."}), 409
        session.clear()
        session.update({"authenticated": True, "username": username})
        return jsonify({"ok": True, "username": username}), 201

    @application.post("/api/auth/login")
    def login() -> Response:
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))
        if not auth_store.authenticate(username, password):
            return jsonify({"error": "The username or password was not accepted."}), 401
        session.clear()
        session.update({"authenticated": True, "username": username})
        return jsonify({"ok": True, "username": username})

    @application.post("/api/auth/logout")
    def logout() -> Response:
        session.clear()
        return jsonify({"ok": True})

    @application.post("/api/scan")
    def scan() -> Response:
        if not session.get("authenticated"):
            return jsonify({"error": "Sign in before running a scan."}), 401
        payload = request.get_json(silent=True) or {}
        if payload.get("authorized") is not True:
            return jsonify({"error": "Confirm that you are authorized to scan this target."}), 400
        try:
            target = normalize_target(str(payload.get("target", "")))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        findings = []
        findings.extend(check_ssl(target["hostname"]))
        findings.extend(check_headers(target["url"]))
        findings.extend(check_ports(target["hostname"]))
        findings.extend(check_misconfigurations(target["url"]))
        result = {
            "id": str(uuid.uuid4()),
            "target": target["url"],
            "hostname": target["hostname"],
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "findings": findings,
            "score": score_findings(findings),
            "privacy_note": "This report was produced locally. SiteSentry sent requests only to the target you entered; it does not use telemetry or third-party APIs.",
        }
        remember_report(result)
        session["last_report_id"] = result["id"]
        return jsonify(result)

    @application.get("/api/reports/<report_id>")
    def export_report(report_id: str) -> Response:
        if not session.get("authenticated"):
            return jsonify({"error": "Sign in before exporting a report."}), 401
        report = REPORTS.get(report_id)
        if not report:
            return jsonify({"error": "This local report is no longer available. Run the scan again to export it."}), 404
        export_format = request.args.get("format", "json").lower()
        filename_root = f"sitesentry-{safe_filename(report['hostname'])}-{report['id'][:8]}"
        if export_format == "json":
            return Response(
                json.dumps(report, indent=2),
                mimetype="application/json",
                headers={"Content-Disposition": f'attachment; filename="{filename_root}.json"'},
            )
        if export_format == "html":
            return Response(
                render_html_report(report),
                mimetype="text/html",
                headers={"Content-Disposition": f'attachment; filename="{filename_root}.html"'},
            )
        if export_format == "pdf":
            return Response(
                render_pdf_report(report),
                mimetype="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="{filename_root}.pdf"'},
            )
        return jsonify({"error": "Choose json, html, or pdf."}), 400

    return application


def normalize_target(raw_target: str) -> dict[str, str]:
    """Accept a public HTTP(S) site while rejecting private/reserved IP targets."""

    candidate = raw_target.strip()
    if not candidate:
        raise ValueError("Enter a website domain or HTTPS URL.")
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Enter a valid HTTP or HTTPS website domain or URL.")
    hostname = parsed.hostname.lower().rstrip(".")
    if parsed.username or parsed.password:
        raise ValueError("Credentials are not allowed in the target URL.")
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".local"):
        raise ValueError("Local and .local targets are not supported by this public-domain MVP.")
    ensure_public_hostname(hostname)
    normalized_port = f":{parsed.port}" if parsed.port else ""
    normalized_url = f"{parsed.scheme}://{hostname}{normalized_port}{parsed.path or '/'}"
    if parsed.query:
        normalized_url += f"?{parsed.query}"
    return {"hostname": hostname, "url": normalized_url}


def ensure_public_hostname(hostname: str) -> None:
    try:
        addresses = {entry[4][0] for entry in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)}
    except socket.gaierror as exc:
        raise ValueError("The target hostname could not be resolved from this machine.") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise ValueError("Targets resolving to private, loopback, link-local, or reserved IP addresses are not supported.")


def remember_report(report: dict) -> None:
    with REPORT_LOCK:
        REPORTS[report["id"]] = report
        while len(REPORTS) > MAX_REPORTS:
            REPORTS.pop(next(iter(REPORTS)))


def safe_filename(value: str) -> str:
    return "".join(character if character.isalnum() or character in {"-", "_", "."} else "-" for character in value)


def severity_label(severity: str) -> str:
    return {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low", "info": "Informational"}.get(severity, severity.title())


def render_html_report(report: dict) -> str:
    rows = "".join(
        f"<article class='finding {html.escape(finding['severity'])}'><p class='label'>{html.escape(severity_label(finding['severity']))} · {html.escape(finding['check'])}</p><h3>{html.escape(finding['title'])}</h3><p>{html.escape(finding['summary'])}</p><p><strong>Recommended action:</strong> {html.escape(finding['remediation'])}</p></article>"
        for finding in report["findings"]
    )
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><title>SiteSentry report for {html.escape(report['hostname'])}</title><style>body{{font-family:Arial,sans-serif;background:#f4f7f6;color:#142322;line-height:1.55;max-width:900px;margin:0 auto;padding:48px 24px}}header{{border-bottom:4px solid #0B8F83;padding-bottom:24px}}.grade{{font-size:68px;font-weight:700;color:#0B8F83;margin:8px 0}}.finding{{background:#fff;padding:22px 24px;margin:16px 0;border-left:6px solid #789}}.critical,.high{{border-color:#bd3d32}}.medium{{border-color:#c5811b}}.low{{border-color:#5485a4}}.info{{border-color:#0B8F83}}.label{{text-transform:uppercase;letter-spacing:.08em;font-size:12px;font-weight:bold}}</style></head><body><header><p>LOCAL-FIRST SECURITY INSPECTION</p><h1>SiteSentry report</h1><p class='grade'>{report['score']['grade']}</p><p><strong>{html.escape(report['target'])}</strong><br>Scanned at {html.escape(report['scanned_at'])}</p><p>{html.escape(report['privacy_note'])}</p></header><main><h2>Findings</h2>{rows}</main></body></html>"""


def render_pdf_report(report: dict) -> bytes:
    from io import BytesIO

    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("SiteSentry local security inspection", styles["Title"]),
        Paragraph(f"Target: {html.escape(report['target'])}", styles["Normal"]),
        Paragraph(f"Grade: <b>{report['score']['grade']}</b> · Score: {report['score']['score']}/100", styles["Heading2"]),
        Paragraph(f"Scanned: {html.escape(report['scanned_at'])}", styles["Normal"]),
        Spacer(1, 0.16 * inch),
        Paragraph(report["privacy_note"], styles["Italic"]),
        Spacer(1, 0.24 * inch),
    ]
    data = [["Severity", "Check", "Finding", "Recommended action"]]
    for finding in report["findings"]:
        data.append([
            severity_label(finding["severity"]),
            finding["check"],
            Paragraph(html.escape(finding["title"] + ". " + finding["summary"]), styles["BodyText"]),
            Paragraph(html.escape(finding["remediation"]), styles["BodyText"]),
        ])
    table = Table(data, colWidths=[0.7 * inch, 0.9 * inch, 2.6 * inch, 2.3 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B8F83")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BFD0CC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8F7")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)
    document.build(story)
    return buffer.getvalue()


if __name__ == "__main__":
    host = os.environ.get("SITESENTRY_HOST", "127.0.0.1")
    port = int(os.environ.get("SITESENTRY_PORT", "5123"))
    create_app().run(host=host, port=port, debug=False)
