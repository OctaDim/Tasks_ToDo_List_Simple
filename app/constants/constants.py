from dataclasses import dataclass

@dataclass(frozen=True)
class ErrorMessages:
    INVALID_QUERY_PARAMS: str = "Query params validation error"
    USER_NOT_FOUND: str = "UserModel not found error"
    TASK_NOT_FOUND: str = "TaskModel not found error"
    EMAIL_EXISTS: str = "Email already exists error"
    STATUS_NOT_FOUND: str = "Status not found error"