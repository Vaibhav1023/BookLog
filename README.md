# BookLog

A personal reading log with JWT authentication and Open Library integration.
Built with Flask, React, and SQLite.

---

## Quick Start

### Backend
```bash
cd backend
python run.py
# Runs on http://localhost:5000
```

### Frontend
```bash
cd frontend
npm install && npm start
# Runs on http://localhost:3000
```

### Tests
```bash
cd backend
python -m unittest discover tests/ -v
# 71 tests, ~6s
```

---

## Project Structure

```
booklog/
├── backend/
│   ├── app/
│   │   ├── models/           # Book, User — pure data, no DB
│   │   │   ├── book.py
│   │   │   └── user.py
│   │   ├── schemas/          # Input validation — no DB, no HTTP
│   │   │   └── schemas.py
│   │   ├── services/         # Business rules — no SQL, no HTTP
│   │   │   ├── auth_service.py
│   │   │   └── book_service.py
│   │   ├── repositories/     # SQL — only layer touching the DB
│   │   │   ├── book_repository.py
│   │   │   └── user_repository.py
│   │   ├── routes/           # HTTP adapter — parse, validate, delegate, respond
│   │   │   ├── auth.py
│   │   │   ├── books.py
│   │   │   └── search.py
│   │   ├── utils/
│   │   │   ├── jwt_utils.py       # Stdlib JWT (HMAC-SHA256)
│   │   │   └── auth_decorator.py  # @require_auth
│   │   ├── database.py       # Schema, connection factory
│   │   └── __init__.py       # App factory, CORS, wiring
│   └── tests/
│       ├── test_auth.py      # Auth route integration tests
│       ├── test_schemas.py   # Validation unit tests
│       ├── test_services.py  # Business logic + data isolation tests
│       └── test_routes.py    # Book route integration tests
├── frontend/
│   └── src/
│       ├── services/api.js   # All HTTP calls — components never use fetch()
│       ├── hooks/
│       │   ├── useAuth.js    # Auth state + JWT storage
│       │   └── useBooks.js   # Book CRUD state
│       ├── pages/
│       │   ├── AuthPage.js   # Login / Register
│       │   └── LibraryPage.js
│       └── components/
│           └── BookFormModal.js  # Add/Edit with Open Library search
├── claude.md    # AI agent rules
├── agents.md    # Autonomous agent constraints
└── README.md
```

---

## Architecture: Four-Layer Backend

```
Route → Schema → Service → Repository
```

| Layer | Responsibility | Cannot do |
|---|---|---|
| Route | Parse HTTP, serialize response | SQL, domain rules |
| Schema | Validate field types & ranges | DB lookups, side effects |
| Service | Enforce domain rules | SQL, HTTP |
| Repository | Execute SQL, map rows | Business logic |

---

## Authentication

JWT (HMAC-SHA256) implemented with Python stdlib only — no PyJWT required.

**Flow:**
1. `POST /api/auth/register` → returns `{ token, user }`
2. `POST /api/auth/login` → returns `{ token, user }`
3. All `/api/books` and `/api/search` requests require `Authorization: Bearer <token>`

**Security decisions:**
- Passwords hashed with PBKDF2-HMAC-SHA256, 260,000 iterations
- Constant-time comparison to prevent timing attacks on login
- Dummy hash run on unknown email to prevent email enumeration
- JWT uses `exp` claim — tokens expire after 8 hours
- Token secret loaded from `JWT_SECRET` env var (falls back to random on startup)

**Data isolation:** Every SQL query in `BookRepository` includes `AND user_id = ?`. Users cannot read or modify each other's data at the database level.

---

## Open Library Integration

`GET /api/search?q=<query>` — proxied through Flask.

**Why proxy instead of calling from the frontend?**
- Keeps third-party API details server-side
- Avoids browser CORS issues with `openlibrary.org`
- Single place to add caching or rate limiting later

**What it returns per result:**
- title, author, ISBN-13 (preferred), page count, cover image URL

The frontend debounces search input (500ms) and shows results in a dropdown. Clicking a result auto-fills the form. If the search fails (network error, API unavailable), the user sees a message and fills in manually — graceful degradation.

---

## Domain Rules

| Rule | Enforced in |
|---|---|
| Rating only on finished/abandoned books | Schema + Service (double) |
| No duplicate ISBN per user | Repository + DB UNIQUE constraint |
| Page count must be positive | Schema |
| date_finished auto-set when status → finished | Service |
| Rating cleared when status → non-ratable | Service |
| All book queries scoped to user_id | Repository (every query) |

---

## API Reference

### Auth
| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/api/auth/register` | `{email, password, name?}` | `{token, user}` 201 |
| POST | `/api/auth/login` | `{email, password}` | `{token, user}` 200 |
| GET | `/api/auth/me` | — | `{user}` 200 |

### Books (all require Bearer token)
| Method | Path | Description |
|---|---|---|
| GET | `/api/books` | List books (`?status=`, `?author=`) |
| GET | `/api/books/stats` | Aggregate stats |
| GET | `/api/books/:id` | Get one book |
| POST | `/api/books` | Create book |
| PATCH | `/api/books/:id` | Partial update |
| DELETE | `/api/books/:id` | Delete book |

### Search (requires Bearer token)
| Method | Path | Description |
|---|---|---|
| GET | `/api/search?q=dune` | Search Open Library |

---

## Technical Decisions

### SQLite + raw sqlite3 (no ORM)
SQLite is appropriate for a personal app. Raw sqlite3 (stdlib) makes every query explicit and auditable — no hidden N+1 queries, no lazy loading surprises. The repository pattern means swapping to Postgres requires changes only in `database.py` and the repository files.

### Stdlib JWT (no PyJWT)
PyJWT wasn't available. The implementation is ~60 lines covering exactly what's needed: HS256 signing, expiry checking, constant-time comparison. It's transparent and reviewable.

### Stdlib validation (no Pydantic)
Pydantic wasn't available. The custom validators are pure functions, easy to test, and make every rule explicit. No magic, no metaclasses.

### CORS without flask-cors
Two `after_request` lines handle CORS — no dependency needed. The allowed origin is configurable via `FRONTEND_ORIGIN` env var.

### App factory pattern
`create_app(config)` means tests get isolated instances with temp databases. No global state.

---

## Known Weaknesses

These are documented honestly, not hidden:

1. **No email verification** — anyone can register with any email address.
2. **JWT secret resets on restart** — all sessions invalidated unless `JWT_SECRET` env var is set.
3. **No refresh tokens** — users must re-login after 8 hours.
4. **No pagination** — `GET /api/books` returns all records. Degrades at ~10,000 books.
5. **Open Library dependency** — search fails gracefully but requires internet access.
6. **SQLite single-writer** — unsuitable for concurrent multi-user deployments.
7. **No rate limiting** — brute-force on `/api/auth/login` is possible.

---

## Test Coverage (71 tests)

| File | Tests | Covers |
|---|---|---|
| `test_schemas.py` | 21 | Field validation, rating/status rule, email format, password length |
| `test_services.py` | 26 | Auth flow, all domain rules, cross-user isolation, stats |
| `test_auth.py` | 13 | Register, login, token validation, case-insensitive email |
| `test_routes.py` | 17 | HTTP codes, auth protection, CRUD, data isolation |

---

## Extension Approach

### Add a `genre` field
1. `models/book.py` — add field to dataclass and `to_dict()`
2. `schemas/schemas.py` — add optional string validation
3. `database.py` — add column in `_SCHEMA`
4. `repositories/book_repository.py` — add to `create()`, `update()`, `_row_to_book()`
5. `frontend/src/components/BookFormModal.js` — add input
6. Add tests

### Add a new reading status
1. `models/book.py` — add to `ReadingStatus` enum
2. Decide if ratable — update `RATABLE_STATUSES` if so
3. `frontend/src/pages/LibraryPage.js` — add to `STATUSES` array
4. Add tests for the new status transitions

### Add rate limiting to login
Add a decorator in `utils/` that counts failed attempts per IP. Apply to the login route only. No service or repository changes needed.

---

## AI Usage

Built with Claude (claude.ai).

**What AI generated:** layer structure, all SQL queries, test cases, React components, JWT implementation.

**How output was verified:**
- Tests run immediately after each file — failures caught and fixed inline
- All SQL reviewed for parameterisation (no string concatenation)
- The rating/status invariant traced through schema, service, and tests
- User isolation tested explicitly: `test_user_cannot_access_other_users_book`, `test_stats_isolated_per_user`, `test_user2_cannot_see_user1_books`
- Password hash verified never appears in API responses or logs

**`claude.md` and `agents.md`** constrain future AI use — any agent must respect layer boundaries and user isolation rules before making changes.
