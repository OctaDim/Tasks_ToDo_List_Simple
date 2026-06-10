from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, Dict, List

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import IntegrityError

from app.app_main import app
from app.db_postgres.session import get_async_session
from app.models_sqlalchemy.task_model import TaskStatusEnum


class InMemoryStore:
    def __init__(self) -> None:
        self.users: Dict[int, SimpleNamespace] = {}
        self.tasks: Dict[int, SimpleNamespace] = {}
        self.user_id_sequence = 1
        self.task_id_sequence = 1

    async def create_user(
            self, session: Any,
            email: str,
            name: str
    ) -> SimpleNamespace:
        if any(user.email == email for user in self.users.values()):
            raise IntegrityError(statement="insert user",
                                 params={"email": email},
                                 orig=Exception("duplicate email"))
        user = SimpleNamespace(id=self.user_id_sequence, email=email, name=name, created_at=datetime.now(UTC))
        self.users[user.id] = user
        self.user_id_sequence += 1
        return user

    async def get_user_by_id(self, session: Any, user_id: int) -> SimpleNamespace | None:
        return self.users.get(user_id)

    async def create_task(
            self,
            session: Any,
            user: SimpleNamespace,
            title: str,
            description: str | None,
    ) -> SimpleNamespace:
        now = datetime.now(UTC)
        task = SimpleNamespace(
            id=self.task_id_sequence,
            user_id=user.id,
            title=title,
            description=description,
            status=TaskStatusEnum.NEW,
            created_at=now,
            updated_at=now,
        )
        self.tasks[task.id] = task
        self.task_id_sequence += 1
        return task

    async def get_task_by_id(self, session: Any, task_id: int) -> SimpleNamespace | None:
        return self.tasks.get(task_id)

    async def list_tasks(
            self,
            session: Any,
            user_id: int,
            status: TaskStatusEnum | None,
            limit: int,
            offset: int,
    ) -> List[SimpleNamespace]:
        tasks = [task for task in self.tasks.values() if task.user_id == user_id]
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        return sorted(tasks, key=lambda task: task.id)[offset: offset + limit]

    async def update_task_status(
            self,
            session: Any,
            task_obj: SimpleNamespace,
            task_status: TaskStatusEnum,
    ) -> SimpleNamespace:
        task_obj.status = task_status
        task_obj.updated_at = datetime.now(UTC)
        return task_obj

    async def delete_task_by_id(self, session: Any, task_id: int) -> bool:
        return self.tasks.pop(task_id, None) is not None

    async def get_user_task_stats(self, session: Any, user_id: int) -> Dict[str, int]:
        stats = {"new": 0, "in_progress": 0, "done": 0, "cancelled": 0}
        for task in self.tasks.values():
            if task.user_id == user_id:
                stats[task.status.value] += 1
        return {"total": sum(stats.values()), **stats}


@pytest_asyncio.fixture()
async def client(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[AsyncClient, None]:
    store = InMemoryStore()

    async def override_session() -> AsyncGenerator[None, None]:
        yield None

    app.dependency_overrides[get_async_session] = override_session
    monkeypatch.setattr("app.api_v1_fastapi.endpoints.create_user.router.create_user", store.create_user)
    monkeypatch.setattr("app.api_v1_fastapi.endpoints.get_user.router.get_user_by_id", store.get_user_by_id)
    monkeypatch.setattr("app.api_v1_fastapi.endpoints.create_task.router.get_user_by_id", store.get_user_by_id)
    monkeypatch.setattr("app.api_v1_fastapi.endpoints.create_task.router.create_task_by_user", store.create_task)
    monkeypatch.setattr("app.api_v1_fastapi.endpoints.list_user_tasks.router.get_user_by_id", store.get_user_by_id)
    monkeypatch.setattr("app.api_v1_fastapi.endpoints.list_user_tasks.router.list_tasks_by_user", store.list_tasks)
    monkeypatch.setattr("app.api_v1_fastapi.endpoints.update_task_status.router.get_task_by_id", store.get_task_by_id)
    monkeypatch.setattr("app.api_v1_fastapi.endpoints.update_task_status.router.update_task_status",
                        store.update_task_status)
    monkeypatch.setattr("app.api_v1_fastapi.endpoints.delete_task.router.delete_task_by_id", store.delete_task_by_id)
    monkeypatch.setattr("app.api_v1_fastapi.endpoints.user_task_stats.router.get_user_by_id", store.get_user_by_id)
    monkeypatch.setattr("app.api_v1_fastapi.endpoints.user_task_stats.router.get_user_tasks_stats",
                        store.get_user_task_stats)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
