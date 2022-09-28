"""
Helpers for the project mutations
"""


from typing import Optional


def verify_argument_ranges(
    consensus_tot_coverage: Optional[int],
    min_consensus_size: Optional[int],
    review_coverage: Optional[int],
):
    """
    Ensure that all arguments are set in a correct range or raise
    a ValueError otherwise
    """
    if consensus_tot_coverage is not None and (
        consensus_tot_coverage < 0 or consensus_tot_coverage > 100
    ):
        raise ValueError('argument "consensus_tot_coverage" must be comprised between 0 and 100')
    if min_consensus_size is not None and (min_consensus_size < 1 or min_consensus_size > 10):
        raise ValueError('argument "min_consensus_size" must be comprised between 1 and 10')
    if review_coverage is not None and (review_coverage < 0 or review_coverage > 100):
        raise ValueError('argument "review_coverage" must be comprised between 0 and 100')
