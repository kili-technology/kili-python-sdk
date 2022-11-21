"""
Asset mutations
"""

from typing import Any, Dict, List, Optional, Union

from typeguard import typechecked

from kili.helpers import format_result
from kili.mutations.asset.helpers import process_update_properties_in_assets_parameters
from kili.mutations.asset.queries import (
    GQL_ADD_ALL_LABELED_ASSETS_TO_REVIEW,
    GQL_DELETE_MANY_FROM_DATASET,
    GQL_SEND_BACK_ASSETS_TO_QUEUE,
    GQL_UPDATE_PROPERTIES_IN_ASSETS,
)
from kili.orm import Asset
from kili.services.asset_import import import_assets
from kili.utils.pagination import _mutate_from_paginated_call


class MutationsAsset:
    """
    Set of Asset mutations
    """

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def append_many_to_dataset(
        self,
        project_id: str,
        content_array: Optional[List[str]] = None,
        external_id_array: Optional[List[str]] = None,
        id_array: Optional[List[str]] = None,
        is_honeypot_array: Optional[List[bool]] = None,
        status_array: Optional[List[str]] = None,
        json_content_array: Optional[List[List[Union[dict, str]]]] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: bool = False,
    ):
        # pylint: disable=line-too-long
        """Append assets to a project.

        Args:
            project_id: Identifier of the project
            content_array: List of elements added to the assets of the project
                Must not be None except if you provide json_content_array.

                - For a `TEXT` project, the content can be either raw text, or URLs to TEXT assets.
                - For an `IMAGE` / `PDF` project, the content can be either URLs or paths to existing
                    images/pdf on your computer.
                - For a VIDEO project, the content can be either URLs pointing to videos hosted on a web server or paths to
                existing video files on your computer. If you want to import video from frames, look at the json_content
                section below.
                - For an `VIDEO_LEGACY` project, the content can be only be URLs
            external_id_array: List of external ids given to identify the assets.
                If None, random identifiers are created.
            is_honeypot_array:  Whether to use the asset for honeypot
            status_array: By default, all imported assets are set to `TODO`. Other options:
                `ONGOING`, `LABELED`, `REVIEWED`.
            json_content_array: Useful for `VIDEO` or `TEXT` projects only.

                - For `VIDEO` projects, each element is a sequence of frames, i.e. a
                    list of URLs to images or a list of paths to images.
                - For `TEXT` projects, each element is a json_content dict,
                    formatted according to documentation [on how to import
                rich-text assets](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/import_text_assets.ipynb)
            json_metadata_array: The metadata given to each asset should be stored in a json like dict with keys.

                - Add metadata visible on the asset with the following keys: `imageUrl`, `text`, `url`.
                    Example for one asset: `json_metadata_array = [{'imageUrl': '','text': '','url': ''}]`.
                - For VIDEO projects (and not VIDEO_LEGACY), you can specify a value with key 'processingParameters' to specify the sampling rate (default: 30).
                    Example for one asset: `json_metadata_array = [{'processingParameters': {'framesPlayedPerSecond': 10}}]`.
            disable_tqdm: If `True`, the progress bar will be disabled

        Returns:
            A result object which indicates if the mutation was successful, or an error message.

        Examples:
            >>> kili.append_many_to_dataset(
                    project_id=project_id,
                    content_array=['https://upload.wikimedia.org/wikipedia/en/7/7d/Lenna_%28test_image%29.png'])

        !!! example "Recipe"
            - For more detailed examples on how to import assets,
                see [the recipe](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/import_assets.ipynb)
                or [other examples](https://docs.kili-technology.com/recipes/importing-data) in our documentation.
            - For more detailed examples on how to import text assets,
                see [the recipe](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/import_text_assets.ipynb).
        """

        if content_array is None and json_content_array is None:
            raise ValueError("Variables content_array and json_content_array cannot be both None.")
        nb_data = (
            len(content_array)
            if content_array is not None
            else len(json_content_array)  # type:ignore
        )
        field_mapping = {
            "content": content_array,
            "json_content": json_content_array,
            "external_id": external_id_array,
            "id": id_array,
            "status": status_array,
            "json_metadata": json_metadata_array,
            "is_honeypot": is_honeypot_array,
        }
        assets = [{}] * nb_data
        for key, value in field_mapping.items():
            if value is not None:
                assets = [{**assets[i], key: value[i]} for i in range(nb_data)]
        result = import_assets(
            self.auth, project_id=project_id, assets=assets, disable_tqdm=disable_tqdm
        )
        return result

    @typechecked
    # pylint: disable=unused-argument
    def update_properties_in_assets(
        self,
        asset_ids: List[str],
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
    ) -> List[dict]:
        """Update the properties of one or more assets.

        Args:
            asset_ids : The asset IDs to modify
            external_ids: Change the external id of the assets
            priorities : You can change the priority of the assets
                By default, all assets have a priority of 0.
            json_metadatas: The metadata given to an asset should be stored
                in a json like dict with keys `imageUrl`, `text`, `url`:
                `json_metadata = {'imageUrl': '','text': '','url': ''}`
            consensus_marks: Should be between 0 and 1
            honeypot_marks: Should be between 0 and 1
            to_be_labeled_by_array: If given, each element of the list should contain the emails of
                the labelers authorized to label the asset.
            contents: - For a NLP project, the content can be directly in text format
                - For an Image / Video / Pdf project, the content must be hosted on a web server,
                and you point Kili to your data by giving the URLs
            json_contents: - For a NLP project, the `json_content`
                is a text formatted using RichText
                - For a Video project, the`json_content` is a json containg urls pointing
                    to each frame of the video.
            status_array: Each element should be in `TODO`, `ONGOING`, `LABELED`, `REVIEWED`
            is_used_for_consensus_array: Whether to use the asset to compute consensus kpis or not
            is_honeypot_array: Whether to use the asset for honeypot

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.update_properties_in_assets(
                    asset_ids=["ckg22d81r0jrg0885unmuswj8",
                        "ckg22d81s0jrh0885pdxfd03n"],
                    consensus_marks=[1, 0.7],
                    contents=[None, 'https://to/second/asset.png'],
                    external_ids=['external-id-of-your-choice-1',
                        'external-id-of-your-choice-2'],
                    honeypot_marks=[0.8, 0.5],
                    is_honeypot_array=[True, True],
                    is_used_for_consensus_array=[True, False],
                    priorities=[None, 2],
                    status_array=['LABELED', 'REVIEWED'],
                    to_be_labeled_by_array=[
                        ['test+pierre@kili-technology.com'], None],
            )
        """

        saved_args = locals()
        parameters = {
            k: v
            for (k, v) in saved_args.items()
            if k
            in [
                "asset_ids",
                "external_ids",
                "priorities",
                "json_metadatas",
                "consensus_marks",
                "honeypot_marks",
                "to_be_labeled_by_array",
                "contents",
                "json_contents",
                "status_array",
                "is_used_for_consensus_array",
                "is_honeypot_array",
            ]
        }
        properties_to_batch = process_update_properties_in_assets_parameters(parameters)

        def generate_variables(batch: Dict) -> Dict:
            data = {
                "externalId": batch["external_ids"],
                "priority": batch["priorities"],
                "jsonMetadata": batch["json_metadatas"],
                "consensusMark": batch["consensus_marks"],
                "honeypotMark": batch["honeypot_marks"],
                "toBeLabeledBy": batch["to_be_labeled_by_array"],
                "shouldResetToBeLabeledBy": batch["should_reset_to_be_labeled_by_array"],
                "content": batch["contents"],
                "jsonContent": batch["json_contents"],
                "status": batch["status_array"],
                "isUsedForConsensus": batch["is_used_for_consensus_array"],
                "isHoneypot": batch["is_honeypot_array"],
            }
            data_array = [dict(zip(data, t)) for t in zip(*data.values())]
            return {
                "whereArray": [{"id": asset_id} for asset_id in batch["asset_ids"]],
                "dataArray": data_array,
            }

        results = _mutate_from_paginated_call(
            self,
            properties_to_batch,
            generate_variables,
            GQL_UPDATE_PROPERTIES_IN_ASSETS,
        )
        formated_results = [format_result("data", result, Asset) for result in results]
        return [item for batch_list in formated_results for item in batch_list]

    @typechecked
    def delete_many_from_dataset(self, asset_ids: List[str]):
        """Delete assets from a project.

        Args:
            asset_ids: The list of identifiers of the assets to delete.

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        properties_to_batch: Dict[str, Optional[List[Any]]] = {"asset_ids": asset_ids}

        def generate_variables(batch):
            return {"where": {"idIn": batch["asset_ids"]}}

        results = _mutate_from_paginated_call(
            self, properties_to_batch, generate_variables, GQL_DELETE_MANY_FROM_DATASET
        )
        return format_result("data", results[0], Asset)

    @typechecked
    def add_to_review(self, asset_ids: List[str]) -> dict:
        """Add assets to review.

        !!! warning
            Assets without any label will be ignored.

        Args:
            asset_ids: The asset IDs to add to review

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.add_to_review(
                    asset_ids=[
                        "ckg22d81r0jrg0885unmuswj8",
                        "ckg22d81s0jrh0885pdxfd03n"
                        ],
        """
        properties_to_batch: Dict[str, Optional[List[Any]]] = {"asset_ids": asset_ids}

        def generate_variables(batch):
            return {"where": {"idIn": batch["asset_ids"]}}

        results = _mutate_from_paginated_call(
            self,
            properties_to_batch,
            generate_variables,
            GQL_ADD_ALL_LABELED_ASSETS_TO_REVIEW,
        )
        return format_result("data", results[0])

    @typechecked
    def send_back_to_queue(self, asset_ids: List[str]):
        """Send assets back to queue.

        Args:
            asset_ids: The asset IDs to add to review

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.send_back_to_queue(
                    asset_ids=[
                        "ckg22d81r0jrg0885unmuswj8",
                        "ckg22d81s0jrh0885pdxfd03n"
                        ],
        """
        properties_to_batch: Dict[str, Optional[List[Any]]] = {"asset_ids": asset_ids}

        def generate_variables(batch):
            return {"where": {"idIn": batch["asset_ids"]}}

        results = _mutate_from_paginated_call(
            self, properties_to_batch, generate_variables, GQL_SEND_BACK_ASSETS_TO_QUEUE
        )
        return format_result("data", results[0])
