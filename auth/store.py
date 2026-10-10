"""
SQLite-backed user store.

Deliberately separate from Neo4j: the agent can execute arbitrary read-only
Cypher, so anything stored in the graph is readable by a prompt-injected
query. Credentials live here instead, where the Neo4j driver cannot reach them.
"""
import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional, List

import config
from auth.models import User, UserInDB

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username      TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL,
    disabled      INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL
)
"""


def _db_path() -> str:
    """Resolve the auth DB path relative to the project root"""
    path = config.AUTH_DB_PATH
    if not os.path.isabs(path):
        path = os.path.join(_PROJECT_ROOT, path)
    return path


def _connect() -> sqlite3.Connection:
    """Open a fresh connection (sqlite3 connections are not thread-safe to share)"""
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the users table if it does not exist yet"""
    with _connect() as conn:
        conn.execute(_SCHEMA)


def get_user(username: str) -> Optional[UserInDB]:
    """Look up a user by username, including the stored hash"""
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT username, password_hash, role, disabled FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if row is None:
        return None

    return UserInDB(
        username=row["username"],
        password_hash=row["password_hash"],
        role=row["role"],
        disabled=bool(row["disabled"]),
    )


class UserAlreadyExistsError(ValueError):
    """Raised when attempting to create a user that already exists"""


def create_user(username: str, password_hash: str, role: str) -> User:
    """
    Insert a new user.

    password_hash must be a bcrypt hash, not plaintext. Raises
    UserAlreadyExistsError (a ValueError) if the username is taken.
    """
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, role, disabled, created_at)"
                " VALUES (?, ?, ?, 0, ?)",
                (username, password_hash, role, created_at),
            )
    except sqlite3.IntegrityError as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise UserAlreadyExistsError(f"User '{username}' already exists") from exc
        raise

    return User(username=username, role=role, disabled=False)


def list_users() -> List[User]:
    """Return all users (without password hashes)"""
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT username, role, disabled FROM users ORDER BY username"
        ).fetchall()

    return [
        User(username=row["username"], role=row["role"], disabled=bool(row["disabled"]))
        for row in rows
    ]


def set_disabled(username: str, disabled: bool) -> bool:
    """Enable/disable an account. Returns False if the user does not exist."""
    init_db()
    with _connect() as conn:
        cursor = conn.execute(
            "UPDATE users SET disabled = ? WHERE username = ?",
            (1 if disabled else 0, username),
        )
    return cursor.rowcount > 0


def update_password(username: str, password_hash: str) -> bool:
    """Replace a user's password hash. Returns False if the user does not exist."""
    init_db()
    with _connect() as conn:
        cursor = conn.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (password_hash, username),
        )
    return cursor.rowcount > 0
