from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.constants.constants import ErrorMessages
from app.api_v1_fastapi.endpoints.create_task.in_schema import InCreateTask
from app.api_v1_fastapi.endpoints.create_task.out_schema import OutCreateTask
from app.db_postgres.session import get_async_session
from app.repositories_utils.tasks_utils import create_task_by_user
from app.repositories_utils.users_utils import get_user_by_id
from app.schemas_common.errors import OutErrorResponse

create_task_router = APIRouter(tags=["all_endpoints", "tasks"])


@create_task_router.post(
    path="/users/{user_id}/tasks",
    response_model=OutCreateTask,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": OutErrorResponse,
            "description": ErrorMessages.USER_NOT_FOUND},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": OutErrorResponse,
            "description": ErrorMessages.INVALID_QUERY_PARAMS}, }, )
async def create_task_endpoint(
        user_id: int,
        create_task_data: InCreateTask,
        session: AsyncSession = Depends(get_async_session),
) -> OutCreateTask:
    user_obj = await get_user_by_id(session=session, user_id=user_id)

    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=ErrorMessages.USER_NOT_FOUND)

    task_obj = await create_task_by_user(
        session=session,
        user=user_obj,
        title=create_task_data.title.strip(),
        description=create_task_data.description)

    validated_inst = OutCreateTask.model_validate(task_obj)
    return validated_inst
