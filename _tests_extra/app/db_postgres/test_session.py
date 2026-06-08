from sqlalchemy.ext.asyncio import AsyncSession

from app.db_postgres.session import async_session_factory
from app.models_sqlalchemy.task_model import TaskModel


def test_async_session_factory_creates_async_session() -> None:
    session = async_session_factory()
    try:
        assert isinstance(session, AsyncSession)
    finally:
        session.sync_session.close()


def test_task_model_matches_initial_migration_table_and_enum_values() -> None:
    assert TaskModel.__tablename__ == "tasks"
    assert TaskModel.__table__.c.status.type.enums == ["new", "in_progress", "done", "cancelled"]
