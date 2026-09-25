"""Asset use cases."""

import itertools
import warnings
from collections import defaultdict
from collections.abc import Callable, Generator
from typing import Literal, Optional, TypeVar

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.constants import QUERY_BATCH_SIZE
from kili.core.helpers import validate_category_search_query
from kili.core.utils.pagination import batcher
from kili.domain.asset import AssetExternalId, AssetFilters, AssetId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import (
    GraphQLError,
    IncompatibleArgumentsError,
    MissingArgumentError,
    NotFound,
)
from kili.services.label_data_parsing.types import Project as LabelParsingProject
from kili.use_cases.asset.asset_label_parsing import parse_labels_of_asset
from kili.use_cases.asset.media_downloader import get_download_assets_function
from kili.use_cases.base import BaseUseCases

# above this many ids, an "in" filter makes the query fail
IDS_BATCH_SIZE = 1000

T = TypeVar("T")


class AssetUseCases(BaseUseCases):
    """Asset use cases."""

    # pylint: disable=too-many-arguments
    def list_assets(
        self,
        filters: AssetFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
        download_media: bool,
        local_media_dir: Optional[str],
        label_output_format: Literal["dict", "parsed_label"],
    ) -> Generator:
        """List assets with given options."""
        if filters.label_category_search:
            validate_category_search_query(filters.label_category_search)

        download_media_function, fields = get_download_assets_function(
            self._kili_api_gateway,
            download_media,
            fields,
            ProjectId(filters.project_id),
            local_media_dir,
        )
        assets_gen = self._kili_api_gateway.list_assets(filters, fields, options)

        if download_media_function is not None:
            # TODO: modify download_media function so it can take a generator of assets
            assets_lists = [
                download_media_function(assets_batch)
                for assets_batch in batcher(assets_gen, QUERY_BATCH_SIZE)
            ]
            assets_gen = (asset for asset in itertools.chain(*assets_lists))

        if label_output_format == "parsed_label":
            project = LabelParsingProject(
                **self._kili_api_gateway.get_project(
                    ProjectId(filters.project_id), ("jsonInterface", "inputType")
                )
            )
            assets_gen = (parse_labels_of_asset(asset, project) for asset in assets_gen)

        return assets_gen

    def count_assets(self, filters: AssetFilters) -> int:
        """Send a GraphQL request calling countAssets resolver."""
        if filters.label_category_search:
            validate_category_search_query(filters.label_category_search)
        return self._kili_api_gateway.count_assets(filters)

    def list_deleted_assets(
        self, project_id: ProjectId, fields: ListOrTuple[str], options: QueryOptions
    ) -> Generator:
        """List the deleted assets of a project that can still be restored."""
        return self._kili_api_gateway.list_assets(
            AssetFilters(project_id=project_id, show_only_restorable=True), fields, options
        )

    def count_deleted_assets(self, project_id: ProjectId) -> int:
        """Count the deleted assets of a project that can still be restored."""
        return self._kili_api_gateway.count_assets(
            AssetFilters(project_id=project_id, show_only_restorable=True)
        )

    def restore_assets(
        self,
        project_id: ProjectId,
        asset_ids: Optional[ListOrTuple[AssetId]],
        external_ids: Optional[ListOrTuple[AssetExternalId]],
    ) -> list[dict[str, Optional[str]]]:
        """Restore deleted assets of a project, all of them or none.

        Every asset is checked before anything is restored: each one must be among the deleted
        assets of the project, and its external id must not be used by an asset of the project,
        nor by another asset being restored.

        Returns:
            The restored assets, in the order they were given, as `id` and `externalId`.
        """
        if asset_ids is not None and external_ids is not None:
            raise IncompatibleArgumentsError(
                "Either provide asset IDs or asset external IDs. Not both at the same time."
            )
        if asset_ids is None and external_ids is None:
            raise MissingArgumentError("Provide the asset IDs or the external IDs to restore.")

        self._check_can_restore(project_id)
        if asset_ids is not None:
            assets_to_restore = self._get_deleted_assets_by_ids(project_id, asset_ids)
        else:
            assert external_ids is not None
            assets_to_restore = self._get_deleted_assets_by_external_ids(project_id, external_ids)
        if not assets_to_restore:
            return []

        self._check_external_ids_are_free(project_id, assets_to_restore)

        restored_ids = set(
            self._kili_api_gateway.restore_deleted_assets(
                project_id, [AssetId(asset["id"]) for asset in assets_to_restore]
            )
        )
        not_restored = [
            asset["id"] for asset in assets_to_restore if asset["id"] not in restored_ids
        ]
        if not_restored:
            warnings.warn(
                f"The assets of ids {not_restored} were not reported as restored: they may have"
                " been permanently deleted meanwhile, or restored by a retried request. Check them"
                " with kili.deleted_assets().",
                stacklevel=2,
            )
        return [
            {"id": asset["id"], "externalId": asset["externalId"]}
            for asset in assets_to_restore
            if asset["id"] in restored_ids
        ]

    def _check_can_restore(self, project_id: ProjectId) -> None:
        # The deleted assets a user can list depend on their role, so the checks below would
        # answer "not found" to a labeler. Restoring no asset runs the backend's permission check
        # alone, and restores nothing.
        try:
            self._kili_api_gateway.restore_deleted_assets(project_id, [])
        except GraphQLError as error:
            original = error.error[0] if isinstance(error.error, list) else error.error
            reason = original["message"] if isinstance(original, dict) else str(original)
            if "[accessDenied]" not in reason:
                raise
            raise GraphQLError(
                f"Only an admin of project {project_id} can restore its deleted assets. Nothing"
                f" was restored: {reason}",
                context=error.context,
            ) from error

    def _list_assets_in_batches(
        self, values: list[T], to_filters: Callable[[list[T]], AssetFilters]
    ) -> list[dict]:
        found: list[dict] = []
        for batch in batcher(values, IDS_BATCH_SIZE):
            found.extend(
                self._kili_api_gateway.list_assets(
                    to_filters(batch), ("id", "externalId"), QueryOptions(disable_tqdm=True)
                )
            )
        return found

    def _get_deleted_assets_by_ids(
        self, project_id: ProjectId, asset_ids: ListOrTuple[AssetId]
    ) -> list[dict]:
        unique_ids = list(dict.fromkeys(asset_ids))
        found = {
            asset["id"]: asset
            for asset in self._list_assets_in_batches(
                unique_ids,
                lambda batch: AssetFilters(
                    project_id, asset_id_in=batch, show_only_restorable=True
                ),
            )
        }
        missing = [asset_id for asset_id in unique_ids if asset_id not in found]
        if missing:
            raise NotFound(
                f"The assets of ids {missing} are not among the deleted assets of project"
                f" {project_id} that can still be restored: they were never deleted, have"
                " already been restored, or have been permanently deleted. Nothing was restored."
            )
        return [found[asset_id] for asset_id in unique_ids]

    def _get_deleted_assets_by_external_ids(
        self, project_id: ProjectId, external_ids: ListOrTuple[AssetExternalId]
    ) -> list[dict]:
        unique_external_ids = list(dict.fromkeys(external_ids))
        found_by_external_id: dict[str, list[dict]] = defaultdict(list)
        for asset in self._list_assets_in_batches(
            unique_external_ids,
            lambda batch: AssetFilters(
                project_id, external_id_strictly_in=batch, show_only_restorable=True
            ),
        ):
            found_by_external_id[asset["externalId"]].append(asset)

        missing = [ext_id for ext_id in unique_external_ids if ext_id not in found_by_external_id]
        if missing:
            raise NotFound(
                f"The assets of external ids {missing} are not among the deleted assets of"
                f" project {project_id} that can still be restored: they were never deleted,"
                " have already been restored, or have been permanently deleted. Nothing was"
                " restored."
            )
        ambiguous = {
            ext_id: [asset["id"] for asset in assets]
            for ext_id, assets in found_by_external_id.items()
            if len(assets) > 1
        }
        if ambiguous:
            raise ValueError(
                "Several deleted assets of project"
                f" {project_id} have the same external id: {ambiguous}. Restore the one you"
                " want with its asset id. Nothing was restored."
            )
        return [found_by_external_id[ext_id][0] for ext_id in unique_external_ids]

    def _check_external_ids_are_free(
        self, project_id: ProjectId, assets_to_restore: list[dict]
    ) -> None:
        ids_by_external_id: dict[AssetExternalId, list[str]] = defaultdict(list)
        for asset in assets_to_restore:
            if asset["externalId"]:
                ids_by_external_id[asset["externalId"]].append(asset["id"])

        shared = {ext_id: ids for ext_id, ids in ids_by_external_id.items() if len(ids) > 1}
        if shared:
            raise ValueError(
                f"The assets to restore share external ids: {shared}. Two assets of project"
                f" {project_id} cannot have the same external id: restore only one asset of"
                " each. Nothing was restored."
            )

        in_use = {
            asset["externalId"]: asset["id"]
            for asset in self._list_assets_in_batches(
                list(ids_by_external_id),
                lambda batch: AssetFilters(project_id, external_id_strictly_in=batch),
            )
        }
        if in_use:
            raise ValueError(
                f"Cannot restore the assets: the external ids {list(in_use)} are already used by"
                f" other assets of project {project_id} (external id: asset id {in_use}). Change"
                " the external id of those assets, or delete them, then restore again. Nothing"
                " was restored."
            )
