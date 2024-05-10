from beanie import Document
from fastapi_users.db import BeanieBaseUser
from pydantic import Field
from pymongo import IndexModel
from pymongo.collation import Collation

from brick_server.minimal.schemas.oauth_account import OAuthAccount


class User(BeanieBaseUser, Document):
    name: str
    oauth_accounts: list[OAuthAccount] = Field(default_factory=list)

    class Settings(BeanieBaseUser.Settings):
        name = "users"
        name_collation = Collation("en", strength=2)
        indexes = [
            IndexModel("name", unique=True),
            IndexModel(
                "name", name="case_insensitive_name_index", collation=name_collation
            ),
        ]
