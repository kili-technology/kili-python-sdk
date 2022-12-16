"""
Helpers for GraphQL Queries and Mutations
"""

import base64
import functools
import glob
import mimetypes
import os
import re
import warnings
from json import dumps, loads
from typing import Callable, Dict, List, Optional, Type, TypeVar, Union

import pyparsing as pp
import requests
from typing_extensions import TypedDict, get_args, get_origin, is_typeddict

from kili.constants import mime_extensions_for_IV2
from kili.exceptions import GraphQLError, NonExistingFieldError

T = TypeVar("T")


def format_result(name: str, result: dict, _object: Optional[Type[T]] = None) -> T:
    """
    Formats the result of the GraphQL queries.

    Args:
        name: name of the field to extract, usually data
        result: query result to parse
        _object: returned type
    """
    if "errors" in result:
        raise GraphQLError(result["errors"])
    formatted_json = format_json(result["data"][name])
    if _object is None:
        return formatted_json  # type:ignore X
    if isinstance(formatted_json, list):
        if get_origin(_object) is list:
            obj = get_args(_object)[0]
            return [obj(element) for element in formatted_json]  # type:ignore
        # the legacy "orm" objects fall into this category.
        return [_object(element) for element in formatted_json]  # type:ignore

    return _object(formatted_json)  # type:ignore


def content_escape(content: str) -> str:
    """
    Escapes the content

    Args:
        content (str): string to escape

    Returns:
        str: escaped string
    """
    return content.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def get_data_type(path: str):
    """
    Get the data type, either image/png or application/pdf

    Args:
        path: path of the file
    """
    mime_type, _ = mimetypes.guess_type(path.lower())
    return mime_type if mime_type else ""


def encode_base64(path):
    """
    Encode a file in base 64

    Args:
        path: path of the file
    """
    data_type = get_data_type(path)
    with open(path, "rb") as image_file:
        return f"data:{data_type};base64," + base64.b64encode(image_file.read()).decode("ascii")


def is_url(path):
    """
    Check if the path is a url or something else

    Args:
        path: path of the file
    """
    return isinstance(path, str) and re.match(r"^(http://|https://)", path.lower())


def format_json_dict(result: dict) -> Dict:
    """
    Formats the dict part of a json return by a GraphQL query into a python object

    Args:
        result: result of a GraphQL query
    """
    for key, value in result.items():
        if key in ["jsonInterface", "jsonMetadata", "jsonResponse"]:
            if (value == "" or value is None) and not (is_url(value) and key == "jsonInterface"):
                result[key] = {}
            elif isinstance(value, str):
                try:
                    if is_url(value):
                        result[key] = requests.get(value, timeout=30).json()
                    else:
                        result[key] = loads(value)
                except Exception as exception:
                    raise ValueError(
                        "Json Metadata / json response / json interface should be valid jsons"
                    ) from exception
        else:
            result[key] = format_json(value)
    return result


D = TypeVar("D")


def format_json(result: Union[None, list, dict, D]) -> Union[None, list, dict, D]:
    """
    Formats the json return by a GraphQL query into a python object

    Args:
        result: result of a GraphQL query
    """
    if result is None:
        return result
    if isinstance(result, list):
        return [format_json(elem) for elem in result]
    if isinstance(result, dict):
        return format_json_dict(result)
    return result


def fragment_builder(fields: List[str], typed_dict_class: Type[TypedDict]):
    """
    Builds a GraphQL fragment for a list of fields to query

    Args:
        fields
        type_of_fields
    """
    type_of_fields = typed_dict_class.__annotations__
    fragment = ""
    subfields = [field.split(".", 1) for field in fields if "." in field]
    if subfields:
        for subquery in {subfield[0] for subfield in subfields}:
            type_of_fields_subquery = type_of_fields[subquery]
            if type_of_fields_subquery == str:
                raise NonExistingFieldError(f"{subquery} field does not take subfields")
            if is_typeddict(type_of_fields_subquery):
                fields_subquery = [subfield[1] for subfield in subfields if subfield[0] == subquery]
                new_fragment = fragment_builder(
                    fields_subquery,
                    type_of_fields_subquery,  # type: ignore
                )
                fragment += f" {subquery}{{{new_fragment}}}"
        fields = [field for field in fields if "." not in field]
    for field in fields:
        try:
            type_of_fields[field]
        except KeyError as exception:
            raise NonExistingFieldError(
                f"Cannot query field {field} on object {typed_dict_class.__name__}. Admissible"
                " fields are: \n- " + "\n- ".join(type_of_fields.keys())
            ) from exception
        if isinstance(field, str):
            fragment += f" {field}"
        else:
            raise Exception("Please provide the fields to query as strings")
    return fragment


def deprecate(
    msg: Optional[str] = None,
    removed_in: Optional[str] = None,
    _type=DeprecationWarning,
):
    """
    Decorator factory that tag a deprecated function.
    - To deprecated the whole function, you can give a message at the decorator level.
    - For more sharp condition on the warning message, integrate this warning inside the function
    but still tag the function with this decorator, without giving a message argument

    Args:
        msg: string message that will be displayed whenever the function is called
        removed_in: string version in the format "Major.Minor"
            in which the deprecation element has to be removed
        type: DeprecationWarning by default
    """

    def decorator(func):
        if removed_in:
            if len(removed_in.split(".")) != 2:
                raise ValueError(
                    f'"removed_in" argument in deprecate wrapper of the function {func.__name__}'
                    'should have the format "Major.Minor"'
                )
            func.removed_in = removed_in

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if msg:
                warnings.warn(msg, _type, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def format_metadata(metadata):
    """
    Formats metadata

    Args:
        metadata: a python object
    """
    if metadata is None:
        return metadata
    if isinstance(metadata, str):
        return metadata
    if isinstance(metadata, (dict, list)):
        return dumps(metadata)
    raise Exception(
        f"Metadata {metadata} of type {type(metadata)} must either be None,"
        " a string a list or a dict."
    )


def convert_to_list_of_none(array, length):
    """
    Turns a value in a list of length length

    Args:
        array
        length
    """
    if isinstance(array, list):
        if len(array) != length:
            raise Exception(f"array should have length {length}")
        return array
    return [None] * length


def is_none_or_empty(_object):
    """
    Tests if an object is none or empty

    Args:
        object: a python object
    """
    object_is_empty = isinstance(_object, list) and len(_object) == 0
    return _object is None or object_is_empty


def list_is_not_none_else_none(_object):
    """
    Formats an object as a singleton if not none

    Args:
        object: a python object
    """
    return [_object] if _object is not None else None


def validate_category_search_query(query):
    """Validate the category search query
    Args:
        query: the query to parse

    Raises:
        ValueError: if `query` is invalid
    """
    operator = pp.oneOf(">= <= > < ==")
    number = pp.pyparsing_common.number()
    dot = "."
    word = pp.Word(pp.alphas, pp.alphanums + "_-*")
    identifier = word + dot + word + dot + "count"
    condition = identifier + operator + number

    expr = pp.infixNotation(
        condition,
        [
            (
                "AND",
                2,
                pp.opAssoc.LEFT,
            ),
            (
                "OR",
                2,
                pp.opAssoc.LEFT,
            ),
        ],
    )
    try:
        expr.parseString(query, parseAll=True)
    except pp.ParseException as error:
        raise ValueError(f"Invalid category search query: {query}") from error


def get_file_paths_to_upload(
    files: List[str], file_check_function: Optional[Callable] = None, verbose: bool = False
) -> List[str]:
    """Get a list of paths for the files to upload given a list of files or folder paths.

    Args:
        files: a list path that can either be file paths, folder paths or unexisting paths
        file_check_function: function to check files. Must use argument path and return a bool
    Returns:
        a list of the paths of the files to upload, compatible with the project type.
    """
    file_check_function = file_check_function or (lambda x: True)
    file_paths = []
    for item in files:
        if os.path.isfile(item):
            file_paths.append(item)
        elif os.path.isdir(item):
            folder_path = os.path.join(item, "")
            file_paths.extend(
                [sub_item for sub_item in glob.glob(folder_path + "*") if os.path.isfile(sub_item)]
            )
        else:
            file_paths.extend(
                [sub_item for sub_item in glob.glob(item) if os.path.isfile(sub_item)]
            )
    file_paths_to_upload = [path for path in file_paths if file_check_function(path)]
    if len(file_paths_to_upload) == 0:
        raise ValueError(
            "No files to upload. Check that the paths exist and that the file type is correct"
        )
    if verbose:
        for path in file_paths:
            if path not in file_paths_to_upload:
                print(f"{path:30} SKIPPED")
        if len(file_paths_to_upload) != len(file_paths):
            print("Paths skipped either do not exist or point towards an incorrect file")
    file_paths_to_upload.sort()
    return file_paths_to_upload


def file_check_function_from_input_type(input_type: str):
    """
    Returns check_file_mime_type function with input_type and verbose as preset argument
    """

    def output_function(path: str):
        return check_file_mime_type(path, input_type, raise_error=False)

    return output_function


def check_file_mime_type(path: str, input_type: str, raise_error=True) -> bool:
    """
    Returns true if the mime type of the file corresponds to the allowed mime types of the project
    """

    mime_type = get_data_type(path.lower())

    if not (mime_extensions_for_IV2[input_type] and mime_type):
        return False

    correct_mime_type = mime_type in mime_extensions_for_IV2[input_type]
    if not correct_mime_type and raise_error:
        raise ValueError(
            f"File mime type for {path} is {mime_type} and does not correspond "
            "to the type of the project. "
            f"File mime type should be one of {mime_extensions_for_IV2[input_type]}"
        )
    return correct_mime_type
