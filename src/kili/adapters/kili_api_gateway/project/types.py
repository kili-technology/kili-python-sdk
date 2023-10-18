"""Types for the Project-related Kili API gateway functions."""

from dataclasses import dataclass
from typing import Dict, Optional

from kili.domain.project import ComplianceTag, InputType
from kili.domain.types import ListOrTuple


@dataclass
# pylint: disable=too-many-instance-attributes
class ProjectDataKiliAPIGatewayInput:
    """Project input data for Kili API Gateway."""

    archived: Optional[bool]
    author: Optional[str]
    compliance_tags: Optional[ListOrTuple[ComplianceTag]]
    consensus_mark: Optional[float]
    consensus_tot_coverage: Optional[int]
    description: Optional[str]
    can_navigate_between_assets: Optional[bool]
    can_skip_asset: Optional[bool]
    honeypot_mark: Optional[float]
    input_type: Optional[InputType]
    instructions: Optional[str]
    json_interface: Optional[str]
    metadata_types: Optional[Dict]
    min_consensus_size: Optional[int]
    number_of_assets: Optional[int]
    rules: Optional[str]
    number_of_skipped_assets: Optional[int]
    number_of_remaining_assets: Optional[int]
    number_of_reviewed_assets: Optional[int]
    review_coverage: Optional[int]
    should_relaunch_kpi_computation: Optional[bool]
    title: Optional[str]
    use_honeypot: Optional[bool]
