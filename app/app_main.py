from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.api_v1_fastapi.router import fast_api_router
from app.constants.constants import ErrorMessages


def _validation_param(error: dict[str, Any]) -> str:
    location = list(error.get("loc", ()))
    if location == ["body"]:
        return "request"
    if location and location[0] in {"body", "query", "path"}:
        return str(location[-1])
    return str(location[-1]) if location else "request"


def _validation_value(error: dict[str, Any]) -> Any:
    value = error.get("input")
    if isinstance(value, dict):
        return value
    return value


async def request_validation_exception_handler(
        request: Request,
        exc: RequestValidationError
) -> JSONResponse:
    detail = [
        {
            "param": _validation_param(error),
            "value": _validation_value(error),
            "message": error.get("msg", ErrorMessages.INVALID_QUERY_PARAMS),
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        content={"detail": detail})


async def integrity_error_exception_handler(
        request: Request,
        exc: IntegrityError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": [
                {
                    "param": "email",
                    "value": None,
                    "message": ErrorMessages.EMAIL_EXISTS,
                }
            ]
        })


def create_fastapi_app() -> FastAPI:
    fastapi_app = FastAPI(
        title="Tasks ToDo List API",
        version="0.1.0",
        description="Backend API service for users tasks managing")
    fastapi_app.include_router(fast_api_router)
    fastapi_app.add_exception_handler(
        exc_class_or_status_code=RequestValidationError,
        handler=request_validation_exception_handler)
    fastapi_app.add_exception_handler(
        exc_class_or_status_code=IntegrityError,
        handler=integrity_error_exception_handler)
    return fastapi_app


app = create_fastapi_app()
