# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: actuate.proto
# flake8: noqa
"""Generated protocol buffer code."""
from google.protobuf import (
    descriptor as _descriptor,
    descriptor_pool as _descriptor_pool,
    symbol_database as _symbol_database,
)
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\ractuate.proto"\x9a\x01\n\x17TemporaryOverrideAction\x12\x0c\n\x04uuid\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\x12\x11\n\x04hour\x18\x03 \x01(\rH\x00\x88\x01\x01\x12\x13\n\x06minute\x18\x04 \x01(\rH\x01\x88\x01\x01\x12\x17\n\nannotation\x18\x05 \x01(\tH\x02\x88\x01\x01\x42\x07\n\x05_hourB\t\n\x07_minuteB\r\n\x0b_annotation"+\n\x08Response\x12\x0e\n\x06status\x18\x01 \x01(\x08\x12\x0f\n\x07\x64\x65tails\x18\x02 \x01(\t2E\n\x07\x41\x63tuate\x12:\n\x11TemporaryOverride\x12\x18.TemporaryOverrideAction\x1a\t.Response"\x00\x62\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "actuate_pb2", globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _TEMPORARYOVERRIDEACTION._serialized_start = 18
    _TEMPORARYOVERRIDEACTION._serialized_end = 172
    _RESPONSE._serialized_start = 174
    _RESPONSE._serialized_end = 217
    _ACTUATE._serialized_start = 219
    _ACTUATE._serialized_end = 288
# @@protoc_insertion_point(module_scope)
