"""
classes to parse a label response from a text project into a python class
"""

from typing import Dict

from .base import BaseAnnotation


class NerTextEntity(BaseAnnotation):
    """
    Class to represents a NER entity in a Text project
    """

    def __init__(self, ner_text_entity: Dict, job_name: str, json_interface: Dict) -> None:
        super().__init__(ner_text_entity, job_name, json_interface)
        self.begin_offset: int = ner_text_entity["beginOffset"]
        self.end_offset: int = ner_text_entity["endOffset"]


class NerTextRelation(BaseAnnotation):
    """
    Class to represents relations between NER entities in a Text project
    """

    def __init__(self, ner_text_relation: Dict, job_name: str, json_interface: Dict) -> None:
        super().__init__(ner_text_relation, job_name, json_interface)
        raise Exception("Not implemented")
