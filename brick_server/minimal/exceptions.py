from fastapi import HTTPException


class BrickServerError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DoesNotExistError(BrickServerError, HTTPException):
    def __init__(self, klass, name, *args, **kwargs):
        if "detail" not in kwargs:
            kwargs["detail"] = f"{name} of {klass} does not exist."
        super().__init__(status_code=404, *args, **kwargs)


class AlreadyExistsError(BrickServerError, HTTPException):
    def __init__(self, klass, name, *args, **kwargs):
        if "detail" not in kwargs:
            kwargs["detail"] = f"{name} of {klass} already exists."
        super().__init__(status_code=409, *args, **kwargs)


class MultipleObjectsFoundError(BrickServerError, HTTPException):
    def __init__(self, klass, name, *args, **kwargs):
        kwargs["detail"] = "There are multiple isntances of {} of {}".format(
            name, klass
        )
        super().__init__(status_code=400, *args, **kwargs)

    def __str__(self):
        return repr(
            "There are multiple isntances of {} of {}".format(self.name, self.klass)
        )


class UserNotApprovedError(BrickServerError, HTTPException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NotAuthorizedError(BrickServerError, HTTPException):
    def __init__(self, **kwargs):
        super().__init__(status_code=401, **kwargs)


class InternalServerError(BrickServerError, HTTPException):
    def __init__(self, **kwargs):
        super().__init__(
            status_code=500, detail="Internal server error, please contact site admin."
        )


class TokenSignatureInvalid(NotAuthorizedError):
    def __init__(self, *args, **kwargs):
        if "detail" not in kwargs:
            kwargs["detail"] = "The token signature is invalid."
        super().__init__(*args, **kwargs)


class TokenSignatureExpired(NotAuthorizedError):
    def __init__(self, *args, **kwargs):
        if "detail" not in kwargs:
            kwargs["detail"] = "The token signature has expired."
        super().__init__(*args, **kwargs)


class GraphDBError(BrickServerError, HTTPException):
    def __init__(self, *args, **kwargs):
        if "detail" not in kwargs:
            kwargs["detail"] = "GraphDB query failed."
        super().__init__(*args, **kwargs)
