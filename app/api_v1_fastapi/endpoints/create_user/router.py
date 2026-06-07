from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.constants.constants import ErrorMessages
from app.api_v1_fastapi.endpoints.create_user.in_schema import InCreateUser
from app.api_v1_fastapi.endpoints.create_user.out_schema import OutCreateUser
from app.db_postgres.session import get_async_session
from app.repositories_utils.users_utils import create_user
from app.schemas_common.errors import OutErrorResponse

create_user_router = APIRouter(tags=["all_endpoints", "users"])


@create_user_router.post(
    path="/users/create_user",
    response_model=OutCreateUser,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": OutErrorResponse,
            "description": ErrorMessages.EMAIL_EXISTS},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": OutErrorResponse,
            "description": ErrorMessages.INVALID_QUERY_PARAMS}, }, )
async def create_user_endpoint(
        create_user_data: InCreateUser,
        session: AsyncSession = Depends(get_async_session)
) -> OutCreateUser:
    user = await create_user(session=session,
                             email=str(create_user_data.email),
                             name=create_user_data.name.strip())

    validated_inst = OutCreateUser.model_validate(user)
    return validated_inst
