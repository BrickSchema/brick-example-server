from beanie import PydanticObjectId
from fastapi_users import schemas

from brick_server.minimal.schemas.base import BaseModel


class UserRead(schemas.BaseUser[PydanticObjectId], BaseModel):
    ...
    # name: str
    # user_id: str


class UserCreate(schemas.BaseUserCreate, BaseModel):
    ...
    # name: str
    # user_id: str


class UserUpdate(schemas.BaseUserUpdate, BaseModel):
    ...
    # name: Optional[str] = None
