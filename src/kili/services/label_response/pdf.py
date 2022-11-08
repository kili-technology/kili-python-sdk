"""
classes to parse a label response from a PDF project into a python class
"""

from typing import Dict

from .base import BaseAnnotation
from .constants import Tools


class PDFBoundingBoxAnnotation(BaseAnnotation):
    """
    Class to represents an annotation in a PDF project
    """

    tool = Tools.RECTANGLE

    def __init__(self, annotation: Dict, job_name: str, json_interface: Dict) -> None:
        super().__init__(annotation, job_name, json_interface)
        pretty_annotation = annotation["annotations"][0]
        self.bounding_poly = pretty_annotation["boundingPoly"][0]
        self.polys = pretty_annotation["polys"][0]
        self.page_number: int = int(pretty_annotation["pageNumberArray"][0])


class PDFRelation(BaseAnnotation):
    """
    Class to represents relations between annotations in a PDF project
    """

    def __init__(self, pdf_relation: Dict, job_name: str, json_interface: Dict) -> None:
        super().__init__(pdf_relation, job_name, json_interface)
        raise Exception("Not implemented")
