import time

import arrow
from fastapi import Form, Path, Query

# from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_rest_framework.config import settings
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse

from brick_server.minimal.auth.authorization import (
    FRONTEND_APP,
    authorized_frontend,
    create_jwt_token,
    jwt_security_scheme,
    oauth,
    parse_jwt_token,
)
from brick_server.minimal.exceptions import DoesNotExistError, NotAuthorizedError
from brick_server.minimal.models import AppToken, User, get_doc, get_docs
from brick_server.minimal.schemas import IsSuccess, TokenResponse, TokensResponse

auth_router = InferringRouter()
# auth_base_url = settings.hostname + "/auth"
frontend_url = settings.frontend


# @auth_router.get('/jwt_pubkey',
#                  status_code=200,
#                  description='Get the current JWT Public Key',
#                  tags=['Auth'],
#                  )
# def get_jwt_pubkey():
#     return PlainTextResponse(_jwt_pub_key, media_type='text/plain')


@auth_router.get(
    "/login",
    tags=["Auth"],
)
async def get_login_via_google(request: Request):
    redirect_uri = request.url_for("get_is_registered")
    print(redirect_uri)
    return {"redirect_uri": redirect_uri}
    # res = await oauth.google.authorize_redirect(request, redirect_uri)
    # return res


@auth_router.get(
    "/is_registered",
    status_code=302,
    response_class=RedirectResponse,
    tags=["Auth"],
)
async def get_is_registered(request: Request):
    token = await oauth.google.authorize_access_token(request)
    t0 = time.time()
    user = await oauth.google.parse_id_token(request, token)
    t1 = time.time()
    print("parsing token took: {} seconds".format(t1 - t0))
    params = {
        "access_token": token["access_token"],
    }
    # resp = requests.get(oauth.google.api_base_url + '/userinfo', params=params)
    assert user["email_verified"]
    try:
        user_doc = get_doc(User, user_id=user["email"])
        redirect_uri = frontend_url + "/logged-in-success"
        app_token_str = create_jwt_token(
            user_id=user["email"],
            app_name=FRONTEND_APP,
        ).decode("utf-8")
        redirect_uri += "?app_token=" + app_token_str
        return RedirectResponse(redirect_uri)
    except DoesNotExistError:
        request.session["access_token"] = token
        profile = (await oauth.google.get("userinfo", token=token)).json()
        redirect_uri = frontend_url + "/register"
        return RedirectResponse(redirect_uri)


@auth_router.get("/logincallback")  # NOTE: Dummy function
async def get_authorize(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    request.session["id_token"] = token
    return dict(user)


@cbv(auth_router)
class AppTokenRouter(object):
    @auth_router.delete(
        "/app_tokens/{app_token}",
        status_code=200,
        tags=["Auth"],
        response_model=IsSuccess,
    )
    @authorized_frontend
    async def del_token(
        self,
        app_token: str = Path(..., description="Token to delete."),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ) -> IsSuccess:
        # user = await _get_id_token_user(request) TODO
        user_id = parse_jwt_token(token.credentials)["user_id"]
        user = get_doc(User, user_id=user_id)
        token_doc = get_doc(AppToken, user=user, token=app_token)
        token_doc.delete()
        # TODO: Register deleted token in a db to check in runtime.
        return IsSuccess()


@cbv(auth_router)
class AppTokensRouter(object):
    @auth_router.post(
        "/app_tokens",
        status_code=200,
        tags=["Auth"],
    )
    @authorized_frontend
    async def gen_token(
        self,
        app_name: str = Query(
            "", description="The name of an app the user needs to generate a token for"
        ),
        token_lifetime: int = Query(
            3600,
            description="Expiration time of the requested token in seconds.",
        ),
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ) -> TokenResponse:
        user_id = parse_jwt_token(token.credentials)["user_id"]
        app_token_str = create_jwt_token(
            token_lifetime=token_lifetime, app_name=app_name
        )
        user = get_doc(User, user_id=user_id)
        app_token = AppToken(
            user=user,
            token=app_token_str,
            name=app_name,
        )
        app_token.save()
        payload = parse_jwt_token(app_token_str)
        return TokenResponse(token=app_token_str, exp=payload["exp"], name=app_name)

    @auth_router.get(
        "/app_tokens",
        status_code=200,
        tags=["Auth"],
        response_model=TokensResponse,
    )
    @authorized_frontend
    async def get_tokens(
        self,
        token: HTTPAuthorizationCredentials = jwt_security_scheme,
    ) -> TokensResponse:
        # user = await _get_id_token_user(request) TODO
        user_id = parse_jwt_token(token.credentials)["user_id"]
        user = get_doc(User, user_id=user_id)

        app_tokens = []
        for app_token in get_docs(AppToken, user=user):
            try:
                payload = parse_jwt_token(app_token.token)
                app_tokens.append(
                    TokenResponse(
                        token=app_token.token,
                        name=app_token.name,
                        exp=payload["exp"],
                    )
                )
            except NotAuthorizedError as e:
                if e.detail == "The token has been expired":
                    app_token.delete()
                else:
                    raise e
        return app_tokens


@auth_router.get(
    "/register",
    status_code=302,
    response_class=RedirectResponse,
    tags=["Auth"],
)
async def post_register_user(
    request: Request,
    is_admin: bool = Form(
        False, description="Designate if the user is going to be an admin or not."
    ),
):
    # TODO: Check if is_admin is allowed somwehow. (Maybe endorsed by the first admin or check the number of admins in the database and allow only one.
    token = request.session["access_token"]
    oauth_user = await oauth.google.parse_id_token(request, token)
    profile = (await oauth.google.get("userinfo", token=token)).json()

    if is_admin:
        assert (
            User.objects.count(is_admin=True) == 0
        ), "There is already an existnig admin, and Brick Server currently allows only on eadmin"
        is_approved = True
    else:
        is_approved = False
    new_user = User(
        name=profile["name"],
        user_id=oauth_user["email"],
        email=oauth_user["email"],
        is_admin=is_admin,
        is_approved=False,
        registration_time=arrow.get().datetime,
    )
    new_user.save()
    app_token_str = create_jwt_token(
        user_id=profile["email"],
        app_name=FRONTEND_APP,
    ).decode("utf-8")
    redirect_uri = frontend_url + "/logged-in-success?app_token=" + app_token_str
    return RedirectResponse(redirect_uri)
