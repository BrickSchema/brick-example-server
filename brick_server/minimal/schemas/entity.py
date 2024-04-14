from copy import deepcopy

from pydantic import conlist

from brick_server.minimal.schemas.base import BaseModel

TupleModel = conlist(str, min_length=2, max_length=2)
Relationship = deepcopy(TupleModel)


class EntityRead(BaseModel):
    relationships: list[Relationship] = []
    types: list[str]
    entity_id: str
    name: str = ""
