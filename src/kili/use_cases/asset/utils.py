"""Utils for use cases."""

from itertools import chain
from typing import TYPE_CHECKING, Optional, cast

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.utils import pagination
from kili.domain.asset import AssetExternalId, AssetFilters, AssetId
from kili.domain.asset.helpers import check_asset_identifier_arguments
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import IncompatibleArgumentsError, MissingArgumentError, NotFound

if TYPE_CHECKING:
    from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway


class AssetUseCasesUtils:
    """Utils for use cases."""

    def __init__(self, kili_api_gateway: "KiliAPIGateway") -> None:
        """Init."""
        self.kili_api_gateway = kili_api_gateway

    def get_asset_ids_or_throw_error(
        self,
        asset_ids: Optional[ListOrTuple[AssetId]],
        external_ids: Optional[ListOrTuple[AssetExternalId]],
        project_id: Optional[ProjectId],
    ) -> ListOrTuple[AssetId]:
        """Check if external id to internal id conversion is valid and needed."""
        check_asset_identifier_arguments(project_id, asset_ids, external_ids)

        if asset_ids is None and external_ids is not None and project_id is not None:
            id_map = self.infer_ids_from_external_ids(external_ids, project_id)
            resolved_asset_ids = [id_map[ext_id] for ext_id in external_ids]
        else:
            resolved_asset_ids = asset_ids or []

        return resolved_asset_ids

    def infer_ids_from_external_ids(
        self,
        asset_external_ids: ListOrTuple[AssetExternalId],
        project_id: ProjectId,
        *,
        refuse_duplicates: bool = False,
    ) -> dict[AssetExternalId, AssetId]:
        """Infer asset ids from their external ids and project Id.

        Args:
            asset_external_ids: asset external ids
            project_id: project id
            refuse_duplicates: raise when several assets of the project have one of the external
                ids, instead of picking one of them

        Returns:
            a dict that maps external ids to internal ids.

        Raises:
            NotFound: when there are asset_ids what have the same external id, or when external ids
            have not been found.
        """
        id_map = self._build_id_map(
            asset_external_ids, project_id, refuse_duplicates=refuse_duplicates
        )

        if len(id_map) < len(set(asset_external_ids)):
            assets_not_found = [
                external_id for external_id in asset_external_ids if external_id not in id_map
            ]
            raise NotFound(
                f"The assets whose external_id are: {assets_not_found} have not been found in the"
                f" project of Id {project_id}"
            )
        if len(id_map) > len(set(asset_external_ids)):
            raise NotFound(
                "Several assets have been found for the same external_id. Please consider using"
                " asset ids instead."
            )
        return id_map

    def get_metadata_targets(
        self,
        project_id: ProjectId,
        asset_ids: Optional[list[str]],
        external_ids: Optional[list[str]],
        nb_metadata: Optional[int] = None,
    ) -> tuple[list[str], dict[str, dict]]:
        """The ids of the assets a metadata call targets, in the order given, and each one's metadata.

        Args:
            project_id: The project of the assets.
            asset_ids: The asset ids, if the call identifies the assets by id.
            external_ids: The external ids, matched exactly, if the call identifies the assets by them.
            nb_metadata: The number of metadata dictionaries the call gives, one per id; None when the
                call gives none.

        Raises:
            MissingArgumentError: If both or neither of `asset_ids` and `external_ids` are given.
            IncompatibleArgumentsError: If the call gives a metadata dictionary count other than the
                id count.
            NotFound: If an id matches no asset of the project, or an external id several.
        """
        if (asset_ids is None) == (external_ids is None):
            raise MissingArgumentError("Please provide either `asset_ids` or `external_ids`.")
        ids_name, given_ids = (
            ("asset_ids", asset_ids) if asset_ids is not None else ("external_ids", external_ids)
        )
        given_ids = cast(list[str], given_ids)
        if nb_metadata is not None and nb_metadata != len(given_ids):
            raise IncompatibleArgumentsError(
                f"`json_metadata` has {nb_metadata} item(s) and `{ids_name}` {len(given_ids)}: give"
                " one metadata dictionary per asset, in the same order."
            )
        if not given_ids:
            return [], {}

        if external_ids is not None:
            id_map = self.infer_ids_from_external_ids(
                cast(list[AssetExternalId], external_ids), project_id, refuse_duplicates=True
            )
            given_ids = [str(id_map[AssetExternalId(external_id)]) for external_id in external_ids]

        unique_ids = list(dict.fromkeys(given_ids))
        assets = self.kili_api_gateway.list_assets(
            AssetFilters(project_id=project_id, asset_id_in=cast(list[AssetId], unique_ids)),
            ["id", "jsonMetadata"],
            QueryOptions(disable_tqdm=True),
        )
        metadata_by_id: dict[str, dict] = {
            asset["id"]: asset.get("jsonMetadata") or {} for asset in assets
        }
        not_found = [asset_id for asset_id in unique_ids if asset_id not in metadata_by_id]
        if not_found:
            raise NotFound(
                f"The assets whose id are: {not_found} have not been found in the project of Id"
                f" {project_id}"
            )
        return given_ids, metadata_by_id

    def _build_id_map(
        self,
        asset_external_ids: ListOrTuple[AssetExternalId],
        project_id: ProjectId,
        *,
        refuse_duplicates: bool = False,
    ) -> dict[AssetExternalId, AssetId]:
        # we batch the queries because too many assets in a "in" query makes the query fail
        assets_generators = (
            self.kili_api_gateway.list_assets(
                AssetFilters(project_id, external_id_strictly_in=external_ids_batch),
                ["id", "externalId"],
                QueryOptions(disable_tqdm=True),
            )
            for external_ids_batch in pagination.batcher(list(asset_external_ids), 1000)
        )
        assets = chain(*assets_generators)
        id_map: dict[AssetExternalId, AssetId] = {}
        asset_external_ids_set = set(asset_external_ids)
        for asset in (asset for asset in assets if asset["externalId"] in asset_external_ids_set):
            external_id = AssetExternalId(asset["externalId"])
            if refuse_duplicates and external_id in id_map:
                raise NotFound(
                    f"Several assets of the project of Id {project_id} have the external_id"
                    f" {external_id!r}: use their asset ids instead."
                )
            id_map[external_id] = AssetId(asset["id"])
        return id_map
