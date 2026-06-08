from pydantic import BaseModel


class OutUserTaskStats(BaseModel):
    total: int = 0
    new: int = 0
    in_progress: int = 0
    done: int = 0
    cancelled: int = 0
