"""Local-only SQLite credential storage and session-secret management."""

from __future__ import annotations

import os
import secrets
import sqlite3
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash


def default_database_path() -> Path:
    configured = os.environ.get("SITESENTRY_DB_PATH")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / ".sitesentry" / "sitesentry.db").resolve()


class LocalAuthStore:
    """Stores only a hashed local password, username, and a local session secret."""

    def __init__(self, database_path: Path | None = None) -> None:
        self.database_path = database_path or default_database_path()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.database_path.parent.chmod(0o700)
        except OSError:
            pass
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS credentials (id INTEGER PRIMARY KEY CHECK (id = 1), username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL)"
            )
            connection.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")

    def configured(self) -> bool:
        with self._connect() as connection:
            return connection.execute("SELECT 1 FROM credentials WHERE id = 1").fetchone() is not None

    def setup(self, username: str, password: str) -> bool:
        if self.configured():
            return False
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO credentials (id, username, password_hash) VALUES (1, ?, ?)",
                (username, generate_password_hash(password)),
            )
        try:
            self.database_path.chmod(0o600)
        except OSError:
            pass
        return True

    def authenticate(self, username: str, password: str) -> bool:
        with self._connect() as connection:
            row = connection.execute("SELECT username, password_hash FROM credentials WHERE id = 1").fetchone()
        return bool(row and row["username"] == username and check_password_hash(row["password_hash"], password))

    def session_secret(self) -> str:
        with self._connect() as connection:
            row = connection.execute("SELECT value FROM settings WHERE key = 'session_secret'").fetchone()
            if row:
                return row["value"]
            secret = secrets.token_urlsafe(48)
            connection.execute("INSERT INTO settings (key, value) VALUES ('session_secret', ?)", (secret,))
            return secret
