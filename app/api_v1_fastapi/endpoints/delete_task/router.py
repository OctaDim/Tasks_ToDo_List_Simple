from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api_v1_fastapi.endpoints.delete_task.out_schema import (
    OutDeleteTask)
from app.constants.constants import ErrorMessages
from app.db_postgres.session import get_async_session
from app.repositories_utils.tasks_utils import delete_task_by_id
from app.schemas_common.errors import OutErrorResponse

delete_task_router = APIRouter(tags=["all_endpoints", "tasks"])


@delete_task_router.delete(
    path="tasks/{task_id}",
    response_model=OutDeleteTask,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": OutErrorResponse,
            "description": ErrorMessages.TASK_NOT_FOUND},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": OutErrorResponse,
            "description": ErrorMessages.INVALID_QUERY_PARAMS}, }, )
async def delete_task_endpoint(
        task_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> OutDeleteTask:
    task_deleted = await delete_task_by_id(session=session,
                                           task_id=task_id)
    if not task_deleted:
        error_log = (f"{ErrorMessages.TASK_NOT_FOUND}: "
                     f"task id: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=error_log)
    validated_resp_inst = OutDeleteTask(ok=True)
    return validated_resp_inst
