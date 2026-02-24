"""
Book domain model.

Pure data — no database, no HTTP, no validation logic.
This is the canonical definition of what a Book IS in this system.
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class ReadingStatus(str, Enum):
    WANT_TO_READ = "want_to_read"
    READING = "reading"
    FINISHED = "finished"
    ABANDONED = "abandoned"


# Only these statuses allow a rating.
RATABLE_STATUSES: frozenset = frozenset(
    [ReadingStatus.FINISHED, ReadingStatus.ABANDONED]
)

RATING_MIN = 1
RATING_MAX = 5


@dataclass
class Book:
    title: str
    author: str
    status: ReadingStatus
    user_id: int
    id: Optional[int] = None
    isbn: Optional[str] = None
    rating: Optional[int] = None
    page_count: Optional[int] = None
    notes: Optional[str] = None
    cover_url: Optional[str] = None
    date_added: Optional[date] = None
    date_finished: Optional[date] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "status": self.status.value,
            "rating": self.rating,
            "page_count": self.page_count,
            "notes": self.notes,
            "cover_url": self.cover_url,
            "date_added": self.date_added.isoformat() if self.date_added else None,
            "date_finished": (
                self.date_finished.isoformat() if self.date_finished else None
            ),
        }
