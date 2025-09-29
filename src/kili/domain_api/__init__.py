"""Domain-based API module for Kili Python SDK.

This module provides the new domain-based API architecture that organizes
SDK methods into logical namespaces for better developer experience.
"""

from .assets import AssetsNamespace
from .base import DomainNamespace
from .cloud_storage import CloudStorageNamespace
from .connections import ConnectionsNamespace
from .integrations import IntegrationsNamespace
from .issues import IssuesNamespace
from .labels import LabelsNamespace
from .notifications import NotificationsNamespace
from .organizations import OrganizationsNamespace
from .plugins import PluginsNamespace
from .projects import ProjectsNamespace
from .tags import TagsNamespace
from .users import UsersNamespace

__all__ = [
    "DomainNamespace",
    "AssetsNamespace",
    "CloudStorageNamespace",
    "ConnectionsNamespace",
    "IntegrationsNamespace",
    "IssuesNamespace",
    "LabelsNamespace",
    "NotificationsNamespace",
    "OrganizationsNamespace",
    "PluginsNamespace",
    "ProjectsNamespace",
    "TagsNamespace",
    "UsersNamespace",
]
