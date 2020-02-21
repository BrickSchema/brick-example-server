import json
import pdb
import os
from starlette.config import Config
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth

os.environ['GOOGLE_CLIENT_ID'] = "266865174382-0k4cp0k0ue2mplrfb0q24trh5st43ciu.apps.googleusercontent.com"
os.environ['GOOGLE_CLIENT_SECRET'] = "ZCCoXWGFhYahHqnJN0OteoGE"

app = Starlette(debug=True)
app.add_middleware(SessionMiddleware, secret_key="!secret")

config = Config('.env')
oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email'
    }
)


@app.route('/')
async def homepage(request):
    user = request.session.get('user')
    if user:
        secret = os.urandom(24)
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/logout">logout</a>'
            f'<a>{secret}</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')


@app.route('/login')
async def login(request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.route('/auth')
async def auth(request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@app.route('/logout')
async def logout(request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app,
                host='0.0.0.0',
                port=8000,
                ssl_keyfile='configs/key.pem',
                ssl_certfile='configs/cert.pem',
                )
