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
