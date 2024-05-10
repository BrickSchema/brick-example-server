from enum import Enum

from brick_server.minimal.schemas.base import StrEnumMixin


class PermissionType(StrEnumMixin, Enum):
    READ = "read"
    WRITE = "write"
    # ADMIN = "admin"
    NA = "na"


class PermissionScope(StrEnumMixin, Enum):
    SITE = "site"
    DOMAIN = "domain"
    ENTITY = "entity"
    USER = "user"
    APP = "app"
