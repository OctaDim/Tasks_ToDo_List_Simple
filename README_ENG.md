# Tasks ToDo List API

FastAPI backend service for user and task management. The project implements the requirements from `project_requirements.md` and exposes a REST API for creating users, creating tasks, listing tasks, changing task statuses, deleting tasks, and getting per-user task statistics.

## Architecture Summary

- `app/app_main.py` creates the FastAPI application and registers exception handlers.
- `main.py` is the root ASGI compatibility entrypoint and re-exports `app` from `app/app_main.py`.
- `app/api_v1_fastapi/endpoints/` keeps one directory per endpoint with `router.py`, `in_schema.py`, and `out_schema.py`.
- `app/repositories_utils/` contains persistence functions used by the routers.
- `app/models_sqlalchemy/` defines SQLAlchemy models for `users` and `tasks`.
- `app/db_postgres/` contains the async SQLAlchemy engine and session dependency.
- `alembic/` stores database migration configuration and revisions.
- `_tests_basic/` contains the isolated basic API checks.
- `_tests_extra/` contains the extended API, config, repository, DB, and Docker tests.

## API - SERVICES - REPOSITORIES

The project follows a lightweight layered structure:

- API layer: accepts HTTP requests, validates request/response schemas, maps errors to HTTP status codes, and orchestrates use-case calls.
- Service layer: holds reusable business-adjacent helpers that are shared across endpoints.
- Repository layer: isolates data access and SQLAlchemy persistence operations.

Modules by layer:

- API layer:
  `app/app_main.py`, `app/main.py`, `app/api_v1_fastapi/router.py`, `app/api_v1_fastapi/endpoints/*`, `app/api_v1_fastapi/schemas_common/*`
- Service layer:
  `app/services_utils/body_validation.py`
- Repository layer:
  `app/repositories_utils/users_utils.py`, `app/repositories_utils/tasks_utils.py`

Supporting infrastructure modules:

- Database and ORM:
  `app/db_postgres/*`, `app/models_sqlalchemy/*`
- Configuration and constants:
  `app/core/*`, `app/constants/*`

Why this split exists:

- API modules stay focused on HTTP contracts instead of raw persistence details.
- Repository modules centralize data access so SQLAlchemy queries are not duplicated across routers.
- Service helpers keep shared validation logic reusable without pushing it into every endpoint module.

## Technology Stack

- Python 3.11+ (Recommended 3.14.5)
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x with async sessions
- PostgreSQL
- Alembic
- Pytest
- Ruff
- Mypy
- Docker
- Docker Compose

 ## Recommendations:
- Add a “password” field to the user entity to prevent the leakage of sensitive confidential data from one user to another and to differentiate access levels.
- Be sure to store passwords in hashed form to prevent password leaks at the administration level.
- Pass the password and email to each router via a dependency and verify them at the service or middleware level.
- Add an “active” field to all entities and use soft deletion (retaining records in the database) rather than hard deletion.
- Create a script or additional background task that will physically delete records marked as inactive after a specified period.
- Add an admin panel for quick access to database information at the administration level.
- Under heavy load, ensure caching of responses returned from the API.  


## Environment Variables

The application reads PostgreSQL settings from environment variables or `docker_compose/.env.postgres`. Uvicorn runtime settings are read from `docker_compose/.env.api_uvicorn`.

Compose note:

- the host-facing PostgreSQL address remains `127.0.0.1:15433`,
- the PostgreSQL container listens on all interfaces inside the Docker network so the `api` container can reach it,
- the `api` container overrides `POSTGRES_HOST` to `db` so inter-container traffic uses the Docker network instead of container-local loopback.
- Docker Compose interpolates published host and port values from `docker_compose/.env.postgres` and `docker_compose/.env.api_uvicorn` when you pass both files with `--env-file`.

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
| `API_PUBLISH_HOST` | No | `127.0.0.1` | Host loopback address published by Docker Compose on the machine running Docker |
| `API_HOST` | No | `0.0.0.0` | Bind host used by Uvicorn inside the Docker runtime |
| `API_PORT` | No | `8000` | Port used by Uvicorn inside the Docker runtime |

## How To Run The Project

### Important!

Don't forget to copy the environment .env.* files to the ‘docker_compose’ directory:

docker_compose/.env.api_uvicorn

docker_compose/.env.postgres

### Option 1. Recommended: Docker Compose

1. Start the TO-DO TASKS backend service:

```bash
docker compose --env-file docker_compose/.env.postgres --env-file docker_compose/.env.api_uvicorn up --build
```

Options:
Adjust `docker_compose/.env.postgres` and `docker_compose/.env.api_uvicorn` if you want custom settings.

IMPORTANT NOTE:
- the container log may print `Uvicorn running on http://0.0.0.0:8000`. It is normal;
- `http://0.0.0.0:8000` is the internal bind address inside the container, not external one and not the browser URL;
- open `http://127.0.0.1:8000`, `http://127.0.0.1:8000/docs`, or `http://127.0.0.1:8000/openapi.json` from the host browser.

What happens:

- PostgreSQL starts from `docker_compose/.env.postgres` and binds to `127.0.0.1:${POSTGRES_PORT}`.
- The `api` container reads `docker_compose/.env.postgres` and `docker_compose/.env.api_uvicorn`.
- Docker Compose publishes `${POSTGRES_HOST}:${POSTGRES_HOST_PORT}` for PostgreSQL and `${API_PUBLISH_HOST}:${API_PORT}` for the API on the host.
- Docker Compose overrides `POSTGRES_HOST=db` for the `api` container so the app reaches PostgreSQL over the internal Docker network.
- The `api` container installs all Python runtime and test dependencies from `requirements.txt` during the Docker build.
- The `api` container runs Alembic migrations automatically before starting Uvicorn.
- Uvicorn starts with `API_HOST` and `API_PORT` from `docker_compose/.env.api_uvicorn`.
- The default `API_HOST=0.0.0.0` is intentional so the service is reachable from the host browser when running in Docker/WSL, while `API_PUBLISH_HOST=127.0.0.1` preserves the external localhost URL.

Default URLs:

- API base URL: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc UI: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

### Option 2. Recommended local shortcuts via `make` command

The repository provides a curated `Makefile` so you do not need to remember the full Docker Compose, Uvicorn, Alembic, or quality-check commands.

Helpful discovery command:

```bash
make help
```

Main startup commands:

```bash
make docker-up-d
make docker-up
make local-python
```

What each command does:

- `make docker-up-d` recommended way: starts the Docker stack in detached mode and prints the main API URLs.
- `make docker-up` possible way: starts the Docker stack in the foreground and streams logs.
- `make local-python` long way: loads both env files literally, starts the Compose `db` service if needed, waits for 
  PostgreSQL readiness, runs Alembic migrations, and then starts Uvicorn through the repository `PYTHON` interpreter.

Backward-compatible aliases are still available:

```bash
make up-d
make up
```

Useful runtime helpers:

```bash
make ps
make docker-logs
make api-logs
make db-logs
make down
make restart
make urls
make swagger
make redoc
make json
make openapi-status
```

## How To Work With `make`

Make help:

```bash
make help
```

Startup and shutdown:

```bash
make docker-up-d
make docker-up
make local-python
make restart
make down
make ps
```

API access helpers:

```bash
make urls
make swagger
make redoc
make json
make openapi-status
```

Testing and quality helpers:

```bash
make test
make test-basic
make test-extra
make test-compose
make test-local
make test-local-basic
make test-local-extra
make ruff
make ruff-fix
make ruff-format-check
make ruff-format-fix
make mypy
make global-check
```

## How To Run Ruff

Note: The project stores default Ruff configuration in `pyproject.toml`; 
that file provides the default project-wide settings for `ruff` command

Recommended commands:

```bash
make ruff
make ruff-format-check
make ruff-fix
make ruff-format-fix
```

Current Ruff coverage includes:

- lint checks such as `pycodestyle`, `pyflakes`, import sorting, selected `pyupgrade`, `bugbear`, naming, and simplification rules;
- formatting checks through `ruff format`;
- repository exclusions for `.venv*`, `build`, `dist`, and `_docs`.

## How To Run Mypy

The project stores default Mypy configuration in `pyproject.toml`; 
that file provides the default project-wide settings for `mypy` command

Recommended command:

```bash
make mypy
```

Current Mypy configuration includes:

- `disallow_untyped_defs = true`
- `check_untyped_defs = true`
- `warn_return_any = true`
- `warn_unused_ignores = true`
- `warn_redundant_casts = true`

## How To Run Swagger

Start the project first, then open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## How To Run BASIC Tests

Recommended Docker-native run after `docker compose --env-file docker_compose/.env.postgres --env-file docker_compose/.env.api_uvicorn up --build`:

Detailed tests logging:
```bash
docker compose exec -T api python -m pytest -vv -s --tb=long --showlocals _tests_basic
```

Brief test logging:
```bash
docker compose exec -T api python -m pytest -q _tests_basic
```

## List of BASIC tests:

### Create user:
- Create user (valid parameters)
- Create user (invalid parameters)
- Create user (missing parameters)
- Create user (empty parameters)
- Create user (duplicate email)

### Create task:
- Create task (valid parameters)
- Create task (invalid parameters)
- Create task (missing parameters)
- Create task (empty parameters)
- Create task (nonexistent user)

### List user tasks:
- List user tasks (valid parameters)
- List user tasks (invalid parameters)
- List user tasks (missing parameters)
- List user tasks (empty parameters)
- List user tasks (nonexistent user)

### Filter tasks by user:
- Filter tasks by status (valid status)
- Filter tasks by status (nonexistent status)
- Filter tasks by status (missing status)
- Filter tasks by status (empty status)

### Update task status:
- Update task status (valid parameters)
- Update task status (invalid parameters)
- Update task status (missing parameters)
- Update task status (empty parameters)
- Update task status (nonexistent task)

### Delete task:
- Delete task (valid parameters)
- Delete task (invalid parameters)
- Delete task (missing parameters)
- Delete task (empty parameters)
- Delete task (nonexistent task)

### Get user tasks statuses statistics:
- Get statistics (valid parameters)
- Get statistics (invalid parameters)
- Get statistics (missing parameters)
- Get statistics (empty parameters)
- Get statistics (nonexistent user)

## How To Run EXTRA Tests 
(See the section above if you want to run the BASIC tests)

Recommended Docker-native runs after `docker compose --env-file docker_compose/.env.postgres --env-file docker_compose/.env.api_uvicorn up --build`:

```bash
docker compose exec -T api python -m pytest -q -vv _tests_extra
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

## Related Subjects
- `alembic/` for DB migrations
- `_tests/` for executable API contract coverage
