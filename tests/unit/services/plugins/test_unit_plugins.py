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
    from kili_events import AssetIssueEvent, AssetSkippedEvent, LabelWorkflowEvent

    from kili.plugins import PluginCore, on_kili_event


    def helper():
        pass


    class PluginHandler(PluginCore):
        @on_kili_event
        def on_skip(self, event: AssetSkippedEvent) -> None:
            pass

        @on_kili_event
        def on_issue_or_label(self, event: AssetIssueEvent | LabelWorkflowEvent) -> None:
            pass

        def not_subscribed(self):
            pass
"""


def test_find_event_subscriptions_reads_the_annotations_a_model_as_its_subject_a_family_as_its_pattern(
    tmp_path,
):
    plugin_path = _plugin_file(tmp_path, SUBSCRIBED_PLUGIN)

    assert find_event_subscriptions(plugin_path) == {
        "on_skip": ["asset.skipped"],
        "on_issue_or_label": ["asset.issue.*", "label.workflow.*"],
    }


def test_find_event_subscriptions_follows_import_aliases_and_every_way_to_write_a_union(tmp_path):
    plugin_path = _plugin_file(
        tmp_path,
        """
        from __future__ import annotations

        import typing
        import kili_events as ke
        from typing import Union as U
        from kili_events import AssetSkippedEvent as Skipped, AssetUnskippedEvent
        from kili import plugins
        from kili.plugins import PluginCore, on_kili_event as subscribe

        SkipEvents = U[Skipped, AssetUnskippedEvent]


        class PluginHandler(PluginCore):
            @subscribe
            def on_skip(self, event: Skipped):
                pass

            @plugins.on_kili_event
            def on_unskip(self, event: ke.AssetUnskippedEvent):
                pass

            @subscribe
            def on_either(self, event: typing.Union[Skipped, "ke.LabelWorkflowEvent"]):
                pass

            @subscribe
            def on_alias(self, event: SkipEvents):
                pass
        """,
    )

    assert find_event_subscriptions(plugin_path) == {
        "on_skip": ["asset.skipped"],
        "on_unskip": ["asset.unskipped"],
        "on_either": ["asset.skipped", "label.workflow.*"],
        "on_alias": ["asset.skipped", "asset.unskipped"],
    }


def test_find_event_subscriptions_sends_any_event_as_the_top_level_families(tmp_path):
    plugin_path = _plugin_file(
        tmp_path,
        """
        from kili_events import AnyEvent
        from kili.plugins import PluginCore, on_kili_event


        class PluginHandler(PluginCore):
            @on_kili_event
            def on_anything(self, event: AnyEvent):
                pass
        """,
    )

    patterns = find_event_subscriptions(plugin_path)["on_anything"]

    assert {"asset.*", "label.*", "project.*"} <= set(patterns)
    assert all(pattern.count(".") == 1 and pattern.endswith(".*") for pattern in patterns)


@pytest.mark.parametrize(
    ("decorator", "signature", "message"),
    [
        (
            "@on_kili_event(AssetSkippedEvent)",
            "def on_something(self, event: AssetSkippedEvent):",
            "takes no arguments",
        ),
        (
            '@on_kili_event("asset.*")',
            "def on_something(self, event: AssetSkippedEvent):",
            "takes no arguments",
        ),
        (
            "@on_kili_event()",
            "def on_something(self, event: AssetSkippedEvent):",
            "takes no arguments",
        ),
        ("@on_kili_event", "def on_something(self, event):", "annotate the event parameter"),
        (
            "@on_kili_event",
            "def on_something(self, event: dict):",
            "'dict' is not a kili_events name",
        ),
        (
            "@on_kili_event",
            "def on_something(self, event: MY_EVENTS):",
            "is not a kili_events name",
        ),
        (
            "@on_kili_event",
            "def on_something(self, event: Optional[AssetSkippedEvent]):",
            "is not a kili_events name",
        ),
        (
            "@on_kili_event",
            "def on_something(self, event: KiliEvent):",
            "'KiliEvent' is not a kili_events model",
        ),
        ("@on_kili_event", "def on_something(self):", "takes self and the event"),
        (
            "@on_kili_event",
            "def on_something(self, event: AssetSkippedEvent, other):",
            "takes self and the event",
        ),
        (
            "@on_kili_event",
            "async def on_something(self, event: AssetSkippedEvent):",
            "async",
        ),
    ],
    ids=[
        "a model argument",
        "a pattern argument",
        "parentheses",
        "no annotation",
        "not from kili_events",
        "a module constant",
        "Optional",
        "KiliEvent",
        "no event parameter",
        "two parameters",
        "async",
    ],
)
def test_find_event_subscriptions_refuses_what_cannot_be_read_or_fire(
    tmp_path, decorator, signature, message
):
    plugin_path = _plugin_file(
        tmp_path,
        f"""
        from typing import Optional

        from kili_events import AssetSkippedEvent, KiliEvent
        from kili.plugins import PluginCore, on_kili_event

        MY_EVENTS = ["asset.skipped"]


        class PluginHandler(PluginCore):
            {decorator}
            {signature}
                pass
        """,
    )

    with pytest.raises(ValueError, match=f"PluginHandler.on_something: .*{message}"):
        find_event_subscriptions(plugin_path)


@pytest.mark.parametrize(
    "annotation",
    [
        "AssetAnalyticsLabelMetricEvent",
        "AssetStorageIntegrationEvent",
        "LabelAnalyticsMetricsSaveStartedEvent",
    ],
    ids=["a family of system events", "a family of events of no project", "a system event"],
)
def test_find_event_subscriptions_refuses_events_plugins_never_receive(tmp_path, annotation):
    plugin_path = _plugin_file(
        tmp_path,
        f"""
        from kili_events import *
        from kili.plugins import PluginCore, on_kili_event


        class PluginHandler(PluginCore):
            @on_kili_event
            def on_something(self, event: {annotation}):
                pass
        """,
    )

    with pytest.raises(ValueError, match=f"Kili never sends {annotation} to plugins"):
        find_event_subscriptions(plugin_path)


def test_upload_sends_the_patterns_of_the_annotations_as_event_matcher(kili, tmp_path):
    uploader = _uploader(kili, _plugin_file(tmp_path, SUBSCRIBED_PLUGIN))

    uploader._retrieve_plugin_src()
    uploader._create_plugin_runner()

    kili.graphql_client.execute.assert_called_once()
    assert kili.graphql_client.execute.call_args.args[1] == {
        "pluginName": PLUGIN_NAME,
        "handlerTypes": None,
        "eventMatcher": ["asset.issue.*", "asset.skipped", "label.workflow.*"],
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


def test_find_event_subscriptions_follows_star_imports(tmp_path):
    plugin_path = _plugin_file(
        tmp_path,
        """
        from kili_events import *
        from kili.plugins import *


        class PluginHandler(PluginCore):
            @on_kili_event
            def on_skip(self, event: AssetSkippedEvent):
                pass
        """,
    )

    assert find_event_subscriptions(plugin_path) == {"on_skip": ["asset.skipped"]}


def test_find_event_subscriptions_warns_of_inherited_handlers(tmp_path, caplog):
    plugin_path = _plugin_file(
        tmp_path,
        """
        from kili_events import AssetSkippedEvent

        from kili.plugins import PluginCore, on_kili_event
        from helpers import MyBase


        class PluginHandler(MyBase):
            @on_kili_event
            def on_skip(self, event: AssetSkippedEvent):
                pass
        """,
    )

    with caplog.at_level(logging.WARNING, logger="kili.services.plugins"):
        find_event_subscriptions(plugin_path)

    assert "PluginHandler inherits from MyBase" in caplog.text


@pytest.mark.parametrize("base", ["Plugin", "PluginCore", "plugins.Plugin"])
def test_find_event_subscriptions_does_not_warn_on_the_kili_bases(tmp_path, caplog, base):
    plugin_path = _plugin_file(
        tmp_path,
        f"""
        from kili_events import AssetSkippedEvent

        from kili import plugins
        from kili.plugins import Plugin, PluginCore, on_kili_event


        class PluginHandler({base}):
            @on_kili_event
            def on_skip(self, event: AssetSkippedEvent):
                pass
        """,
    )

    with caplog.at_level(logging.WARNING, logger="kili.services.plugins"):
        subscriptions = find_event_subscriptions(plugin_path)

    assert subscriptions == {"on_skip": ["asset.skipped"]}
    assert "inherits from" not in caplog.text


def test_upload_refuses_a_plugin_without_handler(kili):
    plugin_path = Path(
        os.path.join(
            "tests", "unit", "services", "plugins", "test_plugins", "no_handlers_implemented.py"
        )
    )

    with pytest.raises(ValueError, match="PluginHandler has no handler"):
        _uploader(kili, plugin_path)._retrieve_plugin_src()


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("", "E = AssetSkippedEvent"),
        ("if TYPE_CHECKING:\n            E = AssetSkippedEvent", ""),
        ("def helper():\n            E = AssetSkippedEvent", ""),
    ],
    ids=["an alias bound after the class", "under TYPE_CHECKING", "in a function"],
)
def test_find_event_subscriptions_reads_only_what_is_bound_when_the_class_is_defined(
    tmp_path, before, after
):
    # the methods are decorated when the class is defined: a name bound later, or never at
    # runtime, fails to resolve then
    plugin_path = _plugin_file(
        tmp_path,
        f"""
        from __future__ import annotations

        from typing import TYPE_CHECKING

        from kili_events import AssetSkippedEvent
        from kili.plugins import PluginCore, on_kili_event

        {before}


        class PluginHandler(PluginCore):
            @on_kili_event
            def on_something(self, event: E):
                pass

        {after}
        """,
    )

    with pytest.raises(ValueError, match="'E' is not a kili_events name"):
        find_event_subscriptions(plugin_path)


def test_find_event_subscriptions_reads_imports_in_try_blocks_and_annotated_aliases(tmp_path):
    plugin_path = _plugin_file(
        tmp_path,
        """
        from typing import Union

        from typing_extensions import TypeAlias

        try:
            from kili_events import AssetSkippedEvent, AssetUnskippedEvent
        except ImportError:
            raise

        from kili.plugins import PluginCore, on_kili_event

        SkipEvents: TypeAlias = Union[AssetSkippedEvent, AssetUnskippedEvent]


        class PluginHandler(PluginCore):
            @on_kili_event
            def on_something(self, event: SkipEvents):
                pass
        """,
    )

    assert find_event_subscriptions(plugin_path) == {
        "on_something": ["asset.skipped", "asset.unskipped"]
    }


def test_find_event_subscriptions_follows_an_import_that_rebinds_an_alias(tmp_path):
    plugin_path = _plugin_file(
        tmp_path,
        """
        from kili_events import AssetSkippedEvent

        AssetUnskippedEvent = AssetSkippedEvent

        from kili_events import AssetUnskippedEvent
        from kili.plugins import PluginCore, on_kili_event


        class PluginHandler(PluginCore):
            @on_kili_event
            def on_unskip(self, event: AssetUnskippedEvent):
                pass
        """,
    )

    assert find_event_subscriptions(plugin_path) == {"on_unskip": ["asset.unskipped"]}


def test_find_event_subscriptions_sends_a_one_event_family_as_its_folder_pattern(tmp_path):
    # the family of a folder holding one event is that event's model: the name says which
    plugin_path = _plugin_file(
        tmp_path,
        """
        from kili_events import (
            ProjectWorkflowBulkActionPrioritizeEvent,
            ProjectWorkflowBulkActionPrioritizeStartedEvent,
        )
        from kili.plugins import PluginCore, on_kili_event


        class PluginHandler(PluginCore):
            @on_kili_event
            def on_family(self, event: ProjectWorkflowBulkActionPrioritizeEvent):
                pass

            @on_kili_event
            def on_model(self, event: ProjectWorkflowBulkActionPrioritizeStartedEvent):
                pass
        """,
    )

    assert find_event_subscriptions(plugin_path) == {
        "on_family": ["project.workflow.bulkAction.prioritize.*"],
        "on_model": ["project.workflow.bulkAction.prioritize.started"],
    }


def test_find_event_subscriptions_reads_an_import_from_a_kili_events_module(tmp_path):
    plugin_path = _plugin_file(
        tmp_path,
        """
        from kili_events.AssetSkippedEvent import AssetSkippedEvent
        from kili.plugins import PluginCore, on_kili_event


        class PluginHandler(PluginCore):
            @on_kili_event
            def on_skip(self, event: AssetSkippedEvent):
                pass
        """,
    )

    assert find_event_subscriptions(plugin_path) == {"on_skip": ["asset.skipped"]}


def test_find_event_subscriptions_says_a_type_checking_import_does_not_count(tmp_path):
    plugin_path = _plugin_file(
        tmp_path,
        """
        from __future__ import annotations

        from typing import TYPE_CHECKING

        from kili.plugins import PluginCore, on_kili_event

        if TYPE_CHECKING:
            from kili_events import AssetSkippedEvent


        class PluginHandler(PluginCore):
            @on_kili_event
            def on_skip(self, event: AssetSkippedEvent):
                pass
        """,
    )

    with pytest.raises(ValueError, match="imported under `if TYPE_CHECKING:` only"):
        find_event_subscriptions(plugin_path)


@pytest.mark.parametrize("other", ["@staticmethod", "@functools.lru_cache"])
def test_find_event_subscriptions_refuses_another_decorator(tmp_path, other):
    plugin_path = _plugin_file(
        tmp_path,
        f"""
        import functools

        from kili_events import AssetSkippedEvent
        from kili.plugins import PluginCore, on_kili_event


        class PluginHandler(PluginCore):
            {other}
            @on_kili_event
            def on_skip(self, event: AssetSkippedEvent):
                pass
        """,
    )

    with pytest.raises(ValueError, match="is the only decorator"):
        find_event_subscriptions(plugin_path)


def test_find_event_subscriptions_reads_only_the_event_annotation(tmp_path):
    # the return annotation names what the import never binds: the upload ignores it, like the
    # decorator, which resolves the event's annotation alone
    plugin_path = _plugin_file(
        tmp_path,
        """
        from __future__ import annotations

        from typing import TYPE_CHECKING

        from kili_events import AssetSkippedEvent
        from kili.plugins import PluginCore, on_kili_event

        if TYPE_CHECKING:
            from reports import Report


        class PluginHandler(PluginCore):
            @on_kili_event
            def on_skip(self: PluginHandler, event: AssetSkippedEvent = None) -> Report:
                pass
        """,
    )

    assert find_event_subscriptions(plugin_path) == {"on_skip": ["asset.skipped"]}
