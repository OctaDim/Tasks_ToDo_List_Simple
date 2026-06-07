from sqlalchemy.ext.asyncio import AsyncSession

from app.models_sqlalchemy.user import User


async def create_user(session: AsyncSession, email: str, name: str) -> User:
    user_obj = User(email=email, name=name)
    session.add(user_obj)
    await session.commit()
    await session.refresh(user_obj)
    return user_obj


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    user = await session.get(User, user_id)
    return user
