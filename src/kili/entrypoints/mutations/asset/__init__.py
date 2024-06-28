"""Asset mutations."""

import warnings
from typing import Any, Dict, List, Literal, Optional, Union, cast

from tenacity import retry
from tenacity.retry import retry_if_exception_type
from tenacity.wait import wait_exponential
from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.helpers import is_empty_list_with_warning
from kili.core.utils.pagination import mutate_from_paginated_call
from kili.domain.asset import AssetFilters
from kili.domain.project import ProjectId
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.entrypoints.mutations.asset.helpers import (
    process_update_properties_in_assets_parameters,
)
from kili.entrypoints.mutations.asset.queries import (
    GQL_ADD_ALL_LABELED_ASSETS_TO_REVIEW,
    GQL_DELETE_MANY_FROM_DATASET,
    GQL_SEND_BACK_ASSETS_TO_QUEUE,
    GQL_UPDATE_PROPERTIES_IN_ASSETS,
)
from kili.entrypoints.mutations.exceptions import MutationError
from kili.exceptions import MissingArgumentError
from kili.services.asset_import import import_assets
from kili.services.asset_import_csv import get_text_assets_from_csv
from kili.utils.assets import PageResolution
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class MutationsAsset(BaseOperationEntrypointMixin):
    """Set of Asset mutations."""

    # pylint: disable=too-many-arguments,too-many-locals
    @typechecked
    def append_many_to_dataset(
        self,
        project_id: str,
        content_array: Optional[Union[List[str], List[dict], List[List[dict]]]] = None,
        multi_layer_content_array: Optional[List[List[dict]]] = None,
        external_id_array: Optional[List[str]] = None,
        id_array: Optional[List[str]] = None,
        is_honeypot_array: Optional[List[bool]] = None,
        status_array: Optional[List[str]] = None,
        json_content_array: Optional[List[Union[List[Union[dict, str]], None]]] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        from_csv: Optional[str] = None,
        csv_separator: str = ",",
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        # pylint: disable=line-too-long
        """Append assets to a project.

        Args:
            project_id: Identifier of the project
            content_array: List of elements added to the assets of the project
                Must not be None except if you provide multi_layer_content_array or json_content_array.

                - For a `TEXT` project, the content can be either raw text, or URLs to TEXT assets.
                - For an `IMAGE` / `PDF` project, the content can be either URLs or paths to existing
                    images/pdf on your computer.
                - For a VIDEO project, the content can be either URLs pointing to videos hosted on a web server or paths to
                existing video files on your computer. If you want to import video from frames, look at the json_content
                section below.
                - For an `VIDEO_LEGACY` project, the content can be only be URLs.
                - For an `LLM_RLHF` project, the content can be dicts with the keys `prompt` and `completions`,
                paths to local json files or URLs to json files.
            multi_layer_content_array: List containing multiple lists of paths.
                Each path correspond to a layer of a geosat asset. Should be used only for `IMAGE` projects.
            external_id_array: List of external ids given to identify the assets.
                If None, random identifiers are created.
            id_array: Disabled parameter. Do not use.
            is_honeypot_array:  Whether to use the asset for honeypot
            status_array: DEPRECATED and does not have any effect.
            json_content_array: Useful for `VIDEO` or `TEXT` or `IMAGE` projects only.

                - For `VIDEO` projects, each element is a sequence of frames, i.e. a
                    list of URLs to images or a list of paths to images.
                - For `TEXT` projects, each element is a json_content dict,
                    formatted according to documentation [on how to import
                rich-text assets](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/import_text_assets/).
                - For `IMAGES` projects, it is used for satellite imagery each element is a list of json_content dicts
                    formatted according to documentation [on how to add multi-layer images]
                    (https://docs.kili-technology.com/docs/adding-assets-to-project#adding-multi-layer-images)

            json_metadata_array: The metadata given to each asset should be stored in a json like dict with keys.

                - Add metadata visible on the asset with the following keys: `imageUrl`, `text`, `url`.
                    Example for one asset: `json_metadata_array = [{'imageUrl': '','text': '','url': ''}]`.
                - For VIDEO projects (and not VIDEO_LEGACY), you can specify a value with key 'processingParameters' to specify the sampling rate (default: 30).
                    Example for one asset: `json_metadata_array = [{'processingParameters': {'framesPlayedPerSecond': 10}}]`.
                - In Image projects with geoTIFF assets, you can specify the epsg, the `minZoom` and `maxZoom` values for the `processingParameters` key.
                    - The epsg is a number that defines the projection that will be used for the asset. Values that can be used are either 4326 or 3857, the 2
                    projections that we support. If this number is not set, by default we keep the initial projection of the asset if it is 4326 or 3857, either
                    we reproject the asset to EPSG:3857 by default.
                    - The `minZoom` parameter defines the zoom level that users are not allowed to zoom out from. It also affects the zoom levels for which we
                    generate the tiles when tiling the asset (for asset with size > 30MB).
                    - The `maxZoom` value affects asset generation: the higher the value, the greater the level of details and the size of the asset. It also affects
                    the zoom levels for which we generate the tiles when tiling the asset (for asset with size > 30MB).
                    - Example for one asset: `json_metadata_array = [{'processingParameters': {'epsg': 3758, 'minZoom': 17, 'maxZoom': 19}}]`.
            disable_tqdm: If `True`, the progress bar will be disabled
            wait_until_availability: If `True`, the function will return once the assets are fully imported in Kili.
                If `False`, the function will return faster but the assets might not be fully processed by the server.
            from_csv: Path to a csv file containing the text assets to import.
                Only used for `TEXT` projects.
                If provided, `content_array` and `external_id_array` must be None.
                The csv file header must specify the columns `content` and `externalId`.
            csv_separator: Separator used in the csv file. Only used if `from_csv` is provided.


        Returns:
            A dictionary with two fields: `id` which is the project id and `asset_ids` which is a list of the created asset ids.
            In the case where assets are uploaded asynchronously (for video imported as frames or big images or tiff images), the method return an empty list of asset ids.

        Examples:
            >>> kili.append_many_to_dataset(
                    project_id=project_id,
                    content_array=['https://upload.wikimedia.org/wikipedia/en/7/7d/Lenna_%28test_image%29.png'])

        !!! example "Recipe"
            - For more detailed examples on how to import assets,
                see [the recipe](https://docs.kili-technology.com/recipes/importing-data).
            - For more detailed examples on how to import text assets,
                see [the recipe](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/import_text_assets/).
        """
        if from_csv is not None:
            if content_array is not None or external_id_array is not None:
                raise ValueError(
                    "If from_csv is provided, content_array and external_id_array must not be"
                    " provided."
                )
            content_array, external_id_array = get_text_assets_from_csv(
                from_csv=from_csv, csv_separator=csv_separator
            )

        if (
            is_empty_list_with_warning("append_many_to_dataset", "content_array", content_array)
            or is_empty_list_with_warning(
                "append_many_to_dataset", "json_content_array", json_content_array
            )
            or is_empty_list_with_warning(
                "append_many_to_dataset", "multi_layer_content_array", multi_layer_content_array
            )
        ):
            return {"id": project_id, "asset_ids": []}

        if status_array is not None:
            warnings.warn(
                "status_array is deprecated and will not be sent in the call. Asset status is"
                " automatically computed based on its labels and cannot be overwritten.",
                DeprecationWarning,
                stacklevel=1,
            )

        if (
            content_array is None
            and multi_layer_content_array is None
            and json_content_array is None
        ):
            raise ValueError(
                "Variables content_array, multi_layer_content_array and json_content_array cannot be both None."
            )

        if content_array is not None and multi_layer_content_array is not None:
            raise ValueError(
                "Variables content_array and multi_layer_content_array cannot be both provided."
            )

        nb_data = (
            len(content_array)
            if content_array is not None
            else (
                len(multi_layer_content_array)
                if multi_layer_content_array is not None
                else len(json_content_array)  # type:ignore
            )
        )

        field_mapping = {
            "content": content_array,
            "multi_layer_content": multi_layer_content_array,
            "json_content": json_content_array,
            "external_id": external_id_array,
            "id": id_array,
            "json_metadata": json_metadata_array,
            "is_honeypot": is_honeypot_array,
        }
        assets = [{}] * nb_data
        for key, value in field_mapping.items():
            if value is not None:
                assets = [{**assets[i], key: value[i]} for i in range(nb_data)]
        created_asset_ids = import_assets(
            self,  # pyright: ignore[reportGeneralTypeIssues]
            project_id=ProjectId(project_id),
            assets=assets,
            disable_tqdm=disable_tqdm,
            verify=wait_until_availability,
        )
        return {"id": project_id, "asset_ids": created_asset_ids}

    @typechecked
    def update_properties_in_assets(
        self,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        priorities: Optional[List[int]] = None,
        json_metadatas: Optional[List[Union[dict, str]]] = None,
        consensus_marks: Optional[List[float]] = None,
        honeypot_marks: Optional[List[float]] = None,
        to_be_labeled_by_array: Optional[List[List[str]]] = None,
        contents: Optional[List[str]] = None,
        json_contents: Optional[List[str]] = None,
        status_array: Optional[List[str]] = None,
        is_used_for_consensus_array: Optional[List[bool]] = None,
        is_honeypot_array: Optional[List[bool]] = None,
        project_id: Optional[str] = None,
        resolution_array: Optional[List[Dict]] = None,
        page_resolutions_array: Optional[
            Union[List[List[dict]], List[List[PageResolution]]]
        ] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Update the properties of one or more assets.

        Args:
            asset_ids: The internal asset IDs to modify.
            external_ids: The external asset IDs to modify (if `asset_ids` is not already provided).
            priorities: You can change the priority of the assets.
                By default, all assets have a priority of 0.
            json_metadatas: The metadata given to an asset should be stored
                in a json like dict with keys `imageUrl`, `text`, `url`:
                `json_metadata = {'imageUrl': '','text': '','url': ''}`
            consensus_marks: Should be between 0 and 1.
            honeypot_marks: Should be between 0 and 1.
            to_be_labeled_by_array: If given, each element of the list should contain the emails of
                the labelers authorized to label the asset.
            contents: - For a NLP project, the content can be directly in text format.
                - For an Image / Video / Pdf project, the content must be hosted on a web server,
                and you point Kili to your data by giving the URLs.
            json_contents: - For a NLP project, the `json_content`
                is a text formatted using RichText.
                - For a Video project, the`json_content` is a json containg urls pointing
                    to each frame of the video.
            status_array: DEPRECATED and does not have any effect.
            is_used_for_consensus_array: Whether to use the asset to compute consensus kpis or not.
            is_honeypot_array: Whether to use the asset for honeypot.
            project_id: The project ID. Only required if `external_ids` argument is provided.
            resolution_array: The resolution of each asset (for image and video assets).
                Each resolution must be passed as a dictionary with keys `width` and `height`.
            page_resolutions_array: The resolution of each page of the asset (for PDF assets).
                Note that each element of the array should contain all the pages resolutions of the
                corresponding asset. Each resolution can be passed as a
                `kili.utils.assets.PageResolution` object, or as a dictionary with keys `width`,
                `height`, `pageNumber` and optionally `rotation`.

        Returns:
            A list of dictionaries with the asset ids.

        Examples:
            >>> kili.update_properties_in_assets(
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
                    consensus_marks=[1, 0.7],
                    contents=[None, 'https://to/second/asset.png'],
                    honeypot_marks=[0.8, 0.5],
                    is_honeypot_array=[True, True],
                    is_used_for_consensus_array=[True, False],
                    priorities=[None, 2],
                    to_be_labeled_by_array=[['test+pierre@kili-technology.com'], None],
                )

                # The following call updates the pages resolutions of PDF assets.
            >>> kili.update_properties_in_assets(
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
                    page_resolutions_array=[
                        [
                            PageResolution(width=480, height=640, page_number=1),
                            PageResolution(width=480, height=640, page_number=2),
                        ],[
                            PageResolution(width=340, height=512, page_number=1),
                            PageResolution(width=680, height=1024, page_number=2, rotation=90),
                            PageResolution(width=680, height=1024, page_number=3),
                        ]
                    ],
                )
        """
        if is_empty_list_with_warning(
            "update_properties_in_assets", "asset_ids", asset_ids
        ) or is_empty_list_with_warning(
            "update_properties_in_assets", "external_ids", external_ids
        ):
            return []

        if status_array is not None:
            warnings.warn(
                "status_array is deprecated and will not be sent in the call. Asset status is"
                " automatically computed based on its labels and cannot be overwritten.",
                DeprecationWarning,
                stacklevel=1,
            )
        if asset_ids is not None and external_ids is not None:
            warnings.warn(
                "The use of `external_ids` argument has changed. It is now used to identify"
                " which properties of which assets to update. Please use"
                " `kili.change_asset_external_ids()` method instead to change asset external"
                " IDs.",
                DeprecationWarning,
                stacklevel=1,
            )
            raise MissingArgumentError("Please provide either `asset_ids` or `external_ids`.")

        resolved_asset_ids = self._resolve_asset_ids(asset_ids, external_ids, project_id)

        properties_to_batch = process_update_properties_in_assets_parameters(
            cast(List[str], resolved_asset_ids),
            priorities=priorities,
            json_metadatas=json_metadatas,
            consensus_marks=consensus_marks,
            honeypot_marks=honeypot_marks,
            to_be_labeled_by_array=to_be_labeled_by_array,
            contents=contents,
            json_contents=json_contents,
            is_used_for_consensus_array=is_used_for_consensus_array,
            is_honeypot_array=is_honeypot_array,
            resolution_array=resolution_array,
            page_resolutions_array=page_resolutions_array,
        )

        def generate_variables(batch: Dict) -> Dict:
            asset_ids = batch.pop("assetId")
            data_array = [dict(zip(batch, t)) for t in zip(*batch.values())]  # type: ignore
            return {
                "whereArray": [{"id": asset_id} for asset_id in asset_ids],
                "dataArray": data_array,
            }

        results = mutate_from_paginated_call(
            self,
            properties_to_batch,
            generate_variables,
            GQL_UPDATE_PROPERTIES_IN_ASSETS,
        )
        formated_results = [self.format_result("data", result, None) for result in results]
        return [item for batch_list in formated_results for item in batch_list]

    @typechecked
    def change_asset_external_ids(
        self,
        new_external_ids: List[str],
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Update the external IDs of one or more assets.

        Args:
            new_external_ids: The new external IDs of the assets.
            asset_ids: The asset IDs to modify.
            external_ids: The external asset IDs to modify (if `asset_ids` is not already provided).
            project_id: The project ID. Only required if `external_ids` argument is provided.

        Returns:
            A list of dictionaries with the asset ids.

        Examples:
            >>> kili.change_asset_external_ids(
                    new_external_ids=["asset1", "asset2"],
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
                )
        """
        if is_empty_list_with_warning(
            "change_asset_external_ids", "new_external_ids", new_external_ids
        ):
            return []

        resolved_asset_ids = self._resolve_asset_ids(asset_ids, external_ids, project_id)

        properties_to_batch = process_update_properties_in_assets_parameters(
            asset_ids=cast(List[str], resolved_asset_ids),
            external_ids=new_external_ids,
        )

        def generate_variables(batch: Dict) -> Dict:
            asset_ids = batch.pop("assetId")
            data_array = [dict(zip(batch, t)) for t in zip(*batch.values())]  # type: ignore
            return {
                "whereArray": [{"id": asset_id} for asset_id in asset_ids],
                "dataArray": data_array,
            }

        results = mutate_from_paginated_call(
            self,
            properties_to_batch,
            generate_variables,
            GQL_UPDATE_PROPERTIES_IN_ASSETS,
        )
        formated_results = [self.format_result("data", result, None) for result in results]
        return [item for batch_list in formated_results for item in batch_list]

    @typechecked
    def delete_many_from_dataset(
        self,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> Optional[Dict[Literal["id"], str]]:
        """Delete assets from a project.

        Args:
            asset_ids: The list of asset internal IDs to delete.
            external_ids: The list of asset external IDs to delete.
            project_id: The project ID. Only required if `external_ids` argument is provided.

        Returns:
            A dict object with the project `id`.
        """
        if is_empty_list_with_warning(
            "delete_many_from_dataset", "asset_ids", asset_ids
        ) or is_empty_list_with_warning("delete_many_from_dataset", "external_ids", external_ids):
            return None

        resolved_asset_ids = self._resolve_asset_ids(asset_ids, external_ids, project_id)

        properties_to_batch = {"asset_ids": resolved_asset_ids}

        def generate_variables(batch):
            return {"where": {"idIn": batch["asset_ids"]}}

        @retry(
            wait=wait_exponential(multiplier=1, min=1, max=8),
            retry=retry_if_exception_type(MutationError),
            reraise=True,
        )
        def verify_last_batch(last_batch: Dict, results: List) -> None:
            """Check that all assets in the last batch have been deleted."""
            if project_id is not None:
                project_id_ = project_id
            # in some case the results is [{'data': None}]
            elif isinstance(results[0]["data"], Dict) and results[0]["data"].get("id"):
                project_id_ = results[0]["data"].get("id")
            else:
                return

            asset_ids = last_batch["asset_ids"][-1:]  # check last asset of the batch only

            nb_assets_in_kili = self.kili_api_gateway.count_assets(
                AssetFilters(
                    project_id=ProjectId(project_id_),
                    asset_id_in=asset_ids,
                )
            )
            if nb_assets_in_kili > 0:
                raise MutationError("Failed to delete some assets.")

        results = mutate_from_paginated_call(
            self,
            properties_to_batch,
            generate_variables,
            GQL_DELETE_MANY_FROM_DATASET,
            last_batch_callback=verify_last_batch,
        )
        return self.format_result("data", results[0])

    @typechecked
    def add_to_review(
        self,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Add assets to review.

        !!! warning
            Assets without any label will be ignored.

        Args:
            asset_ids: The asset internal IDs to add to review.
            external_ids: The asset external IDs to add to review.
            project_id: The project ID. Only required if `external_ids` argument is provided.

        Returns:
            A dict object with the project `id` and the `asset_ids` of assets moved to review.
            `None` if no assets have changed status (already had `TO_REVIEW` status for example).
            An error message if mutation failed.

        Examples:
            >>> kili.add_to_review(
                    asset_ids=[
                        "ckg22d81r0jrg0885unmuswj8",
                        "ckg22d81s0jrh0885pdxfd03n",
                    ],
                )
        """
        if is_empty_list_with_warning(
            "add_to_review", "asset_ids", asset_ids
        ) or is_empty_list_with_warning("add_to_review", "external_ids", external_ids):
            return None

        resolved_asset_ids = self._resolve_asset_ids(asset_ids, external_ids, project_id)

        properties_to_batch = {"asset_ids": resolved_asset_ids}

        def generate_variables(batch):
            return {"where": {"idIn": batch["asset_ids"]}}

        @retry(
            wait=wait_exponential(multiplier=1, min=1, max=8),
            retry=retry_if_exception_type(MutationError),
            reraise=True,
        )
        def verify_last_batch(last_batch: Dict, results: List) -> None:
            """Check that all assets in the last batch have been sent to review."""
            if project_id is not None:
                project_id_ = project_id
            # in some case the results is [{'data': None}]
            elif isinstance(results[0]["data"], Dict) and results[0]["data"].get("id"):
                project_id_ = results[0]["data"].get("id")
            else:
                return

            asset_ids = last_batch["asset_ids"][-1:]  # check last asset of the batch only
            nb_assets_in_review = self.kili_api_gateway.count_assets(
                AssetFilters(
                    project_id=ProjectId(project_id_),
                    asset_id_in=asset_ids,
                    status_in=["TO_REVIEW"],
                )
            )
            if len(asset_ids) != nb_assets_in_review:
                raise MutationError("Failed to send some assets to review")

        results = mutate_from_paginated_call(
            self,
            properties_to_batch,
            generate_variables,
            GQL_ADD_ALL_LABELED_ASSETS_TO_REVIEW,
            last_batch_callback=verify_last_batch,
        )
        result = self.format_result("data", results[0])
        # unlike send_back_to_queue, the add_to_review mutation doesn't always return the project ID
        # it happens when no assets have been sent to review
        if isinstance(result, dict) and "id" in result:
            assets_in_review = self.kili_api_gateway.list_assets(
                AssetFilters(
                    project_id=result["id"],
                    asset_id_in=resolved_asset_ids,
                    status_in=["TO_REVIEW"],
                ),
                ["id"],
                QueryOptions(disable_tqdm=True),
            )
            result["asset_ids"] = [asset["id"] for asset in assets_in_review]
        return result

    @typechecked
    def send_back_to_queue(
        self,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Send assets back to queue.

        Args:
            asset_ids: List of internal IDs of assets to send back to queue.
            external_ids: List of external IDs of assets to send back to queue.
            project_id: The project ID. Only required if `external_ids` argument is provided.

        Returns:
            A dict object with the project `id` and the `asset_ids` of assets moved to queue.
            An error message if mutation failed.

        Examples:
            >>> kili.send_back_to_queue(
                    asset_ids=[
                        "ckg22d81r0jrg0885unmuswj8",
                        "ckg22d81s0jrh0885pdxfd03n",
                        ],
                )
        """
        if is_empty_list_with_warning(
            "send_back_to_queue", "asset_ids", asset_ids
        ) or is_empty_list_with_warning("send_back_to_queue", "external_ids", external_ids):
            return None

        resolved_asset_ids = self._resolve_asset_ids(asset_ids, external_ids, project_id)

        properties_to_batch = {"asset_ids": resolved_asset_ids}

        def generate_variables(batch):
            return {"where": {"idIn": batch["asset_ids"]}}

        @retry(
            wait=wait_exponential(multiplier=1, min=1, max=8),
            retry=retry_if_exception_type(MutationError),
            reraise=True,
        )
        def verify_last_batch(last_batch: Dict, results: List) -> None:
            """Check that all assets in the last batch have been sent back to queue."""
            if project_id is not None:
                project_id_ = project_id
            # in some case the results is [{'data': None}]
            elif isinstance(results[0]["data"], Dict) and results[0]["data"].get("id"):
                project_id_ = results[0]["data"].get("id")
            else:
                return

            asset_ids = last_batch["asset_ids"][-1:]  # check lastest asset of the batch only
            nb_assets_in_queue = self.kili_api_gateway.count_assets(
                AssetFilters(
                    project_id=ProjectId(project_id_),
                    asset_id_in=asset_ids,
                    status_in=["ONGOING"],
                )
            )
            if len(asset_ids) != nb_assets_in_queue:
                raise MutationError("Failed to send some assets back to queue")

        results = mutate_from_paginated_call(
            self,
            properties_to_batch,
            generate_variables,
            GQL_SEND_BACK_ASSETS_TO_QUEUE,
            last_batch_callback=verify_last_batch,
        )
        result = self.format_result("data", results[0])
        if isinstance(result, dict) and "id" in result:
            assets_in_queue = self.kili_api_gateway.list_assets(
                AssetFilters(
                    project_id=result["id"],
                    asset_id_in=resolved_asset_ids,
                    status_in=["ONGOING"],
                ),
                ["id"],
                QueryOptions(disable_tqdm=True),
            )
            result["asset_ids"] = [asset["id"] for asset in assets_in_queue]
        return result
