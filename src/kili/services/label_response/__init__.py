from enum import Enum
from typing import Dict, List

from kili.enums import InputType

from .base import Classification, Transcription
from .constants import MLTasks
from .pdf import PDFBoundingBoxAnnotation
from .text import NerTextEntity


class AnnotationClasses(Enum):
    """
    Possible annotation classes
    """

    NerTextEntity = NerTextEntity
    PDFBoundingBoxAnnotation = PDFBoundingBoxAnnotation


class Response:
    """
    Class to represent a parsed label response
    """

    def __init__(self, json_response: Dict, json_interface: Dict, input_type: InputType) -> None:
        self._job_codes: List[str] = list(json_response.keys())
        self.json_interface = json_interface

        self.classifications: List[Classification] = []
        self.transcriptions: List[Transcription] = []

        self.pdf_bounding_box_annotations: List[PDFBoundingBoxAnnotation] = []
        self.text_entity_annotations: List[NerTextEntity] = []

        jobs = json_interface["jobs"]

        for job_code in self._job_codes:
            job = jobs[job_code]
            job_name: str = job["instruction"]
            ml_task: MLTasks = job["mlTask"]

            if ml_task == MLTasks.CLASSIFICATION.value:
                self.classifications.append(
                    Classification(json_response[job_code], job_name, json_interface)
                )

            if ml_task == MLTasks.TRANSCRIPTION.value:
                self.transcriptions.append(Transcription(json_response[job_code], job_name))
            if ml_task == MLTasks.OBJECT_DETECTION.value and input_type == "PDF":
                raw_annotations: List[Dict] = json_response[job_code]["annotations"]

                for raw_annotation in raw_annotations:
                    pretty_annotation = PDFBoundingBoxAnnotation(
                        raw_annotation, job_name, json_interface
                    )
                    self.pdf_bounding_box_annotations.append(pretty_annotation)

            if ml_task == MLTasks.NAMED_ENTITIES_RECOGNITION.value and input_type == "TEXT":
                raw_annotations: List[Dict] = json_response[job_code]["annotations"]

                for raw_annotation in raw_annotations:
                    pretty_annotation = NerTextEntity(raw_annotation, job_name, json_interface)
                    self.text_entity_annotations.append(pretty_annotation)

        self.annotations = self.pdf_bounding_box_annotations + self.text_entity_annotations
