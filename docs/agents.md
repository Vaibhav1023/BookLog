# agents.md — Autonomous Agent Constraints for BookLog

This file defines what an AI agent is and is not allowed to do when working autonomously on this codebase.

---

## Before Starting Any Task

1. Read `claude.md` — understand the architecture and rules
2. Run the full test suite — all 71 tests must pass before you touch anything
3. Identify which layer your change belongs in

```bash
cd backend && python -m unittest discover tests/ -v
```

---

## Permitted Actions

| Action | Condition |
|---|---|
| Add a new route | Must call schema → service, never SQL directly |
| Add a new validation rule | Schema layer only, must include tests |
| Add a new business rule | Service layer only, must include tests |
| Add a new SQL query | Repository layer only, always parameterised, always includes `user_id` |
| Add or modify tests | Always permitted |
| Update README or documentation | Always permitted |

---

## Prohibited Actions

- Writing SQL in `routes/` or `services/`
- Writing business logic in `routes/` or `repositories/`
- Any database query missing `user_id` scoping
- Removing the rating/status rule from schema OR service
- Logging `password`, `password_hash`, or raw tokens
- Deleting or weakening tests to make the suite pass
- Hardcoding secrets or credentials
- Merging layers to reduce file count

---

## Verification Checklist (run before finishing any task)

```bash
# 1. All tests pass
cd backend && python -m unittest discover tests/ -v

# 2. No SQL in wrong layers
grep -r "sqlite3" backend/app/services/ && echo "VIOLATION — SQL in services"
grep -r "sqlite3" backend/app/routes/ && echo "VIOLATION — SQL in routes"

# 3. No missing user_id in book queries
grep -n "FROM books" backend/app/repositories/book_repository.py
# Every SELECT, UPDATE, DELETE on books must include AND user_id = ?
```

---

## Escalate to a Human When

- A change requires relaxing the rating/status invariant
- A change requires merging two layers
- A change requires modifying existing rows in the database schema
- Authentication or token logic needs to change
- A test needs to be deleted rather than fixed
