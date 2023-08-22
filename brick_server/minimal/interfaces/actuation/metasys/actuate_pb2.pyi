from typing import ClassVar as _ClassVar, Optional as _Optional

from google.protobuf import descriptor as _descriptor, message as _message

DESCRIPTOR: _descriptor.FileDescriptor

class Response(_message.Message):
    __slots__ = ["details", "status"]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    details: str
    status: bool
    def __init__(self, status: bool = ..., details: _Optional[str] = ...) -> None: ...

class TemporaryOverrideAction(_message.Message):
    __slots__ = ["annotation", "hour", "minute", "uuid", "value"]
    ANNOTATION_FIELD_NUMBER: _ClassVar[int]
    HOUR_FIELD_NUMBER: _ClassVar[int]
    MINUTE_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    annotation: str
    hour: int
    minute: int
    uuid: str
    value: str
    def __init__(
        self,
        uuid: _Optional[str] = ...,
        value: _Optional[str] = ...,
        hour: _Optional[int] = ...,
        minute: _Optional[int] = ...,
        annotation: _Optional[str] = ...,
    ) -> None: ...
