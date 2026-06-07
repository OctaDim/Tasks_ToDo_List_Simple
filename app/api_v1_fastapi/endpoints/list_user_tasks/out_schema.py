from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from app.models_sqlalchemy.task_model import TaskStatusEnum


class OutUserTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None
    status: TaskStatusEnum
    created_at: datetime
    updated_at: datetime


class OutUserTasksList(BaseModel):
    tasks: List[OutUserTask]
