from fastapi import APIRouter, Depends, Request
from fastapi_users import BaseUserManager, models as fastapi_users_models

from brick_server.minimal import schemas
from brick_server.minimal.securities.auth import fastapi_users, get_user_manager

router = APIRouter(prefix="/users", tags=["users"])

# router.include_router(
#     fastapi_users.get_users_router(schemas.UserRead, schemas.UserUpdate),
# )

# TODO: add requires_verification to config
requires_verification = False

get_current_active_user = fastapi_users.authenticator.current_user(
    active=True, verified=requires_verification
)
get_current_superuser = fastapi_users.authenticator.current_user(
    active=True, verified=requires_verification, superuser=True
)
user_schema = schemas.UserRead
user_update_schema = schemas.UserUpdate


async def get_user_dependency(
    user: str,
    user_manager: BaseUserManager[
        fastapi_users_models.UP, fastapi_users_models.ID
    ] = Depends(get_user_manager),
) -> fastapi_users_models.UP:
    parsed_id = user_manager.parse_id(user)
    return await user_manager.get(parsed_id)


@router.get(
    path="/me",
    name="users:current_user",
)
async def me(
    user: fastapi_users_models.UP = Depends(get_current_active_user),
) -> schemas.StandardResponse[user_schema]:
    return user_schema.model_validate(user).to_response()


# @router.patch(
#     path="/me",
#     name="users:patch_current_user",
# )
# async def update_me(
#     request: Request,
#     user_update: user_update_schema,  # type: ignore
#     user: fastapi_users_models.UP = Depends(get_current_active_user),
#     user_manager: BaseUserManager[fastapi_users_models.UP, fastapi_users_models.ID] = Depends(get_user_manager),
# ) -> schemas.StandardResponse[user_schema]:
#     try:
#         user = await user_manager.update(user_update, user, safe=True, request=request)
#         return user_schema.model_validate(user).to_response()
#     except fastapi_users_exceptions.UserAlreadyExists:
#         raise BizError(ErrorCode.UserEmailAlreadyExistsError)


@router.get(
    "/{user}",
    name="users:user",
    dependencies=[Depends(get_current_superuser)],
)
async def get_user(
    user=Depends(get_user_dependency),
) -> schemas.StandardResponse[user_schema]:
    return user_schema.model_validate(user).to_response()


# @router.patch(
#     "/{user}",
#     name="users:patch_user",
#     dependencies=[Depends(get_current_superuser)],
# )
# async def update_user(
#     user_update: user_update_schema,  # type: ignore
#     request: Request,
#     user=Depends(get_user_dependency),
#     user_manager: BaseUserManager[fastapi_users_models.UP, fastapi_users_models.ID] = Depends(get_user_manager),
# ) -> schemas.StandardResponse[user_schema]:
#     try:
#         user = await user_manager.update(user_update, user, safe=False, request=request)
#         return user_schema.model_validate(user).to_response()
#     except fastapi_users_exceptions.UserAlreadyExists:
#         raise BizError(ErrorCode.UserEmailAlreadyExistsError)


@router.delete(
    "/{user}",
    name="users:delete_user",
    dependencies=[Depends(get_current_superuser)],
)
async def delete_user(
    request: Request,
    user=Depends(get_user_dependency),
    user_manager: BaseUserManager[
        fastapi_users_models.UP, fastapi_users_models.ID
    ] = Depends(get_user_manager),
) -> schemas.StandardResponse[schemas.Empty]:
    await user_manager.delete(user, request=request)
    return schemas.StandardResponse()
