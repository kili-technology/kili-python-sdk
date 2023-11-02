from collections import defaultdict
from typing import Dict, List, Union

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

    parent_annotations = [ann for ann in annotations if not ann["path"]]

    for parent_ann in parent_annotations:
        parent_ann_id = parent_ann["id"]
        child_annotations = [
            ann
            for ann in annotations
            # ann["path"] is a list of couples (annotationId, category)
            if ann["path"]
            and any(path[0] == parent_ann_id for path in ann["path"])
            # a subjob can only be a transcription or classification job
            and (
                trycast(ann, VideoTranscriptionAnnotation)
                or trycast(ann, VideoClassificationAnnotation)
            )
        ]

        if trycast(parent_ann, VideoObjectDetectionAnnotation):
            ann_json_resp = _video_object_detection_annotation_to_json_response(
                parent_ann, child_annotations
            )
            for frame_id, frame_json_resp in ann_json_resp.items():
                for job_name, job_resp in frame_json_resp.items():
                    if job_name not in json_resp[frame_id]:
                        json_resp[frame_id][job_name] = job_resp
                    else:
                        json_resp[frame_id][job_name]["annotations"].extend(job_resp["annotations"])

        elif trycast(parent_ann, VideoClassificationAnnotation):
            ann_json_resp = _video_classification_annotation_to_json_response(
                parent_ann, child_annotations
            )
            for frame_id, frame_json_resp in ann_json_resp.items():
                json_resp[frame_id] = {**json_resp[frame_id], **frame_json_resp}

        elif trycast(parent_ann, VideoTranscriptionAnnotation):
            ann_json_resp = _video_transcription_annotation_to_json_response(
                parent_ann, child_annotations
            )
            for frame_id, frame_json_resp in ann_json_resp.items():
                json_resp[frame_id] = {**json_resp[frame_id], **frame_json_resp}

        else:
            raise NotImplementedError(f"Cannot convert annotation to json response: {parent_ann}")

    # sort by frame id
    return dict(sorted(json_resp.items(), key=lambda item: int(item[0])))


def _video_transcription_annotation_to_json_response(
    ann: VideoTranscriptionAnnotation,
    child_anns: List[Union[VideoClassificationAnnotation, VideoTranscriptionAnnotation]],
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
    ann: VideoClassificationAnnotation,
    child_anns: List[Union[VideoClassificationAnnotation, VideoTranscriptionAnnotation]],
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
    ann: VideoObjectDetectionAnnotation,
    child_anns: List[Union[VideoClassificationAnnotation, VideoTranscriptionAnnotation]],
) -> Dict[str, Dict[JobName, Dict]]:
    json_resp = defaultdict(dict)

    category = ann["category"]
    job_name = ann["job"]
    norm_vertices = ann["keyAnnotations"][0]["annotationValue"]["vertices"][0][0]  # TODO: fix

    frames_json_resp_child_jobs = {}
    for child_ann in child_anns:
        if trycast(child_ann, VideoClassificationAnnotation):
            sub_job_resp = _video_classification_annotation_to_json_response(child_ann, [])
        elif trycast(child_ann, VideoTranscriptionAnnotation):
            sub_job_resp = _video_transcription_annotation_to_json_response(child_ann, [])
        else:
            raise NotImplementedError(
                f"Cannot convert child annotation to json response: {child_ann}"
            )
        frames_json_resp_child_jobs = {**frames_json_resp_child_jobs, **sub_job_resp}

    for frame_interval in ann["frames"]:
        interval_start = frame_interval["start"]
        interval_end = frame_interval["end"]
        for frame_id in range(interval_start, interval_end + 1):
            child_jobs_json_resp_value = (
                frames_json_resp_child_jobs[str(frame_id)]
                if str(frame_id) in frames_json_resp_child_jobs
                else {}
            )
            json_resp[str(frame_id)] = {
                **json_resp[str(frame_id)],
                job_name: {
                    "annotations": [
                        {
                            "children": child_jobs_json_resp_value,
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
