from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models_sqlalchemy.base_model import Base


class TaskStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskModel(Base):
    __tablename__ = "todo_tasks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="users.id", ondelete="CASCADE"),
        nullable=False,
        index=True)

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False)

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True)

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"),
        nullable=False,
        default=TaskStatus.NEW)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False)

    user_by_task: Mapped["UserModel"] = relationship(
        argument="UserModel",
        back_populates="tasks_by_user")
