from typing import Any, List

from pydantic import BaseModel


class OutValidationErrorItem(BaseModel):
    param: str
    value: Any
    message: str


class OutErrorResponse(BaseModel):
    detail: List[OutValidationErrorItem]