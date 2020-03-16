from fastapi import HTTPException


class BrickServerError(Exception):
    def __init__(self, *args, **kwargs):
        super(BrickServerError, self).__init__(*args, **kwargs)


class DoesNotExistError(BrickServerError):
    def __init__(self, klass, name, *args, **kwargs):
        self.klass = klass
        self.name = name
        super(DoesNotExistError, self).__init__(*args, **kwargs)

    def __str__(self):
        return repr('{0} of {1} does not exist'.format(self.name, self.klass))

class MultipleObjectsFoundError(BrickServerError):
    def __init__(self, klass, name, *args, **kwargs):
        self.klass = klass
        self.name = name
        super(MultipleObjectsFoundError, self).__init__(*args, **kwargs)

    def __str__(self):
        return repr('There are multiple isntances of {0} of {1}'.format(self.name, self.klass))

class UserNotApprovedError(BrickServerError, HTTPException):
    def __init__(self, *args, **kwargs):
        super(UserNotApprovedError, self).__init__(*args, **kwargs)

class NotAuthorizedError(BrickServerError, HTTPException):
    def __init__(self, *args, **kwargs):
        super(NotAuthorizedError, self).__init__(status_code=401, *args, **kwargs)

