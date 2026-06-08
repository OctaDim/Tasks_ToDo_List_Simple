# Tasks ToDo List API

FastAPI backend service for user and task management. The project implements the requirements from `project_requirements.md` and exposes a REST API for creating users, creating tasks, listing tasks, changing task statuses, deleting tasks, and getting per-user task statistics.

## Architecture Summary

- `app/app_main.py` creates the FastAPI application and registers exception handlers.
- `app/api_v1_fastapi/endpoints/` keeps one directory per endpoint with `router.py`, `in_schema.py`, and `out_schema.py`.
- `app/repositories_utils/` contains persistence functions used by the routers.
- `app/models_sqlalchemy/` defines SQLAlchemy models for `users` and `tasks`.
- `app/db_postgres/` contains the async SQLAlchemy engine and session dependency.
- `alembic/` stores database migration configuration and revisions.
- `_tests/` mirrors the application structure and contains API, config, repository, and DB tests.

## Technology Stack

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x with async sessions
- PostgreSQL
- Alembic
- Pytest
- Docker Compose

## Environment Variables

The application reads PostgreSQL settings from environment variables or `docker_compose/.env.postgres`. Uvicorn runtime settings are read from `docker_compose/.env.api_uvicorn`.

### Application variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `POSTGRES_DB_NAME` | No | `tasks_dev_pgs_db` | PostgreSQL database name |
| `POSTGRES_USER` | No | `pgs_dev_user` | PostgreSQL user |
| `POSTGRES_PASSWORD` | No | `pgs_dev_password` | PostgreSQL password |
| `POSTGRES_HOST` | No | `127.0.0.1` | PostgreSQL host for the API process |
| `POSTGRES_PORT` | No | `15433` | PostgreSQL port for the API process |

### PostgreSQL container variables from `docker_compose/.env.postgres`

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `POSTGRES_DB` | No | `todo_tasks_pgs_db` | Database name consumed by the PostgreSQL container entrypoint |
| `POSTGRES_HOST_PORT` | No | `15433` | Host port mapped to the PostgreSQL container |

### Uvicorn variables from `docker_compose/.env.api_uvicorn`

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `API_HOST` | No | `127.0.0.1` | Host used by Uvicorn inside the Docker runtime |
| `API_PORT` | No | `8000` | Port used by Uvicorn inside the Docker runtime |

## How To Run The Project

### Option 1. Recommended: Docker Compose

1. Adjust `docker_compose/.env.postgres` and `docker_compose/.env.api_uvicorn` if you want custom values.
2. Start the stack:

```bash
docker compose up --build
```

What happens:

- PostgreSQL starts from `docker_compose/.env.postgres` and binds to `127.0.0.1:${POSTGRES_PORT}`.
- The `api` container reads `docker_compose/.env.postgres` and `docker_compose/.env.api_uvicorn`.
- The `api` container runs Alembic migrations automatically before starting Uvicorn.
- Uvicorn starts with `API_HOST` and `API_PORT` from `docker_compose/.env.api_uvicorn`.

Available URLs:

- API base URL: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

### Option 2. Local Python run

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

3. Export database settings and apply migrations:

```bash
set -a
. ./docker_compose/.env.postgres
set +a
alembic -c alembic/alembic.ini upgrade head
```

4. Start the API:

```bash
set -a
. ./docker_compose/.env.api_uvicorn
set +a
uvicorn app.main:app --host "${API_HOST:-127.0.0.1}" --port "${API_PORT:-8000}"
```

## How To Run Swagger

Start the project first, then open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## How To Run BASIC Tests

Run only the basic tests from `_tests_basic`:

```bash
python -m pytest -q _tests_basic
```

If this repository uses the local verified virtual environment:

```bash
.venv3145/bin/python -m pytest -q _tests_basic
```

Run the basic tests separately from `_tests_extra/app`:

```bash
python -m pytest -q _tests_basic --ignore=_tests_extra/app
```

`_tests_basic` is now self-contained and does not depend on `_tests` or `_tests_extra`.

List of tests:

- Create user (valid parameters)
- Create user (invalid parameters)
- Create user (missing parameters)
- Create user (empty parameters)
- Create user (duplicate email)
- Create task (valid parameters)
- Create task (invalid parameters)
- Create task (missing parameters)
- Create task (empty parameters)
- Create task (nonexistent user)
- List user tasks (valid parameters)
- List user tasks (invalid parameters)
- List user tasks (missing parameters)
- List user tasks (empty parameters)
- List user tasks (nonexistent user)
- Filter tasks by status (valid status)
- Filter tasks by status (nonexistent status)
- Filter tasks by status (missing status)
- Filter tasks by status (empty status)
- Update task status (valid parameters)
- Update task status (invalid parameters)
- Update task status (missing parameters)
- Update task status (empty parameters)
- Update task status (nonexistent task)
- Delete task (valid parameters)
- Delete task (invalid parameters)
- Delete task (missing parameters)
- Delete task (empty parameters)
- Delete task (nonexistent task)
- Get statistics (valid parameters)
- Get statistics (invalid parameters)
- Get statistics (missing parameters)
- Get statistics (empty parameters)
- Get statistics (nonexistent user)

## How To Run Tests

Run the full test suite from the repository root:

```bash
python -m pytest -q
```

If this repository uses the local verified virtual environment:

```bash
.venv3145/bin/python -m pytest -q
```

Run only API tests:

```bash
python -m pytest -q _tests_extra/app/api
```

Run Docker/Compose contract checks:

```bash
python -m pytest -q _tests_extra/docker_compose
```

## API Endpoints

### `POST /users`

Creates a new user.

Request body:

| Field | Type | Required | Example |
| --- | --- | --- | --- |
| `email` | `string` (`email`) | Yes | `alice@example.com` |
| `name` | `string` | Yes | `Alice Johnson` |

Example request:

```http
POST /users
Content-Type: application/json

{
  "email": "alice@example.com",
  "name": "Alice Johnson"
}
```

Success response `201 Created`:

```json
{
  "id": 1,
  "email": "alice@example.com",
  "name": "Alice Johnson",
  "created_at": "2026-06-08T12:00:00Z"
}
```

Response fields:

| Field | Type | Example |
| --- | --- | --- |
| `id` | `integer` | `1` |
| `email` | `string` (`email`) | `alice@example.com` |
| `name` | `string` | `Alice Johnson` |
| `created_at` | `string` (`date-time`) | `2026-06-08T12:00:00Z` |

Error responses:

- `409 Conflict` for duplicate email
- `422 Unprocessable Entity` for invalid body

### `GET /users/{user_id}`

Returns one user by id.

Path parameters:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `user_id` | `integer` | Yes | `1` |

Example request:

```http
GET /users/1
```

Success response `200 OK`:

```json
{
  "id": 1,
  "email": "alice@example.com",
  "name": "Alice Johnson",
  "created_at": "2026-06-08T12:00:00Z"
}
```

Error responses:

- `404 Not Found` if the user does not exist
- `422 Unprocessable Entity` if `user_id` is invalid

### `POST /users/{user_id}/tasks`

Creates a task for an existing user.

Path parameters:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `user_id` | `integer` | Yes | `1` |

Request body:

| Field | Type | Required | Example |
| --- | --- | --- | --- |
| `title` | `string` | Yes | `Prepare weekly report` |
| `description` | `string \| null` | No | `Collect metrics and summary` |

Example request:

```http
POST /users/1/tasks
Content-Type: application/json

{
  "title": "Prepare weekly report",
  "description": "Collect metrics and summary"
}
```

Success response `201 Created`:

```json
{
  "id": 10,
  "user_id": 1,
  "title": "Prepare weekly report",
  "description": "Collect metrics and summary",
  "status": "new",
  "created_at": "2026-06-08T12:10:00Z",
  "updated_at": "2026-06-08T12:10:00Z"
}
```

Response fields:

| Field | Type | Example |
| --- | --- | --- |
| `id` | `integer` | `10` |
| `user_id` | `integer` | `1` |
| `title` | `string` | `Prepare weekly report` |
| `description` | `string \| null` | `Collect metrics and summary` |
| `status` | `string` enum | `new` |
| `created_at` | `string` (`date-time`) | `2026-06-08T12:10:00Z` |
| `updated_at` | `string` (`date-time`) | `2026-06-08T12:10:00Z` |

Error responses:

- `404 Not Found` if the user does not exist
- `422 Unprocessable Entity` for invalid body or path parameter

### `GET /users/{user_id}/tasks`

Returns tasks for one user with optional status filtering and pagination.

Path parameters:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `user_id` | `integer` | Yes | `1` |

Query parameters:

| Parameter | Type | Required | Example | Notes |
| --- | --- | --- | --- | --- |
| `status` | `string` enum | No | `done` | Allowed values: `new`, `in_progress`, `done`, `cancelled` |
| `limit` | `integer` | No | `10` | Default `1000`, minimum `1`, maximum `1000` |
| `offset` | `integer` | No | `0` | Default `0`, minimum `0` |

Example request:

```http
GET /users/1/tasks?status=done&limit=10&offset=0
```

Success response `200 OK`:

```json
{
  "tasks": [
    {
      "id": 10,
      "user_id": 1,
      "title": "Prepare weekly report",
      "description": "Collect metrics and summary",
      "status": "done",
      "created_at": "2026-06-08T12:10:00Z",
      "updated_at": "2026-06-08T12:20:00Z"
    }
  ]
}
```

Response fields:

| Field | Type | Example |
| --- | --- | --- |
| `tasks` | `array[task]` | See example above |

Error responses:

- `404 Not Found` if the user does not exist
- `422 Unprocessable Entity` for invalid query or path parameters

### `PATCH /tasks/{task_id}/status`

Updates the status of a task.

Path parameters:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `task_id` | `integer` | Yes | `10` |

Request body:

| Field | Type | Required | Example |
| --- | --- | --- | --- |
| `status` | `string` enum | Yes | `in_progress` |

Allowed `status` values:

- `new`
- `in_progress`
- `done`
- `cancelled`

Example request:

```http
PATCH /tasks/10/status
Content-Type: application/json

{
  "status": "in_progress"
}
```

Success response `200 OK`:

```json
{
  "id": 10,
  "user_id": 1,
  "title": "Prepare weekly report",
  "description": "Collect metrics and summary",
  "status": "in_progress",
  "created_at": "2026-06-08T12:10:00Z",
  "updated_at": "2026-06-08T12:30:00Z"
}
```

Error responses:

- `404 Not Found` if the task does not exist
- `422 Unprocessable Entity` for invalid body or path parameter

### `DELETE /tasks/{task_id}`

Deletes a task by id.

Path parameters:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `task_id` | `integer` | Yes | `10` |

Example request:

```http
DELETE /tasks/10
```

Success response `200 OK`:

```json
{
  "ok": true
}
```

Response fields:

| Field | Type | Example |
| --- | --- | --- |
| `ok` | `boolean` | `true` |

Error responses:

- `404 Not Found` if the task does not exist
- `422 Unprocessable Entity` if `task_id` is invalid

### `GET /users/{user_id}/tasks/stats`

Returns task counters for one user.

Path parameters:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `user_id` | `integer` | Yes | `1` |

Example request:

```http
GET /users/1/tasks/stats
```

Success response `200 OK`:

```json
{
  "total": 3,
  "new": 1,
  "in_progress": 1,
  "done": 1,
  "cancelled": 0
}
```

Response fields:

| Field | Type | Example |
| --- | --- | --- |
| `total` | `integer` | `3` |
| `new` | `integer` | `1` |
| `in_progress` | `integer` | `1` |
| `done` | `integer` | `1` |
| `cancelled` | `integer` | `0` |

Error responses:

- `404 Not Found` if the user does not exist
- `422 Unprocessable Entity` if `user_id` is invalid

## Validation Notes

- Validation errors are returned as `{"detail": [{"param": "...", "value": "...", "message": "..."}]}`.
- Blank required body fields are rejected.
- Duplicate user email returns HTTP `409`.
- Task statuses are limited to `new`, `in_progress`, `done`, and `cancelled`.

## Related Documentation

- `PROJECT_ARCHITECTURE.md` for the detailed repository map, ADRs, and operational notes
- `project_requirements.md` for the original assignment and acceptance constraints
- `alembic/` for DB migrations
- `_tests/` for executable API contract coverage
