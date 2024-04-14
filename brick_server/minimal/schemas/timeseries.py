from enum import Enum
from typing import Any

from brick_server.minimal.schemas.base import BaseModel, StrEnumMixin


class ValueType(StrEnumMixin, Enum):
    number = "number"
    text = "text"
    loc = "loc"


class ColumnType(StrEnumMixin, Enum):
    number = "number"
    text = "text"
    loc = "loc"
    uuid = "uuid"
    timestamp = "timestamp"


class TimeseriesData(BaseModel):
    data: list[list[Any]]
    columns: list[ColumnType] = ["uuid", "timestamp", "number"]
