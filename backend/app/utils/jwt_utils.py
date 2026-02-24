"""
Minimal JWT implementation using Python stdlib only.

Uses HMAC-SHA256 signing. No third-party library required.

Why not PyJWT?
--------------
Not available in this environment. This implementation covers exactly
what we need: sign a payload, verify a token, reject expired tokens.
It is NOT a general-purpose JWT library — it handles only HS256.
"""

import base64
import hashlib
import hmac
import json
import time
from typing import Optional

# Loaded from app config at startup — never hardcoded.
_SECRET: Optional[str] = None
TOKEN_TTL_SECONDS = 60 * 60 * 8  # 8 hours


def init_jwt(secret: str) -> None:
    """Call once during app startup with the secret key."""
    global _SECRET
    _SECRET = secret


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64_decode(s: str) -> bytes:
    # Re-add padding
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def create_token(user_id: int, email: str) -> str:
    """Create a signed JWT with user_id and email claims."""
    if not _SECRET:
        raise RuntimeError("JWT secret not initialised.")

    header = _b64_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64_encode(
        json.dumps(
            {
                "sub": user_id,
                "email": email,
                "iat": int(time.time()),
                "exp": int(time.time()) + TOKEN_TTL_SECONDS,
            }
        ).encode()
    )
    signing_input = f"{header}.{payload}"
    sig = _b64_encode(
        hmac.new(
            _SECRET.encode(), signing_input.encode(), hashlib.sha256
        ).digest()
    )
    return f"{signing_input}.{sig}"


def decode_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT.

    Returns the payload dict or None if invalid/expired.
    Never raises — callers check for None.
    """
    if not _SECRET:
        return None
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}"

        expected_sig = _b64_encode(
            hmac.new(
                _SECRET.encode(), signing_input.encode(), hashlib.sha256
            ).digest()
        )

        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(expected_sig, sig_b64):
            return None

        payload = json.loads(_b64_decode(payload_b64))

        if payload.get("exp", 0) < int(time.time()):
            return None  # Expired

        return payload
    except Exception:
        return None
