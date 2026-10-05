import warnings
from unittest.mock import MagicMock

import pytest

from kili.client import Kili as KiliLegacy
from kili.client_domain import Kili
from kili.plugins import Plugin, PluginCore


def test_plugin_wraps_the_legacy_client_the_runner_gives():
    legacy = MagicMock(spec=KiliLegacy)

    plugin = Plugin(legacy, project_id="project")  # the SaaS runner passes it positionally

    assert isinstance(plugin.kili, Kili)
    assert plugin.kili.legacy_client is legacy
    legacy.assert_not_called()  # no second sign-in


def test_plugin_keeps_a_domain_client():
    kili = Kili.from_legacy(MagicMock(spec=KiliLegacy))

    assert Plugin(kili=kili, project_id="project").kili is kili  # plugins-runner passes kili=


def test_plugin_core_keeps_the_legacy_client():
    legacy = MagicMock(spec=KiliLegacy)

    with pytest.warns(DeprecationWarning):

        class PluginHandler(PluginCore):
            pass

    assert PluginHandler(legacy, project_id="project").kili is legacy


def test_subclassing_plugin_core_warns_at_the_plugin_class():
    with pytest.warns(DeprecationWarning, match="Subclass `kili.plugins.Plugin` instead") as record:

        class PluginHandler(PluginCore):
            pass

    assert record[0].filename == __file__  # the plugin author's line, not kili's


def test_subclassing_plugin_does_not_warn():
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        class PluginHandler(Plugin):
            pass

        PluginHandler(MagicMock(spec=KiliLegacy), project_id="project")
