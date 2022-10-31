# pylint: skip-file
"""Legacy code for importing assets, to be removed soon"""

import csv
import mimetypes
import os
from json import dumps
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union
from uuid import uuid4

from kili.authentication import KiliAuth
from kili.graphql.operations.asset.mutations import (
    GQL_APPEND_MANY_FRAMES_TO_DATASET,
    GQL_APPEND_MANY_TO_DATASET,
)
from kili.helpers import (
    check_file_mime_type,
    encode_base64,
    format_result,
    get_data_type,
    is_url,
)
from kili.orm import Asset
from kili.utils import bucket, pagination

from .base import LoggerParams, ProcessingParams, ProjectParams
from .types import AssetLike


class LegacyDataImporter:
    """Legacy Asset importer
    First switch form new list of dict paradigm to the old set of list one, then import assets"""

    def __init__(
        self,
        auth: KiliAuth,
        project_params: ProjectParams,
        processing_params: ProcessingParams,
        logger_params: LoggerParams,
    ):
        self.auth = auth
        self.project_id = project_params.project_id
        self.input_type = project_params.input_type

    def import_assets(self, assets: List[AssetLike]):
        def ternary(field: str, default=None) -> Optional[List[Any]]:
            if assets[0].get(field, None):
                return [asset.get(field, default) for asset in assets]
            else:
                return None

        content_array = ternary("content")
        json_content_array = ternary("json_content")
        external_id_array = ternary("external_id", uuid4().hex)
        status_array = ternary("status", "TODO")
        is_honeypot_array = ternary("is_honeypot", False)
        json_metadata_array = ternary("json_metadata", {})

        (properties_to_batch, upload_type, request,) = process_append_many_to_dataset_parameters(
            self,
            content_array,
            external_id_array,
            is_honeypot_array,
            status_array,
            json_content_array,
            json_metadata_array,
        )

        def generate_variables(batch):
            if request == GQL_APPEND_MANY_FRAMES_TO_DATASET:
                payload_data = {
                    "contentArray": batch["content_array"],
                    "externalIDArray": batch["external_id_array"],
                    "jsonMetadataArray": batch["json_metadata_array"],
                    "uploadType": upload_type,
                }
            else:
                payload_data = {
                    "contentArray": batch["content_array"],
                    "externalIDArray": batch["external_id_array"],
                    "isHoneypotArray": batch["is_honeypot_array"],
                    "statusArray": batch["status_array"],
                    "jsonContentArray": batch["json_content_array"],
                    "jsonMetadataArray": batch["json_metadata_array"],
                }
            return {"data": payload_data, "where": {"id": self.project_id}}

        results = pagination._mutate_from_paginated_call(
            self, properties_to_batch, generate_variables, request
        )
        return format_result("data", results[0], Asset)


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
    return dict(zip(json_content_index, json_content_urls))


def get_file_mimetype(
    content_array: Union[List[str], None], json_content_array: Union[List[str], None]
) -> Optional[str]:
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
    Process the array of json_contents and upload json if not already hosted
    """
    if json_content_array is None:
        return [""] * len(content_array)
    processed_json_content_array = []
    for json_content in json_content_array:
        if is_url(json_content):
            processed_json_content_array.append(json_content)
        else:
            if input_type in ("FRAME", "VIDEO"):
                json_content = process_frame_json_content(json_content)
            processed_json_content_array.append(dumps(json_content))
    return processed_json_content_array


def upload_content(signed_url: str, content: str, input_type: str):
    """
    Upload the content to a bucket if it is either a local file or raw text given for a TEXT project
    Args:
        content: the content to process, can be a local file or raw text
        signed_url: a signed_url to possibily use to upload the content
        input_type: input type of the project
    """
    if os.path.exists(content) and check_file_mime_type(content, input_type):
        with open(content, "rb") as file:
            data = file.read()
        content_type = get_data_type(content)
        uploaded_content_url = bucket.upload_data_via_rest(signed_url, data, content_type)
        return uploaded_content_url
    elif not os.path.exists(content) and input_type == "TEXT":
        data = content
        content_type = "text/plain"
        uploaded_content_url = bucket.upload_data_via_rest(signed_url, data, content_type)
        return uploaded_content_url
    else:
        raise ValueError(f"File: {content} not found")


def generate_unique_ids(size: int) -> List[str]:
    """
    Returns ids
    """
    return [bucket.generate_unique_id() for _ in range(size)]


# pylint: disable=too-many-arguments
def process_and_store_content(
    legacy_data_importer: LegacyDataImporter,
    content_array: List[str],
    json_content_array: Union[List[List[Union[dict, str]]], None],
) -> Tuple[List[str], List[str]]:
    """
    Process the array of contents and upload content if not already hosted
    """
    asset_ids = generate_unique_ids(len(content_array))
    if legacy_data_importer.input_type == "TIME_SERIES":
        return list(map(process_time_series, content_array)), asset_ids
    if json_content_array is not None:
        return content_array, asset_ids
    has_local_files = any(not is_url(content) for content in content_array)
    url_content_array = []
    if has_local_files:
        project_bucket_path = Path("projects") / legacy_data_importer.project_id / "assets"
        asset_content_paths = [
            Path(project_bucket_path) / asset_id / "content" for asset_id in asset_ids
        ]
        signed_urls = bucket.request_signed_urls(legacy_data_importer.auth, asset_content_paths)
    for i, content in enumerate(content_array):
        url_content = (is_url(content) and content) or upload_content(
            signed_urls[i], content, legacy_data_importer.input_type  # type:ignore X
        )
        url_content_array.append(url_content)
    return url_content_array, asset_ids


def process_time_series(content: str) -> str:
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
        return ""

    reader = csv.reader(content.split("\n"), delimiter=",")
    return process_csv_content(reader, delimiter=delimiter)


def is_float(number: str) -> bool:
    """
    Check if a string can be converted to float
    """
    try:
        float(number)
        return True
    except ValueError:
        return False


def process_csv_content(reader, file_name=None, delimiter=",") -> str:
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
            return ""
        value = row[1] if (is_float(row[1]) or first_row) else ""
        processed_lines.append(delimiter.join([row[0], value]))
        first_row = False
    return "\n".join(processed_lines)


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
    for key, default_value in video_parameters:
        processing_parameters[key] = processing_parameters.get(key, default_value)
    return {**json_metadata, "processingParameters": processing_parameters}


def process_metadata(
    input_type: str,
    content_array: List[str],
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
    mime_type: Optional[str],
) -> Tuple[str, Optional[str]]:
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


# pylint: disable=too-many-arguments, too-many-locals
def process_append_many_to_dataset_parameters(
    legacy_data_importer: LegacyDataImporter,
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
    if content_array is None:
        assert (
            json_content_array
        ), "When content_array is not passed, you should pass json_content_array"
        content_array = [""] * len(json_content_array)
    if external_id_array is None:
        external_id_array = [uuid4().hex for _ in range(len(content_array))]
    is_honeypot_array_ = (
        [False] * len(content_array) if is_honeypot_array is None else is_honeypot_array
    )
    status_array = ["TODO"] * len(content_array) if not status_array else status_array
    formatted_json_metadata_array = process_metadata(
        legacy_data_importer.input_type, content_array, json_content_array, json_metadata_array
    )

    mime_type = get_file_mimetype(content_array, json_content_array)  # type:ignore
    content_array, id_array = process_and_store_content(
        legacy_data_importer, content_array, json_content_array  # type:ignore X
    )
    formatted_json_content_array = process_json_content(
        legacy_data_importer.input_type,
        content_array,  # type:ignore X
        json_content_array,  # type:ignore X
    )

    request, upload_type = get_request_to_execute(
        legacy_data_importer.input_type, json_metadata_array, json_content_array, mime_type
    )
    properties = {
        "content_array": content_array,
        "external_id_array": external_id_array,
        "is_honeypot_array": is_honeypot_array_,
        "id_array": id_array,
        "status_array": status_array,
        "json_content_array": formatted_json_content_array,
        "json_metadata_array": formatted_json_metadata_array,
    }
    return (properties, upload_type, request)
