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
    annotations: List[VideoAnnotation], json_interface: Dict
) -> Dict[str, Dict[JobName, Dict]]:
    """Convert video label annotations to a video json response."""
    json_resp = defaultdict(dict)

    for i, ann in enumerate(annotations):
        if ann["path"]:  # skip child annotations
            continue

        other_annotations = annotations[:i] + annotations[i + 1 :]

        if trycast(ann, VideoObjectDetectionAnnotation):
            ann_json_resp = _video_object_detection_annotation_to_json_response(
                ann, other_annotations, json_interface=json_interface
            )
            for frame_id, frame_json_resp in ann_json_resp.items():
                for job_name, job_resp in frame_json_resp.items():
                    json_resp[frame_id].setdefault(job_name, {}).setdefault(
                        "annotations", []
                    ).extend(job_resp["annotations"])

        elif trycast(ann, VideoClassificationAnnotation):
            ann_json_resp = _video_classification_annotation_to_json_response(
                ann, other_annotations
            )
            for frame_id, frame_json_resp in ann_json_resp.items():
                for job_name, job_resp in frame_json_resp.items():
                    json_resp[frame_id].setdefault(job_name, {}).setdefault(
                        "categories", []
                    ).extend(job_resp["categories"])
                    json_resp[frame_id][job_name]["isKeyFrame"] = job_resp["isKeyFrame"]

        elif trycast(ann, VideoTranscriptionAnnotation):
            ann_json_resp = _video_transcription_annotation_to_json_response(ann)
            for frame_id, frame_json_resp in ann_json_resp.items():
                json_resp[frame_id] = {**json_resp[frame_id], **frame_json_resp}

        else:
            raise NotImplementedError(f"Cannot convert annotation to json response: {ann}")

    # sort by frame id
    return dict(sorted(json_resp.items(), key=lambda item: int(item[0])))


def _video_transcription_annotation_to_json_response(
    annotation: VideoTranscriptionAnnotation,
) -> Dict[str, Dict[JobName, Dict]]:
    """Convert video transcription annotation to json response.

    Transcription jobs cannot have child jobs.
    """
    json_resp: Dict[str, Dict[JobName, Dict]] = defaultdict(dict)

    for frame_interval in annotation["frames"]:
        # range of frames on which the annotation lies
        frame_range = range(frame_interval["start"], frame_interval["end"] + 1)
        for frame_id in frame_range:
            for key_ann_index, key_ann in enumerate(annotation["keyAnnotations"]):
                # skip the key annotation if the key annotation start frame
                # is not in current frame range
                if key_ann["frame"] not in frame_range:
                    continue

                # compute the key annotation frame range
                key_ann_start = key_ann["frame"]
                key_ann_end = min(
                    frame_interval["end"] + 1,
                    annotation["keyAnnotations"][key_ann_index + 1]["frame"]
                    if key_ann_index + 1 < len(annotation["keyAnnotations"])
                    else float("inf"),
                )

                # if the current frame id is not within the key annotation range, we skip
                if not key_ann_start <= frame_id < key_ann_end:
                    continue

                json_resp[str(frame_id)][annotation["job"]] = {
                    "isKeyFrame": frame_id == key_ann_start,
                    "text": key_ann["annotationValue"]["text"],
                }

    return json_resp


def _get_child_annotations(
    annotation: VideoAnnotation, other_annotations: List[VideoAnnotation]
) -> List[Union[VideoTranscriptionAnnotation, VideoClassificationAnnotation]]:
    return [
        ann
        for ann in other_annotations
        # ann["path"] is a list of couples (annotationId, category)
        if ann["path"]
        and any(path[0] == annotation["id"] for path in ann["path"])
        # a subjob can only be a transcription or classification job
        and (
            trycast(ann, VideoTranscriptionAnnotation)
            or trycast(ann, VideoClassificationAnnotation)
        )
    ]


def _compute_children_json_resp(
    child_annotations: List[Union[VideoTranscriptionAnnotation, VideoClassificationAnnotation]],
    other_annotations: List[VideoAnnotation],
) -> Dict[str, Dict[JobName, Dict]]:
    children_json_resp = defaultdict(dict)
    for child_ann in child_annotations:
        if trycast(child_ann, VideoClassificationAnnotation):
            sub_job_resp = _video_classification_annotation_to_json_response(
                child_ann, other_annotations
            )
        elif trycast(child_ann, VideoTranscriptionAnnotation):
            sub_job_resp = _video_transcription_annotation_to_json_response(child_ann)
        else:
            raise NotImplementedError(
                f"Cannot convert child annotation to json response: {child_ann}"
            )

        for frame_id, frame_json_resp in sub_job_resp.items():
            children_json_resp[frame_id] = {
                **children_json_resp[frame_id],
                **frame_json_resp,
            }

    return children_json_resp


def _video_classification_annotation_to_json_response(
    annotation: VideoClassificationAnnotation,
    other_annotations: List[VideoAnnotation],
) -> Dict[str, Dict[JobName, Dict]]:
    # get the child annotations of the current annotation
    # and compute the json response of those child jobs
    child_annotations = _get_child_annotations(annotation, other_annotations)
    json_resp_child_jobs = (
        _compute_children_json_resp(child_annotations, other_annotations)
        if child_annotations
        else {}
    )

    json_resp: Dict[str, Dict[JobName, Dict]] = defaultdict(dict)

    for frame_interval in annotation["frames"]:
        # range of frames on which the annotation lies
        frame_range = range(frame_interval["start"], frame_interval["end"] + 1)
        for frame_id in frame_range:
            # get the frame json response of child jobs
            child_jobs_frame_json_resp = json_resp_child_jobs.get(str(frame_id), {})

            for key_ann_index, key_ann in enumerate(annotation["keyAnnotations"]):
                # skip the key annotation if the key annotation start frame
                # is not in current frame range
                if key_ann["frame"] not in frame_range:
                    continue

                # compute the key annotation frame range
                key_ann_start = key_ann["frame"]
                key_ann_end = min(
                    frame_interval["end"] + 1,
                    annotation["keyAnnotations"][key_ann_index + 1]["frame"]
                    if key_ann_index + 1 < len(annotation["keyAnnotations"])
                    else float("inf"),
                )

                # if the current frame id is not within the key annotation range, we skip
                if not key_ann_start <= frame_id < key_ann_end:
                    continue

                # initialize the frame json response
                json_resp[str(frame_id)][annotation["job"]] = {
                    "categories": [],
                    "isKeyFrame": frame_id == key_ann_start,
                }

                # a frame can have one or multiple categories
                categories = key_ann["annotationValue"]["categories"]
                for category in categories:
                    category_annotation: Dict = {"name": category}

                    # search among the child annotations the ones
                    # that have a path (annotationId, category)
                    children_json_resp = {}
                    for child_ann in child_annotations:
                        if [annotation["id"], category] in child_ann["path"] and child_ann[
                            "job"
                        ] in child_jobs_frame_json_resp:
                            children_json_resp[child_ann["job"]] = child_jobs_frame_json_resp[
                                child_ann["job"]
                            ]

                    if children_json_resp:
                        category_annotation["children"] = children_json_resp

                    json_resp[str(frame_id)][annotation["job"]]["categories"].append(
                        category_annotation
                    )

    return json_resp


def _video_object_detection_annotation_to_json_response(
    annotation: VideoObjectDetectionAnnotation,
    other_annotations: List[VideoAnnotation],
    json_interface: Dict,
) -> Dict[str, Dict[JobName, Dict]]:
    child_annotations = _get_child_annotations(annotation, other_annotations)
    json_resp = defaultdict(dict)

    category = annotation["category"]
    job_name = annotation["job"]
    norm_vertices = annotation["keyAnnotations"][0]["annotationValue"]["vertices"][0][
        0
    ]  # TODO: fix

    frames_json_resp_child_jobs = defaultdict(dict)
    for child_ann in child_annotations:
        if trycast(child_ann, VideoClassificationAnnotation):
            sub_job_resp = _video_classification_annotation_to_json_response(child_ann, [])
        elif trycast(child_ann, VideoTranscriptionAnnotation):
            sub_job_resp = _video_transcription_annotation_to_json_response(child_ann)
        else:
            raise NotImplementedError(
                f"Cannot convert child annotation to json response: {child_ann}"
            )

        for frame_id, frame_json_resp in sub_job_resp.items():
            frames_json_resp_child_jobs[frame_id] = {
                **frames_json_resp_child_jobs[frame_id],
                **frame_json_resp,
            }

    for frame_interval in annotation["frames"]:
        frame_range = range(frame_interval["start"], frame_interval["end"] + 1)
        for frame_id in frame_range:
            # initialize the frame json response
            json_resp[str(frame_id)][job_name] = {"annotations": []}

            child_jobs_json_resp_value = (
                frames_json_resp_child_jobs[str(frame_id)]
                if str(frame_id) in frames_json_resp_child_jobs
                else {}
            )

            annotation_dict = {
                "children": child_jobs_json_resp_value,
                "isKeyFrame": frame_id == frame_interval["start"],
                "categories": [{"name": category}],
                "mid": annotation["mid"],
                "type": json_interface["jobs"][job_name]["tools"][0],
            }

            if json_interface["jobs"][job_name]["tools"] == ["marker"]:  # point job
                annotation_dict["point"] = norm_vertices[0]

            else:
                annotation_dict["boundingPoly"] = [{"normalizedVertices": norm_vertices}]
            json_resp[str(frame_id)][job_name]["annotations"].append(annotation_dict)
    return json_resp
