"""
Open Library search proxy.

Why proxy through Flask instead of calling from the frontend?
- Keeps third-party API details server-side
- Lets us transform/filter the response
- Avoids CORS issues with the Open Library API
- Easy to add caching or rate limiting later

Endpoint: GET /api/search?q=dune
"""

import json
import logging
import urllib.request
import urllib.parse

from flask import Blueprint, jsonify, request
from app.utils.auth_decorator import require_auth

logger = logging.getLogger(__name__)
search_bp = Blueprint("search", __name__, url_prefix="/api/search")


def _fetch_open_library(query: str, limit: int = 8) -> list[dict]:
    """Call Open Library search API and return normalised results."""
    encoded = urllib.parse.quote(query)
    url = (
        f"https://openlibrary.org/search.json"
        f"?q={encoded}&limit={limit}&fields=title,author_name,isbn,number_of_pages_median,cover_i"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "BookLog/1.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read())

    results = []
    for doc in data.get("docs", []):
        isbn_list = doc.get("isbn", [])
        # Prefer ISBN-13 (length 13), fall back to first available
        isbn = next((i for i in isbn_list if len(i) == 13), isbn_list[0] if isbn_list else None)

        cover_i = doc.get("cover_i")
        cover_url = (
            f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg" if cover_i else None
        )

        results.append({
            "title": doc.get("title", ""),
            "author": ", ".join(doc.get("author_name", [])) or "",
            "isbn": isbn,
            "page_count": doc.get("number_of_pages_median"),
            "cover_url": cover_url,
        })

    return results


@search_bp.route("", methods=["GET"])
@require_auth
def search_books(current_user_id: int):
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400
    if len(query) > 200:
        return jsonify({"error": "Query is too long."}), 400

    try:
        results = _fetch_open_library(query)
        return jsonify({"results": results}), 200
    except Exception:
        logger.exception("Open Library search failed")
        return jsonify({"error": "Search is unavailable. Add the book manually."}), 503
