# pylint: disable=missing-function-docstring,redefined-outer-name,protected-access
import os
from pathlib import Path
from unittest.mock import MagicMock
from zipfile import ZipFile

import pytest

from kili.services.plugins.upload import PluginUploader
from kili.utils.tempfile import TemporaryDirectory

PLUGIN_NAME = "test_plugin"


@pytest.fixture
def kili():
    return MagicMock()


def test_wrong_plugin_path(kili):
    """Test exception handling when plugin_path is neither a file nor a directory"""
    plugin_path = "plugin.py"
    with pytest.raises(
        FileNotFoundError, match=r"The provided path .* is neither a directory nor a file"
    ):
        PluginUploader(kili, plugin_path, PLUGIN_NAME, False)


def test_no_pluginhandler_when_creating_zip_from_file(kili):
    with TemporaryDirectory() as tmp_dir:
        plugin_path = tmp_dir / "plugin.py"

        with plugin_path.open("w", encoding="utf-8") as file:
            file.write('print("hello world")')

        with pytest.raises(ValueError, match="PluginHandler class is not present"):
            PluginUploader(kili, str(plugin_path), PLUGIN_NAME, False)._create_zip(tmp_dir)


def test_zip_creation_from_file(kili):
    with TemporaryDirectory() as tmp_dir:
        plugin_path = Path(os.path.join("tests", "services", "plugins", "plugin_folder", "main.py"))

        PluginUploader(kili, str(plugin_path), PLUGIN_NAME, False)._create_zip(tmp_dir)

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
            PluginUploader(kili, str(plugin_path), PLUGIN_NAME, False)._create_zip(tmp_dir)


def test_no_pluginhandler_when_creating_zip_from_folder(kili):
    with TemporaryDirectory() as tmp_dir:
        plugin_path = tmp_dir / "plugin_folder"
        plugin_path.mkdir()

        script_path = plugin_path / "main.py"
        with Path(script_path).open("w", encoding="utf-8") as file:
            file.write('print("hello world")')

        with pytest.raises(ValueError, match="PluginHandler class is not present"):
            PluginUploader(kili, str(plugin_path), PLUGIN_NAME, False)._create_zip(tmp_dir)


def test_zip_creation_from_folder(kili):
    with TemporaryDirectory() as tmp_dir:
        plugin_path = Path(os.path.join("tests", "services", "plugins", "plugin_folder"))

        PluginUploader(kili, str(plugin_path), PLUGIN_NAME, False)._create_zip(tmp_dir)

        zip_path = tmp_dir / "archive.zip"
        assert zip_path.is_file()

        with ZipFile(zip_path, "r") as archive:
            file_list = archive.infolist()
            assert len(file_list) == 3
            file_names = [file.filename for file in file_list]
            file_names.sort()
            assert file_names == ["main.py", "requirements.txt", "sub_folder/helpers.py"]
