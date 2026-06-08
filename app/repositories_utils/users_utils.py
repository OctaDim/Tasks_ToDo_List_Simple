from sqlalchemy.ext.asyncio import AsyncSession

from app.models_sqlalchemy.user_model import UserModel


async def create_user(
        session: AsyncSession,
        email: str,
        name: str
) -> UserModel:
    user_obj = UserModel(email=email, name=name)
    session.add(user_obj)
    await session.commit()
    await session.refresh(user_obj)
    return user_obj


async def get_user_by_id(
        session: AsyncSession,
        user_id: int
) -> UserModel | None:
    user_obj = await session.get(UserModel, user_id)
    return user_obj
