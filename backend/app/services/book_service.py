"""
BookService — domain rules for the reading log.

Receives clean validated data. Enforces business invariants.
All queries are scoped to user_id.
"""

from datetime import date
from typing import Optional

from app.models.book import RATABLE_STATUSES, Book, ReadingStatus
from app.repositories.book_repository import BookRepository


class BookNotFoundError(Exception):
    pass


class BookRuleViolation(Exception):
    pass


class BookService:
    def __init__(self, repository: BookRepository):
        self._repo = repository

    def list_books(self, user_id: int, status: Optional[str] = None, author: Optional[str] = None) -> list[Book]:
        return self._repo.get_all(user_id, status=status, author=author)

    def get_book(self, book_id: int, user_id: int) -> Book:
        book = self._repo.get_by_id(book_id, user_id)
        if book is None:
            raise BookNotFoundError(f"Book {book_id} not found.")
        return book

    def get_stats(self, user_id: int) -> dict:
        return self._repo.stats(user_id)

    def add_book(self, user_id: int, data: dict) -> Book:
        status = ReadingStatus(data["status"])

        if data.get("rating") is not None and status not in RATABLE_STATUSES:
            raise BookRuleViolation("Rating can only be set when status is finished or abandoned.")

        date_added = (
            date.fromisoformat(data["date_added"]) if data.get("date_added") else date.today()
        )

        date_finished = None
        if data.get("date_finished"):
            date_finished = date.fromisoformat(data["date_finished"])
        elif status == ReadingStatus.FINISHED:
            date_finished = date.today()

        book = Book(
            user_id=user_id,
            title=data["title"],
            author=data["author"],
            isbn=data.get("isbn"),
            status=status,
            rating=data.get("rating"),
            page_count=data.get("page_count"),
            notes=data.get("notes"),
            cover_url=data.get("cover_url"),
            date_added=date_added,
            date_finished=date_finished,
        )
        return self._repo.create(book)

    def update_book(self, book_id: int, user_id: int, data: dict) -> Book:
        existing = self._repo.get_by_id(book_id, user_id)
        if existing is None:
            raise BookNotFoundError(f"Book {book_id} not found.")

        new_status_str = data.get("status")
        effective_status = ReadingStatus(new_status_str) if new_status_str else existing.status

        # Clear rating if moving to non-ratable status
        if new_status_str and effective_status not in RATABLE_STATUSES:
            if "rating" not in data:
                data = {**data, "rating": None}

        if data.get("rating") is not None and effective_status not in RATABLE_STATUSES:
            raise BookRuleViolation("Rating can only be set when status is finished or abandoned.")

        # Auto-set date_finished when marking finished
        if (
            effective_status == ReadingStatus.FINISHED
            and existing.status != ReadingStatus.FINISHED
            and "date_finished" not in data
        ):
            data = {**data, "date_finished": date.today().isoformat()}

        return self._repo.update(book_id, user_id, data)

    def delete_book(self, book_id: int, user_id: int) -> None:
        if not self._repo.delete(book_id, user_id):
            raise BookNotFoundError(f"Book {book_id} not found.")
