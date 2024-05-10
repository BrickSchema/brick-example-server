from bson import ObjectId
from fastapi import APIRouter, Body, Depends, Request
from fastapi_users import (
    BaseUserManager,
    exceptions as fastapi_users_exceptions,
    models as fastapi_users_models,
)

from brick_server.minimal import models, schemas
from brick_server.minimal.securities.auth import get_token_user, get_user_manager
from brick_server.minimal.securities.checker import PermissionChecker
from brick_server.minimal.utilities.dependencies import get_path_user
from brick_server.minimal.utilities.exceptions import BizError, ErrorCode

router = APIRouter(prefix="/users", tags=["users"])

# router.include_router(
#     fastapi_users.get_users_router(schemas.UserRead, schemas.UserUpdate),
# )

# requires_verification = False
# get_current_active_user = fastapi_users.authenticator.current_user(
#     active=True, verified=requires_verification
# )
# get_current_superuser = fastapi_users.authenticator.current_user(
#     active=True, verified=requires_verification, superuser=True
# )
# user_schema = schemas.UserRead
# user_update_schema = schemas.UserUpdate


# async def get_user_dependency(
#     user: str,
#     user_manager: BaseUserManager[
#         fastapi_users_models.UP, fastapi_users_models.ID
#     ] = Depends(get_user_manager),
# ) -> fastapi_users_models.UP:
#     parsed_id = user_manager.parse_id(user)
#     return await user_manager.get(parsed_id)


@router.get(
    path="/me",
    name="users:current_user",
)
async def me(
    user: models.User = Depends(get_token_user),
) -> schemas.StandardResponse[schemas.UserRead]:
    return schemas.UserRead.model_validate(user).to_response()


@router.patch(
    path="/me",
    name="users:patch_current_user",
    dependencies=[
        Depends(
            PermissionChecker(
                permission_scope=schemas.PermissionScope.USER,
            )
        ),
    ],
)
async def update_me(
    request: Request,
    user_update: schemas.UserUpdate = Body(...),
    user: models.User = Depends(get_token_user),
    user_manager: BaseUserManager[
        fastapi_users_models.UP, fastapi_users_models.ID
    ] = Depends(get_user_manager),
) -> schemas.StandardResponse[schemas.UserRead]:
    if user_update.email is not None:
        raise BizError(ErrorCode.UserNotUpdatableError, "email can not be updated")
    if user_update.name is not None and ObjectId.is_valid(user_update.name):
        raise BizError(ErrorCode.UserNotUpdatableError, "name can not be an ObjectId")
    try:
        user = await user_manager.update(user_update, user, safe=True, request=request)
        return schemas.UserRead.model_validate(user).to_response()
    except fastapi_users_exceptions.UserAlreadyExists:
        raise BizError(ErrorCode.UserEmailAlreadyExistsError)


@router.get(
    "/{user}",
    name="users:user",
    dependencies=[
        Depends(
            PermissionChecker(
                permission_scope=schemas.PermissionScope.USER,
            )
        ),
    ],
)
async def get_user(
    user: models.User = Depends(get_path_user),
) -> schemas.StandardResponse[schemas.UserRead]:
    return schemas.UserRead.model_validate(user).to_response()


@router.patch(
    "/{user}",
    name="users:patch_user",
    dependencies=[
        Depends(
            PermissionChecker(
                permission_scope=schemas.PermissionScope.SITE,
            )
        ),
    ],
)
async def update_user(
    request: Request,
    user_update: schemas.UserUpdate = Body(),
    user: models.User = Depends(get_path_user),
    user_manager: BaseUserManager[
        fastapi_users_models.UP, fastapi_users_models.ID
    ] = Depends(get_user_manager),
) -> schemas.StandardResponse[schemas.UserRead]:
    try:
        user = await user_manager.update(user_update, user, safe=False, request=request)
        return schemas.UserRead.model_validate(user).to_response()
    except fastapi_users_exceptions.UserAlreadyExists:
        raise BizError(ErrorCode.UserEmailAlreadyExistsError)


@router.delete(
    "/{user}",
    name="users:delete_user",
    dependencies=[
        Depends(
            PermissionChecker(
                permission_scope=schemas.PermissionScope.SITE,
            )
        ),
    ],
)
async def delete_user(
    request: Request,
    user: models.User = Depends(get_path_user),
    user_manager: BaseUserManager[
        fastapi_users_models.UP, fastapi_users_models.ID
    ] = Depends(get_user_manager),
) -> schemas.StandardResponse[schemas.Empty]:
    await user_manager.delete(user, request=request)
    return schemas.StandardResponse()


@router.get(
    "/",
    name="users:list_users",
    dependencies=[
        Depends(
            PermissionChecker(
                permission_scope=schemas.PermissionScope.DOMAIN,
            )
        ),
    ],
)
async def list_users() -> schemas.StandardListResponse[schemas.UserRead]:
    users = await models.User.find_all().to_list()
    return schemas.StandardListResponse(
        [schemas.UserRead.model_validate(user.dict()) for user in users]
    )
