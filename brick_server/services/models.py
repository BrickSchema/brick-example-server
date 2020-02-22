from pydantic import BaseModel
from typing import List, Dict, Any
from enum import Enum

from fastapi import Security

from ..auth.authorization import auth_scheme

Relationship = List[str] ## [Predicate, Object] for the Subject

class Relationships(BaseModel):
    relationships: List[Relationship]


class Entity(BaseModel):
    relationships: List[Relationship] = []
    type: str
    entity_id: str
    name: str = None

class EntityIds(BaseModel):
    entity_ids: List[str]


class Entities(BaseModel):
    entities: List[Entity]

class TimeseriesData(BaseModel):
    data: List[List[Any]] #TODO: Documentation?
    columns: List[str] = ['uuid', 'timestamp', 'number']

class ValueType(str, Enum):
    number = 'number'
    text = 'text'
    loc = 'loc'

ValueTypes = List[ValueType]

SparqlResult = Dict

class IsSuccess(BaseModel):
    is_success: bool = True
    reason: str = ''


class ActuationRequest(BaseModel):
    value: float
    #scheduled_time: float = Field(None)

jwt_security_scheme = Security(auth_scheme)


entity_id_description = 'The identifier of an entity. Often a URI'
graph_description = 'The name of the graph. This is similar to a database name in relational databases.'
