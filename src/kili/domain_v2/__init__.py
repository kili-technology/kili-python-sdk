"""Domain v2: TypedDict-based domain contracts for Kili SDK.

This module provides TypedDict-based domain contracts as a lightweight alternative
to dataclasses. These contracts enable better type safety while maintaining the
flexibility of dictionaries.
"""

from .adapters import ContractValidator, DataFrameAdapter
from .asset import (
    AssetContract,
    AssetCreateResponse,
    AssetCreateResponseContract,
    AssetView,
    WorkflowStepResponse,
    WorkflowStepResponseContract,
    validate_asset,
    validate_asset_create_response,
    validate_workflow_step_response,
)
from .connection import ConnectionContract, ConnectionView, validate_connection
from .integration import IntegrationContract, IntegrationView, validate_integration
from .issue import IssueContract, IssueView, validate_issue
from .label import (
    LabelContract,
    LabelExportResponse,
    LabelView,
    filter_labels_by_type,
    sort_labels_by_created_at,
    validate_label,
)
from .notification import NotificationContract, NotificationView, validate_notification
from .organization import (
    OrganizationContract,
    OrganizationMetricsContract,
    OrganizationMetricsView,
    OrganizationView,
    validate_organization,
    validate_organization_metrics,
)
from .plugin import PluginContract, PluginView, validate_plugin
from .project import (
    IdListResponse,
    IdResponse,
    ProjectContract,
    ProjectRoleView,
    ProjectVersionContract,
    ProjectVersionView,
    ProjectView,
    StatusResponse,
    WorkflowStepView,
    get_ordered_steps,
    get_step_by_name,
    validate_project,
    validate_project_role,
    validate_project_version,
    validate_workflow_step,
)
from .tag import TagContract, TagView, validate_tag
from .user import (
    UserContract,
    UserView,
    filter_users_by_activated,
    sort_users_by_email,
    validate_user,
)

__all__ = [
    # Asset
    "AssetContract",
    "AssetCreateResponse",
    "AssetCreateResponseContract",
    "AssetView",
    "WorkflowStepResponse",
    "WorkflowStepResponseContract",
    "validate_asset",
    "validate_asset_create_response",
    "validate_workflow_step_response",
    # Connection
    "ConnectionContract",
    "ConnectionView",
    "validate_connection",
    # Integration
    "IntegrationContract",
    "IntegrationView",
    "validate_integration",
    # Issue
    "IssueContract",
    "IssueView",
    "validate_issue",
    # Label
    "LabelContract",
    "LabelExportResponse",
    "LabelView",
    "filter_labels_by_type",
    "sort_labels_by_created_at",
    "validate_label",
    # Notification
    "NotificationContract",
    "NotificationView",
    "validate_notification",
    # Organization
    "OrganizationContract",
    "OrganizationMetricsContract",
    "OrganizationMetricsView",
    "OrganizationView",
    "validate_organization",
    "validate_organization_metrics",
    # Plugin
    "PluginContract",
    "PluginView",
    "validate_plugin",
    # Project
    "IdListResponse",
    "IdResponse",
    "ProjectContract",
    "ProjectRoleView",
    "ProjectVersionContract",
    "ProjectVersionView",
    "ProjectView",
    "StatusResponse",
    "WorkflowStepView",
    "get_ordered_steps",
    "get_step_by_name",
    "validate_project",
    "validate_project_role",
    "validate_project_version",
    "validate_workflow_step",
    # Tag
    "TagContract",
    "TagView",
    "validate_tag",
    # User
    "UserContract",
    "UserView",
    "validate_user",
    "filter_users_by_activated",
    "sort_users_by_email",
    # Adapters
    "DataFrameAdapter",
    "ContractValidator",
]
