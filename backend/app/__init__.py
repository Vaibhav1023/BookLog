"""
Application factory.

Wires together all layers. CORS handled here without external library.
"""

import logging
import os
import secrets
from pathlib import Path

from flask import Flask, jsonify

from app.database import init_db
from app.repositories.book_repository import BookRepository
from app.repositories.user_repository import UserRepository
from app.routes.auth import auth_bp
from app.routes.books import books_bp
from app.routes.search import search_bp
from app.services.auth_service import AuthService
from app.services.book_service import BookService
from app.utils.jwt_utils import init_jwt


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)

    # ── Config ──────────────────────────────────────────────────────
    app.config["DB_PATH"] = str(Path(__file__).parent.parent / "booklog.db")
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", secrets.token_hex(32))
    app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.config["FRONTEND_ORIGIN"] = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    if config:
        app.config.update(config)

    # ── Logging ─────────────────────────────────────────────────────
    logging.basicConfig(
        level=logging.DEBUG if app.config["DEBUG"] else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # ── JWT ─────────────────────────────────────────────────────────
    init_jwt(app.config["JWT_SECRET"])

    # ── Database ────────────────────────────────────────────────────
    init_db(app.config["DB_PATH"])

    # ── Dependency wiring ───────────────────────────────────────────
    user_repo = UserRepository(db_path=app.config["DB_PATH"])
    book_repo = BookRepository(db_path=app.config["DB_PATH"])

    app.extensions["user_repository"] = user_repo
    app.extensions["auth_service"] = AuthService(repository=user_repo)
    app.extensions["book_service"] = BookService(repository=book_repo)

    # ── Blueprints ──────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(search_bp)

    # ── CORS ────────────────────────────────────────────────────────
    # Manual CORS — no flask-cors dependency needed.
    @app.after_request
    def add_cors_headers(response):
        origin = app.config["FRONTEND_ORIGIN"]
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
        return response

    @app.route("/api/<path:path>", methods=["OPTIONS"])
    def handle_options(path):
        return "", 204

    # ── Health ──────────────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # ── Error handlers ──────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        logging.getLogger(__name__).exception("Unhandled 500")
        return jsonify({"error": "Internal server error."}), 500

    return app
