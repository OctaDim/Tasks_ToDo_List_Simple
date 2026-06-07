from sqlalchemy.ext.asyncio import AsyncSession

from app.models_sqlalchemy.task import Task
from app.models_sqlalchemy.user import User


async def create_task_by_user(
        session: AsyncSession,
        user: User,
        title: str,
        description: str | None
) -> Task:
    task_obj = Task(user_id=user.id,
                    title=title,
                    description=description)
    session.add(task_obj)
    await session.commit()
    await session.refresh(task_obj)
    return task_obj
