from typing import List

from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.models_sqlalchemy.task_model import TaskModel, TaskStatusEnum
from app.models_sqlalchemy.user_model import UserModel


async def create_task_by_user(
        session: AsyncSession,
        user: UserModel,
        title: str,
        description: str | None
) -> TaskModel:
    task_obj = TaskModel(user_id=user.id,
                         title=title,
                         description=description)
    session.add(task_obj)
    await session.commit()
    await session.refresh(task_obj)
    return task_obj


async def list_tasks_by_user(
        session: AsyncSession,
        user_id: int,
        status: TaskStatusEnum | None,
        limit: int,
        offset: int,
) -> List[TaskModel] | Sequence[TaskModel]:
    stmt = select(
        TaskModel
    ).where(
        TaskModel.user_id == user_id
    ).order_by(TaskModel.id).limit(limit).offset(offset)

    if status:
        stmt = stmt.where(TaskModel.status == status)

    stmt_result = await session.execute(stmt)
    stmt_result = stmt_result.scalars().all()
    return stmt_result


async def get_task_by_id(
        session: AsyncSession,
        task_id: int
) -> TaskModel | None:
    task_obj = await session.get(TaskModel, task_id)
    return task_obj


async def update_task_status(
        session: AsyncSession,
        task_obj: TaskModel,
        task_status: TaskStatusEnum
) -> TaskModel:
    task_obj.status = task_status
    await session.commit()
    await session.refresh(task_obj)
    return task_obj
