from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api_v1_fastapi.endpoints.update_task_status.in_schema import (
    InUpdateTaskStatus)
from app.api_v1_fastapi.endpoints.update_task_status.out_schema import (
    OutUpdateTaskStatus)
from app.constants.constants import ErrorMessages
from app.db_postgres.session import get_async_session
from app.models_sqlalchemy.task_model import TaskStatusEnum
from app.repositories_utils.tasks_utils import (
    get_task_by_id, update_task_status)
from app.schemas_common.errors import OutErrorResponse

update_task_status_router = APIRouter(tags=["all_endpoints", "tasks"])


@update_task_status_router.patch(
    path="/tasks/{task_id}/status",
    response_model=OutUpdateTaskStatus,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": OutErrorResponse,
            "description": ErrorMessages.TASK_NOT_FOUND},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": OutErrorResponse,
            "description": ErrorMessages.INVALID_QUERY_PARAMS}, }, )
async def update_task_status_endpoint(
        task_id: int,
        update_task_data: InUpdateTaskStatus,
        session: AsyncSession = Depends(get_async_session),
) -> OutUpdateTaskStatus:
    status_upd_value = update_task_data.status
    if not TaskStatusEnum.has_value(status_upd_value):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail=ErrorMessages.STATUS_NOT_FOUND)

    task_obj = await get_task_by_id(session=session, task_id=task_id)

    if not task_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=ErrorMessages.TASK_NOT_FOUND)

    updated_task_obj = await update_task_status(
        session=session,
        task_obj=task_obj,
        task_status=update_task_data.status)

    validated_inst = OutUpdateTaskStatus.model_validate(updated_task_obj)
    return validated_inst
