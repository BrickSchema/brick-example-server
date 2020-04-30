
from typing import Callable

from ..auth.authorization import _get_jwt_token_user

class BaseResource(object):
    get_user: Callable = Depends(_get_jwt_token_user)
