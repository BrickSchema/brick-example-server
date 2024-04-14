from fastapi import APIRouter, Depends, Request
from fastapi_users import (
    BaseUserManager,
    exceptions as fastapi_users_exceptions,
    models as fastapi_users_models,
)

from brick_server.minimal import schemas
from brick_server.minimal.config.manager import settings
from brick_server.minimal.securities.auth import (
    bearer_auth_backend,
    cookie_auth_backend,
    fastapi_users,
    get_user_manager,
)
from brick_server.minimal.securities.oauth import oauth_google_client
from brick_server.minimal.utilities.exceptions import BizError, ErrorCode

router = APIRouter(prefix="/auth", tags=["auth"])

user_schema = schemas.UserRead
user_create_schema = schemas.UserCreate

# generate /login and /logout routes for cookie authentication backend
router.include_router(
    fastapi_users.get_auth_router(cookie_auth_backend),
    prefix="/cookie",
)

# generate /login and /logout routes for jwt authentication backend
router.include_router(
    fastapi_users.get_auth_router(bearer_auth_backend),
    prefix="/bearer",
)


# generate a /register route to allow a user to create a new account
# router.include_router(
#     fastapi_users.get_register_router(schemas.UserRead, schemas.UserCreate),
# )
@router.post(
    "/register",
    name="register:register",
)
async def register(
    request: Request,
    user_create: user_create_schema,
    user_manager: BaseUserManager[
        fastapi_users_models.UP, fastapi_users_models.ID
    ] = Depends(get_user_manager),
) -> schemas.StandardResponse[user_schema]:
    try:
        created_user = await user_manager.create(
            user_create, safe=True, request=request
        )
    except fastapi_users_exceptions.UserAlreadyExists:
        raise BizError(ErrorCode.UserAlreadyExistsError)
    except fastapi_users_exceptions.InvalidPasswordException as e:
        raise BizError(ErrorCode.UserInvalidPasswordError, e.reason)

    return user_schema.model_validate(created_user).to_response()


# generate a /verify route to manage user email verification
router.include_router(
    fastapi_users.get_verify_router(schemas.UserRead),
)

# generate /forgot-password (the user asks for a token to reset its password) and
# /reset-password (the user changes its password given the token) routes
router.include_router(
    fastapi_users.get_reset_password_router(),
)

for auth_type, auth_backend in (
    ("cookie", cookie_auth_backend),
    ("bearer", bearer_auth_backend),
):
    router.include_router(
        fastapi_users.get_oauth_router(
            oauth_google_client,
            auth_backend,
            settings.JWT_SECRET_KEY,
            associate_by_email=True,
            is_verified_by_default=True,
        ),
        prefix=f"/{auth_type}/google",
    )
