"""
Book routes — protected API endpoints.

Every route requires a valid JWT via @require_auth.
The decorator injects current_user_id as the first argument.
"""

import logging
from flask import Blueprint, current_app, jsonify, request

from app.schemas import validate_create_book, validate_update_book
from app.services.book_service import BookNotFoundError, BookRuleViolation
from app.utils.auth_decorator import require_auth

logger = logging.getLogger(__name__)
books_bp = Blueprint("books", __name__, url_prefix="/api/books")


def _get_service():
    return current_app.extensions["book_service"]


@books_bp.route("", methods=["GET"])
@require_auth
def list_books(current_user_id: int):
    status = request.args.get("status")
    author = request.args.get("author")
    books = _get_service().list_books(current_user_id, status=status, author=author)
    return jsonify([b.to_dict() for b in books]), 200


@books_bp.route("/stats", methods=["GET"])
@require_auth
def get_stats(current_user_id: int):
    return jsonify(_get_service().get_stats(current_user_id)), 200


@books_bp.route("/<int:book_id>", methods=["GET"])
@require_auth
def get_book(current_user_id: int, book_id: int):
    try:
        return jsonify(_get_service().get_book(book_id, current_user_id).to_dict()), 200
    except BookNotFoundError as e:
        return jsonify({"error": str(e)}), 404


@books_bp.route("", methods=["POST"])
@require_auth
def create_book(current_user_id: int):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    clean, errors = validate_create_book(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        book = _get_service().add_book(current_user_id, clean)
        return jsonify(book.to_dict()), 201
    except BookRuleViolation as e:
        return jsonify({"error": str(e)}), 422
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception:
        logger.exception("Unexpected error creating book")
        return jsonify({"error": "An unexpected error occurred."}), 500


@books_bp.route("/<int:book_id>", methods=["PATCH"])
@require_auth
def update_book(current_user_id: int, book_id: int):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    clean, errors = validate_update_book(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        book = _get_service().update_book(book_id, current_user_id, clean)
        return jsonify(book.to_dict()), 200
    except BookNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except BookRuleViolation as e:
        return jsonify({"error": str(e)}), 422
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception:
        logger.exception("Unexpected error updating book")
        return jsonify({"error": "An unexpected error occurred."}), 500


@books_bp.route("/<int:book_id>", methods=["DELETE"])
@require_auth
def delete_book(current_user_id: int, book_id: int):
    try:
        _get_service().delete_book(book_id, current_user_id)
        return "", 204
    except BookNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        logger.exception("Unexpected error deleting book")
        return jsonify({"error": "An unexpected error occurred."}), 500
