# CLAUDE.md

FastAPI + PostgreSQL social media API (users, posts, votes, JWT). See README.md for usage.

## Commands

All confirmed by running them. Settings come from env vars or `.env` (copy `.env.example`).

```
pip install -r requirements-dev.txt
alembic upgrade head                 # create/upgrade tables
alembic check                        # models vs migrations drift
uvicorn app.main:app --reload        # run
pytest                               # needs <DATABASE_NAME>_test to exist; drops all its tables per test
docker compose -f docker-compose-dev.yml up --build
```

## Notes

- `app/database.py` builds the DB URL with `URL.create`; `alembic/env.py` and `test/conftest.py` reuse the same settings, so passwords with special characters work.
- Tests share one session with the app, which is closed after every request. Read ids off fixtures before making a request, not after.
- Passwords and keys must not be committed. Compose files read them from `.env`.
- `GET /posts/` and `GET /posts/{id}` return `{"Post": ..., "Votes": n}`.
