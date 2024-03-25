"""Custom Types."""

from typing import List, Tuple, TypeVar, Union

from typing_extensions import TypeAlias

T = TypeVar("T")

ListOrTuple: TypeAlias = Union[List[T], Tuple[T, ...]]
