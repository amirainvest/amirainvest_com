import typing as t

from pydantic import BaseModel
from pydantic.generics import GenericModel


ResultsType = t.TypeVar("ResultsType")
ErrorType = t.TypeVar("ErrorType")


class ListModelBase(GenericModel, t.Generic[ResultsType]):
    results: t.List[ResultsType]
    result_count: int


class ErrorMessageModelBase(GenericModel, t.Generic[ErrorType]):
    detail: ErrorType


class StatusDetailModel(BaseModel):
    sub_status_code: int
    message: str
