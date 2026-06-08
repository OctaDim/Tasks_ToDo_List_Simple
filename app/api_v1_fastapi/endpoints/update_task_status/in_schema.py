from typing import Any, Dict

from pydantic import BaseModel, model_validator

from app.models_sqlalchemy.task_model import TaskStatusEnum
from app.services_utils.body_validation import ensure_req_body_dict


class InUpdateTaskStatus(BaseModel):
    status: TaskStatusEnum

    @model_validator(mode="before")
    @classmethod
    def validate_request_body(cls, data: dict | any) -> Dict[str, Any]:
        req_body_dict = ensure_req_body_dict(data)
        if "status" not in req_body_dict:
            error_log = f"Missing parameter 'status' error: {req_body_dict}"
            raise ValueError(error_log)
        return req_body_dict
