"""Custom Types."""

from typing import TypeAlias, TypeVar, Union

T = TypeVar("T")

ListOrTuple: TypeAlias = Union[list[T], tuple[T, ...]]
