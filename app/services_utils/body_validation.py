from collections.abc import Sequence
from typing import Any, Dict

from app.constants.constants import ErrorMessages


def ensure_req_body_dict(
        request_data: Dict | Any
) -> Dict[str, Any] | None:
    if not isinstance(request_data, dict):
        error_log = (f"{ErrorMessages.INVALID_REQUEST_BODY}: "
                     f"request data type: {type(request_data)}")
        raise ValueError(error_log)
    return request_data


def validate_not_blank(
        request_data: Dict[str, Any],
        required_fields: Sequence[str]
) -> bool:
    invalid_fields = []
    for field_name in required_fields:
        field_value = request_data.get(field_name)
        if not isinstance(field_value, str) or not field_value.strip():
            field_error = f"{field_name}={field_value!r}"
            invalid_fields.append(field_error)

    if invalid_fields:
        all_fields_errors = "| ".join(invalid_fields)
        error_log = (f"{ErrorMessages.INVALID_STR_FIELD}: "
                     f"fields errors: {all_fields_errors}")
        raise ValueError(error_log)
    return True
