"""
Input validation schemas.

All external input is validated HERE before reaching the service layer.
Returns (clean_data, errors) — never raises exceptions.
Pure functions, no DB access, no side effects.
"""

import re
from datetime import date
from typing import Any, Optional

from app.models.book import RATABLE_STATUSES, RATING_MAX, RATING_MIN, ReadingStatus

# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

def _require_str(value: Any, field: str, max_len: int = 500) -> Optional[str]:
    if value is None or (isinstance(value, str) and not value.strip()):
        return f"{field} is required and cannot be empty."
    if not isinstance(value, str):
        return f"{field} must be a string."
    if len(value.strip()) > max_len:
        return f"{field} must be {max_len} characters or fewer."
    return None


def _optional_str(value: Any, field: str, max_len: int = 2000) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        return f"{field} must be a string."
    if len(value) > max_len:
        return f"{field} must be {max_len} characters or fewer."
    return None


def _validate_email(value: Any) -> Optional[str]:
    if not value or not isinstance(value, str):
        return "email is required."
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(pattern, value.strip()):
        return "email must be a valid email address."
    return None


def _validate_password(value: Any) -> Optional[str]:
    if not value or not isinstance(value, str):
        return "password is required."
    if len(value) < 8:
        return "password must be at least 8 characters."
    if len(value) > 128:
        return "password must be 128 characters or fewer."
    return None


def _validate_isbn(isbn: Any) -> Optional[str]:
    if isbn is None:
        return None
    if not isinstance(isbn, str):
        return "isbn must be a string."
    cleaned = isbn.replace("-", "").replace(" ", "")
    if not cleaned.isdigit() or len(cleaned) != 13:
        return "isbn must be a 13-digit number (hyphens allowed)."
    return None


def _validate_page_count(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        return "page_count must be a positive integer."
    if value <= 0:
        return "page_count must be greater than zero."
    if value > 50000:
        return "page_count seems unreasonably large."
    return None


def _validate_status(value: Any) -> Optional[str]:
    if value is None:
        return "status is required."
    valid = [s.value for s in ReadingStatus]
    if value not in valid:
        return f"status must be one of: {', '.join(valid)}."
    return None


def _validate_rating(rating: Any, status_str: Any) -> Optional[str]:
    if rating is None:
        return None
    if not isinstance(rating, int) or isinstance(rating, bool):
        return "rating must be an integer."
    if rating < RATING_MIN or rating > RATING_MAX:
        return f"rating must be between {RATING_MIN} and {RATING_MAX}."
    ratable_values = {s.value for s in RATABLE_STATUSES}
    if status_str not in ratable_values:
        return (
            f"rating can only be set when status is one of: "
            f"{', '.join(sorted(ratable_values))}."
        )
    return None


def _validate_date(value: Any, field: str) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        return f"{field} must be an ISO date string (YYYY-MM-DD)."
    try:
        date.fromisoformat(value)
    except ValueError:
        return f"{field} must be a valid ISO date (YYYY-MM-DD)."
    return None


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

def validate_register(data: dict) -> tuple[dict, list[str]]:
    errors = []

    email_err = _validate_email(data.get("email"))
    if email_err:
        errors.append(email_err)

    password_err = _validate_password(data.get("password"))
    if password_err:
        errors.append(password_err)

    name_err = _optional_str(data.get("name"), "name", max_len=100)
    if name_err:
        errors.append(name_err)

    if errors:
        return {}, errors

    return {
        "email": data["email"].strip().lower(),
        "password": data["password"],
        "name": data.get("name", "").strip() or None,
    }, []


def validate_login(data: dict) -> tuple[dict, list[str]]:
    errors = []

    email_err = _validate_email(data.get("email"))
    if email_err:
        errors.append(email_err)

    if not data.get("password"):
        errors.append("password is required.")

    if errors:
        return {}, errors

    return {
        "email": data["email"].strip().lower(),
        "password": data["password"],
    }, []


# ---------------------------------------------------------------------------
# Book schemas
# ---------------------------------------------------------------------------

def validate_create_book(data: dict) -> tuple[dict, list[str]]:
    errors = []

    for err in [
        _require_str(data.get("title"), "title", max_len=300),
        _require_str(data.get("author"), "author", max_len=300),
        _validate_status(data.get("status")),
        _validate_isbn(data.get("isbn")),
        _validate_page_count(data.get("page_count")),
        _optional_str(data.get("notes"), "notes"),
        _validate_rating(data.get("rating"), data.get("status")),
        _validate_date(data.get("date_added"), "date_added"),
        _validate_date(data.get("date_finished"), "date_finished"),
        _optional_str(data.get("cover_url"), "cover_url", max_len=500),
    ]:
        if err:
            errors.append(err)

    if errors:
        return {}, errors

    isbn_raw = data.get("isbn")
    return {
        "title": data["title"].strip(),
        "author": data["author"].strip(),
        "status": data["status"],
        "isbn": isbn_raw.replace("-", "").replace(" ", "") if isbn_raw else None,
        "rating": data.get("rating"),
        "page_count": data.get("page_count"),
        "notes": data.get("notes"),
        "cover_url": data.get("cover_url"),
        "date_added": data.get("date_added"),
        "date_finished": data.get("date_finished"),
    }, []


def validate_update_book(data: dict) -> tuple[dict, list[str]]:
    errors = []
    clean: dict = {}

    field_validators = {
        "title": lambda v: _require_str(v, "title", max_len=300),
        "author": lambda v: _require_str(v, "author", max_len=300),
        "status": _validate_status,
        "isbn": _validate_isbn,
        "page_count": _validate_page_count,
        "notes": lambda v: _optional_str(v, "notes"),
        "cover_url": lambda v: _optional_str(v, "cover_url", max_len=500),
        "date_added": lambda v: _validate_date(v, "date_added"),
        "date_finished": lambda v: _validate_date(v, "date_finished"),
    }

    for field, validator in field_validators.items():
        if field in data:
            err = validator(data[field])
            if err:
                errors.append(err)
            else:
                val = data[field]
                if field == "title" or field == "author":
                    val = val.strip() if val else val
                if field == "isbn" and val:
                    val = val.replace("-", "").replace(" ", "")
                clean[field] = val

    if "rating" in data:
        effective_status = data.get("status")
        err = _validate_rating(data["rating"], effective_status)
        if err:
            errors.append(err)
        else:
            clean["rating"] = data["rating"]

    if errors:
        return {}, errors

    return clean, []
