from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api_v1_fastapi.endpoints.list_user_tasks.in_schema import (
    InListUserTasksQuery)
from app.api_v1_fastapi.endpoints.list_user_tasks.out_schema import (
    OutUserTasksList, OutUserTask)
from app.constants.constants import ErrorMessages
from app.db_postgres.session import get_async_session
from app.repositories_utils.tasks_utils import list_tasks_by_user
from app.repositories_utils.users_utils import get_user_by_id
from app.schemas_common.errors import OutErrorResponse

list_user_tasks_router = APIRouter(tags=["all_endpoints", "users"])


@list_user_tasks_router.get(
    path="/users/{user_id}/tasks",
    response_model=OutUserTasksList,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": OutErrorResponse,
            "description": ErrorMessages.USER_NOT_FOUND},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": OutErrorResponse,
            "description": ErrorMessages.INVALID_QUERY_PARAMS}, }, )
async def list_user_tasks_endpoint(
        user_id: int,
        query_params: Annotated[InListUserTasksQuery, Query()],
        session: AsyncSession = Depends(get_async_session),
) -> OutUserTasksList:
    user_obj = await get_user_by_id(session=session, user_id=user_id)

    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=ErrorMessages.USER_NOT_FOUND)

    tasks_objs = await list_tasks_by_user(session=session,
                                          user_id=user_id,
                                          status=query_params.status,
                                          limit=query_params.limit,
                                          offset=query_params.offset)

    validated_tasks = [OutUserTask.model_validate(tsk) for tsk in tasks_objs]
    validated_resp_inst = OutUserTasksList(tasks=validated_tasks)
    return validated_resp_inst
