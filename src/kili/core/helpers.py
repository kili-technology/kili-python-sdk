"""Helpers for GraphQL Queries and Mutations."""

import functools
import glob
import json
import mimetypes
import os
import re
import warnings
from json import dumps, loads
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

import pyparsing as pp
import requests
import tenacity
from typing_extensions import get_args, get_origin

from kili.adapters.http_client import HttpClient
from kili.core.constants import mime_extensions_for_IV2
from kili.log.logging import logger

T = TypeVar("T")


def format_result(
    name: str, result: dict, object_: Optional[Type[T]], http_client: HttpClient
) -> T:
    """Formats the result of the GraphQL queries.

    Args:
        name: name of the field to extract, usually data
        result: query result to parse
        object_: returned type
        http_client: http client to use for the query
    """
    formatted_json = format_json(result[name], http_client)
    if object_ is None:
        return formatted_json  # pyright: ignore[reportGeneralTypeIssues]
    if isinstance(formatted_json, list):
        if get_origin(object_) is list:
            obj = get_args(object_)[0]
            # pylint: disable=line-too-long
            return [obj(element) for element in formatted_json]  # pyright: ignore[reportGeneralTypeIssues]
        # the legacy "orm" objects fall into this category.
        # pylint: disable=line-too-long
        return [object_(element) for element in formatted_json]  # pyright: ignore[reportGeneralTypeIssues]

    return object_(formatted_json)


def get_mime_type(path: str):
    """Provide the mime type of a file (e.g. image/png).

    Args:
        path: path of the file
    """
    path = path.lower()
    mime_type, _ = mimetypes.guess_type(path)

    # guess_type does not recognize JP2 files on Windows
    if mime_type is None and path.endswith(".jp2"):
        return "image/jp2"
    # guess_type provides a wrong mime type for NITF files on Ubuntu
    if path.endswith((".ntf", ".nitf")) and mime_type != "application/vnd.nitf":
        return "application/vnd.nitf"
    return mime_type


def is_url(path: object):
    """Check if the path is a url or something else.

    Args:
        path: path of the file
    """
    return isinstance(path, str) and re.match(r"^(http://|https://)", path.lower())


def __format_json_dict(result: Dict, http_client: HttpClient) -> Dict:
    """Parse a dictionary inside the result of a graphQL query to format json fields.

    If json fields (i.e "jsonInterface", "jsonMetadata" and "jsonResponse")
    are part of the keys, either:
        - fetch the json from the url if it is hosted on a bucket
        - load the json from the string if the json is given as a string

    Args:
        result: a dictionary included in the result of a GraphQL query
        http_client: http client to use for the query
    """
    for key, value in result.items():
        if key in ["jsonInterface", "jsonMetadata", "jsonResponse"]:  # TODO: also parse jsonContent
            if (value == "" or value is None) and not (is_url(value) and key == "jsonInterface"):
                result[key] = {}
            elif isinstance(value, str):
                try:
                    if is_url(value):
                        result[key] = http_client.get(value, timeout=30).json()
                    else:
                        result[key] = loads(value)
                except Exception as exception:
                    raise ValueError(
                        "Json Metadata / json response / json interface should be valid jsons"
                    ) from exception
        else:
            result[key] = format_json(value, http_client)
    return result


D = TypeVar("D")


def format_json(
    result: Union[None, list, dict, D], http_client: HttpClient
) -> Union[None, list, dict, D]:
    """Recusively parse the result of a GraphQL query in order to get json fields as a dictionary.

    Args:
        result: result of a GraphQL query
        http_client: http client to use for the query
    """
    if result is None:
        return result
    if isinstance(result, list):
        return [format_json(elem, http_client) for elem in result]
    if isinstance(result, dict):
        return __format_json_dict(result, http_client)
    return result


def deprecate(
    msg: Optional[str] = None,
    removed_in: Optional[str] = None,
    type_: Type[Warning] = DeprecationWarning,
):
    """Decorator factory that tag a deprecated function.

    - To deprecated the whole function, you can give a message at the decorator level.
    - For more sharp condition on the warning message, integrate this warning inside the function
    but still tag the function with this decorator, without giving a message argument

    Args:
        msg: string message that will be displayed whenever the function is called
        removed_in: string version in the format "Major.Minor"
            in which the deprecation element has to be removed
        type_: DeprecationWarning by default
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
                warnings.warn(msg, type_, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def format_metadata(metadata: object):
    """Formats metadata.

    Args:
        metadata: a python object
    """
    if metadata is None:
        return metadata
    if isinstance(metadata, str):
        return metadata
    if isinstance(metadata, (dict, list)):
        return dumps(metadata)
    raise TypeError(
        f"Metadata {metadata} of type {type(metadata)} must either be None,"
        " a string a list or a dict."
    )


def convert_to_list_of_none(array: List, length: int) -> List:
    """Turns a value in a list of length length.

    Args:
        array: the array to convert
        length: the length of the array
    """
    if isinstance(array, list):
        if len(array) != length:
            raise ValueError(f"array should have length {length}")
        return array
    return [None] * length


def is_none_or_empty(object_: object) -> bool:
    """Tests if an object is none or empty.

    Args:
        object_: a python object
    """
    object_is_empty = isinstance(object_, list) and len(object_) == 0
    return object_ is None or object_is_empty


def validate_category_search_query(query: str):
    """Validate the category search query.

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
        verbose: if True, print the files that will be uploaded

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


def check_file_mime_type(path: str, input_type: str, raise_error=True) -> bool:
    # pylint: disable=line-too-long
    """Returns true if the mime type of the file corresponds to the allowed mime types of the project."""
    mime_type = get_mime_type(path.lower())

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


class RetryLongWaitWarner:  # pylint: disable=too-few-public-methods
    """Class that warns when retry takes too long."""

    def __init__(
        self,
        warn_message: str,
        logger_func: Callable,
        warn_after: float = 10,
    ) -> None:
        """Class that warns when retry takes too long.

        Args:
            warn_message: custom warning message. If not provided, a default message is used.
            logger_func: function to log the message (print, warning, logger.warning, etc.)
            warn_after: time in seconds after which the warning is raised.
        """
        self.warn_message = warn_message
        self.logger_func = logger_func
        self.warn_after = warn_after

        self.warned = False

    def __call__(self, retry_state: tenacity.RetryCallState):
        if not self.warned and float(retry_state.outcome_timestamp or 0) > self.warn_after:
            self.logger_func(self.warn_message)
            self.warned = True


def is_empty_list_with_warning(method_name: str, argument_name: str, argument_value: Any) -> bool:
    """Check if an input list argument is empty and warn the user if it is.

    Returns True if the list is empty, False otherwise
    """
    if isinstance(argument_value, List) and len(argument_value) == 0:
        warnings.warn(
            f"Method '{method_name}' did nothing because the following argument"
            f" is empty: {argument_name}.",
            stacklevel=5,
        )
        return True
    return False


def log_raise_for_status(response: requests.Response) -> None:
    """Log the error message of a requests.Response if it is not ok.

    Args:
        response: a requests.Response
    """
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.exception("An error occurred while processing the response: %s", err)
        raise


def get_response_json(response: requests.Response) -> dict:
    """Get the json from a requests.Response.

    Args:
        response: a requests.Response
    """
    try:
        return response.json()
    except json.JSONDecodeError:
        logger.exception("An error occurred while decoding the json response")
        return {}
