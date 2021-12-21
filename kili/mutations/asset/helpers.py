"""
Helpers for the asset mutations
"""
from json import dumps
from uuid import uuid4
from typing import List, Union

from ...helpers import encode_base64, is_url
from .queries import (GQL_APPEND_MANY_TO_DATASET,
                      GQL_APPEND_MANY_FRAMES_TO_DATASET)


def encode_object_if_not_url(content):
    """
    Return the object if it is a url, else it should be a path to a file.
    In that case, the file is returned as a base64 string
    """
    if is_url(content):
        return content
    return encode_base64(content)


def process_frame_json_content(json_content):
    """
    Function to process individual json_content of FRAME projects
    """
    if is_url(json_content):
        return json_content
    json_content_index = range(len(json_content))
    json_content_urls = list(map(encode_object_if_not_url, json_content))
    return dumps(dict(zip(json_content_index, json_content_urls)))


def process_json_content(input_type: str,
                         content_array: List[str],
                         json_content_array: Union[List[str], None]):
    """
    Process the array of json_contents
    """
    if json_content_array is None:
        return [''] * len(content_array)
    if input_type == 'FRAME':
        return list(map(process_frame_json_content, json_content_array))
    return [element if is_url(element) else dumps(element) for element in json_content_array]


def process_content(input_type: str,
                    content_array: Union[List[str], None],
                    json_content_array: Union[List[List[Union[dict, str]]], None]):
    """
    Process the array of contents
    """
    if input_type in ['IMAGE', 'PDF']:
        return [content if is_url(content) else encode_base64(
            content) for content in content_array]
    if input_type == 'FRAME' and json_content_array is None:
        content_array = list(map(encode_object_if_not_url, content_array))
    return content_array


def add_video_parameters(json_metadata, should_use_native_video):
    """
    Add necessary video parameters to the metadata of the video
    """
    processing_parameters = json_metadata.get('processingParameters', {})
    video_parameters = [('shouldKeepNativeFrameRate', should_use_native_video), (
        'framesPlayedPerSecond', 30), ('shouldUseNativeVideo', should_use_native_video)]
    for (key, default_value) in video_parameters:
        processing_parameters[key] = processing_parameters.get(
            key, default_value)
    return {**json_metadata, 'processingParameters': processing_parameters}


def process_metadata(input_type: str, content_array: Union[List[str], None],
                     json_content_array: Union[List[List[Union[dict, str]]], None],
                     json_metadata_array: Union[List[dict], None]):
    """
    Process the metadata of each asset
    """
    json_metadata_array = [
        {}] * len(content_array) if json_metadata_array is None else json_metadata_array
    if input_type == 'FRAME':
        should_use_native_video = json_content_array is None
        json_metadata_array = [add_video_parameters(
            json_metadata, should_use_native_video) for json_metadata in json_metadata_array]
    return list(map(dumps, json_metadata_array))


def get_request_to_execute(
    input_type: str,
    json_metadata_array: Union[List[dict], None],
    json_content_array: Union[List[List[Union[dict, str]]], None]
) -> str:
    """
    Selects the right query to run versus the data given
    """
    if input_type != 'FRAME' or json_content_array is not None:
        return GQL_APPEND_MANY_TO_DATASET
    if json_metadata_array is None:
        return GQL_APPEND_MANY_TO_DATASET
    if (isinstance(json_metadata_array, list) and
        len(json_metadata_array) > 0 and
        not json_metadata_array[0].get(
            'processingParameters', {}).get('shouldUseNativeVideo', True)):
        return GQL_APPEND_MANY_FRAMES_TO_DATASET
    return GQL_APPEND_MANY_TO_DATASET


# pylint: disable=too-many-arguments
def process_append_many_to_dataset_parameters(
        input_type: str,
        content_array: Union[List[str], None],
        external_id_array: Union[List[str], None],
        is_honeypot_array: Union[List[str], None],
        status_array: Union[List[str], None],
        json_content_array: Union[List[List[Union[dict, str]]], None],
        json_metadata_array: Union[List[dict], None]
) -> dict:
    """
    Process arguments of the append_many_to_dataset method and return the data payload.
    """
    if content_array is None and json_content_array is None:
        raise ValueError(
            "Variables content_array and json_content_array cannot be both None.")
    if content_array is None:
        content_array = [''] * len(json_content_array)
    if external_id_array is None:
        external_id_array = [
            uuid4().hex for _ in range(len(content_array))]
    is_honeypot_array = [
        False] * len(content_array) if is_honeypot_array is None else is_honeypot_array
    status_array = ['TODO'] * \
        len(content_array) if not status_array else status_array
    formatted_json_metadata_array = process_metadata(
        input_type, content_array, json_content_array, json_metadata_array)
    content_array = process_content(
        input_type, content_array, json_content_array)
    formatted_json_content_array = process_json_content(
        input_type, content_array, json_content_array)

    request = get_request_to_execute(
        input_type, json_metadata_array, json_content_array)
    if request == GQL_APPEND_MANY_FRAMES_TO_DATASET:
        payload_data = {'contentArray': content_array,
                        'externalIDArray': external_id_array,
                        'jsonMetadataArray': formatted_json_metadata_array}
    else:
        payload_data = {'contentArray': content_array,
                        'externalIDArray': external_id_array,
                        'isHoneypotArray': is_honeypot_array,
                        'statusArray': status_array,
                        'jsonContentArray': formatted_json_content_array,
                        'jsonMetadataArray': formatted_json_metadata_array}

    return payload_data, request
