"""Service for exporting kili objects."""

from typing import Dict, List, Optional, Union

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset.asset import AssetFilters
from kili.domain.project import ProjectId

from .dynamic import LLMDynamicExporter
from .static import LLMStaticExporter


def export(  # pylint: disable=too-many-arguments, too-many-locals
    kili_api_gateway: KiliAPIGateway,
    project_id: ProjectId,
    asset_filter: AssetFilters,
    disable_tqdm: Optional[bool],
) -> Optional[List[Dict[str, Union[List[str], str]]]]:
    """Export the selected assets with their labels into the required format, and save it into a file archive."""
    project = kili_api_gateway.get_project(project_id, ["id", "inputType", "jsonInterface"])
    input_type = project["inputType"]

    if input_type == "LLM_RLHF":
        return LLMStaticExporter(kili_api_gateway, disable_tqdm).export(
            project_id, asset_filter, project["jsonInterface"]
        )
    if input_type == "LLM_INSTR_FOLLOWING":
        asset_filter.status_in = ["LABELED", "REVIEWED", "TO_REVIEW"]
        return LLMDynamicExporter(kili_api_gateway, disable_tqdm).export(
            asset_filter, project["jsonInterface"]
        )
    raise ValueError(f'Project Input type "{input_type}" cannot be used for llm exports.')
