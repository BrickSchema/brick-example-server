from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi_users import exceptions as fastapi_users_exceptions
from loguru import logger
from pydantic import ValidationError

from brick_server.minimal.utilities.exceptions import BizError, ErrorCode, ErrorShowType


def business_error_response(exc: BizError) -> JSONResponse:
    return JSONResponse(
        jsonable_encoder(
            {
                "errorCode": exc.error_code,
                "errorMessage": exc.error_message,
                "showType": exc.show_type,
                "data": {},
            }
        ),
        status_code=status.HTTP_200_OK,
    )


def fastapi_users_error_handler(
    request: Request, exc: fastapi_users_exceptions.FastAPIUsersException
) -> JSONResponse:
    try:
        raise exc
    except (fastapi_users_exceptions.UserNotExists, fastapi_users_exceptions.InvalidID):
        return business_error_response(
            BizError(ErrorCode.UserNotFoundError, show_type=ErrorShowType.ErrorMessage)
        )
    except fastapi_users_exceptions.UserAlreadyExists:
        return business_error_response(
            BizError(
                ErrorCode.UserAlreadyExistsError, show_type=ErrorShowType.ErrorMessage
            )
        )
    except fastapi_users_exceptions.InvalidPasswordException as e:
        return business_error_response(
            BizError(
                ErrorCode.UserInvalidPasswordError, e.reason, ErrorShowType.ErrorMessage
            )
        )
    except (
        fastapi_users_exceptions.InvalidVerifyToken,
        fastapi_users_exceptions.InvalidResetPasswordToken,
    ):
        return business_error_response(
            BizError(
                ErrorCode.InvalidTokenError,
                exc.__class__.__name__,
                ErrorShowType.ErrorMessage,
            )
        )
    except fastapi_users_exceptions.UserAlreadyVerified:
        return business_error_response(
            BizError(
                ErrorCode.UserAlreadyVerifiedError, show_type=ErrorShowType.WarnMessage
            )
        )
    except fastapi_users_exceptions.UserInactive:
        return business_error_response(
            BizError(ErrorCode.UserInactiveError, show_type=ErrorShowType.WarnMessage)
        )
    except fastapi_users_exceptions.FastAPIUsersException:
        return business_error_response(
            BizError(
                ErrorCode.InternalServerError,
                exc.__class__.__name__,
                ErrorShowType.ErrorMessage,
            )
        )


def business_error_handler(request: Request, exc: BizError) -> JSONResponse:
    return business_error_response(exc)


def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    logger.exception(exc)
    return business_error_response(
        BizError(
            ErrorCode.ValidationError, str(exc.errors()), ErrorShowType.ErrorMessage
        )
    )


def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return business_error_response(
            BizError(
                ErrorCode.UnauthorizedError, exc.detail, ErrorShowType.ErrorMessage
            )
        )
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        return business_error_response(
            BizError(ErrorCode.PermissionError, exc.detail, ErrorShowType.ErrorMessage)
        )
    else:
        return business_error_response(
            BizError(
                ErrorCode.InternalServerError, exc.detail, ErrorShowType.ErrorMessage
            )
        )


async def catch_exceptions_middleware(request: Request, call_next: Any) -> JSONResponse:
    try:
        return await call_next(request)
    except Exception as e:
        logger.exception(f"Unexpected Error: {e.__class__.__name__}")
        return business_error_response(
            BizError(
                ErrorCode.InternalServerError,
                e.__class__.__name__,
                ErrorShowType.ErrorMessage,
            )
        )


def register_error_handlers(backend_app: FastAPI) -> None:
    backend_app.add_exception_handler(
        fastapi_users_exceptions.FastAPIUsersException, fastapi_users_error_handler
    )
    backend_app.add_exception_handler(BizError, business_error_handler)
    backend_app.add_exception_handler(ValidationError, validation_error_handler)
    backend_app.add_exception_handler(HTTPException, http_error_handler)
    backend_app.middleware("http")(catch_exceptions_middleware)
