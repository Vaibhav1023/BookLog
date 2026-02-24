# claude.md — AI Agent Guidance for BookLog

Read this before making any change to the codebase.

---

## Architecture

```
HTTP Request
    │
    ▼
[routes/]       ← HTTP only: parse, call schema, call service, respond
    │
    ▼
[schemas/]      ← Validation only: field types, ranges, cross-field rules
    │
    ▼
[services/]     ← Business logic only: domain rules, orchestration
    │
    ▼
[repositories/] ← SQL only: queries, row mapping
    │
    ▼
[models/]       ← Data definitions: dataclasses, enums, constants
```

**Every layer communicates only with its direct neighbor.**

---

## Absolute Rules

### 1. All books queries must include user_id
```python
# WRONG — leaks data across users
conn.execute("SELECT * FROM books WHERE id = ?", (book_id,))

# CORRECT — always scope to user
conn.execute("SELECT * FROM books WHERE id = ? AND user_id = ?", (book_id, user_id))
```

### 2. Rating requires a ratable status
`RATABLE_STATUSES = {finished, abandoned}` — enforced in BOTH schema AND service.  
Do not remove either enforcement point.

### 3. No SQL outside repositories/
### 4. No business logic in routes/
### 5. No validation in services/
### 6. Passwords never logged or returned in API responses
### 7. JWT secret comes from config — never hardcoded

---

## Where to Add Things

| Feature | Layer |
|---|---|
| New API endpoint | `routes/` |
| New field validation | `schemas/schemas.py` |
| New domain rule | `services/book_service.py` |
| New DB query | `repositories/` |
| New model field | `models/` + schema in `database.py` |

---

## Tests Must Pass After Every Change

```bash
cd backend && python -m unittest discover tests/ -v
```

71 tests. A failing test = a broken invariant. Fix the code, not the test.

---

## What AI Must NOT Do

- Add SQL to service or route files
- Add business logic to route handlers  
- Remove user_id scoping from any repository query
- Remove the rating/status double enforcement
- Log or return password hashes
- Use string concatenation in SQL (use parameterised queries only)
- Add a third error response shape (only `{error}` and `{errors:[]}` exist)
- Merge layers "for simplicity"

---

## Known Weaknesses (do not hide these)

- No email verification on registration
- JWT secret resets on server restart (use env var JWT_SECRET in production)
- No refresh tokens — sessions expire after 8 hours
- No pagination on book list
- Open Library search depends on external availability
- SQLite doesn't support concurrent writes
