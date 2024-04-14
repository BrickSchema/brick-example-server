from beanie import Document
from fastapi_users.db import BeanieBaseUser
from pydantic import Field

from brick_server.minimal.schemas.oauth_account import OAuthAccount


class User(BeanieBaseUser, Document):
    # name: str
    # user_id: str
    oauth_accounts: list[OAuthAccount] = Field(default_factory=list)

    # class Settings(BeanieBaseUser.Settings):
    #     user_id_collation = Collation("en", strength=2)
    #     indexes = [
    #         IndexModel("user_id", unique=True),
    #         IndexModel("user_id", name="case_insensitive_user_id_index", collation=user_id_collation),
    #     ]
