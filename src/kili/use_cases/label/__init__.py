"""Label use cases."""

import mimetypes
from collections.abc import Generator
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, cast

import requests

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.label.types import (
    AppendLabelData,
    AppendManyLabelsData,
    AppendToLabelsData,
)
from kili.domain.asset import AssetExternalId, AssetFilters, AssetId
from kili.domain.asset.helpers import check_asset_identifier_arguments
from kili.domain.label import LabelFilters, LabelId, LabelType
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.domain.user import UserId
from kili.exceptions import GraphQLError, NotFound
from kili.use_cases.asset.utils import AssetUseCasesUtils
from kili.use_cases.base import BaseUseCases
from kili.utils.labels.parsing import parse_labels

from .types import LabelToCreateUseCaseInput
from .validator import check_input_labels

ASSET_LEVEL_KEY = "assetLevel"

if TYPE_CHECKING:
    import pandas as pd


LOCK_ERRORS = {
    "AlreadyHaveLabelOnCurrentStep": "You cannot edit this asset as you've already submitted a label.",
    "AssetAlreadyAssigned": "This asset is assigned to someone else. You cannot edit it.",
    "AssetAlreadyLocked": "This asset is currently being edited by another user.",
    "AssetInDoneStepStatus": "This asset is already labeled or reviewed and cannot be edited.",
    "AssetInDoneStepStatusWithCorrectAction": "You already labeled this asset, but you can still correct it.",
    "AssetInDoneStepStatusWithReviewAction": "This asset is completed. Take it for review to make changes.",
    "AssetInNextStepWithCorrectAction": "This asset is awaiting to be reviewed but can still be corrected.",
    "AssetLockedNoReason": "This asset is currently locked. You cannot edit it.",
    "BlockedByEnforceStepSeparation": "You can't edit this asset as you already worked on another step.",
    "LabelNotEditable": "This label was created in another step and is read-only.",
    "NotAssignedWithAssignAction": "This asset is in read-only mode because you are not assigned to it."
    + "To make edits, add yourself as an assignee.",
    "NotInStepAssignees": "You cannot edit this asset in its current step.",
}


class LabelUseCases(BaseUseCases):
    """Label use cases."""

    def count_labels(self, filters: LabelFilters) -> int:
        """Count labels."""
        return self._kili_api_gateway.count_labels(filters=filters)

    def _resolve_file_jobs(
        self, json_response: dict, project_id: Optional[ProjectId], asset_id: AssetId
    ) -> dict:
        """Uploads the files a json response names by path, and puts the answers in their place.

        A file job is answered with a path, and the upload happens here rather than in a call of
        its own: a file only means anything as the answer to a job, so there is no way to put bytes
        in Kili that are not an annotation.

        A plain string is what marks one. No other task answers with a bare string -- a
        transcription answers `{"text": ...}`, a classification `{"categories": [...]}` -- so there
        is nothing to disambiguate, and an answer already carrying a `fileId` is left alone, which
        is what lets a label read back from Kili be submitted again.
        """

        def resolve(jobs: dict) -> dict:
            resolved = {}
            for job_name, answer in jobs.items():
                if not isinstance(answer, str):
                    resolved[job_name] = answer
                    continue
                if project_id is None:
                    raise ValueError(
                        f"Job '{job_name}' names a file to upload, which needs the project it"
                        " belongs to: pass project_id to append_labels."
                    )
                resolved[job_name] = self.upload_annotation_file(
                    project_id=project_id, asset_id=asset_id, file_path=Path(answer)
                )
            return resolved

        # On video an asset level job sits under `assetLevel`; the sibling keys are frame numbers,
        # and a file has no frame, so they are left untouched.
        asset_level = json_response.get(ASSET_LEVEL_KEY)
        if isinstance(asset_level, dict):
            return {**json_response, ASSET_LEVEL_KEY: resolve(asset_level)}

        return resolve(json_response)

    def upload_annotation_file(
        self, project_id: ProjectId, asset_id: AssetId, file_path: Path
    ) -> dict:
        """Upload a file and return what a file job answers with.

        Two steps, as the tools that produce these files do them: the id is minted server side
        along with a short lived url, then the bytes go straight to the bucket. Nothing references
        the file until the returned answer is written into a label, so an upload that is never
        referenced simply leaves an unused blob.

        The mime type is what the file name suggests; the server fills it in the same way when it
        is not given, so a name it does not recognise is left for the server to decide.
        """
        upload = self._kili_api_gateway.create_annotation_file_upload(
            project_id=project_id, asset_id=asset_id
        )

        mime_type = mimetypes.guess_type(file_path.name)[0] or ""
        headers = {"Content-Length": str(file_path.stat().st_size)}
        if mime_type:
            headers["Content-Type"] = mime_type

        with file_path.open("rb") as file:
            response = self._kili_api_gateway.http_client.put(
                upload["uploadUrl"],
                data=file,
                headers=headers,
                timeout=300,
            )

        # The bucket answers an upload it refuses with a reason in the body, which
        # `raise_for_status` drops -- leaving a bare status and the signed url.
        if not response.ok:
            raise GraphQLError(
                f"Uploading {file_path.name} failed with {response.status_code}:"
                f" {response.text[:500]}"
            )

        return {
            "fileId": upload["fileId"],
            "fileName": file_path.name,
            "fileMimeType": mime_type,
        }

    def download_annotation_file(
        self,
        project_id: ProjectId,
        asset_id: Optional[AssetId],
        asset_external_id: Optional[AssetExternalId],
        file_id: str,
        output_path: Path,
    ) -> str:
        """Download the file a file annotation points at.

        A file annotation stores an id, never a url: the url is signed when asked for and is short
        lived, so it is fetched here rather than kept. Streamed in chunks because the files this
        exists for -- renders, scene files -- are large.

        The asset is named by either identifier, but the project always has to be given: the file
        lives under the project in the bucket, so there is no addressing it without one.
        """
        check_asset_identifier_arguments(
            project_id,
            [asset_id] if asset_id else None,
            [asset_external_id] if asset_external_id else None,
        )
        resolved_asset_id = (
            asset_id
            or AssetUseCasesUtils(self._kili_api_gateway).get_asset_ids_or_throw_error(
                asset_ids=None,
                external_ids=[cast(AssetExternalId, asset_external_id)],
                project_id=project_id,
            )[0]
        )

        url = self._kili_api_gateway.get_annotation_file_url(
            project_id=project_id, asset_id=resolved_asset_id, file_id=file_id
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with self._kili_api_gateway.http_client.get(url, stream=True, timeout=30) as response:
            # The bucket path is keyed on the asset, so a file id belonging to another asset is a
            # 404 just like one belonging to nothing. Raising the bucket's own error would say
            # neither, and would put the signed url -- a credential -- in the caller's logs.
            if response.status_code == requests.codes.not_found:
                raise NotFound(
                    f"file {file_id} on asset {resolved_asset_id}: use the fileId read from this"
                    " asset's label"
                )
            response.raise_for_status()
            with output_path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    file.write(chunk)

        return str(output_path)

    def list_labels(
        self,
        project_id: ProjectId,
        filters: LabelFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
        output_format: Literal["dict", "parsed_label"],
    ) -> Generator:
        """List labels."""
        label_parser_post_function = None
        if output_format == "parsed_label":
            if "jsonResponse" not in fields:
                raise ValueError(
                    "The field 'jsonResponse' is required to parse labels. Please add it to the"
                    " 'fields' argument."
                )

            project = self._kili_api_gateway.get_project(
                project_id, fields=("jsonInterface", "inputType")
            )

            label_parser_post_function = partial(
                parse_labels,
                json_interface=project["jsonInterface"],
                input_type=project["inputType"],
            )

        labels_gen = self._kili_api_gateway.list_labels(
            fields=fields, filters=filters, options=options
        )

        if label_parser_post_function is not None:
            labels_gen = label_parser_post_function(labels=labels_gen)

        return labels_gen

    def delete_labels(
        self, ids: ListOrTuple[LabelId], disable_tqdm: Optional[bool]
    ) -> list[LabelId]:
        """Delete labels."""
        return self._kili_api_gateway.delete_labels(ids=ids, disable_tqdm=disable_tqdm)

    def append_labels(
        self,
        labels: list[LabelToCreateUseCaseInput],
        label_type: LabelType,
        overwrite: Optional[bool],
        project_id: Optional[ProjectId],
        fields: ListOrTuple[str],
        disable_tqdm: Optional[bool],
        step_name: Optional[str] = None,
    ) -> list[dict]:
        """Append labels."""
        check_input_labels(labels)

        asset_id_array_maybe_none = [label.asset_id for label in labels]
        resolved_asset_ids: ListOrTuple[AssetId]
        if any(asset_id is None for asset_id in asset_id_array_maybe_none):
            external_id_array: list[AssetExternalId] = []
            for label in labels:
                if label.asset_external_id is None:
                    raise ValueError("Either specify all externalId or all assetId")
                external_id_array.append(label.asset_external_id)

            resolved_asset_ids = AssetUseCasesUtils(
                self._kili_api_gateway
            ).get_asset_ids_or_throw_error(
                asset_ids=None,
                external_ids=external_id_array,
                project_id=project_id,
            )
        else:
            # All asset_ids are non-None, safe to cast
            resolved_asset_ids = cast(list[AssetId], asset_id_array_maybe_none)

        labels_to_add = [
            AppendLabelData(
                author_id=label.author_id,
                asset_id=asset_id,
                seconds_to_label=label.seconds_to_label,
                json_response=self._resolve_file_jobs(label.json_response, project_id, asset_id),
                model_name=label.model_name,
                client_version=None,
                referenced_label_id=label.referenced_label_id,
            )
            for label, asset_id in zip(labels, resolved_asset_ids, strict=False)
        ]

        data = AppendManyLabelsData(
            label_type=label_type,
            step_name=step_name,
            overwrite=overwrite,
            labels_data=labels_to_add,
        )
        try:
            return self._kili_api_gateway.append_many_labels(
                fields=fields,
                disable_tqdm=disable_tqdm,
                data=data,
                project_id=project_id,
            )
        except GraphQLError as e:
            if e.context and e.context.get("reason"):
                reason = e.context.get("reason")
                if reason in LOCK_ERRORS:
                    raise ValueError(LOCK_ERRORS[reason]) from e

            raise e

    def append_to_labels(
        self,
        author_id: Optional[UserId],
        json_response: dict,
        label_type: LabelType,
        seconds_to_label: Optional[float],
        asset_id: AssetId,
        fields: ListOrTuple[str],
    ) -> dict:
        """Append to labels."""
        data = AppendToLabelsData(
            author_id=(
                author_id
                if author_id is not None
                else self._kili_api_gateway.get_current_user(fields=("id",))["id"]
            ),
            json_response=json_response,
            label_type=label_type,
            seconds_to_label=seconds_to_label,
            client_version=None,
            skipped=None,
        )
        return self._kili_api_gateway.append_to_labels(data=data, asset_id=asset_id, fields=fields)

    def create_honeypot_label(
        self,
        json_response: dict,
        asset_id: Optional[AssetId],
        asset_external_id: Optional[AssetExternalId],
        project_id: Optional[ProjectId],
        fields: ListOrTuple[str],
    ) -> dict:
        """Create honeypot label."""
        if asset_id is None:
            if asset_external_id is None or project_id is None:
                raise ValueError(
                    "Either provide `asset_id` or `asset_external_id` and `project_id`."
                )

            asset_id = AssetUseCasesUtils(self._kili_api_gateway).infer_ids_from_external_ids(
                asset_external_ids=[asset_external_id],
                project_id=project_id,
            )[asset_external_id]

        return self._kili_api_gateway.create_honeypot_label(
            json_response=json_response, asset_id=asset_id, fields=fields
        )

    def export_labels_as_df(
        self,
        *,
        project_id: ProjectId,
        label_fields: ListOrTuple[str],
        asset_fields: ListOrTuple[str],
    ) -> "pd.DataFrame":
        """Export labels as a pandas DataFrame."""
        assets_gen = self._kili_api_gateway.list_assets(
            AssetFilters(project_id=ProjectId(project_id)),
            tuple(asset_fields) + tuple("labels." + field for field in label_fields),
            QueryOptions(disable_tqdm=False),
        )

        labels = [
            dict(
                label,
                **{f"asset_{key}": asset[key] for key in asset if key != "labels"},
            )
            for asset in assets_gen
            for label in asset["labels"]
        ]

        try:
            import pandas as pd  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            raise ImportError("Install `pip install kili[pandas]` for format='pandas'.") from e
        return pd.DataFrame(labels)
