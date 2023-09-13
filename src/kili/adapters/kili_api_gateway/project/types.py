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

    def __post_init__(self) -> None:
        _check_argument_ranges(
            consensus_tot_coverage=self.consensus_tot_coverage,
            min_consensus_size=self.min_consensus_size,
            review_coverage=self.review_coverage,
        )


def _check_argument_ranges(
    consensus_tot_coverage: Optional[int],
    min_consensus_size: Optional[int],
    review_coverage: Optional[int],
) -> None:
    """Ensure that all arguments are set in a correct range.

    Raises:
        ValueError: if one of the arguments is not in the correct range.
    """
    if consensus_tot_coverage is not None and not (0 <= consensus_tot_coverage <= 100):
        raise ValueError('argument "consensus_tot_coverage" must be comprised between 0 and 100')

    if min_consensus_size is not None and not (1 <= min_consensus_size <= 10):
        raise ValueError('argument "min_consensus_size" must be comprised between 1 and 10')

    if review_coverage is not None and not (0 <= review_coverage <= 100):
        raise ValueError('argument "review_coverage" must be comprised between 0 and 100')
