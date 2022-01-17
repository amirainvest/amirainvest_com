import typing as t

from pydantic.generics import GenericModel


ResultsType = t.TypeVar("ResultsType")


class ListModelBase(GenericModel, t.Generic[ResultsType]):
    results: t.List[ResultsType]
    result_count: int
