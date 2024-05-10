from enum import Enum
from functools import lru_cache
from typing import Annotated, Any, Generic, List, Optional, Tuple, Type, TypeVar, Union

from beanie import Document, PydanticObjectId
from humps import camelize
from pydantic import BaseModel as PydanticBaseModel, ConfigDict, Field, create_model

from brick_server.minimal.utilities.exceptions import ErrorCode, ErrorShowType

BT = TypeVar("BT", bound=PydanticBaseModel)


@lru_cache(maxsize=128)
def get_standard_list_response_sub_model(
    cls: Type[PydanticBaseModel],
) -> Type[PydanticBaseModel]:
    name = cls.__name__
    return create_model(
        f"{name}List",
        count=(int, 0),
        results=(List[cls], []),  # type: ignore
    )


@lru_cache(maxsize=256)
def get_standard_response_model(
    cls: Type[PydanticBaseModel], is_list: bool = False
) -> Tuple[Type[PydanticBaseModel], Optional[Type[PydanticBaseModel]]]:
    name = cls.__name__
    sub_model: Optional[Type[PydanticBaseModel]]
    if is_list:
        model_name = f"{name}ListResp"
        sub_model = get_standard_list_response_sub_model(cls)
        data_type = (Optional[sub_model], None)
    else:
        model_name = f"{name}Resp"
        sub_model = None
        data_type = (Optional[cls], None)

    config = ConfigDict(
        alias_generator=camelize,
        populate_by_name=True,
    )

    model = create_model(
        model_name,
        error_code=(ErrorCode, ...),
        error_message=(str, ""),
        show_type=(ErrorShowType, ErrorShowType.Silent),
        data=data_type,
        __config__=config,
    )

    return model, sub_model


class Empty(PydanticBaseModel):
    pass


class StandardResponse(Generic[BT]):
    def __class_getitem__(cls, item: Any) -> Type[Any]:
        return get_standard_response_model(item)[0]

    def __new__(cls, data: Union[BT, Empty] = Empty()) -> "StandardResponse[BT]":
        response_type, _ = get_standard_response_model(type(data))  # type: ignore
        response_data = data

        return response_type(  # type: ignore
            error_code=ErrorCode.Success,
            error_message="",
            show_type=ErrorShowType.Silent,
            data=response_data,
        )


class StandardListResponse(Generic[BT]):
    def __class_getitem__(cls, item: Any) -> Type[Any]:
        return get_standard_response_model(item, True)[0]

    def __new__(
        cls,
        results: Optional[List[BT]] = None,
        count: Optional[int] = None,
    ) -> "StandardListResponse[BT]":
        if results is None:
            results = []
        data_type = len(results) and type(results[0]) or Empty
        response_type, sub_model_type = get_standard_response_model(data_type, True)  # type: ignore
        if count is None:
            count = len(results)
        response_data: PydanticBaseModel
        if sub_model_type is None:
            response_data = Empty()
        else:
            response_data = sub_model_type(count=count, results=results)

        return response_type(  # type: ignore
            error_code=ErrorCode.Success,
            error_message="",
            show_type=ErrorShowType.Silent,
            data=response_data,
        )


class BaseModel(PydanticBaseModel):
    class Config:
        # reference: fastapi-camelcase
        alias_generator = camelize
        # The name of this configuration setting was changed in pydantic v2 from
        #         `allow_population_by_alias` to `populate_by_name`.
        populate_by_name = True
        validate_default = True

    def to_response(self: BT) -> StandardResponse[BT]:
        return StandardResponse(self)

    def update_model(self: BT, model: Document) -> None:
        for k, v in self.dict().items():
            if v is not None:
                setattr(model, k, v)


PaginationLimit = 500


class PaginationQuery(BaseModel):
    offset: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(gt=0, le=PaginationLimit)]


class DBRef(BaseModel):
    id: PydanticObjectId
    # collection: str | None = None


class StrEnumMixin(str, Enum):
    def __str__(self) -> str:
        return self.value
