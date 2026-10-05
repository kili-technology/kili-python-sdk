import logging
import subprocess
import sys
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kili.client import Kili as KiliLegacy
from kili.client_domain import Kili
from kili.plugins import Plugin, PluginCore
from kili.services.plugins.upload import check_file_contains_handler


def test_plugin_wraps_the_legacy_client_the_runner_gives():
    legacy = MagicMock(spec=KiliLegacy)

    with patch("kili.client_domain.KiliLegacy") as new_legacy_client:
        plugin = Plugin(legacy, project_id="project")  # the SaaS runner passes it positionally

    assert isinstance(plugin.kili, Kili)
    assert plugin.kili.legacy_client is legacy
    new_legacy_client.assert_not_called()  # no second sign-in


def test_plugin_keeps_a_domain_client():
    kili = Kili.from_legacy(MagicMock(spec=KiliLegacy))

    assert Plugin(kili=kili, project_id="project").kili is kili  # plugins-runner passes kili=


def test_plugin_core_keeps_the_legacy_client_and_unwraps_a_domain_one():
    legacy = MagicMock(spec=KiliLegacy)
    with pytest.warns(DeprecationWarning):

        class PluginHandler(PluginCore):
            pass

    assert PluginHandler(legacy, project_id="project").kili is legacy
    assert PluginHandler(Kili.from_legacy(legacy), project_id="project").kili is legacy
    assert not isinstance(PluginHandler(legacy, project_id="project"), Plugin)


def test_subclassing_plugin_core_warns_at_the_plugin_class():
    with pytest.warns(DeprecationWarning, match="Subclass `kili.plugins.Plugin` instead") as record:

        class PluginHandler(PluginCore):
            pass

    assert record[0].filename == __file__  # the plugin author's line, not kili's


def test_a_plugin_core_run_logs_the_deprecation_to_the_plugin_logs():
    logger = MagicMock(spec=logging.Logger)
    with pytest.warns(DeprecationWarning):

        class PluginHandler(PluginCore):
            pass

    PluginHandler(MagicMock(spec=KiliLegacy), project_id="project", logger=logger)

    assert "Subclass `kili.plugins.Plugin` instead" in logger.warning.call_args.args[0]


def test_subclassing_plugin_does_not_warn():
    logger = MagicMock(spec=logging.Logger)
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        class PluginHandler(Plugin):
            pass

        PluginHandler(MagicMock(spec=KiliLegacy), project_id="project", logger=logger)

    logger.warning.assert_not_called()


def test_plugin_core_still_runs_a_mixin_s_class_hooks():
    seen = []

    class Mixin:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            seen.append("__init_subclass__")

        def __new__(cls, *args, **kwargs):
            seen.append("__new__")
            return super().__new__(cls)

    with pytest.warns(DeprecationWarning):

        class PluginHandler(PluginCore, Mixin):
            pass

    PluginHandler(MagicMock(spec=KiliLegacy), project_id="project")

    assert seen == ["__init_subclass__", "__new__"]


@pytest.mark.parametrize("base, warns", [("PluginCore", True), ("Plugin", False)])
def test_upload_warns_about_a_plugin_core_handler(tmp_path: Path, base: str, warns: bool):
    plugin = tmp_path / "main.py"
    plugin.write_text(
        f"from kili.plugins import {base}\n\nclass PluginHandler({base}):\n"
        "    def on_submit(self, label, asset_id):\n        pass\n"
    )

    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        check_file_contains_handler(plugin)

    assert any("Subclass `kili.plugins.Plugin`" in str(w.message) for w in record) is warns


@pytest.mark.parametrize(
    "flags, shown", [([], True), (["-W", "ignore::DeprecationWarning"], False)]
)
def test_the_plugin_core_warning_shows_outside_main_unless_silenced(
    tmp_path: Path, flags: list, shown: bool
):
    (tmp_path / "my_plugin.py").write_text(
        "from kili.plugins import PluginCore\n\nclass PluginHandler(PluginCore):\n    pass\n"
    )

    stderr = subprocess.run(
        [sys.executable, *flags, "-c", "import my_plugin"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    ).stderr

    assert ("my_plugin.py:3: DeprecationWarning" in stderr) is shown
