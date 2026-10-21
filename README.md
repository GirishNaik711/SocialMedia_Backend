# SocialMedia_Backend

REST API for a small social network: users, posts and votes. FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT login.

## Requirements

- Python 3.11 (what the Dockerfile and CI use; also runs on 3.13)
- PostgreSQL (the compose files and CI use 17)
- Docker, optional

## Install

```
python -m venv venv
venv\Scripts\activate        # Linux/macOS: source venv/bin/activate
pip install -r requirements-dev.txt
```

`requirements.txt` has the runtime dependencies only; `requirements-dev.txt` adds pytest and httpx.

## Config

Copy `.env.example` to `.env` and fill it in. The app reads these from the environment or from `.env`:

| Variable | Purpose |
|---|---|
| `DATABASE_HOSTNAME`, `DATABASE_PORT` | Postgres host and port |
| `DATABASE_NAME`, `DATABASE_USERNAME`, `DATABASE_PASSWORD` | Postgres database and credentials |
| `SECRET_KEY` | JWT signing key. Generate one with `openssl rand -hex 32` |
| `ALGORITHM` | JWT algorithm, `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime |

## Run

Create the tables, then start the server:

```
alembic upgrade head
uvicorn app.main:app --reload
```

The API is on http://127.0.0.1:8000 and the interactive docs on `/docs`.

With Docker, Postgres comes up with it and the migrations run on start. Set the variables above in `.env` first (`DATABASE_HOSTNAME` and `DATABASE_PORT` are overridden to the compose Postgres):

```
docker compose -f docker-compose-dev.yml up --build
```

## Endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/users/` | no | `{"email", "password"}`. 409 if the email exists |
| GET | `/users/{id}` | no | |
| POST | `/login` | no | Form fields `username` (the email) and `password`. Returns a bearer token |
| GET | `/posts/` | yes | Query: `limit` (1-100, default 10), `skip`, `search` (title). Each item has `Post` and `Votes` |
| POST | `/posts/` | yes | `{"title", "content", "published"}` |
| GET | `/posts/{id}` | yes | |
| PUT | `/posts/{id}` | yes | Owner only |
| DELETE | `/posts/{id}` | yes | Owner only |
| POST | `/vote/` | yes | `{"post_id", "dir"}`. `dir: 1` adds a vote, `0` removes it |

## Tests

The tests run against `<DATABASE_NAME>_test` on the same server and drop and recreate every table in it before each test. Create that database once:

```
createdb fastapi_test
```

or, with Postgres in Docker:

```
docker exec <container> psql -U postgres -c "CREATE DATABASE fastapi_test"
```

Then:

```
pytest
```

## Deployment

GitHub Actions (`.github/workflows/main.yml`) runs the tests on every push and pull request. Pushes to `main` then deploy over SSH: `git pull` and `systemctl restart app` in `~/app/src` on the server. It needs these repository secrets: the eight config variables above (`DATABASE_HOSTNAME` should be `localhost` for the CI Postgres service) plus `PROD_HOST`, `PROD_USERNAME`, `PROD_PASSWORD`.

Other files:

- `gunicorn.service`: systemd unit for the server (gunicorn with uvicorn workers).
- `nginx`: reverse proxy config for port 8000.
- `Procfile`: Heroku-style start command.
- `docker-compose-prod.yml`: runs the `naikgirish711/fastapi` image. Build and push it yourself with `docker build -t naikgirish711/fastapi .`.

The server deploy does not install dependencies or run `alembic upgrade head`. Do that by hand after a release that changes the requirements or models.

## Known limits

- CORS only allows `https://www.google.com`. Change `origins` in `app/main.py` for a real frontend.
- `GET /users/{id}` needs no login.
- `app/calculations.py` is leftover pytest practice code and nothing in the API uses it.
- Startup logs `error reading bcrypt version` from passlib. It is harmless.
