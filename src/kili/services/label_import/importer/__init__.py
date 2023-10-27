"""Label Importers."""

import csv
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, NamedTuple, Optional, Type

import yaml

from kili.core.helpers import get_file_paths_to_upload
from kili.domain.label import LabelType
from kili.domain.project import ProjectId
from kili.services.helpers import get_external_id_from_file_path
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
from kili.services.types import LogLevel
from kili.use_cases.asset.utils import AssetUseCasesUtils
from kili.use_cases.label import LabelUseCases
from kili.use_cases.label.types import LabelToCreateUseCaseInput

if TYPE_CHECKING:
    from kili.client import Kili


class LoggerParams(NamedTuple):
    """Contains all parameters related to logging."""

    disable_tqdm: Optional[bool]
    level: LogLevel


class AbstractLabelImporter(ABC):
    """Abstract Label Importer."""

    def __init__(
        self, kili: "Kili", logger_params: LoggerParams, input_format: LabelFormat
    ) -> None:
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
        overwrite: bool,
    ):
        """Performs the import from the label files."""
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
            overwrite=overwrite,
            model_name=model_name,
        )

        self.logger.warning("%d labels have been successfully imported", len(labels))

    def process_from_dict(  # pylint: disable=too-many-arguments
        self,
        project_id: Optional[str],
        labels: List[Dict],
        label_type: LabelType,
        overwrite: bool,
        model_name: Optional[str] = None,
    ) -> List:
        """Imports labels from a list of dictionaries representing labels."""
        should_retrieve_asset_ids = labels[0].get("asset_id") is None
        if should_retrieve_asset_ids:
            assert project_id
            asset_external_ids = [label["asset_external_id"] for label in labels]
            asset_id_map = AssetUseCasesUtils(
                self.kili.kili_api_gateway
            ).infer_ids_from_external_ids(asset_external_ids, ProjectId(project_id))
            labels = [
                {**label, "asset_id": asset_id_map[label["asset_external_id"]]} for label in labels
            ]

        labels_data = [
            LabelToCreateUseCaseInput(
                json_response=label["json_response"],
                asset_id=label.get("asset_id"),
                seconds_to_label=label.get("seconds_to_label"),
                model_name=model_name,
                author_id=label.get("author_id"),
                asset_external_id=None,
                label_type=label_type,
            )
            for label in labels
        ]

        return LabelUseCases(self.kili.kili_api_gateway).append_labels(
            disable_tqdm=self.logger_params.disable_tqdm,
            overwrite=overwrite,
            label_type=label_type,
            project_id=ProjectId(project_id) if project_id else None,
            fields=("id",),
            labels=labels_data,
        )

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
        """Extracts the labels files and their metadata from the label files."""
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
    """Label importer in the yolo format."""

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
    """# Label importer in the Kili format."""

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
