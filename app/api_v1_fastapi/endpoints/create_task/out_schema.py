from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models_sqlalchemy.task import TaskStatus


class OutCreateTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
