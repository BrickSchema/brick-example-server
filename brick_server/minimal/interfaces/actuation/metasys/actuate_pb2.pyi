from typing import ClassVar as _ClassVar, Optional as _Optional

from google.protobuf import descriptor as _descriptor, message as _message

DESCRIPTOR: _descriptor.FileDescriptor

class ReadObjectCurrentAction(_message.Message):
    __slots__ = ("uuid", "attribute")
    UUID_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    attribute: str
    def __init__(
        self, uuid: _Optional[str] = ..., attribute: _Optional[str] = ...
    ) -> None: ...

class TemporaryOverrideAction(_message.Message):
    __slots__ = ("uuid", "value", "hour", "minute", "annotation")
    UUID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    HOUR_FIELD_NUMBER: _ClassVar[int]
    MINUTE_FIELD_NUMBER: _ClassVar[int]
    ANNOTATION_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    value: str
    hour: int
    minute: int
    annotation: str
    def __init__(
        self,
        uuid: _Optional[str] = ...,
        value: _Optional[str] = ...,
        hour: _Optional[int] = ...,
        minute: _Optional[int] = ...,
        annotation: _Optional[str] = ...,
    ) -> None: ...

class Response(_message.Message):
    __slots__ = ("status", "details")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    details: str
    def __init__(self, status: bool = ..., details: _Optional[str] = ...) -> None: ...
