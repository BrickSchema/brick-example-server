from typing import Optional

from beanie import PydanticObjectId

from brick_server.minimal.schemas.base import BaseModel


class DomainRead(BaseModel):
    id: PydanticObjectId
    name: str
    initialized: bool


class DomainCreate(BaseModel):
    name: str


class DomainUpdate(BaseModel):
    name: Optional[str] = None
