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
                parent_ann, child_annotations, json_interface=json_interface
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
                for job_name, job_resp in frame_json_resp.items():
                    if job_name not in json_resp[frame_id]:
                        json_resp[frame_id][job_name] = job_resp
                    else:
                        json_resp[frame_id][job_name]["categories"].extend(job_resp["categories"])

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
    job_name = ann["job"]

    json_resp = defaultdict(dict)

    frames_json_resp_child_jobs = defaultdict(dict)
    for child_ann in child_anns:
        if trycast(child_ann, VideoClassificationAnnotation):
            sub_job_resp = _video_classification_annotation_to_json_response(child_ann, [])
        elif trycast(child_ann, VideoTranscriptionAnnotation):
            sub_job_resp = _video_transcription_annotation_to_json_response(child_ann, [])
        else:
            raise NotImplementedError(
                f"Cannot convert child annotation to json response: {child_ann}"
            )

        for frame_id, frame_json_resp in sub_job_resp.items():
            frames_json_resp_child_jobs[frame_id] = {
                **frames_json_resp_child_jobs[frame_id],
                **frame_json_resp,
            }

    for frame_interval in ann["frames"]:
        frame_range = range(frame_interval["start"], frame_interval["end"] + 1)
        for frame_id in frame_range:
            # initialize the frame json response
            json_resp[str(frame_id)][job_name] = {
                "categories": [],
                "isKeyFrame": frame_id == frame_interval["start"],
            }

            # get the frame json response of child jobs
            child_jobs_frame_json_resp = (
                frames_json_resp_child_jobs[str(frame_id)]
                if str(frame_id) in frames_json_resp_child_jobs
                else {}
            )

            for key_annotation in ann["keyAnnotations"]:
                if key_annotation["frame"] not in frame_range:
                    continue

                # a frame can have one or multiple categories
                categories = key_annotation["annotationValue"]["categories"]
                for category in categories:
                    # search among the child annotations the ones
                    # that have a path (annotationId, category)
                    children_json_resp = {}
                    for child_ann in child_anns:
                        if [ann["id"], category] in child_ann["path"]:
                            children_json_resp[child_ann["job"]] = child_jobs_frame_json_resp[
                                child_ann["job"]
                            ]

                    category_annotation = {"name": category, "children": children_json_resp}

                    if not category_annotation["children"]:
                        del category_annotation["children"]

                    json_resp[str(frame_id)][job_name]["categories"].append(category_annotation)
    return json_resp


def _video_object_detection_annotation_to_json_response(
    ann: VideoObjectDetectionAnnotation,
    child_anns: List[Union[VideoClassificationAnnotation, VideoTranscriptionAnnotation]],
    json_interface: Dict,
) -> Dict[str, Dict[JobName, Dict]]:
    json_resp = defaultdict(dict)

    category = ann["category"]
    job_name = ann["job"]
    norm_vertices = ann["keyAnnotations"][0]["annotationValue"]["vertices"][0][0]  # TODO: fix

    frames_json_resp_child_jobs = defaultdict(dict)
    for child_ann in child_anns:
        if trycast(child_ann, VideoClassificationAnnotation):
            sub_job_resp = _video_classification_annotation_to_json_response(child_ann, [])
        elif trycast(child_ann, VideoTranscriptionAnnotation):
            sub_job_resp = _video_transcription_annotation_to_json_response(child_ann, [])
        else:
            raise NotImplementedError(
                f"Cannot convert child annotation to json response: {child_ann}"
            )

        for frame_id, frame_json_resp in sub_job_resp.items():
            frames_json_resp_child_jobs[frame_id] = {
                **frames_json_resp_child_jobs[frame_id],
                **frame_json_resp,
            }

    for frame_interval in ann["frames"]:
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
                "mid": ann["mid"],
                "type": json_interface["jobs"][job_name]["tools"][0],
            }

            if json_interface["jobs"][job_name]["tools"] == ["marker"]:  # point job
                annotation_dict["point"] = norm_vertices[0]

            else:
                annotation_dict["boundingPoly"] = [{"normalizedVertices": norm_vertices}]
            json_resp[str(frame_id)][job_name]["annotations"].append(annotation_dict)
    return json_resp
