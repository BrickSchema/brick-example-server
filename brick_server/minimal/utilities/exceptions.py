import inspect
from enum import Enum

from loguru import logger


class ErrorShowType(Enum):
    Silent = 0
    WarnMessage = 1
    ErrorMessage = 2
    Notification = 3
    Redirect = 9


class ErrorCode(str, Enum):
    Success = "Success"
    Error = "Error"

    # General Errors
    UnauthorizedError = "UnauthorizedError"
    PermissionError = "PermissionError"
    InternalServerError = "InternalServerError"
    InvalidTokenError = "InvalidTokenError"
    UnknownFieldError = "UnknownFieldError"
    IllegalFieldError = "IllegalFieldError"
    IntegrityError = "IntegrityError"
    ValidationError = "ValidationError"
    ApiNotImplementedError = "ApiNotImplementedError"

    # User Errors
    UserManagerError = "UserManagerError"
    UserNotFoundError = "UserNotFoundError"
    UserInvalidPasswordError = "UserInvalidPasswordError"
    UserAlreadyExistsError = "UserAlreadyExistsError"
    UserEmailAlreadyExistsError = "UserEmailAlreadyExistsError"
    UserAlreadyVerifiedError = "UserAlreadyVerifiedError"
    UserInactiveError = "UserInactiveError"

    # Domain Errors
    DomainNotFoundError = "DomainNotFoundError"
    DomainAlreadyExistsError = "DomainAlreadyExistsError"

    # GraphDB Errors
    GraphDBError = "GraphDBError"

    # Actuation Errors
    ActuationDriverNotFoundError = "ActuationDriverNotFoundError"
    TimeseriesDriverNotFoundError = "TimeseriesDriverNotFoundError"


class BizError(Exception):
    def __init__(
        self,
        error_code: ErrorCode,
        error_message: str = "",
        show_type: ErrorShowType = ErrorShowType.ErrorMessage,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.show_type = show_type
        try:
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            logger.info(
                f"BizError: {calframe[1][3]} {error_code.value} {error_message}"
            )
        except Exception:
            ...
