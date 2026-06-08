from pydantic import BaseModel


class OutDeleteTask(BaseModel):
    ok: bool
