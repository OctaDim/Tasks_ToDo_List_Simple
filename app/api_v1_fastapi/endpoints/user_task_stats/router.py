from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api_v1_fastapi.endpoints.user_task_stats.out_schema import (
    OutUserTaskStats)
from app.constants.constants import ErrorMessages
from app.db_postgres.session import get_async_session
from app.repositories_utils.tasks_utils import get_user_tasks_stats
from app.repositories_utils.users_utils import get_user_by_id
from app.schemas_common.errors import OutErrorResponse

user_task_stats_router = APIRouter(tags=["all_endpoints", "tasks"])


@user_task_stats_router.get(
    path="/users/{user_id}/tasks/stats",
    response_model=OutUserTaskStats,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": OutErrorResponse,
            "description": ErrorMessages.USER_NOT_FOUND},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": OutErrorResponse,
            "description": ErrorMessages.INVALID_QUERY_PARAMS}, }, )
async def user_task_stats_endpoint(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> OutUserTaskStats:
    user_obj = await get_user_by_id(session=session, user_id=user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=ErrorMessages.USER_NOT_FOUND)

    statuses_result = await get_user_tasks_stats(session=session,
                                                 user_id=user_id)
    validated_resp_inst = OutUserTaskStats(**statuses_result)
    return validated_resp_inst
