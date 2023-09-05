# pylint: disable=missing-function-docstring,redefined-outer-name,protected-access
import os
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
)
from kili.utils.tempfile import TemporaryDirectory

PLUGIN_NAME = "test_plugin"


@pytest.fixture
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
        )


def test_no_plugin_handler():
    plugin_path = Path(
        os.path.join("tests", "unit", "services", "plugins", "test_plugins", "no_plugin_handler.py")
    )

    contains_handler, handlers = check_file_contains_handler(plugin_path)
    assert contains_handler is False
    assert handlers is None


def test_no_handlers_implemented():
    plugin_path = Path(
        os.path.join(
            "tests", "unit", "services", "plugins", "test_plugins", "no_handlers_implemented.py"
        )
    )

    contains_handler, handlers = check_file_contains_handler(plugin_path)
    assert contains_handler is True
    assert handlers == []


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

    contains_handler, handlers = check_file_contains_handler(plugin_path)
    assert contains_handler is True
    assert handlers == ["onSubmit", "onReview"]


def test_commented_handler():
    plugin_path = Path(
        os.path.join("tests", "unit", "services", "plugins", "test_plugins", "commented_handler.py")
    )

    contains_handler, handlers = check_file_contains_handler(plugin_path)
    assert contains_handler is True
    assert handlers == ["onSubmit"]


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
        )._create_zip(tmp_dir)

        zip_path = tmp_dir / "archive.zip"
        assert zip_path.is_file()

        with ZipFile(zip_path, "r") as archive:
            file_list = archive.infolist()
            assert len(file_list) == 3
            file_names = [file.filename for file in file_list]
            file_names.sort()
            assert file_names == ["main.py", "requirements.txt", "sub_folder/helpers.py"]
