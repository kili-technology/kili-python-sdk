"""Custom Types."""

from typing import List, Tuple, Type, TypedDict, TypeVar, Union

from typeguard import TypeCheckError, check_type
from typing_extensions import TypeGuard

T = TypeVar("T")

ListOrTuple = Union[List[T], Tuple[T, ...]]

T = TypeVar("T", bound=TypedDict)


def trycast(value: TypedDict, expected_type: Type[T]) -> TypeGuard[T]:
    """Try to cast a value to a given type."""
    try:
        check_type(value, expected_type)
    except TypeCheckError as err:
        _ = err
        return False

    return True
