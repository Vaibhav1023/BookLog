# claude.md — AI Guidance for BookLog

This file guides AI agents working on this codebase. Read it before making any change.

---

## Architecture

```
Route → Schema → Service → Repository → Database
```

Each layer has exactly one responsibility and communicates only with its direct neighbour.

| Layer | Responsibility | Must NOT do |
|---|---|---|
| Route | Parse HTTP, return response | SQL, business logic |
| Schema | Validate input fields | DB access, side effects |
| Service | Enforce domain rules | SQL, HTTP |
| Repository | Execute SQL, map rows | Business logic |
| Model | Define data shapes | Anything |

---

## Non-Negotiable Rules

### 1. Every book query must be scoped to user_id
```python
# WRONG — leaks data across users
conn.execute("SELECT * FROM books WHERE id = ?", (book_id,))

# CORRECT
conn.execute("SELECT * FROM books WHERE id = ? AND user_id = ?", (book_id, user_id))
```

### 2. Rating is only valid on finished or abandoned books
Enforced in **both** `schemas/schemas.py` and `services/book_service.py`.
Never remove either enforcement point.

### 3. No SQL outside repositories/
### 4. No business logic in routes/
### 5. No validation in services/
### 6. Passwords never logged or returned in API responses
### 7. All SQL must use parameterised queries — no string concatenation

---

## Where to Add Things

| What you want to add | Where it goes |
|---|---|
| New API endpoint | `routes/` |
| New input validation rule | `schemas/schemas.py` |
| New business rule | `services/book_service.py` |
| New database query | `repositories/` |
| New model field | `models/` + update `database.py` schema |

---

## Before Submitting Any Change

```bash
cd backend && python -m unittest discover tests/ -v
```

All 71 tests must pass. A failing test means a broken invariant — fix the code, not the test.

---

## What AI Must Never Do

- Add SQL to service or route files
- Remove `user_id` scoping from any repository query
- Remove the rating/status enforcement from schema OR service
- Log or return password hashes
- Use string concatenation in SQL queries
- Add a third error response shape (only `{"error": "..."}` and `{"errors": [...]}` exist)
- Merge layers to simplify code

