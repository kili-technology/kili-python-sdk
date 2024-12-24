"""Types for the ProjectWorkflow-related Kili API gateway functions."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProjectWorkflowDataKiliAPIGatewayInput:
    """ProjectWorkflow input data for Kili API Gateway."""

    enforce_step_separation: Optional[bool]
