"""Annotation object to json response converter."""
import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generator, List, Optional, Tuple, TypeVar, Union, cast, overload

from kili.domain.annotation import (
    ClassicAnnotation,
    ClassificationAnnotation,
    RankingAnnotation,
    TranscriptionAnnotation,
    Vertice,
    VideoAnnotation,
    VideoClassificationAnnotation,
    VideoClassificationKeyAnnotation,
    VideoObjectDetectionAnnotation,
    VideoObjectDetectionKeyAnnotation,
    VideoTranscriptionAnnotation,
    VideoTranscriptionKeyAnnotation,
)
from kili.domain.ontology import JobName, JobTool


class AnnotationsToJsonResponseConverter:
    """Convert annotations to JSON response."""

    def __init__(self, project_input_type: str, json_interface) -> None:
        """Initialize the converter."""
        self._project_input_type = project_input_type
        self._project_json_interface = json_interface

    def _label_has_json_response_data(self, label: Dict) -> bool:
        if self._project_input_type == "VIDEO":
            job_names_in_json_resp = {
                job_name for frame_resp in label["jsonResponse"].values() for job_name in frame_resp
            }
        else:
            job_names_in_json_resp = set(label["jsonResponse"].keys())

        if any(
            job_name in job_names_in_json_resp for job_name in self._project_json_interface["jobs"]
        ):
            return True

        return False

    def patch_label_json_response(
        self, label: Dict, annotations: Union[List[VideoAnnotation], List[ClassicAnnotation]]
    ) -> None:
        """Patch the label json response using the annotations.

        Modifies the input label.
        """
        if self._project_input_type in {"VIDEO", "LLM_RLHF"}:
            if not annotations and self._label_has_json_response_data(label):
                return

            if self._project_input_type == "VIDEO":
                annotations = cast(List[VideoAnnotation], annotations)
                converted_json_resp = _video_annotations_to_json_response(
                    annotations=annotations, json_interface=self._project_json_interface
                )
            else:
                annotations = cast(List[ClassicAnnotation], annotations)
                converted_json_resp = _classic_annotations_to_json_response(annotations=annotations)

            label["jsonResponse"] = converted_json_resp


def _add_annotation_metadata(annotations: List[VideoAnnotation], json_response: Dict) -> None:
    for ann in annotations:
        if ann["__typename"] == "VideoObjectDetectionAnnotation":
            ann = cast(VideoObjectDetectionAnnotation, ann)
            job_counter = (
                json_response["0"]
                .setdefault("ANNOTATION_JOB_COUNTER", {})
                .setdefault(ann["job"], defaultdict(int))
            )
            job_counter[ann["category"]] += 1
            json_response["0"].setdefault("ANNOTATION_NAMES_JOB", {})[ann["mid"]] = ann["name"]


def _fill_empty_frames(json_response: Dict) -> None:
    max_frame_id = max((int(frame_id) for frame_id in json_response), default=-1)
    for frame_id in range(max_frame_id + 1):
        json_response.setdefault(str(frame_id), {})


def _video_annotations_to_json_response(
    annotations: List[VideoAnnotation], json_interface: Dict
) -> Dict[str, Dict[JobName, Dict]]:
    """Convert video label annotations to a video json response."""
    json_resp = defaultdict(dict)

    for i, ann in enumerate(annotations):
        if ann["path"]:  # skip child annotations
            continue

        other_annotations = annotations[:i] + annotations[i + 1 :]

        if ann["__typename"] == "VideoObjectDetectionAnnotation":
            ann = cast(VideoObjectDetectionAnnotation, ann)
            ann_json_resp = _video_object_detection_annotation_to_json_response(
                ann, other_annotations, json_interface=json_interface
            )
            for frame_id, frame_json_resp in ann_json_resp.items():
                for job_name, job_resp in frame_json_resp.items():
                    json_resp[frame_id].setdefault(job_name, {}).setdefault(
                        "annotations", []
                    ).extend(job_resp["annotations"])

        elif ann["__typename"] == "VideoClassificationAnnotation":
            ann = cast(VideoClassificationAnnotation, ann)
            ann_json_resp = _video_classification_annotation_to_json_response(
                ann, other_annotations
            )
            for frame_id, frame_json_resp in ann_json_resp.items():
                for job_name, job_resp in frame_json_resp.items():
                    json_resp[frame_id].setdefault(job_name, {}).setdefault(
                        "categories", []
                    ).extend(job_resp["categories"])
                    json_resp[frame_id][job_name]["isKeyFrame"] = job_resp["isKeyFrame"]

        elif ann["__typename"] == "VideoTranscriptionAnnotation":
            ann = cast(VideoTranscriptionAnnotation, ann)
            ann_json_resp = _video_transcription_annotation_to_json_response(ann)
            for frame_id, frame_json_resp in ann_json_resp.items():
                json_resp[frame_id] = {**json_resp[frame_id], **frame_json_resp}

        else:
            raise NotImplementedError(f"Cannot convert video annotation to json response: {ann}")

    _add_annotation_metadata(annotations, json_resp)
    _fill_empty_frames(json_resp)

    return dict(sorted(json_resp.items(), key=lambda item: int(item[0])))  # sort by frame id


def _classic_annotations_to_json_response(
    annotations: List[ClassicAnnotation],
) -> Dict[str, Dict[JobName, Dict]]:
    """Convert label annotations to a json response."""
    json_resp = defaultdict(dict)

    for i, ann in enumerate(annotations):
        if ann["path"]:  # skip child annotations
            continue

        other_annotations = annotations[:i] + annotations[i + 1 :]

        if ann["__typename"] == "ClassificationAnnotation":
            ann = cast(ClassificationAnnotation, ann)
            ann_json_resp = _classification_annotation_to_json_response(ann, other_annotations)
            for job_name, job_resp in ann_json_resp.items():
                json_resp.setdefault(job_name, {}).setdefault("categories", []).extend(
                    job_resp["categories"]
                )

        elif ann["__typename"] == "RankingAnnotation":
            ann = cast(RankingAnnotation, ann)
            ann_json_resp = _ranking_annotation_to_json_response(ann)
            for job_name, job_resp in ann_json_resp.items():
                json_resp.setdefault(job_name, {}).setdefault("orders", []).extend(
                    job_resp["orders"]
                )

        elif ann["__typename"] == "TranscriptionAnnotation":
            ann = cast(TranscriptionAnnotation, ann)
            ann_json_resp = _transcription_annotation_to_json_response(ann)
            for job_name, job_resp in ann_json_resp.items():
                json_resp.setdefault(job_name, {}).setdefault("text", job_resp["text"])

        else:
            raise NotImplementedError(f"Cannot convert classic annotation to json response: {ann}")

    return dict(json_resp)


@overload
def _key_annotations_iterator(
    annotation: VideoTranscriptionAnnotation,
) -> Generator[
    Tuple[
        VideoTranscriptionKeyAnnotation,
        int,
        int,
        Optional[VideoTranscriptionKeyAnnotation],
        Optional[int],
    ],
    None,
    None,
]:
    ...


@overload
def _key_annotations_iterator(
    annotation: VideoClassificationAnnotation,
) -> Generator[
    Tuple[
        VideoClassificationKeyAnnotation,
        int,
        int,
        Optional[VideoClassificationKeyAnnotation],
        Optional[int],
    ],
    None,
    None,
]:
    ...


@overload
def _key_annotations_iterator(
    annotation: VideoObjectDetectionAnnotation,
) -> Generator[
    Tuple[
        VideoObjectDetectionKeyAnnotation,
        int,
        int,
        Optional[VideoObjectDetectionKeyAnnotation],
        Optional[int],
    ],
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
    # previous_key_ann is used to keep track of the previous key annotation
    # in case where keyframe is not present in the current frame range
    previous_key_ann = {}
    previous_key_ann_index = 0
    # iterate over the frame ranges of the annotation
    for frame_interval in annotation["frames"]:
        frame_range = range(frame_interval["start"], frame_interval["end"] + 1)
        # has_key_annotation is used to keep track of whether the current frame range
        # has a key annotation or not. It could be that the current frame range does not
        # have a key annotation, or that the first keyframe is after the start of the frame range
        has_key_annotation = False
        for key_ann_index, key_ann in enumerate(sorted_key_annotations):
            # skip the key annotation if the key annotation start frame
            # is not in current frame range
            if key_ann["frame"] not in frame_range:
                continue

            if key_ann["frame"] > frame_interval["start"] and not has_key_annotation:
                # if the key annotation start frame is after the start of the frame range,
                # then we need to yield the previous key annotation
                key_ann_frame = previous_key_ann["frame"]
                yield (
                    previous_key_ann,
                    frame_interval["start"],
                    key_ann["frame"],
                    key_ann,
                    key_ann_frame,
                )
            # compute the key annotation frame range
            # the start frame of key annotation is given, but not the end frame
            key_ann_start = key_ann["frame"]
            key_ann_frame = key_ann["frame"]
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

            has_key_annotation = True
            previous_key_ann = key_ann
            previous_key_ann_index = key_ann_index

            yield key_ann, key_ann_start, key_ann_end, next_key_ann, key_ann_frame

        if not has_key_annotation:
            key_ann_frame = previous_key_ann["frame"]
            next_key_ann = (
                sorted_key_annotations[previous_key_ann_index + 1]
                if previous_key_ann_index + 1 < len(sorted_key_annotations)
                else None
            )
            yield (
                previous_key_ann,
                frame_interval["start"],
                frame_interval["end"] + 1,
                next_key_ann,
                key_ann_frame,
            )


def _ranking_annotation_to_json_response(
    annotation: RankingAnnotation,
) -> Dict[JobName, Dict]:
    """Convert ranking annotation to a json response.

    Ranking jobs cannot have child jobs.
    """
    json_resp = {
        annotation["job"]: {
            "orders": sorted(
                annotation["annotationValue"]["orders"], key=lambda item: int(item["rank"])
            ),
        }
    }

    return json_resp


def _transcription_annotation_to_json_response(
    annotation: TranscriptionAnnotation,
) -> Dict[JobName, Dict]:
    """Convert transcription annotation to a json response.

    Transcription jobs cannot have child jobs.
    """
    json_resp = {
        annotation["job"]: {
            "text": annotation["annotationValue"]["text"],
        }
    }

    return json_resp


def _video_transcription_annotation_to_json_response(
    annotation: VideoTranscriptionAnnotation,
) -> Dict[str, Dict[JobName, Dict]]:
    """Convert video transcription annotation to a json response.

    Transcription jobs cannot have child jobs.
    """
    json_resp: Dict[str, Dict[JobName, Dict]] = defaultdict(dict)

    for key_ann, key_ann_start, key_ann_end, _, key_ann_frame in _key_annotations_iterator(
        annotation
    ):
        for frame_id in range(key_ann_start, key_ann_end):
            json_resp[str(frame_id)][annotation["job"]] = {
                "isKeyFrame": frame_id == key_ann_frame,
                "text": key_ann["annotationValue"]["text"],
            }

    return json_resp


T = TypeVar("T", VideoAnnotation, ClassicAnnotation)


def _get_child_annotations(annotation: T, other_annotations: List[T]) -> List[T]:
    """Get the child annotations (child jobs) of a video annotation."""
    return [
        ann
        for ann in other_annotations
        # ann["path"] is a list of couples (annotationId, category)
        if len(ann["path"]) > 0
        and ann["path"][-1][0] == annotation["id"]
        and annotation["path"] == ann["path"][:-1]
    ]


def _compute_children_json_resp(
    child_annotations: Union[List[ClassicAnnotation], List[VideoAnnotation]],
    other_annotations: Union[List[ClassicAnnotation], List[VideoAnnotation]],
) -> Dict[str, Dict[JobName, Dict]]:
    """Compute the video json response of the child jobs of a video annotation."""
    children_json_resp = defaultdict(dict)

    for child_ann in child_annotations:
        if child_ann["__typename"] == "ClassificationAnnotation":
            child_ann = cast(ClassificationAnnotation, child_ann)
            other_annotations = cast(List[ClassicAnnotation], other_annotations)
            sub_job_resp = _classification_annotation_to_json_response(
                child_ann, _get_child_annotations(child_ann, other_annotations)
            )

        elif child_ann["__typename"] == "RankingAnnotation":
            child_ann = cast(RankingAnnotation, child_ann)
            sub_job_resp = _ranking_annotation_to_json_response(child_ann)

        elif child_ann["__typename"] == "TranscriptionAnnotation":
            child_ann = cast(TranscriptionAnnotation, child_ann)
            sub_job_resp = _transcription_annotation_to_json_response(child_ann)

        elif child_ann["__typename"] == "VideoClassificationAnnotation":
            child_ann = cast(VideoClassificationAnnotation, child_ann)
            other_annotations = cast(List[VideoAnnotation], other_annotations)
            sub_job_resp = _video_classification_annotation_to_json_response(
                child_ann, _get_child_annotations(child_ann, other_annotations)
            )

        elif child_ann["__typename"] == "VideoTranscriptionAnnotation":
            child_ann = cast(VideoTranscriptionAnnotation, child_ann)
            sub_job_resp = _video_transcription_annotation_to_json_response(child_ann)

        else:
            raise NotImplementedError(
                f"Cannot convert child annotation to json response: {child_ann}"
            )

        for frame_id, frame_json_resp in sub_job_resp.items():
            children_json_resp[frame_id] = {**children_json_resp[frame_id], **frame_json_resp}

    return children_json_resp


def _classification_annotation_to_json_response(
    annotation: ClassificationAnnotation,
    other_annotations: List[ClassicAnnotation],
) -> Dict[JobName, Dict]:
    # initialize the json response
    json_resp = {
        annotation["job"]: {
            "categories": [],
        }
    }

    # get the child annotations of the current annotation
    # and compute the json response of those child jobs
    child_annotations = _get_child_annotations(annotation, other_annotations)
    json_resp_child_jobs = (
        _compute_children_json_resp(child_annotations, other_annotations)
        if child_annotations
        else {}
    )

    # a frame can have one or multiple categories
    categories = annotation["annotationValue"]["categories"]

    for category in categories:
        category_annotation: Dict = {"name": category}

        # search among the child annotations the ones
        # that have a path (annotationId, category)
        children_json_resp = {}
        for child_ann in child_annotations:
            if [annotation["id"], category] in child_ann["path"] and child_ann[
                "job"
            ] in json_resp_child_jobs:
                children_json_resp[child_ann["job"]] = json_resp_child_jobs[child_ann["job"]]

        if children_json_resp:
            category_annotation["children"] = children_json_resp

        json_resp[annotation["job"]]["categories"].append(category_annotation)

    return json_resp


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

    for key_ann, key_ann_start, key_ann_end, _, key_ann_frame in _key_annotations_iterator(
        annotation
    ):
        for frame_id in range(key_ann_start, key_ann_end):
            # initialize the frame json response
            json_resp[str(frame_id)][annotation["job"]] = {
                "categories": [],
                "isKeyFrame": frame_id == key_ann_frame,
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
        _compute_children_json_resp(child_annotations, other_annotations)
        if child_annotations
        else {}
    )

    json_resp = defaultdict(dict)

    for (
        key_ann,
        key_ann_start,
        key_ann_end,
        next_key_ann,
        key_ann_frame,
    ) in _key_annotations_iterator(annotation):
        for frame_id in range(key_ann_start, key_ann_end):
            # get the frame json response of child jobs
            child_jobs_frame_json_resp = json_resp_child_jobs.get(str(frame_id), {})

            annotation_dict = {
                "children": child_jobs_frame_json_resp,
                "isKeyFrame": frame_id == key_ann_frame,
                "categories": [{"name": annotation["category"]}],
                "mid": annotation["mid"],
                "type": json_interface["jobs"][annotation["job"]]["tools"][0],
            }

            if frame_id == key_ann_frame or next_key_ann is None:
                norm_vertices = key_ann["annotationValue"]["vertices"]
            # between two key frame annotations, an object (point, bbox, polygon) is
            # interpolated in the UI
            else:
                object_inital_state = key_ann["annotationValue"]["vertices"]
                object_final_state = next_key_ann["annotationValue"]["vertices"]
                norm_vertices = _interpolate_object(
                    object_type=json_interface["jobs"][annotation["job"]]["tools"][0],
                    object_initial_state=object_inital_state,
                    initial_state_frame_index=key_ann["frame"],
                    object_final_state=object_final_state,
                    final_state_frame_index=next_key_ann["frame"],
                    at_frame=frame_id,
                )

            if json_interface["jobs"][annotation["job"]]["tools"][0] == "marker":
                annotation_dict["point"] = norm_vertices[0][0][0]

            elif json_interface["jobs"][annotation["job"]]["tools"][0] in {"polygon", "rectangle"}:
                annotation_dict["boundingPoly"] = [{"normalizedVertices": norm_vertices[0][0]}]

            elif json_interface["jobs"][annotation["job"]]["tools"][0] == "semantic":
                annotation_dict["boundingPoly"] = [
                    {"normalizedVertices": norm_vert} for norm_vert in norm_vertices[0]
                ]

            json_resp[str(frame_id)].setdefault(annotation["job"], {}).setdefault(
                "annotations", []
            ).append(annotation_dict)

    return json_resp


def _interpolate_object(
    *,
    object_type: str,
    object_initial_state: List[List[List[Vertice]]],
    initial_state_frame_index: int,
    object_final_state: List[List[List[Vertice]]],
    final_state_frame_index: int,
    at_frame: int,
) -> List[List[List[Vertice]]]:
    """Interpolate an object between two key frames."""
    # if the two frames are consecutive, we do not interpolate
    if at_frame == initial_state_frame_index:
        return object_initial_state

    if at_frame == final_state_frame_index:
        return object_final_state

    if object_type == JobTool.MARKER:
        # for point jobs, we interpolate for each frame
        return [
            [
                [
                    _interpolate_point(
                        previous_point=object_initial_state[0][0][0],
                        next_point=object_final_state[0][0][0],
                        weight=(at_frame - initial_state_frame_index)
                        / (final_state_frame_index - initial_state_frame_index),
                    )
                ]
            ]
        ]

    if object_type == JobTool.RECTANGLE:
        return [
            [
                _interpolate_rectangle(
                    previous_vertices=object_initial_state[0][0],
                    next_vertices=object_final_state[0][0],
                    weight=(at_frame - initial_state_frame_index)
                    / (final_state_frame_index - initial_state_frame_index),
                )
            ]
        ]

    if object_type == JobTool.POLYGON:
        return object_initial_state  # for polygon jobs, we keep the initial state

    if object_type == JobTool.SEMANTIC:
        return object_initial_state  # for semantic jobs, we keep the initial state

    raise NotImplementedError(f"Cannot interpolate object of type {object_type}")


def _interpolate_point(previous_point: Vertice, next_point: Vertice, weight: float) -> Vertice:
    """Interpolate a point."""
    return Vertice(
        x=_interpolate_number(previous_point["x"], next_point["x"], weight),
        y=_interpolate_number(previous_point["y"], next_point["y"], weight),
    )


def _interpolate_rectangle(
    *,
    previous_vertices: List[Vertice],
    next_vertices: List[Vertice],
    weight: float,
) -> List[Vertice]:
    """Interpolate a rectangle.

    It finds a bijection between the rectangles, calculates their properties, and then smoothly
    interpolates the angle, center, length, and width between
    the two rectangles based on the specified weight.
    The interpolated properties are used to reconstruct the vertices of the interpolated rectangle,
    which are then converted back to normalized coordinates.
    """
    permuted_new_vertices = _find_rectangle_vertices_bijection(previous_vertices, next_vertices)

    previous_rectangle_properties = _find_rectangle_properties(previous_vertices)
    next_rectangle_properties = _find_rectangle_properties(permuted_new_vertices)

    interpolated_angle = _interpolate_angle(
        previous_rectangle_properties.angle, next_rectangle_properties.angle, weight
    )
    interpolated_center = _interpolate_point(
        previous_rectangle_properties.center, next_rectangle_properties.center, weight
    )
    interpolated_length = _interpolate_number(
        previous_rectangle_properties.length, next_rectangle_properties.length, weight
    )
    interpolated_width = _interpolate_number(
        previous_rectangle_properties.width, next_rectangle_properties.width, weight
    )

    interpolated_rectangle_properties = _RectangleProperties(
        angle=interpolated_angle,
        center=interpolated_center,
        length=interpolated_length,
        width=interpolated_width,
    )

    interpolated_rectangle = _reconstruct_rectangle_from_properties(
        interpolated_rectangle_properties
    )

    return interpolated_rectangle


def _find_rectangle_vertices_bijection(
    rectangle1: List[Vertice], rectangle2: List[Vertice]
) -> List[Vertice]:
    """Find the bijection between two rectangles that minimizes the cost."""
    permutation_array = [
        [rectangle2[0], rectangle2[1], rectangle2[2], rectangle2[3]],
        [rectangle2[1], rectangle2[2], rectangle2[3], rectangle2[0]],
        [rectangle2[2], rectangle2[3], rectangle2[0], rectangle2[1]],
        [rectangle2[3], rectangle2[0], rectangle2[1], rectangle2[2]],
        [rectangle2[3], rectangle2[2], rectangle2[1], rectangle2[0]],
        [rectangle2[2], rectangle2[1], rectangle2[0], rectangle2[3]],
        [rectangle2[1], rectangle2[0], rectangle2[3], rectangle2[2]],
        [rectangle2[0], rectangle2[3], rectangle2[2], rectangle2[1]],
    ]
    bijection_cost_array = [
        _bijection_cost(permuted_rectangle, rectangle1) for permuted_rectangle in permutation_array
    ]

    optimal_permutation_index = bijection_cost_array.index(min(bijection_cost_array))
    return permutation_array[optimal_permutation_index]


def _bijection_cost(permuted_rectangle: List[Vertice], rectangle: List[Vertice]) -> float:
    """Compute the cost of a bijection between two rectangles."""
    cost = 0
    for i in range(2):
        ab_x = rectangle[i + 1]["x"] - rectangle[i]["x"]
        apermbperm_x = permuted_rectangle[i + 1]["x"] - permuted_rectangle[i]["x"]

        ab_y = rectangle[i + 1]["y"] - rectangle[i]["y"]
        apermbperm_y = permuted_rectangle[i + 1]["y"] - permuted_rectangle[i]["y"]

        ab_norm = math.sqrt(ab_x**2 + ab_y**2)
        apermbnorm = math.sqrt(apermbperm_x**2 + apermbperm_y**2)

        cos = (ab_x * apermbperm_x + ab_y * apermbperm_y) / (ab_norm * apermbnorm)

        cost -= cos

    return cost


@dataclass
class _RectangleProperties:
    """Rectangle properties."""

    angle: float
    center: Vertice
    length: float
    width: float


def _find_rectangle_properties(rectangle: List[Vertice]) -> _RectangleProperties:
    """Find the properties of a rectangle."""
    if len(rectangle) != 4:  # noqa: PLR2004
        raise RuntimeError("Invalid rectangle format")

    angle = _find_rectangle_angle(rectangle)
    center = _find_rectangle_center(rectangle)
    length = _find_rectangle_length(rectangle)
    width = _find_rectangle_width(rectangle)

    return _RectangleProperties(angle=angle, center=center, length=length, width=width)


def _find_rectangle_angle(rectangle: List[Vertice]) -> float:
    """Find the angle of a rectangle."""
    vector_ab = Vertice(
        x=rectangle[2]["x"] - rectangle[1]["x"], y=rectangle[2]["y"] - rectangle[1]["y"]
    )
    return math.atan2(vector_ab["y"], vector_ab["x"])


def _find_rectangle_center(rectangle: List[Vertice]) -> Vertice:
    """Find the center of a rectangle."""
    point_a = rectangle[0]
    point_c = rectangle[2]
    return Vertice(x=(point_a["x"] + point_c["x"]) / 2, y=(point_a["y"] + point_c["y"]) / 2)


def _find_rectangle_length(rectangle: List[Vertice]) -> float:
    """Find the length of a rectangle."""
    return _distance_between_points(rectangle[1], rectangle[2])


def _find_rectangle_width(rectangle: List[Vertice]) -> float:
    """Find the width of a rectangle."""
    return _distance_between_points(rectangle[0], rectangle[1])


def _distance_between_points(point1: Vertice, point2: Vertice) -> float:
    """Compute the distance between two points."""
    return math.sqrt((point1["x"] - point2["x"]) ** 2 + (point1["y"] - point2["y"]) ** 2)


def _interpolate_angle(previous_angle: float, angle: float, weight: float) -> float:
    """Interpolate an angle."""
    difference = min(
        abs(angle - previous_angle),
        2 * math.pi - abs(angle - previous_angle),
    )
    sign = (
        math.copysign(1, angle - previous_angle)
        if abs(angle - previous_angle) < 2 * math.pi - abs(angle - previous_angle)
        else math.copysign(1, 2 * math.pi - abs(angle - previous_angle))
    )
    interpolated_angle = previous_angle + sign * difference * weight
    return interpolated_angle if math.isfinite(interpolated_angle) else 0


def _interpolate_number(previous_number: float, number: float, weight: float) -> float:
    """Interpolate a number."""
    interpolated_number = number * weight + (1 - weight) * previous_number
    return interpolated_number if math.isfinite(interpolated_number) else 0


def _rotate_vector(vector: Vertice, angle: float) -> Vertice:
    """Rotate a vector."""
    return Vertice(
        x=vector["x"] * math.cos(angle) - vector["y"] * math.sin(angle),
        y=vector["x"] * math.sin(angle) + vector["y"] * math.cos(angle),
    )


def _reconstruct_rectangle_from_properties(properties: _RectangleProperties) -> List[Vertice]:
    """Reconstruct a rectangle from its properties."""
    u = Vertice(x=0, y=properties.width)
    v = Vertice(x=properties.length, y=0)

    rotated_u = _rotate_vector(u, properties.angle)
    rotated_v = _rotate_vector(v, properties.angle)

    point_a = Vertice(
        x=properties.center["x"] + (rotated_u["x"] + rotated_v["x"]) / 2,
        y=properties.center["y"] + (rotated_u["y"] + rotated_v["y"]) / 2,
    )
    point_b = Vertice(
        x=properties.center["x"] + (-rotated_u["x"] + rotated_v["x"]) / 2,
        y=properties.center["y"] + (-rotated_u["y"] + rotated_v["y"]) / 2,
    )
    point_c = Vertice(
        x=properties.center["x"] - (rotated_u["x"] + rotated_v["x"]) / 2,
        y=properties.center["y"] - (rotated_u["y"] + rotated_v["y"]) / 2,
    )
    point_d = Vertice(
        x=properties.center["x"] - (-rotated_u["x"] + rotated_v["x"]) / 2,
        y=properties.center["y"] - (-rotated_u["y"] + rotated_v["y"]) / 2,
    )

    return [point_a, point_b, point_c, point_d]
