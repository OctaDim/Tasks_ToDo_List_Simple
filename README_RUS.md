# Tasks ToDo List API

Бэкенд-сервис FastAPI для управления пользователями и задачами. Проект реализует требования из `project_requirements.md` и предоставляет REST API для создания пользователей, создания задач, получения списка задач, изменения статусов задач, удаления задач и получения статистики задач по пользователю.

## Краткое описание архитектуры

- `app/app_main.py` создает приложение FastAPI и регистрирует обработчики исключений.
- `main.py` является корневой ASGI-точкой входа для совместимости и реэкспортирует `app` из `app/app_main.py`.
- `app/api_v1_fastapi/endpoints/` хранит отдельную директорию для каждого endpoint с файлами `router.py`, `in_schema.py` и `out_schema.py`.
- `app/repositories_utils/` содержит функции доступа к данным, используемые роутерами.
- `app/models_sqlalchemy/` определяет SQLAlchemy-модели для `users` и `tasks`.
- `app/db_postgres/` содержит асинхронный SQLAlchemy engine и зависимость сессии.
- `alembic/` хранит конфигурацию миграций базы данных и ревизии.
- `_tests_basic/` содержит изолированные базовые проверки API.
- `_tests_extra/` содержит расширенные тесты API, конфигурации, репозиториев, БД и Docker.

## API - SERVICES - REPOSITORIES

Проект следует облегченной слоистой структуре:

- Слой API: принимает HTTP-запросы, валидирует схемы запросов и ответов, сопоставляет ошибки с HTTP-статусами и координирует вызовы сценариев использования.
- Слой сервисов: содержит переиспользуемые вспомогательные компоненты, связанные с бизнес-логикой и разделяемые между endpoint'ами.
- Слой репозиториев: изолирует доступ к данным и операции сохранения через SQLAlchemy.

Модули по слоям:

- Слой API:
  `app/app_main.py`, `app/main.py`, `app/api_v1_fastapi/router.py`, `app/api_v1_fastapi/endpoints/*`, `app/api_v1_fastapi/schemas_common/*`
- Слой сервисов:
  `app/services_utils/body_validation.py`
- Слой репозиториев:
  `app/repositories_utils/users_utils.py`, `app/repositories_utils/tasks_utils.py`

Поддерживающие инфраструктурные модули:

- База данных и ORM:
  `app/db_postgres/*`, `app/models_sqlalchemy/*`
- Конфигурация и константы:
  `app/core/*`, `app/constants/*`

Почему существует такое разделение:

- Модули API остаются сфокусированными на HTTP-контрактах, а не на деталях низкоуровневой работы с хранилищем.
- Модули репозиториев централизуют доступ к данным, чтобы SQLAlchemy-запросы не дублировались в роутерах.
- Сервисные хелперы позволяют переиспользовать общую валидацию, не размазывая ее по каждому endpoint'у.

## Стек технологий

- Python 3.11+ (рекомендуется 3.14.5)
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x с асинхронными сессиями
- PostgreSQL
- Alembic
- Pytest
- Ruff
- Mypy
- Docker
- Docker Compose

## Рекомендации:
- Добавить для сущности пользователя поле password, чтобы исключить утечку чувствительных секретных данных одних пользователей к другим пользователям и разграничить уровень доступа.
- Обязательно сохранять пароли в хэшированном виде, чтобы исключить утечку паролей на уровне администрирования
- Передавать пароль и email в каждый роутер через dependency зависимость и сверять на сервисном уровне или уровне middleware. 
- Для всех сущностей добавить поле "active" и применять не жесткое, а мягкое удаление с сохранением записей в базе данных.
- Создать скрипт или дополнительную фоновую задачу, которая будет физически удалять записи помеченные, как неактивные по истечении определенного срока.
- Добавить админ-панель для быстрого доступа к информации в базе данных на уровне администрирования.


## Переменные окружения

Приложение читает настройки PostgreSQL из переменных окружения или из `docker_compose/.env.postgres`. Настройки запуска Uvicorn читаются из `docker_compose/.env.api_uvicorn`.

Примечание по Compose:

- адрес PostgreSQL, доступный с хоста, остается `127.0.0.1:15433`,
- контейнер PostgreSQL слушает на всех интерфейсах внутри Docker-сети, чтобы контейнер `api` мог до него достучаться,
- контейнер `api` переопределяет `POSTGRES_HOST` на `db`, чтобы межконтейнерный трафик шел через Docker-сеть, а не через локальный loopback контейнера.
- Docker Compose подставляет публикуемые хост и порт из `docker_compose/.env.postgres` и `docker_compose/.env.api_uvicorn`, когда вы передаете оба файла через `--env-file`.

### Переменные приложения

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `POSTGRES_DB_NAME` | No | `tasks_dev_pgs_db` | Имя базы данных PostgreSQL |
| `POSTGRES_USER` | No | `pgs_dev_user` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | No | `pgs_dev_password` | Пароль PostgreSQL |
| `POSTGRES_HOST` | No | `127.0.0.1` | Хост PostgreSQL для процесса API |
| `POSTGRES_PORT` | No | `15433` | Порт PostgreSQL для процесса API |

### Переменные контейнера PostgreSQL из `docker_compose/.env.postgres`

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `POSTGRES_DB` | No | `todo_tasks_pgs_db` | Имя базы данных, которое использует entrypoint контейнера PostgreSQL |
| `POSTGRES_HOST_PORT` | No | `15433` | Порт хоста, отображенный на контейнер PostgreSQL |

### Переменные Uvicorn из `docker_compose/.env.api_uvicorn`

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `API_PUBLISH_HOST` | No | `127.0.0.1` | Адрес loopback хоста, публикуемый Docker Compose на машине с Docker |
| `API_HOST` | No | `0.0.0.0` | Хост привязки, который Uvicorn использует внутри Docker runtime |
| `API_PORT` | No | `8000` | Порт, который Uvicorn использует внутри Docker runtime |


## Как запустить проект

## копирование фалов переменных окружения

### Внимание!

Не забудьте скопировать .env.* файлы переменного окружения в директорию 'docker_compose':

docker_compose/.env.api_uvicorn

docker_compose/.env.postgres

### Вариант 1. Рекомендуется: Docker Compose

1. Запустите бэкенд-сервис TO-DO TASKS:

```bash
docker compose --env-file docker_compose/.env.postgres --env-file docker_compose/.env.api_uvicorn up --build
```

Параметры:
При необходимости измените `docker_compose/.env.postgres` и `docker_compose/.env.api_uvicorn`.

ВАЖНОЕ ПРИМЕЧАНИЕ:
- в логах контейнера может появиться строка `Uvicorn running on http://0.0.0.0:8000`. Это нормально;
- `http://0.0.0.0:8000` является внутренним адресом привязки внутри контейнера, а не внешним адресом и не URL для браузера;
- открывайте `http://127.0.0.1:8000`, `http://127.0.0.1:8000/docs` или `http://127.0.0.1:8000/openapi.json` в браузере на хосте.

Что происходит:

- PostgreSQL запускается с параметрами из `docker_compose/.env.postgres` и привязывается к `127.0.0.1:${POSTGRES_PORT}`.
- Контейнер `api` читает `docker_compose/.env.postgres` и `docker_compose/.env.api_uvicorn`.
- Docker Compose публикует `${POSTGRES_HOST}:${POSTGRES_HOST_PORT}` для PostgreSQL и `${API_PUBLISH_HOST}:${API_PORT}` для API на хосте.
- Docker Compose переопределяет `POSTGRES_HOST=db` для контейнера `api`, чтобы приложение подключалось к PostgreSQL по внутренней Docker-сети.
- Контейнер `api` устанавливает все Python-зависимости времени выполнения и тестовые зависимости из `requirements.txt` во время Docker-сборки.
- Контейнер `api` автоматически запускает миграции Alembic перед стартом Uvicorn.
- Uvicorn запускается с `API_HOST` и `API_PORT` из `docker_compose/.env.api_uvicorn`.
- Значение по умолчанию `API_HOST=0.0.0.0` выбрано намеренно, чтобы сервис был доступен из браузера на хосте при запуске в Docker/WSL, а `API_PUBLISH_HOST=127.0.0.1` сохраняет внешний localhost URL.

URL по умолчанию:

- Базовый URL API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc UI: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

### Вариант 2. Рекомендуемые локальные сокращения через команду `make`

Репозиторий содержит подготовленный `Makefile`, поэтому не нужно запоминать полные команды Docker Compose, Uvicorn, Alembic или проверок качества.

Полезная команда для знакомства:

```bash
make help
```

Основные команды запуска:

```bash
make docker-up-d
make docker-up
make local-python
```

Что делает каждая команда:

- `make docker-up-d` рекомендуемый способ: запускает Docker-стек в фоновом режиме и выводит основные URL API.
- `make docker-up` возможный способ: запускает Docker-стек в foreground-режиме и транслирует логи.
- `make local-python` длинный путь: буквально загружает оба env-файла, при необходимости запускает сервис `db` из Compose, ждет готовности PostgreSQL, выполняет миграции Alembic и затем запускает Uvicorn через интерпретатор `PYTHON`, настроенный в репозитории.

Алиасы для обратной совместимости по-прежнему доступны:

```bash
make up-d
make up
```

Полезные runtime-хелперы:

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

## Как работать с `make`

Справка по Make:

```bash
make help
```

Запуск и остановка:

```bash
make docker-up-d
make docker-up
make local-python
make restart
make down
make ps
```

Хелперы для доступа к API:

```bash
make urls
make swagger
make redoc
make json
make openapi-status
```

Хелперы для тестирования и качества:

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

## Как запускать Ruff

Примечание: проект хранит конфигурацию Ruff по умолчанию в `pyproject.toml`; 
этот файл задает проектные настройки по умолчанию для команды `ruff`

Рекомендуемые команды:

```bash
make ruff
make ruff-format-check
make ruff-fix
make ruff-format-fix
```

Текущее покрытие Ruff включает:

- проверки линтера, такие как `pycodestyle`, `pyflakes`, сортировка импортов, выбранные правила `pyupgrade`, `bugbear`, именования и упрощения;
- проверки форматирования через `ruff format`;
- исключения на уровне репозитория для `.venv*`, `build`, `dist` и `_docs`.

## Как запускать Mypy

Проект хранит конфигурацию Mypy по умолчанию в `pyproject.toml`; 
этот файл задает проектные настройки по умолчанию для команды `mypy`

Рекомендуемая команда:

```bash
make mypy
```

Текущая конфигурация Mypy включает:

- `disallow_untyped_defs = true`
- `check_untyped_defs = true`
- `warn_return_any = true`
- `warn_unused_ignores = true`
- `warn_redundant_casts = true`

## Как открыть Swagger

Сначала запустите проект, затем откройте:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Как запускать BASIC-тесты

Рекомендуемый Docker-native запуск после `docker compose --env-file docker_compose/.env.postgres --env-file docker_compose/.env.api_uvicorn up --build`:

Подробное логирование тестов:
```bash
docker compose exec -T api python -m pytest -vv -s --tb=long --showlocals _tests_basic
```

Краткое логирование тестов:
```bash
docker compose exec -T api python -m pytest -q _tests_basic
```

## Список BASIC-тестов:

### Создание пользователя:
- Создание пользователя (корректные параметры)
- Создание пользователя (некорректные параметры)
- Создание пользователя (отсутствующие параметры)
- Создание пользователя (пустые параметры)
- Создание пользователя (дублирующийся email)

### Создание задачи:
- Создание задачи (корректные параметры)
- Создание задачи (некорректные параметры)
- Создание задачи (отсутствующие параметры)
- Создание задачи (пустые параметры)
- Создание задачи (несуществующий пользователь)

### Получение списка задач пользователя:
- Получение списка задач пользователя (корректные параметры)
- Получение списка задач пользователя (некорректные параметры)
- Получение списка задач пользователя (отсутствующие параметры)
- Получение списка задач пользователя (пустые параметры)
- Получение списка задач пользователя (несуществующий пользователь)

### Фильтрация задач пользователя:
- Фильтрация задач по статусу (корректный статус)
- Фильтрация задач по статусу (несуществующий статус)
- Фильтрация задач по статусу (отсутствующий статус)
- Фильтрация задач по статусу (пустой статус)

### Обновление статуса задачи:
- Обновление статуса задачи (корректные параметры)
- Обновление статуса задачи (некорректные параметры)
- Обновление статуса задачи (отсутствующие параметры)
- Обновление статуса задачи (пустые параметры)
- Обновление статуса задачи (несуществующая задача)

### Удаление задачи:
- Удаление задачи (корректные параметры)
- Удаление задачи (некорректные параметры)
- Удаление задачи (отсутствующие параметры)
- Удаление задачи (пустые параметры)
- Удаление задачи (несуществующая задача)

### Получение статистики статусов задач пользователя:
- Получение статистики (корректные параметры)
- Получение статистики (некорректные параметры)
- Получение статистики (отсутствующие параметры)
- Получение статистики (пустые параметры)
- Получение статистики (несуществующий пользователь)

## Как запускать EXTRA-тесты
(См. раздел выше, если хотите запускать BASIC-тесты)

Рекомендуемый Docker-native запуск после `docker compose --env-file docker_compose/.env.postgres --env-file docker_compose/.env.api_uvicorn up --build`:

```bash
docker compose exec -T api python -m pytest -q -vv _tests_extra
```

## API Endpoints

### `POST /users`

Создает нового пользователя.

Тело запроса:

| Field | Type | Required | Example |
| --- | --- | --- | --- |
| `email` | `string` (`email`) | Yes | `alice@example.com` |
| `name` | `string` | Yes | `Alice Johnson` |

Пример запроса:

```http
POST /users
Content-Type: application/json

{
  "email": "alice@example.com",
  "name": "Alice Johnson"
}
```

Успешный ответ `201 Created`:

```json
{
  "id": 1,
  "email": "alice@example.com",
  "name": "Alice Johnson",
  "created_at": "2026-06-08T12:00:00Z"
}
```

Поля ответа:

| Field | Type | Example |
| --- | --- | --- |
| `id` | `integer` | `1` |
| `email` | `string` (`email`) | `alice@example.com` |
| `name` | `string` | `Alice Johnson` |
| `created_at` | `string` (`date-time`) | `2026-06-08T12:00:00Z` |

Ошибки:

- `409 Conflict` для дублирующегося email
- `422 Unprocessable Entity` для некорректного тела запроса

### `GET /users/{user_id}`

Возвращает одного пользователя по идентификатору.

Параметры пути:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `user_id` | `integer` | Yes | `1` |

Пример запроса:

```http
GET /users/1
```

Успешный ответ `200 OK`:

```json
{
  "id": 1,
  "email": "alice@example.com",
  "name": "Alice Johnson",
  "created_at": "2026-06-08T12:00:00Z"
}
```

Ошибки:

- `404 Not Found`, если пользователь не существует
- `422 Unprocessable Entity`, если `user_id` некорректен

### `POST /users/{user_id}/tasks`

Создает задачу для существующего пользователя.

Параметры пути:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `user_id` | `integer` | Yes | `1` |

Тело запроса:

| Field | Type | Required | Example |
| --- | --- | --- | --- |
| `title` | `string` | Yes | `Prepare weekly report` |
| `description` | `string \| null` | No | `Collect metrics and summary` |

Пример запроса:

```http
POST /users/1/tasks
Content-Type: application/json

{
  "title": "Prepare weekly report",
  "description": "Collect metrics and summary"
}
```

Успешный ответ `201 Created`:

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

Поля ответа:

| Field | Type | Example |
| --- | --- | --- |
| `id` | `integer` | `10` |
| `user_id` | `integer` | `1` |
| `title` | `string` | `Prepare weekly report` |
| `description` | `string \| null` | `Collect metrics and summary` |
| `status` | `string` enum | `new` |
| `created_at` | `string` (`date-time`) | `2026-06-08T12:10:00Z` |
| `updated_at` | `string` (`date-time`) | `2026-06-08T12:10:00Z` |

Ошибки:

- `404 Not Found`, если пользователь не существует
- `422 Unprocessable Entity` для некорректного тела запроса или параметра пути

### `GET /users/{user_id}/tasks`

Возвращает задачи одного пользователя с необязательной фильтрацией по статусу и пагинацией.

Параметры пути:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `user_id` | `integer` | Yes | `1` |

Параметры запроса:

| Parameter | Type | Required | Example | Notes |
| --- | --- | --- | --- | --- |
| `status` | `string` enum | No | `done` | Допустимые значения: `new`, `in_progress`, `done`, `cancelled` |
| `limit` | `integer` | No | `10` | Значение по умолчанию `1000`, минимум `1`, максимум `1000` |
| `offset` | `integer` | No | `0` | Значение по умолчанию `0`, минимум `0` |

Пример запроса:

```http
GET /users/1/tasks?status=done&limit=10&offset=0
```

Успешный ответ `200 OK`:

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

Поля ответа:

| Field | Type | Example |
| --- | --- | --- |
| `tasks` | `array[task]` | См. пример выше |

Ошибки:

- `404 Not Found`, если пользователь не существует
- `422 Unprocessable Entity` для некорректных query-параметров или параметров пути

### `PATCH /tasks/{task_id}/status`

Обновляет статус задачи.

Параметры пути:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `task_id` | `integer` | Yes | `10` |

Тело запроса:

| Field | Type | Required | Example |
| --- | --- | --- | --- |
| `status` | `string` enum | Yes | `in_progress` |

Допустимые значения `status`:

- `new`
- `in_progress`
- `done`
- `cancelled`

Пример запроса:

```http
PATCH /tasks/10/status
Content-Type: application/json

{
  "status": "in_progress"
}
```

Успешный ответ `200 OK`:

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

Ошибки:

- `404 Not Found`, если задача не существует
- `422 Unprocessable Entity` для некорректного тела запроса или параметра пути

### `DELETE /tasks/{task_id}`

Удаляет задачу по идентификатору.

Параметры пути:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `task_id` | `integer` | Yes | `10` |

Пример запроса:

```http
DELETE /tasks/10
```

Успешный ответ `200 OK`:

```json
{
  "ok": true
}
```

Поля ответа:

| Field | Type | Example |
| --- | --- | --- |
| `ok` | `boolean` | `true` |

Ошибки:

- `404 Not Found`, если задача не существует
- `422 Unprocessable Entity`, если `task_id` некорректен

### `GET /users/{user_id}/tasks/stats`

Возвращает счетчики задач по одному пользователю.

Параметры пути:

| Parameter | Type | Required | Example |
| --- | --- | --- | --- |
| `user_id` | `integer` | Yes | `1` |

Пример запроса:

```http
GET /users/1/tasks/stats
```

Успешный ответ `200 OK`:

```json
{
  "total": 3,
  "new": 1,
  "in_progress": 1,
  "done": 1,
  "cancelled": 0
}
```

Поля ответа:

| Field | Type | Example |
| --- | --- | --- |
| `total` | `integer` | `3` |
| `new` | `integer` | `1` |
| `in_progress` | `integer` | `1` |
| `done` | `integer` | `1` |
| `cancelled` | `integer` | `0` |

Ошибки:

- `404 Not Found`, если пользователь не существует
- `422 Unprocessable Entity`, если `user_id` некорректен

## Примечания по валидации

- Ошибки валидации возвращаются в формате `{"detail": [{"param": "...", "value": "...", "message": "..."}]}`.
- Пустые обязательные поля тела запроса отклоняются.
- Дублирующийся email пользователя возвращает HTTP `409`.
- Статусы задач ограничены значениями `new`, `in_progress`, `done` и `cancelled`.

## Связанные разделы
- `alembic/` для миграций БД
- `_tests/` для исполняемого покрытия API-контрактов
