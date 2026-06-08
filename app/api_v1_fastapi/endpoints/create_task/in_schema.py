from typing import Any, Dict

from pydantic import BaseModel, model_validator

from app.services_utils.body_validation import ensure_req_body_dict, validate_not_blank


class InCreateTask(BaseModel):
    title: str
    description: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_request_body(cls, data: dict | Any) -> Dict[str, Any]:
        req_body_dict = ensure_req_body_dict(request_data=data)
        validate_not_blank(request_data=req_body_dict,
                           required_fields=("title",))
        return req_body_dict
