from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models_sqlalchemy.base_model import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True)

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
        index=True)

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False)

    tasks_by_user: Mapped[List["TaskModel"]] = relationship(
        argument="TaskModel",
        back_populates="user_by_task",
        cascade="all, delete-orphan")
