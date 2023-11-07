"""Utils for use cases."""

from itertools import chain
from typing import TYPE_CHECKING, Dict, Optional

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.utils import pagination
from kili.domain.asset import AssetExternalId, AssetFilters, AssetId
from kili.domain.asset.helpers import check_asset_identifier_arguments
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import NotFound

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
        self, asset_external_ids: ListOrTuple[AssetExternalId], project_id: ProjectId
    ) -> Dict[AssetExternalId, AssetId]:
        """Infer asset ids from their external ids and project Id.

        Args:
            asset_external_ids: asset external ids
            project_id: project id

        Returns:
            a dict that maps external ids to internal ids.

        Raises:
            NotFound: when there are asset_ids what have the same external id, or when external ids
            have not been found.
        """
        id_map = self._build_id_map(asset_external_ids, project_id)

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

    def _build_id_map(
        self, asset_external_ids: ListOrTuple[AssetExternalId], project_id: ProjectId
    ) -> Dict[AssetExternalId, AssetId]:
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
        id_map: Dict[AssetExternalId, AssetId] = {}
        asset_external_ids_set = set(asset_external_ids)
        for asset in (asset for asset in assets if asset["externalId"] in asset_external_ids_set):
            id_map[AssetExternalId(asset["externalId"])] = AssetId(asset["id"])
        return id_map
