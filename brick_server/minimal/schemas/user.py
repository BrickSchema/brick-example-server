from beanie import PydanticObjectId
from fastapi_users import schemas

from brick_server.minimal.schemas.base import BaseModel


class UserRead(schemas.BaseUser[PydanticObjectId], BaseModel):
    name: str


class UserCreate(schemas.BaseUserCreate, BaseModel):
    name: str


class UserUpdate(schemas.BaseUserUpdate, BaseModel):
    name: str | None = None
