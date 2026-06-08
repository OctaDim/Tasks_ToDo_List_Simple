from typing import Any

from app.models_sqlalchemy.task_model import TaskStatusEnum
from app.repositories_utils.tasks_utils import get_user_tasks_stats


class FakeTuplesResult:
    def __init__(self, rows: list[tuple[TaskStatusEnum, int]]) -> None:
        self.rows = rows

    def all(self) -> list[tuple[TaskStatusEnum, int]]:
        return self.rows


class FakeExecuteResult:
    def __init__(self, rows: list[tuple[TaskStatusEnum, int]]) -> None:
        self.rows = rows

    def tuples(self) -> FakeTuplesResult:
        return FakeTuplesResult(self.rows)


class FakeSession:
    async def execute(self, stmt: Any) -> FakeExecuteResult:
        return FakeExecuteResult(
            [
                (TaskStatusEnum.NEW, 1),
                (TaskStatusEnum.IN_PROGRESS, 1),
                (TaskStatusEnum.DONE, 1),
            ]
        )


async def test_get_user_tasks_stats_returns_total_and_all_statuses() -> None:
    stats = await get_user_tasks_stats(session=FakeSession(), user_id=1)

    assert stats == {
        "total": 3,
        "new": 1,
        "in_progress": 1,
        "done": 1,
        "cancelled": 0,
    }
