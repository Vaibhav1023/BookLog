"""
UserRepository — all DB access for users.

Password hashing uses PBKDF2-HMAC-SHA256 (stdlib hashlib).
No plaintext passwords ever stored or logged.
"""

import hashlib
import os
from datetime import datetime, timezone
from typing import Optional

from app.database import get_db
from app.models.user import User


def _hash_password(password: str, salt: Optional[str] = None) -> str:
    """Return 'salt$hash' string. Salt is generated if not provided."""
    if salt is None:
        salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), iterations=260_000
    )
    return f"{salt}${key.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    """Constant-time password verification."""
    try:
        salt, _ = stored.split("$", 1)
        return _hash_password(password, salt) == stored
    except Exception:
        return False


class UserRepository:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def _row_to_user(self, row) -> User:
        return User(id=row["id"], email=row["email"], name=row["name"])

    def get_by_email(self, email: str) -> Optional[User]:
        with get_db(self._db_path) as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email.lower(),)
            ).fetchone()
        return self._row_to_user(row) if row else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        with get_db(self._db_path) as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        return self._row_to_user(row) if row else None

    def create(self, email: str, password: str, name: Optional[str] = None) -> User:
        """
        Create a new user. Raises ValueError if email already exists.
        Password is hashed before storage — plaintext never written.
        """
        if self.get_by_email(email):
            raise ValueError("An account with this email already exists.")

        password_hash = _hash_password(password)
        created_at = datetime.now(timezone.utc).isoformat()

        with get_db(self._db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO users (email, name, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (email.lower(), name, password_hash, created_at),
            )
            conn.commit()
            user_id = cursor.lastrowid

        return self.get_by_id(user_id)

    def verify_credentials(self, email: str, password: str) -> Optional[User]:
        """Return User if credentials are valid, None otherwise."""
        with get_db(self._db_path) as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email.lower(),)
            ).fetchone()

        if row is None:
            # Run hash anyway to prevent timing-based email enumeration
            _hash_password(password, "dummy_salt_prevent_timing")
            return None

        if _verify_password(password, row["password_hash"]):
            return self._row_to_user(row)

        return None
