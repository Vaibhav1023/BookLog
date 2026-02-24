"""
Auth decorator for protecting Flask routes.

Usage:
    @books_bp.route("/", methods=["GET"])
    @require_auth
    def list_books(current_user_id: int):
        ...

The decorator injects current_user_id as the first argument.
Routes never parse tokens directly.
"""

import logging
from functools import wraps

from flask import jsonify, request

from app.utils.jwt_utils import decode_token

logger = logging.getLogger(__name__)


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization header missing or invalid."}), 401

        token = auth_header[len("Bearer "):]
        payload = decode_token(token)

        if payload is None:
            return jsonify({"error": "Token is invalid or expired."}), 401

        return f(payload["sub"], *args, **kwargs)

    return decorated
