"""Handle LLM_RLHF project exports."""

import logging
from typing import Union

from kili_formats import convert_from_kili_to_llm_rlhf_format

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.project import ProjectId
from kili.use_cases.asset.media_downloader import MediaDownloader
from kili.utils.tempfile import TemporaryDirectory


class LLMRLHFExporter:
    """Handle exports of LLM_RLHF projects."""

    def __init__(self, kili_api_gateway: KiliAPIGateway):
        self.kili_api_gateway = kili_api_gateway

    def export(
        self, assets: list[dict], project_id: ProjectId, json_interface: dict
    ) -> list[dict[str, Union[list[str], str]]]:
        """Assets are static, with n labels."""
        with TemporaryDirectory() as tmpdirname:
            assets = MediaDownloader(
                tmpdirname,
                project_id,
                False,
                "LLM_RLHF",
                self.kili_api_gateway.http_client,
            ).download_assets(assets)
            return convert_from_kili_to_llm_rlhf_format(assets, json_interface, logging)
