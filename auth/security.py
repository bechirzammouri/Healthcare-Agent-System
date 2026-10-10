"""
Password hashing and JWT issuance/verification
"""
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

import config
from auth.models import TokenData

# bcrypt silently ignores anything past 72 bytes, which would make two different
# long passwords interchangeable. Reject them instead.
BCRYPT_MAX_BYTES = 72


class AuthConfigError(RuntimeError):
    """Raised when the JWT signing secret is missing or unusable"""


def _signing_key() -> str:
    """Return the JWT secret, failing loudly if it was never configured"""
    if not config.JWT_SECRET_KEY:
        raise AuthConfigError(
            "JWT_SECRET_KEY is not set. Add it to .env "
            '(generate with: python -c "import secrets; print(secrets.token_hex(32))")'
        )
    return config.JWT_SECRET_KEY


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt (includes a per-password salt)"""
    encoded = password.encode("utf-8")
    if len(encoded) > BCRYPT_MAX_BYTES:
        raise ValueError(
            f"Password is longer than bcrypt's {BCRYPT_MAX_BYTES}-byte limit."
        )
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash"""
    encoded = password.encode("utf-8")
    if len(encoded) > BCRYPT_MAX_BYTES:
        return False
    try:
        return bcrypt.checkpw(encoded, password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        # Malformed/corrupt hash in storage - treat as a failed login
        return False


def create_access_token(
    username: str, role: str, expires_minutes: Optional[int] = None
) -> tuple[str, int]:
    """
    Build a signed JWT for the given user.

    Returns (token, expires_in_seconds). The 'role' claim is what downstream
    authorization checks read, so adding new roles needs no token changes.
    """
    minutes = (
        expires_minutes
        if expires_minutes is not None
        else config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(minutes=minutes)

    payload = {
        "sub": username,
        "role": role,
        "iat": issued_at,
        "exp": expires_at,
    }
    token = jwt.encode(payload, _signing_key(), algorithm=config.JWT_ALGORITHM)
    return token, minutes * 60


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Verify a JWT's signature and expiry.

    Returns the decoded claims, or None if the token is invalid, expired,
    tampered with, or missing required claims.
    """
    try:
        payload = jwt.decode(
            token, _signing_key(), algorithms=[config.JWT_ALGORITHM]
        )
    except jwt.PyJWTError:
        return None

    username = payload.get("sub")
    role = payload.get("role")
    if not username or not role:
        return None

    return TokenData(username=username, role=role)
