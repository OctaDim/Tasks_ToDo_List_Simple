from typing import Any, Dict

from pydantic import BaseModel, EmailStr, model_validator

from app.constants.constants import ErrorMessages
from app.services_utils.body_validation import (
    ensure_req_body_dict, validate_not_blank)


class InCreateUser(BaseModel):
    email: EmailStr
    name: str

    @model_validator(mode="before")
    @classmethod
    def validate_request_body(cls, data: dict | Any) -> Dict[str, Any] | None:
        req_body_dict = ensure_req_body_dict(data)
        if not req_body_dict or req_body_dict is None:
            raise ValueError(ErrorMessages.INVALID_REQUEST_BODY)
        validate_not_blank(request_data=req_body_dict,
                           required_fields=("email", "name",))
        return req_body_dict
