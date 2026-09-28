# pylint: disable=missing-function-docstring,redefined-outer-name,protected-access
import logging
import os
import textwrap
from pathlib import Path
from unittest.mock import MagicMock
from zipfile import ZipFile

import pytest

from kili.adapters.http_client import HttpClient
from kili.core.constants import mime_extensions_for_py_scripts
from kili.services.plugins.upload import (
    PluginUploader,
    check_file_contains_handler,
    check_file_mime_type,
    find_event_subscriptions,
)
from kili.utils.tempfile import TemporaryDirectory

PLUGIN_NAME = "test_plugin"


@pytest.fixture()
def kili():
    return MagicMock()


def test_invalid_mime_type():
    plugin_path = Path(
        os.path.join("tests", "unit", "services", "plugins", "plugin_folder", "requirements.txt")
    )

    mime_type = check_file_mime_type(plugin_path, mime_extensions_for_py_scripts)
    assert mime_type is False


def test_wrong_plugin_path(kili):
    """Test exception handling when plugin_path is neither a file nor a directory."""
    plugin_path = "plugin.py"
    with pytest.raises(
        FileNotFoundError, match=r"The provided path .* is neither a directory nor a file"
    ):
        PluginUploader(
            kili,
            plugin_path,
            PLUGIN_NAME,
            False,
            HttpClient(
                kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
            ),
            event_matcher=None,
        )


def test_no_plugin_handler():
    plugin_path = Path(
        os.path.join("tests", "unit", "services", "plugins", "test_plugins", "no_plugin_handler.py")
    )

    contains_handler, handlers, has_on_event = check_file_contains_handler(plugin_path)
    assert contains_handler is False
    assert handlers is None
    assert has_on_event is False


def test_no_handlers_implemented():
    plugin_path = Path(
        os.path.join(
            "tests", "unit", "services", "plugins", "test_plugins", "no_handlers_implemented.py"
        )
    )

    contains_handler, handlers, has_on_event = check_file_contains_handler(plugin_path)
    assert contains_handler is True
    assert handlers is None
    assert has_on_event is False


def test_handlers_correctly_implemented():
    plugin_path = Path(
        os.path.join(
            "tests",
            "unit",
            "services",
            "plugins",
            "test_plugins",
            "handlers_correctly_implemented.py",
        )
    )

    contains_handler, handlers, has_on_event = check_file_contains_handler(plugin_path)
    assert contains_handler is True
    assert handlers == ["onSubmit", "onReview"]
    assert has_on_event is False


def test_handlers_correctly_implemented_with_events():
    plugin_path = Path(
        os.path.join(
            "tests",
            "unit",
            "services",
            "plugins",
            "test_plugins",
            "handlers_correctly_implemented_events.py",
        )
    )

    contains_handler, handlers, has_on_event = check_file_contains_handler(plugin_path)
    assert contains_handler is True
    assert handlers is None
    assert has_on_event is True


def test_handlers_correctly_implemented_with_events_and_handlers():
    plugin_path = Path(
        os.path.join(
            "tests",
            "unit",
            "services",
            "plugins",
            "test_plugins",
            "handlers_correctly_implemented_events_handlers.py",
        )
    )

    contains_handler, handlers, has_on_event = check_file_contains_handler(plugin_path)
    assert contains_handler is True
    assert handlers == ["onSubmit", "onReview"]
    assert has_on_event is True


def test_commented_handler():
    plugin_path = Path(
        os.path.join("tests", "unit", "services", "plugins", "test_plugins", "commented_handler.py")
    )

    contains_handler, handlers, has_on_event = check_file_contains_handler(plugin_path)
    assert contains_handler is True
    assert handlers == ["onSubmit"]
    assert has_on_event is False


def test_no_pluginhandler_when_creating_zip_from_file(kili):
    with TemporaryDirectory() as tmp_dir:
        plugin_path = tmp_dir / "plugin.py"

        with plugin_path.open("w", encoding="utf-8") as file:
            file.write('print("hello world")')

        with pytest.raises(ValueError, match="PluginHandler class is not present"):
            PluginUploader(
                kili,
                str(plugin_path),
                PLUGIN_NAME,
                False,
                HttpClient(
                    kili_endpoint="https://fake_endpoint.kili-technology.com",
                    api_key="",
                    verify=True,
                ),
                event_matcher=None,
            )._create_zip(tmp_dir)


def test_zip_creation_from_file(kili):
    with TemporaryDirectory() as tmp_dir:
        plugin_path = Path(
            os.path.join("tests", "unit", "services", "plugins", "plugin_folder", "main.py")
        )

        PluginUploader(
            kili,
            str(plugin_path),
            PLUGIN_NAME,
            False,
            HttpClient(
                kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
            ),
            event_matcher=None,
        )._create_zip(tmp_dir)

        zip_path = tmp_dir / "archive.zip"
        assert zip_path.is_file()

        with ZipFile(zip_path, "r") as archive:
            file_list = archive.infolist()
            assert len(file_list) == 1
            file = file_list[0]
            assert file.filename == "main.py"


def test_no_main_when_creating_zip_from_folder(kili):
    with TemporaryDirectory() as tmp_dir:
        plugin_path = tmp_dir / "plugin_folder"
        plugin_path.mkdir()

        script_path = plugin_path / "plugin.py"
        with Path(script_path).open("w", encoding="utf-8") as file:
            file.write('print("hello world")')

        with pytest.raises(FileNotFoundError, match="No main.py file"):
            PluginUploader(
                kili,
                str(plugin_path),
                PLUGIN_NAME,
                False,
                HttpClient(
                    kili_endpoint="https://fake_endpoint.kili-technology.com",
                    api_key="",
                    verify=True,
                ),
                event_matcher=None,
            )._create_zip(tmp_dir)


def test_no_pluginhandler_when_creating_zip_from_folder(kili):
    with TemporaryDirectory() as tmp_dir:
        plugin_path = tmp_dir / "plugin_folder"
        plugin_path.mkdir()

        script_path = plugin_path / "main.py"
        with Path(script_path).open("w", encoding="utf-8") as file:
            file.write('print("hello world")')

        with pytest.raises(ValueError, match="PluginHandler class is not present"):
            PluginUploader(
                kili,
                str(plugin_path),
                PLUGIN_NAME,
                False,
                HttpClient(
                    kili_endpoint="https://fake_endpoint.kili-technology.com",
                    api_key="",
                    verify=True,
                ),
                event_matcher=None,
            )._create_zip(tmp_dir)


def test_zip_creation_from_folder(kili):
    with TemporaryDirectory() as tmp_dir:
        plugin_path = Path(os.path.join("tests", "unit", "services", "plugins", "plugin_folder"))

        PluginUploader(
            kili,
            str(plugin_path),
            PLUGIN_NAME,
            False,
            HttpClient(
                kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
            ),
            event_matcher=None,
        )._create_zip(tmp_dir)

        zip_path = tmp_dir / "archive.zip"
        assert zip_path.is_file()

        with ZipFile(zip_path, "r") as archive:
            file_list = archive.infolist()
            assert len(file_list) == 3
            file_names = [file.filename for file in file_list]
            file_names.sort()
            assert file_names == ["main.py", "requirements.txt", "sub_folder/helpers.py"]


def _uploader(kili, plugin_path, event_matcher=None):
    return PluginUploader(
        kili,
        str(plugin_path),
        PLUGIN_NAME,
        False,
        HttpClient(
            kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
        ),
        event_matcher=event_matcher,
    )


def _plugin_file(tmp_path, source):
    plugin_path = tmp_path / "main.py"
    plugin_path.write_text(textwrap.dedent(source), encoding="utf-8")
    return plugin_path


SUBSCRIBED_PLUGIN = """
    from kili_events import AssetSkippedEvent, AssetIssueEvent

    from kili.plugins import PluginCore, on_kili_event


    def helper():
        pass


    class PluginHandler(PluginCore):
        @on_kili_event(AssetSkippedEvent)
        def on_skip(self, event):
            pass

        @on_kili_event(AssetIssueEvent, "label.workflow.*")
        def on_issue_or_label(self, event):
            pass

        def not_subscribed(self):
            pass
"""


def test_find_event_subscriptions_reads_models_families_and_patterns(tmp_path):
    plugin_path = _plugin_file(tmp_path, SUBSCRIBED_PLUGIN)

    assert find_event_subscriptions(plugin_path) == {
        "on_skip": ["asset.skipped"],
        "on_issue_or_label": [
            "asset.issue.cancelled",
            "asset.issue.created",
            "asset.issue.resolved",
            "label.workflow.*",
        ],
    }


def test_find_event_subscriptions_follows_import_aliases(tmp_path):
    plugin_path = _plugin_file(
        tmp_path,
        """
        import kili_events as ke
        from kili_events import AssetSkippedEvent as Skipped
        from kili import plugins
        from kili.plugins import PluginCore, on_kili_event as subscribe


        class PluginHandler(PluginCore):
            @subscribe(Skipped)
            def on_skip(self, event):
                pass

            @plugins.on_kili_event(ke.AssetUnskippedEvent)
            def on_unskip(self, event):
                pass
        """,
    )

    assert find_event_subscriptions(plugin_path) == {
        "on_skip": ["asset.skipped"],
        "on_unskip": ["asset.unskipped"],
    }


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ('"label.wokflow.*"', "'label.wokflow.\\*' matches no Kili event"),
        ('"asset.>"', "Invalid event pattern 'asset.>'"),
        ("MY_EVENTS", "'MY_EVENTS' is not a kili_events name"),
        ("", "needs the events to receive"),
    ],
    ids=["typo", "malformed", "unresolvable", "empty"],
)
def test_find_event_subscriptions_rejects_what_cannot_fire(tmp_path, arguments, message):
    plugin_path = _plugin_file(
        tmp_path,
        f"""
        from kili.plugins import PluginCore, on_kili_event

        MY_EVENTS = ["asset.skipped"]


        class PluginHandler(PluginCore):
            @on_kili_event({arguments})
            def on_something(self, event):
                pass
        """,
    )

    with pytest.raises(ValueError, match=f"PluginHandler.on_something: .*{message}"):
        find_event_subscriptions(plugin_path)


def test_upload_sends_the_patterns_of_the_decorators_as_event_matcher(kili, tmp_path):
    uploader = _uploader(kili, _plugin_file(tmp_path, SUBSCRIBED_PLUGIN))

    uploader._retrieve_plugin_src()
    uploader._create_plugin_runner()

    kili.graphql_client.execute.assert_called_once()
    assert kili.graphql_client.execute.call_args.args[1] == {
        "pluginName": PLUGIN_NAME,
        "handlerTypes": None,
        "eventMatcher": [
            "asset.issue.cancelled",
            "asset.issue.created",
            "asset.issue.resolved",
            "asset.skipped",
            "label.workflow.*",
        ],
    }


@pytest.mark.parametrize(
    ("extra_method", "message"),
    [
        ("def on_submit(self, label, asset_id):", "either implements on_submit"),
        ("def on_event(self, payload):", "remove it from PluginHandler"),
    ],
    ids=["legacy handler", "on_event"],
)
def test_upload_refuses_decorators_beside_another_handler(kili, tmp_path, extra_method, message):
    source = (
        SUBSCRIBED_PLUGIN
        + f"""
        {extra_method}
            pass
"""
    )
    uploader = _uploader(kili, _plugin_file(tmp_path, source))

    with pytest.raises(ValueError, match=message):
        uploader._retrieve_plugin_src()


def test_upload_refuses_decorators_with_an_event_matcher(kili, tmp_path):
    uploader = _uploader(kili, _plugin_file(tmp_path, SUBSCRIBED_PLUGIN), ["asset.*"])

    with pytest.raises(ValueError, match="upload without event_matcher"):
        uploader._retrieve_plugin_src()


def test_upload_of_an_on_event_plugin_warns_it_is_deprecated(kili, caplog):
    plugin_path = Path(
        os.path.join(
            "tests",
            "unit",
            "services",
            "plugins",
            "test_plugins",
            "handlers_correctly_implemented_events.py",
        )
    )
    uploader = _uploader(kili, plugin_path, ["asset.*"])

    with caplog.at_level(logging.WARNING, logger="kili.services.plugins"):
        uploader._retrieve_plugin_src()

    assert uploader.event_matcher == ["asset.*"]
    assert "Overriding on_event is deprecated" in caplog.text
