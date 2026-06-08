from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api_v1_fastapi.endpoints.get_user.out_schema import OutGetUser
from app.constants.constants import ErrorMessages
from app.db_postgres.session import get_async_session
from app.repositories_utils.users_utils import get_user_by_id
from app.schemas_common.errors import OutErrorResponse

get_user_router = APIRouter(tags=["all_endpoints", "users"])


@get_user_router.get(
    path="/users/{user_id}",
    response_model=OutGetUser,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": OutErrorResponse,
            "description": ErrorMessages.USER_NOT_FOUND},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": OutErrorResponse,
            "description": ErrorMessages.INVALID_QUERY_PARAMS}, }, )
async def get_user_endpoint(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> OutGetUser:
    user_obj = await get_user_by_id(session=session, user_id=user_id)
    if not user_obj:
        error_log = (f"{ErrorMessages.USER_NOT_FOUND}: "
                     f"user_id: {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=error_log)

    validated_resp_inst = OutGetUser.model_validate(user_obj)
    return validated_resp_inst
