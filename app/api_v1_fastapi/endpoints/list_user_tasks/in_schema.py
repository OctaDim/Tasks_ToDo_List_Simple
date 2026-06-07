from pydantic import BaseModel, Field

from app.core.options import PaginationOptions
from app.models_sqlalchemy.task_model import TaskStatusEnum


class InListUserTasksQuery(BaseModel):
    status: TaskStatusEnum | None = None
    limit: int = Field(default=PaginationOptions.DEFAULT_PAGINATION,
                       ge=1, le=PaginationOptions.MAX_LIMIT)
    offset: int = Field(default=0, ge=0)
