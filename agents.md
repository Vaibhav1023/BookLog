# agents.md — Autonomous Agent Constraints

## Before Starting
1. Read `claude.md`
2. Run `python -m unittest discover backend/tests/ -v` — all 71 must pass
3. Identify which layer your change belongs in

## Permitted
- Add routes (must call schema → service, never SQL directly)
- Add validations (schema layer only, with tests)
- Add domain rules (service layer only, with tests)
- Add SQL queries (repository layer only, always parameterised, always include user_id)
- Add tests (always permitted)

## Prohibited
- SQL outside `repositories/`
- Business logic in `routes/`
- Any query missing `user_id` scoping
- Removing rating/status enforcement from schema OR service
- Logging `password_hash` or `password`
- Deleting tests to make suite pass
- Hardcoding secrets

## Before Submitting
```bash
# All tests pass
cd backend && python -m unittest discover tests/ -v

# No raw SQL in wrong layers
grep -r "sqlite3.connect" backend/app/services/ && echo "VIOLATION"
grep -r "sqlite3.connect" backend/app/routes/ && echo "VIOLATION"
```

## Escalate to Human If
- Change requires relaxing the rating/status invariant
- Change requires merging layers
- Change requires modifying existing rows in the DB schema
- Authentication logic needs to change
