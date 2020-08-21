from pydantic import BaseModel, Field, conlist
from typing import List, Dict, Any
from enum import Enum
from copy import deepcopy

from fastapi import Security

from ..auth.authorization import auth_scheme

class ValueType(str, Enum):
    number = 'number'
    text = 'text'
    loc = 'loc'

class ColumnType(str, Enum):
    number = 'number'
    text = 'text'
    loc = 'loc'
    uuid = 'uuid'
    timestamp = 'timestamp'



value_types = [val.value for val in ValueType]

entity_desc = "An entity can be defined in two ways. It's an instance of a (Brick) Class. More specifically, it is either a physical or a virtual thing whose properties are well-maintained to be a thing. Top three Brick Classes are Point (e.g., sensors, setpoints, etc.), Equipment (e.g., VAV, Luminaire, AHU, etc.), and Location (e.g., Room, Floor, etc.)"
entity_id_desc = 'The identifier of an entity. Often a URI. This should be unique across the target systems (i.e., the graphs of the interest.)'
graph_desc = 'The name of the graph. This is similar to a database name in relational databases.'
relationships_desc = "The list of relationships for the target entity. Assuming the target entity is the subject, each relation consists of the subject's predicate and object.s"
type_desc = "The entity's type, which is often a Brick Class."
name_desc = "An informative name for the entity. This does not have to be unique."
start_time_desc = 'Starting time of the data in UNIX timestamp in seconds (float). If not given, the beginning of the data will be assumed.'
end_time_desc = 'Ending time of the data in UNIX timestamp in seconds (float). If not given, the end of the data will be assumed.'
value_type_desc = 'The type of value. Currently, there are numbers (for both floating points and integers), texts, and locations (blobs are under dev.)'
timeseries_data_desc = 'A table of data where each row represents a value tuple. `data` field contains actual data and `columns` field contains information about the columns of the data.'
data_desc = 'A value tuple is actually an array in JSON and consists of different columns such as an identifier, a timestamp, and a number. For example, `["http://brickserver.com#znt1", 1582412083, 71.4]`. A list of such tuples is a set of data. They share the same type of columns in a set of data, and the columns are explicitly represented in a separate field.'
columns_desc = 'Columns explain how to interpret the values in the data. `uuid` and `timestamp` are mandatory, and specific `value_type`s can be specified.'
sql_desc = 'A raw SQL query for timeseries data. The table consist of the columns as in `value_types`.'
sparql_desc = 'A raw SPARQL query.'
actuation_value_desc = 'A value to set the target entity.'
relation_query_desc = 'A list of object URIs for the corresponding predicate. Brick Server will find entities having relations with all the objects with the predicate (i.e., AND operation.)'

#Relationship = List[str] ## [Predicate, Object] for the Subject
TripleModel = conlist(str, min_items=3, max_items=3)
TupleModel = conlist(str, min_items=2, max_items=2)
Relationship = deepcopy(TupleModel)

class Relationships(BaseModel):
    relationships: List[Relationship]


class Entity(BaseModel):
    relationships: List[Relationship] = Field([], description=relationships_desc)
    type: str = Field(..., description=type_desc)
    entity_id: str = Field(..., description=entity_id_desc)
    name: str = Field(None, description=name_desc)

class EntityIds(BaseModel):
    entity_ids: List[str] = Field(..., description='The list of `entity_id`s')


class Entities(BaseModel):
    entities: List[Entity] = Field(..., description='The list ot entities')


class TimeseriesData(BaseModel):
    data: List[List[Any]] = Field(..., description=data_desc)
    columns: List[ColumnType] = Field(['uuid', 'timestamp', 'number'], description=columns_desc)

ValueTypes = List[ValueType]

SparqlResult = Dict

class IsSuccess(BaseModel):
    is_success: bool = True
    reason: str = ''


class ActuationRequest(BaseModel):
    value: float = Field(..., description=actuation_value_desc)
    #scheduled_time: float = Field(None)

class CreateEntityRequest(BaseModel):
    number: int = Field(..., description='The number of instances to create for the Brick Class')
    #ignore_brick_type: bool = Bool(False, description='If true, does not check whether the given type is defined in Brick or not') #TODO: Implement this

BrickClass = str

CreateEntitiesRequest = Dict[BrickClass,# = Field(..., description='A Class name, often defined in Brick'),
                             int# = Field(...,description='The number of instances to create for the Brick Class')
                             ]

EntitiesCreateResponse = Dict[BrickClass, List[str]]

jwt_security_scheme = Security(auth_scheme)


class GrafanaDashboardResponse(BaseModel):
    url: str = Field(..., description='Grafana dashboard url for the user')
    uid: str = Field(..., description='Grafana dashboard uid for the user')
    grafana_id: str = Field(..., description='Grafana dashboard id for the user')
