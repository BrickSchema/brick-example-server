from typing import Callable, Optional, Set

import jwt
from beanie import PydanticObjectId
from fastapi import Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi_users import BaseUserManager, FastAPIUsers, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
    Strategy,
)
from fastapi_users.authentication.authenticator import (
    name_to_strategy_variable_name,
    name_to_variable_name,
)
from fastapi_users.jwt import decode_jwt, generate_jwt
from fastapi_users_db_beanie import BeanieUserDatabase, ObjectIDIDMixin
from loguru import logger
from makefun import with_signature

from brick_server.minimal.config.manager import settings
from brick_server.minimal.models.user import User
from brick_server.minimal.schemas.oauth_account import OAuthAccount
from brick_server.minimal.schemas.permission import PermissionScope, PermissionType
from brick_server.minimal.utilities.exceptions import BizError, ErrorCode


class RedirectCookieTransport(CookieTransport):
    async def get_login_response(self, token: str) -> Response:
        response = RedirectResponse(
            settings.FRONTEND_URL, status_code=status.HTTP_303_SEE_OTHER
        )
        return self._set_login_cookie(response, token)


cookie_transport = RedirectCookieTransport(
    cookie_secure=not settings.DEBUG, cookie_max_age=settings.JWT_EXPIRE_SECONDS
)
bearer_transport = BearerTransport(tokenUrl="/brickapi/v1/auth/bearer/login")


class MyJWTStrategy(JWTStrategy):
    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[dict]:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
            )
        except jwt.PyJWTError:
            return None

        return data

    async def write_token(self, user: models.UP) -> str:
        data = {
            "sub": str(user.email),
            "aud": self.token_audience,
        }
        return generate_jwt(
            data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
        )


def get_jwt_strategy() -> MyJWTStrategy:
    return MyJWTStrategy(
        secret=settings.JWT_SECRET_KEY,
        lifetime_seconds=settings.JWT_EXPIRE_SECONDS,
        token_audience=[settings.JWT_TOKEN_PREFIX],
        algorithm=settings.JWT_ALGORITHM,
    )


cookie_auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

bearer_auth_backend = AuthenticationBackend(
    name="bearer",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserDatabase(BeanieUserDatabase):
    async def get_by_user_id(self, string: str) -> Optional[User]:
        """Get a single user by user_id."""
        return await self.user_model.find_one(
            self.user_model.user_id == string,
            collation=self.user_model.Settings.user_id_collation,
        )


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = settings.JWT_SECRET_KEY
    verification_token_secret = settings.JWT_SECRET_KEY

    # async def get_by_email(self, user_email: str) -> User:
    #     self.user_db: UserDatabase
    #     user = await self.user_db.get_by_email(user_email)
    #     if user is None:
    #         user = await self.user_db.get_by_user_id(user_email)
    #     if user is None:
    #         raise exceptions.UserNotExists()
    #     return user

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.email} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.email} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(
            f"Verification requested for user {user.email}. Verification token: {token}"
        )

    async def validate_password(self, password: str, user: User) -> None:
        pass
        # if not re.match(PASSWORD_REGEX, password):
        #     raise InvalidPasswordException("Password does not meet requirements")


async def get_user_db():
    yield UserDatabase(User, OAuthAccount)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, PydanticObjectId](
    get_user_manager,
    [cookie_auth_backend, bearer_auth_backend],
)

# current_active_user = fastapi_users.current_user(active=True)
# current_user_token = fastapi_users.authenticator.current_user_token(active=True)


async def jwt_authenticate(
    *args, user_manager: BaseUserManager[models.UP, models.ID], **kwargs
) -> Optional[dict]:
    data: Optional[dict] = None
    for backend in fastapi_users.authenticator.backends:
        token = kwargs[name_to_variable_name(backend.name)]
        strategy: Strategy[models.UP, models.ID] = kwargs[
            name_to_strategy_variable_name(backend.name)
        ]
        if token is not None:
            data = await strategy.read_token(token, user_manager)
            if data:
                break
    if not data:
        raise BizError(ErrorCode.UnauthorizedError)
    return data


signature = fastapi_users.authenticator._get_dependency_signature()


@with_signature(signature)
async def get_jwt_payload(*args, **kwargs):
    return await jwt_authenticate(
        *args,
        **kwargs,
    )


async def get_token_user(
    token: Optional[dict] = Depends(get_jwt_payload),
    user_manager: UserManager = Depends(get_user_manager),
) -> User:
    try:
        user_email = token.get("sub")
        user = await user_manager.get_by_email(user_email)
        return user
    except Exception:
        raise BizError(ErrorCode.UnauthorizedError)


def default_auth_logic(
    user: User = Depends(get_token_user),
) -> Callable[[Set[str], PermissionType, PermissionScope], bool]:
    def _auth_logic(
        entity_ids: Set[str],
        permission_type: PermissionType,
        permission_scope: PermissionScope,
    ):
        logger.info(user)
        return True

    return _auth_logic
