import time

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer
from fastapi_rest_framework.config import settings

from ..exceptions import NotAuthorizedError

auth_scheme = HTTPBearer(bearerFormat="JWT")


def create_jwt_token(
    user_id: str = "admin",
    app_name: str = None,
    domain: str = None,
    token_lifetime: int = settings.jwt_expire_seconds,
):
    payload = {
        "user_id": user_id,
        "exp": time.time() + token_lifetime,
        "app_name": app_name,
        "domain": domain,
    }
    jwt_token = jwt.encode(
        payload, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    return jwt_token


def parse_jwt_token(jwt_token):
    try:
        payload = jwt.decode(
            jwt_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.exceptions.InvalidSignatureError as e:
        raise NotAuthorizedError(detail="The token's signature is invalid.")
    except jwt.exceptions.ExpiredSignatureError as e:
        raise NotAuthorizedError(detail="The token has been expired")
    except Exception as e:
        raise HTTPException(status_code=400, detail="The token is invalid")
    return payload


# A list of auth_logics


# def auth_logic_template(action_type, target_ids, *args, **kwargs):
#     raise Exception(
#         "Not Implemented and this is not meant to be used but just for reference."
#     )

jwt_security_scheme = Security(auth_scheme)
