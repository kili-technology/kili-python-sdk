"""Custom Types."""

from typing import List, Tuple, TypeVar, Union

T = TypeVar("T")

ListOrTuple = Union[List[T], Tuple[T, ...]]
