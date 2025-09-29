"""Domain-based API module for Kili Python SDK.

This module provides the new domain-based API architecture that organizes
SDK methods into logical namespaces for better developer experience.
"""

from .assets import AssetsNamespace
from .base import DomainNamespace
from .exports import ExportNamespace
from .issues import IssuesNamespace
from .labels import LabelsNamespace
from .organizations import OrganizationsNamespace
from .plugins import PluginsNamespace
from .projects import ProjectsNamespace
from .questions import QuestionsNamespace
from .storages import StoragesNamespace
from .tags import TagsNamespace
from .users import UsersNamespace

__all__ = [
    "DomainNamespace",
    "AssetsNamespace",
    "ExportNamespace",
    "IssuesNamespace",
    "LabelsNamespace",
    "OrganizationsNamespace",
    "PluginsNamespace",
    "ProjectsNamespace",
    "QuestionsNamespace",
    "StoragesNamespace",
    "TagsNamespace",
    "UsersNamespace",
]
