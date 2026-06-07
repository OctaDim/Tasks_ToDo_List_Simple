from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class OutGetUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    created_at: datetime
