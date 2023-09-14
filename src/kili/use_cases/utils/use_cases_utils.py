from itertools import chain
from typing import Dict, Generator, List, Optional

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.utils import pagination
from kili.domain.asset import AssetFilters
from kili.domain.asset.helpers import check_asset_identifier_arguments
from kili.exceptions import NotFound


class UseCasesUtils:
    def __init__(self, kili_api_gateway: KiliAPIGateway) -> None:
        self.kili_api_gateway = kili_api_gateway

    def get_asset_ids_or_throw_error(
        self,
        asset_ids: Optional[List[str]],
        external_ids: Optional[List[str]],
        project_id: Optional[str],
    ) -> List[str]:
        """Check if external id to internal id conversion is valid and needed."""
        check_asset_identifier_arguments(project_id, asset_ids, external_ids)

        if asset_ids is None:
            id_map = self.infer_ids_from_external_ids(
                external_ids, project_id  # type: ignore
            )  # type: ignore
            asset_ids = [id_map[id] for id in external_ids]  # type: ignore

        return asset_ids

    def infer_ids_from_external_ids(
        self, asset_external_ids: List[str], project_id: str
    ) -> Dict[str, str]:
        """Infer asset ids from their external ids and project Id.

        Args:
            kili_api_gateway: Kili API gateway
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

    def _build_id_map(self, asset_external_ids, project_id):
        assets_generators: List[Generator[Dict, None, None]] = []
        # query all assets by external ids batches when there are too many
        for external_ids_batch in pagination.BatchIteratorBuilder(asset_external_ids, 1000):
            assets_generators.append(
                self.kili_api_gateway.list_assets(
                    AssetFilters(project_id, external_id_strictly_in=external_ids_batch),
                    ["id", "externalId"],
                    QueryOptions(disable_tqdm=True),
                )
            )
        assets = chain(*assets_generators)
        id_map: Dict[str, str] = {}
        asset_external_ids_set = set(asset_external_ids)
        for asset in (asset for asset in assets if asset["externalId"] in asset_external_ids_set):
            id_map[asset["externalId"]] = asset["id"]
        return id_map
