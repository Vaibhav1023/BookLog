"""
BookRepository — all SQL for books.

CRITICAL: Every query filters by user_id.
A user can never read or modify another user's books.
This is enforced at the SQL level, not just application logic.
"""

from datetime import date
from typing import Optional

from app.database import get_db
from app.models.book import Book, ReadingStatus


class BookRepository:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def _row_to_book(self, row) -> Book:
        return Book(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            author=row["author"],
            isbn=row["isbn"],
            status=ReadingStatus(row["status"]),
            rating=row["rating"],
            page_count=row["page_count"],
            notes=row["notes"],
            cover_url=row["cover_url"],
            date_added=(
                date.fromisoformat(row["date_added"]) if row["date_added"] else None
            ),
            date_finished=(
                date.fromisoformat(row["date_finished"])
                if row["date_finished"]
                else None
            ),
        )

    def get_all(
        self,
        user_id: int,
        status: Optional[str] = None,
        author: Optional[str] = None,
    ) -> list[Book]:
        query = "SELECT * FROM books WHERE user_id = ?"
        params: list = [user_id]

        if status:
            query += " AND status = ?"
            params.append(status)
        if author:
            query += " AND LOWER(author) LIKE ?"
            params.append(f"%{author.lower()}%")

        query += " ORDER BY date_added DESC"

        with get_db(self._db_path) as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_book(r) for r in rows]

    def get_by_id(self, book_id: int, user_id: int) -> Optional[Book]:
        """Fetch by id AND user_id — prevents cross-user access."""
        with get_db(self._db_path) as conn:
            row = conn.execute(
                "SELECT * FROM books WHERE id = ? AND user_id = ?",
                (book_id, user_id),
            ).fetchone()
        return self._row_to_book(row) if row else None

    def get_by_isbn(self, isbn: str, user_id: int) -> Optional[Book]:
        with get_db(self._db_path) as conn:
            row = conn.execute(
                "SELECT * FROM books WHERE isbn = ? AND user_id = ?",
                (isbn, user_id),
            ).fetchone()
        return self._row_to_book(row) if row else None

    def create(self, book: Book) -> Book:
        if book.isbn and self.get_by_isbn(book.isbn, book.user_id):
            raise ValueError(f"ISBN {book.isbn} is already in your library.")

        sql = """
            INSERT INTO books
                (user_id, title, author, isbn, status, rating, page_count,
                 notes, cover_url, date_added, date_finished)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            book.user_id,
            book.title,
            book.author,
            book.isbn,
            book.status.value,
            book.rating,
            book.page_count,
            book.notes,
            book.cover_url,
            book.date_added.isoformat() if book.date_added else None,
            book.date_finished.isoformat() if book.date_finished else None,
        )

        with get_db(self._db_path) as conn:
            cursor = conn.execute(sql, params)
            conn.commit()
            new_id = cursor.lastrowid

        return self.get_by_id(new_id, book.user_id)

    def update(self, book_id: int, user_id: int, fields: dict) -> Optional[Book]:
        allowed = {
            "title", "author", "isbn", "status", "rating",
            "page_count", "notes", "cover_url", "date_added", "date_finished",
        }
        safe_fields = {k: v for k, v in fields.items() if k in allowed}

        if not safe_fields:
            return self.get_by_id(book_id, user_id)

        if "isbn" in safe_fields and safe_fields["isbn"] is not None:
            existing = self.get_by_isbn(safe_fields["isbn"], user_id)
            if existing and existing.id != book_id:
                raise ValueError(f"ISBN {safe_fields['isbn']} is already in your library.")

        if "status" in safe_fields:
            v = safe_fields["status"]
            safe_fields["status"] = v.value if isinstance(v, ReadingStatus) else v

        set_clause = ", ".join(f"{k} = ?" for k in safe_fields)
        params = list(safe_fields.values()) + [book_id, user_id]
        sql = f"UPDATE books SET {set_clause} WHERE id = ? AND user_id = ?"

        with get_db(self._db_path) as conn:
            conn.execute(sql, params)
            conn.commit()

        return self.get_by_id(book_id, user_id)

    def delete(self, book_id: int, user_id: int) -> bool:
        with get_db(self._db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM books WHERE id = ? AND user_id = ?",
                (book_id, user_id),
            )
            conn.commit()
        return cursor.rowcount > 0

    def stats(self, user_id: int) -> dict:
        sql = """
            SELECT
                COUNT(*)                                            AS total,
                COUNT(CASE WHEN status='finished'     THEN 1 END)  AS finished,
                COUNT(CASE WHEN status='reading'      THEN 1 END)  AS reading,
                COUNT(CASE WHEN status='want_to_read' THEN 1 END)  AS want_to_read,
                COUNT(CASE WHEN status='abandoned'    THEN 1 END)  AS abandoned,
                ROUND(AVG(CASE WHEN rating IS NOT NULL THEN rating END), 2) AS avg_rating,
                SUM(COALESCE(page_count, 0))                       AS total_pages
            FROM books
            WHERE user_id = ?
        """
        with get_db(self._db_path) as conn:
            row = conn.execute(sql, (user_id,)).fetchone()
        return dict(row)
