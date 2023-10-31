from collections import defaultdict
from typing import Dict, List

from kili.domain.annotation import (
    VideoAnnotation,
    VideoClassificationAnnotation,
    VideoObjectDetectionAnnotation,
    VideoTranscriptionAnnotation,
)
from kili.domain.ontology import JobName
from kili.utils.typed_dict import trycast


def video_label_annotations_to_json_response(
    annotations: List[VideoAnnotation]
) -> Dict[str, Dict[JobName, Dict]]:
    """Convert video label annotations to json response."""
    json_resp = defaultdict(dict)

    for ann in annotations:
        if trycast(ann, VideoObjectDetectionAnnotation):
            ann_json_resp = _video_object_detection_annotation_to_json_response(ann)

        elif trycast(ann, VideoClassificationAnnotation):
            ann_json_resp = _video_classification_annotation_to_json_response(ann)

        elif trycast(ann, VideoTranscriptionAnnotation):
            ann_json_resp = _video_transcription_annotation_to_json_response(ann)

        else:
            raise NotImplementedError

        for frame_id, job_dict in ann_json_resp.items():
            json_resp[frame_id] = {**json_resp[frame_id], **job_dict}

    return json_resp


def _video_transcription_annotation_to_json_response(
    ann: VideoTranscriptionAnnotation
) -> Dict[str, Dict[JobName, Dict]]:
    json_resp = defaultdict(dict)

    job_name = ann["job"]

    for frame_interval in ann["frames"]:
        interval_start = frame_interval["start"]
        interval_end = frame_interval["end"]
        frame_range = range(interval_start, interval_end + 1)
        for frame_id in frame_range:
            for key_annotation in ann["keyAnnotations"]:
                text = key_annotation["annotationValue"]["text"]
                frame = key_annotation["frame"]
                if frame in frame_range:
                    json_resp[str(frame_id)] = {
                        **json_resp[str(frame_id)],
                        job_name: {
                            "isKeyFrame": frame_id == interval_start,
                            "text": text,
                        },
                    }

    return json_resp


def _video_classification_annotation_to_json_response(
    ann: VideoClassificationAnnotation
) -> Dict[str, Dict[JobName, Dict]]:
    json_resp = defaultdict(dict)

    job_name = ann["job"]
    category = ann["keyAnnotations"][0]["annotationValue"]["categories"][0]  # TODO: fix
    for frame_interval in ann["frames"]:
        interval_start = frame_interval["start"]
        interval_end = frame_interval["end"]
        for frame_id in range(interval_start, interval_end + 1):
            json_resp[str(frame_id)] = {
                **json_resp[str(frame_id)],
                job_name: {
                    "categories": [{"name": category, "children": {}}],  # TODO: fix
                    "isKeyFrame": frame_id == interval_start,
                },
            }
    return json_resp


def _video_object_detection_annotation_to_json_response(
    ann: VideoObjectDetectionAnnotation
) -> Dict[str, Dict[JobName, Dict]]:
    json_resp = defaultdict(dict)

    category = ann["category"]
    job_name = ann["job"]
    norm_vertices = ann["keyAnnotations"][0]["annotationValue"]["vertices"][0][0]  # TODO: fix

    for frame_interval in ann["frames"]:
        interval_start = frame_interval["start"]
        interval_end = frame_interval["end"]
        for frame_id in range(interval_start, interval_end + 1):
            json_resp[str(frame_id)] = {
                **json_resp[str(frame_id)],
                job_name: {
                    "annotations": [
                        {
                            "children": {},  # TODO: fix
                            "isKeyFrame": frame_id == interval_start,
                            "boundingPoly": [{"normalizedVertices": norm_vertices}],
                            "categories": [{"name": category}],
                            "mid": ann["mid"],
                            "type": "rectangle",  # TODO: fix
                        }
                    ]
                },
            }

    return json_resp
