from collections import defaultdict
from typing import Dict, Generator, List, Optional, Tuple, Union, overload

from kili.domain.annotation import (
    Vertice,
    VideoAnnotation,
    VideoClassificationAnnotation,
    VideoClassificationKeyAnnotation,
    VideoObjectDetectionAnnotation,
    VideoObjectDetectionKeyAnnotation,
    VideoTranscriptionAnnotation,
    VideoTranscriptionKeyAnnotation,
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


@overload
def _key_annotations_iterator(
    annotation: VideoTranscriptionAnnotation
) -> Generator[
    Tuple[VideoTranscriptionKeyAnnotation, int, int, Optional[VideoTranscriptionKeyAnnotation]],
    None,
    None,
]:
    ...


@overload
def _key_annotations_iterator(
    annotation: VideoClassificationAnnotation
) -> Generator[
    Tuple[VideoClassificationKeyAnnotation, int, int, Optional[VideoClassificationKeyAnnotation]],
    None,
    None,
]:
    ...


@overload
def _key_annotations_iterator(
    annotation: VideoObjectDetectionAnnotation
) -> Generator[
    Tuple[VideoObjectDetectionKeyAnnotation, int, int, Optional[VideoObjectDetectionKeyAnnotation]],
    None,
    None,
]:
    ...


def _key_annotations_iterator(annotation: VideoAnnotation) -> Generator:
    """Helper to iterate over the key annotations of a video annotation.

    The key annotations are sorted by frame id.
    """
    sorted_key_annotations = sorted(
        annotation["keyAnnotations"], key=lambda key_ann: int(key_ann["frame"])
    )

    # iterate over the frame ranges of the annotation
    for frame_interval in annotation["frames"]:
        frame_range = range(frame_interval["start"], frame_interval["end"] + 1)
        for key_ann_index, key_ann in enumerate(sorted_key_annotations):
            # skip the key annotation if the key annotation start frame
            # is not in current frame range
            if key_ann["frame"] not in frame_range:
                continue

            # compute the key annotation frame range
            # the start frame of key annotation is given, but not the end frame
            key_ann_start = key_ann["frame"]
            key_ann_end = min(
                frame_interval["end"] + 1,
                sorted_key_annotations[key_ann_index + 1]["frame"]
                if key_ann_index + 1 < len(sorted_key_annotations)
                else frame_interval["end"] + 1,
            )

            # get the next key annotation, if it exists
            next_key_ann = (
                sorted_key_annotations[key_ann_index + 1]
                if key_ann_index + 1 < len(sorted_key_annotations)
                else None
            )

            yield key_ann, key_ann_start, key_ann_end, next_key_ann


def _video_transcription_annotation_to_json_response(
    annotation: VideoTranscriptionAnnotation,
) -> Dict[str, Dict[JobName, Dict]]:
    """Convert video transcription annotation to a json response.

    Transcription jobs cannot have child jobs.
    """
    json_resp: Dict[str, Dict[JobName, Dict]] = defaultdict(dict)

    for key_ann, key_ann_start, key_ann_end, _ in _key_annotations_iterator(annotation):
        for frame_id in range(key_ann_start, key_ann_end):
            json_resp[str(frame_id)][annotation["job"]] = {
                "isKeyFrame": frame_id == key_ann_start,
                "text": key_ann["annotationValue"]["text"],
            }

    return json_resp


def _get_child_annotations(
    annotation: VideoAnnotation, other_annotations: List[VideoAnnotation]
) -> List[Union[VideoTranscriptionAnnotation, VideoClassificationAnnotation]]:
    """Get the child annotations (child jobs) of a video annotation."""
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
    """Compute the video json response of the child jobs of a video annotation."""
    children_json_resp = defaultdict(dict)

    for child_ann in child_annotations:
        if trycast(child_ann, VideoClassificationAnnotation):
            sub_job_resp = _video_classification_annotation_to_json_response(
                child_ann,
                _get_child_annotations(child_ann, other_annotations),  # pyright: ignore[reportGeneralTypeIssues]
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
        _compute_children_json_resp(
            child_annotations, [ann for ann in other_annotations if ann not in child_annotations]
        )
        if child_annotations
        else {}
    )

    json_resp: Dict[str, Dict[JobName, Dict]] = defaultdict(dict)

    for key_ann, key_ann_start, key_ann_end, _ in _key_annotations_iterator(annotation):
        for frame_id in range(key_ann_start, key_ann_end):
            # initialize the frame json response
            json_resp[str(frame_id)][annotation["job"]] = {
                "categories": [],
                "isKeyFrame": frame_id == key_ann_start,
            }

            # get the frame json response of child jobs
            child_jobs_frame_json_resp = json_resp_child_jobs.get(str(frame_id), {})

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
    # get the child annotations of the current annotation
    # and compute the json response of those child jobs
    child_annotations = _get_child_annotations(annotation, other_annotations)
    json_resp_child_jobs = (
        _compute_children_json_resp(
            child_annotations, [ann for ann in other_annotations if ann not in child_annotations]
        )
        if child_annotations
        else {}
    )

    json_resp = defaultdict(dict)

    for key_ann, key_ann_start, key_ann_end, next_key_ann in _key_annotations_iterator(annotation):
        for frame_id in range(key_ann_start, key_ann_end):
            # get the frame json response of child jobs
            child_jobs_frame_json_resp = json_resp_child_jobs.get(str(frame_id), {})

            annotation_dict = {
                "children": child_jobs_frame_json_resp,
                "isKeyFrame": frame_id == key_ann_start,
                "categories": [{"name": annotation["category"]}],
                "mid": annotation["mid"],
                "type": json_interface["jobs"][annotation["job"]]["tools"][0],
            }

            # between two key frame annotations, an object (point, bbox, polygon) is
            # interpolated in the UI
            if frame_id == key_ann_start:
                norm_vertices = key_ann["annotationValue"]["vertices"][0][0]

            else:
                object_inital_state = key_ann["annotationValue"]["vertices"][0][0]
                object_final_state = (
                    next_key_ann["annotationValue"]["vertices"][0][0]
                    if next_key_ann is not None
                    else object_inital_state
                )
                norm_vertices = _interpolate_object_(
                    object_initial_state=object_inital_state,
                    initial_state_frame_index=key_ann_start,
                    object_final_state=object_final_state,
                    final_state_frame_index=key_ann_end,
                    at_frame=frame_id,
                )

            if json_interface["jobs"][annotation["job"]]["tools"] == ["marker"]:  # point job
                annotation_dict["point"] = norm_vertices[0]

            else:  # bbox or polygon jobs
                annotation_dict["boundingPoly"] = [{"normalizedVertices": norm_vertices}]

            json_resp[str(frame_id)].setdefault(annotation["job"], {}).setdefault(
                "annotations", []
            ).append(annotation_dict)

    return json_resp


def _interpolate_vertex(
    vertex_initial_state: Vertice,
    vertex_final_state: Vertice,
    initial_state_frame_index: int,
    final_state_frame_index: int,
    at_frame: int,
) -> Vertice:
    """Generate vertex at some frame between two vertice states."""
    nb_frames_in_between = final_state_frame_index - initial_state_frame_index

    return Vertice(
        x=vertex_initial_state["x"]
        + (vertex_final_state["x"] - vertex_initial_state["x"])
        * (at_frame - initial_state_frame_index)
        / nb_frames_in_between,
        y=vertex_initial_state["y"]
        + (vertex_final_state["y"] - vertex_initial_state["y"])
        * (at_frame - initial_state_frame_index)
        / nb_frames_in_between,
    )


def _interpolate_object_(
    *,
    object_initial_state: List[Vertice],
    initial_state_frame_index: int,
    object_final_state: List[Vertice],
    final_state_frame_index: int,
    at_frame: int,
) -> List[Vertice]:
    """Interpolate the bounding boxes between two frames."""
    # if the two frames are consecutive, we do not interpolate
    if at_frame == initial_state_frame_index:
        return object_initial_state

    if at_frame == final_state_frame_index:
        return object_final_state

    return [
        _interpolate_vertex(
            vertex_initial_state=object_initial_state[vertex_index],
            vertex_final_state=object_final_state[vertex_index],
            initial_state_frame_index=initial_state_frame_index,
            final_state_frame_index=final_state_frame_index,
            at_frame=at_frame,
        )
        for vertex_index in range(len(object_initial_state))
    ]
