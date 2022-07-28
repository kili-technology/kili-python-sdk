"""
Helpers for the asset mutations
"""
import csv
import mimetypes
import os
from json import dumps
from typing import List, Union
from uuid import uuid4

from ...helpers import (
    check_file_mime_type,
    convert_to_list_of_none,
    encode_base64,
    format_metadata,
    is_none_or_empty,
    is_url,
)
from .queries import GQL_APPEND_MANY_FRAMES_TO_DATASET, GQL_APPEND_MANY_TO_DATASET


def encode_object_if_not_url(content, input_type):
    """
    Return the object if it is a url, else it should be a path to a file.
    In that case, the file is returned as a base64 string
    """
    if is_url(content):
        return content
    if check_file_mime_type(content, input_type):
        return encode_base64(content)
    return None


def process_frame_json_content(json_content):
    """
    Function to process individual json_content of VIDEO projects
    """
    if is_url(json_content):
        return json_content
    json_content_index = range(len(json_content))
    json_content_urls = [encode_object_if_not_url(content, "IMAGE") for content in json_content]
    return dumps(dict(zip(json_content_index, json_content_urls)))


def get_file_mimetype(
    content_array: Union[List[str], None], json_content_array: Union[List[str], None]
) -> Union[str, None]:
    """
    Returns the mimetype of the first file of the content array
    """
    if json_content_array is not None:
        return None
    if content_array is None:
        return None
    if len(content_array) > 0:
        first_asset = content_array[0]
        if is_url(first_asset):
            return None
        if not os.path.exists(first_asset):
            return None
        return mimetypes.guess_type(first_asset)[0]
    return None


def process_json_content(
    input_type: str,
    content_array: List[str],
    json_content_array: Union[List[str], None],
):
    """
    Process the array of json_contents
    """
    if json_content_array is None:
        return [""] * len(content_array)
    if input_type in ("FRAME", "VIDEO"):
        return list(map(process_frame_json_content, json_content_array))
    return [element if is_url(element) else dumps(element) for element in json_content_array]


def process_content(
    input_type: str,
    content_array: Union[List[str], None],
    json_content_array: Union[List[List[Union[dict, str]]], None],
):
    """
    Process the array of contents
    """
    if input_type in ["IMAGE", "PDF"]:
        return [
            content
            if is_url(content)
            else (
                content
                if (json_content_array is not None and json_content_array[i] is not None)
                else (encode_base64(content) if check_file_mime_type(content, input_type) else None)
            )
            for i, content in enumerate(content_array)
        ]
    if input_type in ("FRAME", "VIDEO") and json_content_array is None:
        content_array = [encode_object_if_not_url(content, input_type) for content in content_array]
    if input_type == "TIME_SERIES":
        content_array = list(map(process_time_series, content_array))
    return content_array


def process_time_series(content: str) -> Union[str, None]:
    """
    Process the content for TIME_SERIES projects: if it is a file, read the content
    and also check if the content corresponds to the expected format, else return None
    """
    delimiter = ","
    if os.path.isfile(content):
        if check_file_mime_type(content, "TIME_SERIES"):
            with open(content, "r", encoding="utf8") as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter)
                return process_csv_content(reader, file_name=content, delimiter=delimiter)
        return None

    reader = csv.reader(content.split("\n"), delimiter=",")
    return process_csv_content(reader, delimiter=delimiter)


def process_csv_content(reader, file_name=None, delimiter=",") -> bool:
    """
    Process the content of csv for time_series and check if it corresponds to the expected format
    """
    first_row = True
    processed_lines = []
    for row in reader:
        if not (len(row) == 2 and (first_row or (not first_row and is_float(row[0])))):
            print(
                f"""The content {file_name if file_name else row} does not correspond to the \
correct format: it should have only 2 columns, the first one being the timestamp \
(an integer or a float) and the second one a numeric value (an integer or a float, \
otherwise it will be considered as missing value). The first row should have the names \
of the 2 columns. The delimiter used should be ','."""
            )
            return None
        value = row[1] if (is_float(row[1]) or first_row) else ""
        processed_lines.append(delimiter.join([row[0], value]))
        first_row = False
    return "\n".join(processed_lines)


def is_float(number: str) -> bool:
    """
    Check if a string can be converted to float
    """
    try:
        float(number)
        return True
    except ValueError:
        return False


def add_video_parameters(json_metadata, should_use_native_video):
    """
    Add necessary video parameters to the metadata of the video
    """
    processing_parameters = json_metadata.get("processingParameters", {})
    video_parameters = [
        ("shouldKeepNativeFrameRate", should_use_native_video),
        ("framesPlayedPerSecond", 30),
        ("shouldUseNativeVideo", should_use_native_video),
    ]
    for (key, default_value) in video_parameters:
        processing_parameters[key] = processing_parameters.get(key, default_value)
    return {**json_metadata, "processingParameters": processing_parameters}


def process_metadata(
    input_type: str,
    content_array: Union[List[str], None],
    json_content_array: Union[List[List[Union[dict, str]]], None],
    json_metadata_array: Union[List[dict], None],
):
    """
    Process the metadata of each asset
    """
    json_metadata_array = (
        [{}] * len(content_array) if json_metadata_array is None else json_metadata_array
    )
    if input_type in ("FRAME", "VIDEO"):
        should_use_native_video = json_content_array is None
        json_metadata_array = [
            add_video_parameters(json_metadata, should_use_native_video)
            for json_metadata in json_metadata_array
        ]
    return list(map(dumps, json_metadata_array))


def get_request_to_execute(
    input_type: str,
    json_metadata_array: Union[List[dict], None],
    json_content_array: Union[List[List[Union[dict, str]]], None],
    mime_type: Union[str, None],
) -> str:
    """
    Selects the right query to run versus the data given
    """
    if json_content_array is not None:
        return GQL_APPEND_MANY_TO_DATASET, None
    if input_type not in ("FRAME", "VIDEO"):
        if input_type == "IMAGE" and mime_type == "image/tiff":
            return GQL_APPEND_MANY_FRAMES_TO_DATASET, "GEO_SATELLITE"
        return GQL_APPEND_MANY_TO_DATASET, None
    if json_metadata_array is None:
        return GQL_APPEND_MANY_TO_DATASET, None
    if (
        isinstance(json_metadata_array, list)
        and len(json_metadata_array) > 0
        and not json_metadata_array[0]
        .get("processingParameters", {})
        .get("shouldUseNativeVideo", True)
    ):
        return GQL_APPEND_MANY_FRAMES_TO_DATASET, "VIDEO"
    return GQL_APPEND_MANY_TO_DATASET, None


# pylint: disable=too-many-arguments
def process_append_many_to_dataset_parameters(
    input_type: str,
    content_array: Union[List[str], None],
    external_id_array: Union[List[str], None],
    is_honeypot_array: Union[List[str], None],
    status_array: Union[List[str], None],
    json_content_array: Union[List[List[Union[dict, str]]], None],
    json_metadata_array: Union[List[dict], None],
):
    """
    Process arguments of the append_many_to_dataset method and return the data payload.
    """
    if content_array is None and json_content_array is None:
        raise ValueError("Variables content_array and json_content_array cannot be both None.")
    if content_array is None:
        content_array = [""] * len(json_content_array)
    if external_id_array is None:
        external_id_array = [uuid4().hex for _ in range(len(content_array))]
    is_honeypot_array = (
        [False] * len(content_array) if is_honeypot_array is None else is_honeypot_array
    )
    status_array = ["TODO"] * len(content_array) if not status_array else status_array
    formatted_json_metadata_array = process_metadata(
        input_type, content_array, json_content_array, json_metadata_array
    )
    mime_type = get_file_mimetype(content_array, json_content_array)
    content_array = process_content(input_type, content_array, json_content_array)
    formatted_json_content_array = process_json_content(
        input_type, content_array, json_content_array
    )

    request, upload_type = get_request_to_execute(
        input_type, json_metadata_array, json_content_array, mime_type
    )
    properties = {
        "content_array": content_array,
        "external_id_array": external_id_array,
        "is_honeypot_array": is_honeypot_array,
        "status_array": status_array,
        "json_content_array": formatted_json_content_array,
        "json_metadata_array": formatted_json_metadata_array,
    }

    return properties, upload_type, request


def process_update_properties_in_assets_parameters(properties) -> dict:
    """
    Process arguments of the update_properties_in_assets method
    and return the properties for the paginated loop
    """
    formatted_json_metadatas = None
    if properties["json_metadatas"] is None:
        formatted_json_metadatas = None
    else:
        if isinstance(properties["json_metadatas"], list):
            formatted_json_metadatas = list(map(format_metadata, properties["json_metadatas"]))
        else:
            raise Exception(
                "json_metadatas",
                "Should be either a None or a list of None, string, list or dict",
            )
    properties["json_metadatas"] = formatted_json_metadatas
    nb_assets_to_modify = len(properties["asset_ids"])
    properties = {
        k: convert_to_list_of_none(v, length=nb_assets_to_modify) for k, v in properties.items()
    }
    properties["should_reset_to_be_labeled_by_array"] = list(
        map(is_none_or_empty, properties["to_be_labeled_by_array"])
    )
    return properties


def generate_json_metadata_array(as_frames, fps, nb_files, input_type):
    """Generate the json_metadata_array for input of the append_many_to_dataset resolver
    when uploading from a list of path

    Args:
        as_frames: for a frame project, if videos should be split in frames
        fps: for a frame project, import videos with this frame rate
        nb_files: the number of files to upload in the call
        input_type: the input type of the project to upload to
    """

    json_metadata_array = None
    if input_type in ("FRAME", "VIDEO"):
        json_metadata_array = [
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": fps is None,
                    "framesPlayedPerSecond": fps,
                    "shouldUseNativeVideo": not as_frames,
                }
            }
        ] * nb_files
    return json_metadata_array
