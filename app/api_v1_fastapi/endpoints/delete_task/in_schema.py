from pydantic import BaseModel


class InDeleteTask(BaseModel):
    task_id: int
