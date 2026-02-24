"""
User domain model.

Passwords are NEVER stored here in plain text.
The repository stores only the hashed value.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    email: str
    id: Optional[int] = None
    name: Optional[str] = None

    def to_dict(self) -> dict:
        return {"id": self.id, "email": self.email, "name": self.name}
