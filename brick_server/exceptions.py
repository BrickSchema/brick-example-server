from fastapi import HTTPException


class BrickServerError(Exception):
    def __init__(self, *args, **kwargs):
        super(BrickServerError, self).__init__(*args, **kwargs)


class DoesNotExistError(BrickServerError, HTTPException):
    def __init__(self, klass, name, *args, **kwargs):
        if 'detail' not in kwargs:
            kwargs['detail'] = f'{name} of {klass} does not exist.'
        super(DoesNotExistError, self).__init__(status_code=404, *args, **kwargs)

class AlreadyExistsError(BrickServerError, HTTPException):
    def __init__(self, klass, name, *args, **kwargs):
        if 'detail' not in kwargs:
            kwargs['detail'] = f'{name} of {klass} already exists.'
        super(AlreadyExistsError, self).__init__(status_code=409, *args, **kwargs)

class MultipleObjectsFoundError(BrickServerError, HTTPException):
    def __init__(self, klass, name, *args, **kwargs):
        kwargs['detail'] = 'There are multiple isntances of {0} of {1}'.format(name, klass)
        super(MultipleObjectsFoundError, self).__init__(status_code=400, *args, **kwargs)

    def __str__(self):
        return repr('There are multiple isntances of {0} of {1}'.format(self.name, self.klass))

class UserNotApprovedError(BrickServerError, HTTPException):
    def __init__(self, *args, **kwargs):
        super(UserNotApprovedError, self).__init__(*args, **kwargs)

class NotAuthorizedError(BrickServerError, HTTPException):
    def __init__(self, *args, **kwargs):
        super(NotAuthorizedError, self).__init__(status_code=401, *args, **kwargs)

class TokenSignatureInvalid(NotAuthorizedError):
    def __init__(self, *args, **kwargs):
        if 'detail' not in kwargs:
            kwargs['detail'] = 'The token signature is invalid.'
        super(TokenSignatureInvalid, self).__init__(*args, **kwargs)

class TokenSignatureExpired(NotAuthorizedError):
    def __init__(self, *args, **kwargs):
        if 'detail' not in kwargs:
            kwargs['detail'] = 'The token signature has expired.'
        super(TokenSignatureExpired, self).__init__(*args, **kwargs)


