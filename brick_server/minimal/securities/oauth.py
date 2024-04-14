from httpx_oauth.clients.google import GoogleOAuth2

from brick_server.minimal.config.manager import settings

oauth_google_client = GoogleOAuth2(
    client_id=settings.OAUTH_GOOGLE_CLIENT_ID,
    client_secret=settings.OAUTH_GOOGLE_CLIENT_SECRET,
)
