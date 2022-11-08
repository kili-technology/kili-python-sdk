"""
Common and generic classes to parse a label response into a python class
"""
from typing import Dict, List

from .constants import MLTasks


class Category:
    """
    Class to represent a category
    """

    def __init__(self, raw_category: Dict, json_interface: Dict) -> None:
        children = raw_category.get("children")
        if children:
            self.children = ChildrenResponse(children, json_interface)
        self.confidence: float = raw_category["confidence"]
        self.name: str = raw_category["name"]


class BaseAnnotation:
    """
    Class to represents common properties to all annotations
    """

    def __init__(self, base_annotation: Dict, job_name: str, json_interface: Dict) -> None:
        self.category = Category(base_annotation["categories"][0], json_interface)
        children = base_annotation.get("children")
        if children:
            self.children = ChildrenResponse(children, json_interface)
        self.job_name: str = job_name
        self.mid: str = base_annotation["mid"]


class Transcription:
    """
    Class to represent a transcription annotation
    """

    def __init__(self, transcription: Dict, job_name: str) -> None:
        self.text: str = transcription["text"]
        self.job_name: str = job_name


class Classification:
    """
    Class to represent a classification annotation
    """

    def __init__(self, classification: Dict, job_name: str, json_interface: Dict) -> None:
        self.job_name: str = job_name
        self.categories = [
            Category(raw_category, json_interface) for raw_category in classification["categories"]
        ]


class ChildrenResponse:
    """
    Class to represent a children response
    """

    def __init__(self, json_response: Dict, json_interface: Dict) -> None:
        self._job_codes: List[str] = list(json_response.keys())
        self.classifications: List[Classification] = []
        self.transcriptions: List[Transcription] = []

        jobs = json_interface["jobs"]

        for job_code in self._job_codes:
            job = jobs[job_code]
            job_name = job["instruction"]
            ml_task: MLTasks = job["mlTask"]

            if ml_task == MLTasks.CLASSIFICATION.value:
                self.classifications.append(
                    Classification(json_response[job_code], job_name, json_interface)
                )

            if ml_task == MLTasks.TRANSCRIPTION.value:
                self.transcriptions.append(Transcription(json_response[job_code], job_name))
