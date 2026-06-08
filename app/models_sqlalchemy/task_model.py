from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models_sqlalchemy.base_model import Base


class TaskStatusEnum(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

    @classmethod
    def has_value(cls, value: object) -> bool:
        enum_value = value.value if isinstance(value, cls) else value
        return enum_value in {status.value for status in cls}


class TaskModel(Base):
    __tablename__ = "tasks"

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

    status: Mapped[TaskStatusEnum] = mapped_column(
        Enum(
            TaskStatusEnum,
            name="task_status",
            values_callable=lambda enum_class: [status.value for status in enum_class],
        ),
        nullable=False,
        default=TaskStatusEnum.NEW)

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
