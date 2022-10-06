"""
Label Importers
"""
import csv
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Type, cast

import yaml

from kili.helpers import get_file_paths_to_upload
from kili.services.helpers import (
    check_exclusive_options,
    get_external_id_from_file_path,
)
from kili.services.label_import.exceptions import (
    LabelParsingError,
    MissingExternalIdError,
    MissingMetadataError,
    MissingTargetJobError,
)
from kili.services.label_import.parser import (
    AbstractLabelParser,
    KiliRawLabelParser,
    YoloLabelParser,
)
from kili.services.label_import.types import Classes, LabelFormat, LabelToImport
from kili.services.types import LabelType, LogLevel, ProjectId
from kili.utils.tqdm import tqdm


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
        labels_file_path: Optional[Path],
        labels_files: Optional[List[Path]],
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
        labels = self.extract_from_files(labels_file_path, labels_files)
        if is_prediction:
            assert model_name
            self._import_as_predictions(labels, label_parser, project_id, model_name)
        else:
            self._import_as_labels(labels, label_parser, project_id)

        self.logger.warning(print(f"{len(labels)} labels have been successfully imported"))

    def _import_as_labels(
        self, labels: List[LabelToImport], label_parser: AbstractLabelParser, project_id: ProjectId
    ):
        for label in tqdm(labels, disable=self.logger_params.disable_tqdm):
            kwargs = dict(label.copy())
            del kwargs["path"]
            try:
                json_response = label_parser.parse(Path(label["path"]))
            except Exception as exc:
                path = label["path"]
                raise LabelParsingError(f"Failed to parse the file {path}") from exc

            self.kili.append_to_labels(
                json_response=json_response,
                project_id=project_id,
                **kwargs,
            )

    def _import_as_predictions(
        self,
        labels: List[LabelToImport],
        label_parser: AbstractLabelParser,
        project_id: ProjectId,
        model_name: str,
    ):
        assert model_name
        json_response_array: List[Dict] = []
        external_id_array: List[str] = []
        model_name_array: List[str] = []
        for label in tqdm(labels, disable=self.logger_params.disable_tqdm):
            kwargs = dict(label.copy())
            del kwargs["path"]
            json_response_array.append(label_parser.parse(Path(label["path"])))
            external_id = label.get("label_asset_external_id")
            if external_id is None:
                path = label["path"]
                raise MissingExternalIdError(f"There is no associated asset external id to {path}")
            external_id_array.append(external_id)
            model_name_array.append(model_name)
        self.kili.create_predictions(
            json_response_array=json_response_array,
            external_id_array=external_id_array,
            model_name_array=model_name_array,
            project_id=project_id,
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
        self, labels_file_path: Optional[Path], labels_files: Optional[List[Path]]
    ) -> List[LabelToImport]:
        """
        Extracts the labels files and their metadata from the label files (given
        explicitely or through a CSV)
        """
        check_exclusive_options(labels_file_path, labels_files)

        labels = []
        if labels_files is not None and len(labels_files) > 0:
            label_paths = get_file_paths_to_upload(
                [str(f) for f in labels_files],
                lambda path: path.endswith(self._get_label_file_extension()),
                verbose=self.logger_params.level in ["INFO", "DEBUG"],
            )
            if len(label_paths) == 0:
                raise ValueError(
                    "No label files to upload. "
                    "Check that the paths exist and file types are .json"
                )
            external_ids = [get_external_id_from_file_path(Path(path)) for path in label_paths]
            labels = [
                LabelToImport(path=p, label_asset_external_id=e_id)
                for (p, e_id) in zip(label_paths, external_ids)
            ]

        elif labels_file_path is not None:
            labels = self._read_labels_file_path(labels_file_path)

            if len(labels) == 0:
                raise ValueError(f"No label file was found in csv: {labels_file_path}")
        return labels

    @classmethod
    def _read_labels_file_path(cls, labels_file: Path) -> List[LabelToImport]:
        """
        Read CSV and fill a list of labels to import.
        """
        data = []
        with labels_file.open("r") as l_f:
            csv_reader = csv.reader(l_f)
            data = []
            headers = []
            for ind, row in enumerate(csv_reader):
                if ind == 0:
                    headers = row
                else:
                    headers_row = zip(headers, row)
                    str_dict = dict(headers_row)

                    typed_dict: Dict[str, Any] = {
                        "path": str_dict["path"],
                    }
                    if len(str_dict.get("label_asset_id", "")):
                        typed_dict["label_asset_id"] = str_dict["label_asset_id"]

                    if len(str_dict.get("label_asset_external_id", "")):
                        typed_dict["label_asset_external_id"] = str_dict["label_asset_external_id"]

                    if len(str_dict.get("label_type", "")):
                        typed_dict["label_type"] = cast(LabelType, str_dict["label_type"])

                    if len(str_dict.get("seconds_to_label", "")):
                        typed_dict["seconds_to_label"] = int(str_dict["seconds_to_label"])

                    if len(str_dict.get("author_id", "")):
                        typed_dict["author_id"] = str_dict["author_id"]

                    data.append(LabelToImport(**typed_dict))
        return data


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
