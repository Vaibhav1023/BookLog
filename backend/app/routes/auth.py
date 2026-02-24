"""
Auth routes — register, login, me.

Thin HTTP adapter: parse → validate → service → respond.
No business logic here.
"""

import logging
from flask import Blueprint, current_app, jsonify, request

from app.schemas import validate_register, validate_login
from app.services.auth_service import AuthError
from app.utils.auth_decorator import require_auth

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _get_auth_service():
    return current_app.extensions["auth_service"]

def _get_user_repo():
    return current_app.extensions["user_repository"]


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    clean, errors = validate_register(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        user, token = _get_auth_service().register(**clean)
        return jsonify({"token": token, "user": user.to_dict()}), 201
    except AuthError as e:
        return jsonify({"error": str(e)}), 409
    except Exception:
        logger.exception("Unexpected error during registration")
        return jsonify({"error": "An unexpected error occurred."}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    clean, errors = validate_login(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        user, token = _get_auth_service().login(**clean)
        return jsonify({"token": token, "user": user.to_dict()}), 200
    except AuthError as e:
        return jsonify({"error": str(e)}), 401
    except Exception:
        logger.exception("Unexpected error during login")
        return jsonify({"error": "An unexpected error occurred."}), 500


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me(current_user_id: int):
    user = _get_user_repo().get_by_id(current_user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"user": user.to_dict()}), 200
