from typing import List, Dict

from sqlalchemy import select, Sequence, func
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

    executed_stmt = await session.execute(stmt)
    user_tasks = executed_stmt.scalars().all()
    return user_tasks


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


async def delete_task_by_id(
        session: AsyncSession,
        task_id: int
) -> bool:
    task_obj = await get_task_by_id(session=session, task_id=task_id)
    if not task_obj:
        return False
    await session.delete(task_obj)
    await session.commit()
    return True


async def get_user_tasks_stats(
        session: AsyncSession,
        user_id: int
) -> Dict[str, int]:
    stmt = select(
        TaskModel.status, func.count(TaskModel.id)
    ).where(
        TaskModel.user_id == user_id
    ).group_by(TaskModel.status)

    executed_stmt = await session.execute(stmt)
    stmt_result = executed_stmt.tuples().all()

    user_statuses_counts = {status.value: count for status, count in stmt_result}
    user_statuses_counts["total"] = sum(user_statuses_counts.values())
    return user_statuses_counts
