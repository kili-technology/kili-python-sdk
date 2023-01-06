"""
Label Importers
"""
import csv
import logging
from abc import ABC, abstractmethod
from json import dumps
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Type

import yaml

from kili.graphql.operations.label.mutations import GQL_APPEND_MANY_LABELS
from kili.helpers import format_result, get_file_paths_to_upload
from kili.orm import Label
from kili.services.helpers import (
    get_external_id_from_file_path,
    infer_ids_from_external_ids,
)
from kili.services.label_import.exceptions import (
    LabelParsingError,
    MissingMetadataError,
    MissingTargetJobError,
)
from kili.services.label_import.parser import (
    AbstractLabelParser,
    KiliRawLabelParser,
    YoloLabelParser,
)
from kili.services.label_import.types import Classes, LabelFormat
from kili.services.types import LabelType, LogLevel, ProjectId
from kili.utils import pagination, tqdm


class LoggerParams(NamedTuple):
    """
    Contains all parameters related to logging.
    """

    disable_tqdm: bool
    level: LogLevel


class AbstractLabelImporter(ABC):
    """
    Abstract Label Importer
    """

    def __init__(self, kili, logger_params: LoggerParams, input_format: LabelFormat):
        self.kili = kili
        self.logger_params = logger_params
        self.input_format: LabelFormat = input_format

        self.logger = logging.getLogger("kili.services.label_import")
        self.logger.setLevel(logger_params.level)

    def process_from_files(  # pylint: disable=too-many-arguments
        self,
        labels_files: List[Path],
        meta_file_path: Optional[Path],
        project_id: ProjectId,
        target_job_name: Optional[str],
        model_name: Optional[str],
        is_prediction: bool,
    ):
        """
        Performs the import from the label files
        """
        self._check_arguments_compatibility(meta_file_path, target_job_name)
        class_by_id = self._read_classes_from_meta_file(meta_file_path, self.input_format)
        label_parser_class = self._select_label_parser()
        label_parser = label_parser_class(class_by_id, target_job_name)

        self.logger.warning("Importing labels")
        labels = self.extract_from_files(labels_files, label_parser)
        label_type = "PREDICTION" if is_prediction else "DEFAULT"
        self.process_from_dict(
            project_id=project_id,
            labels=labels,
            label_type=label_type,
            model_name=model_name,
        )

        self.logger.warning(print(f"{len(labels)} labels have been successfully imported"))

    def process_from_dict(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        project_id: Optional[str],
        labels: List[Dict],
        label_type: LabelType,
        model_name: Optional[str] = None,
    ) -> List:
        """
        Imports labels from a list of dictionaries representing labels.
        """
        should_retrieve_asset_ids = labels[0].get("asset_id") is None
        if should_retrieve_asset_ids:
            assert project_id
            asset_external_ids = [label["asset_external_id"] for label in labels]
            asset_id_map = infer_ids_from_external_ids(self.kili, asset_external_ids, project_id)
            labels = [
                {**label, "asset_id": asset_id_map[label["asset_external_id"]]} for label in labels
            ]
        labels_data = [
            {
                "jsonResponse": dumps(label.get("json_response")),
                "assetID": label.get("asset_id"),
                "secondsToLabel": label.get("seconds_to_label"),
                "modelName": model_name,
                "authorID": label.get("author_id"),
            }
            for label in labels
        ]
        batch_generator = pagination.batch_iterator_builder(labels_data)
        result = []
        with tqdm.tqdm(total=len(labels_data), disable=self.logger_params.disable_tqdm) as pbar:
            for batch_labels in batch_generator:
                variables = {
                    "data": {"labelType": label_type, "labelsData": batch_labels},
                    "where": {"idIn": [label["assetID"] for label in batch_labels]},
                }
                batch_result = self.kili.auth.client.execute(GQL_APPEND_MANY_LABELS, variables)
                result.extend(format_result("data", batch_result, Label))
                pbar.update(len(batch_labels))
        return result

    @staticmethod
    @abstractmethod
    def _check_arguments_compatibility(
        meta_file_path: Optional[Path], target_job_name: Optional[str]
    ):
        pass

    @classmethod
    @abstractmethod
    def _read_classes_from_meta_file(
        cls, meta_file_path: Optional[Path], input_format: LabelFormat
    ) -> Optional[Classes]:
        pass

    @abstractmethod
    def _select_label_parser(self) -> Type[AbstractLabelParser]:
        pass

    @abstractmethod
    def _get_label_file_extension(self) -> str:
        pass

    def extract_from_files(
        self, labels_files: List[Path], label_parser: AbstractLabelParser
    ) -> List[Dict]:
        """
        Extracts the labels files and their metadata from the label files
        """

        label_paths = get_file_paths_to_upload(
            [str(f) for f in labels_files],
            lambda path: path.endswith(self._get_label_file_extension()),
            verbose=self.logger_params.level in ["INFO", "DEBUG"],
        )
        if len(label_paths) == 0:
            raise ValueError(
                "No label files to upload. Check that the paths exist and file types are .json"
            )
        labels = []
        for path in label_paths:
            try:
                labels.append(
                    {
                        "json_response": label_parser.parse(Path(path)),
                        "asset_external_id": get_external_id_from_file_path(Path(path)),
                    }
                )
            except Exception as exc:
                raise LabelParsingError(f"Failed to parse the file {path}") from exc
        return labels


class YoloLabelImporter(AbstractLabelImporter):
    """
    Label importer in the yolo format.
    """

    def _get_label_file_extension(self) -> str:
        return ".txt"

    @staticmethod
    def _check_arguments_compatibility(
        meta_file_path: Optional[Path], target_job_name: Optional[str]
    ):
        if meta_file_path is None:
            raise MissingMetadataError("Meta file is needed to import the label")
        if target_job_name is None:
            raise MissingTargetJobError("A target job name is needed to import the label")

    @staticmethod
    def _read_classes_from_meta_file(
        meta_file_path: Optional[Path], input_format: LabelFormat
    ) -> Classes:
        assert meta_file_path
        classes: Classes = Classes({})
        if input_format == "yolo_v4":
            try:
                # layout: id class\n
                with meta_file_path.open("r", encoding="utf-8") as m_f:
                    csv_reader = csv.reader(m_f, delimiter=" ")
                    classes = Classes({int(r[0]): r[1] for r in csv_reader if r[0] != " "})
            except (ValueError, IndexError):
                with meta_file_path.open("r", encoding="utf-8") as m_f:
                    classes = Classes(dict(enumerate(m_f.read().splitlines())))

        elif input_format == "yolo_v5":
            with meta_file_path.open("r", encoding="utf-8") as m_f:
                m_d = yaml.load(m_f, yaml.FullLoader)
                classes = Classes(m_d["names"])
        elif input_format == "yolo_v7":
            with meta_file_path.open("r", encoding="utf-8") as m_f:
                m_d = yaml.load(m_f, yaml.FullLoader)
                classes = Classes(dict(enumerate(m_d["names"])))
        else:
            raise NotImplementedError(f"The format f{input_format} does not have a metadata parser")

        return classes

    def _select_label_parser(self) -> Type[AbstractLabelParser]:
        return YoloLabelParser


class KiliRawLabelImporter(AbstractLabelImporter):
    """
    # Label importer in the Kili format.
    """

    def _get_label_file_extension(self) -> str:
        return ".json"

    @staticmethod
    def _check_arguments_compatibility(
        meta_file_path: Optional[Path], target_job_name: Optional[str]
    ):
        pass

    @classmethod
    def _read_classes_from_meta_file(
        cls, meta_file_path: Optional[Path], input_format: LabelFormat
    ) -> Optional[Classes]:
        return None

    def _select_label_parser(self) -> Type[AbstractLabelParser]:
        return KiliRawLabelParser
