import json
import os
import tempfile
from pathlib import Path

from kili.core.config_loader import load_config_from_file


def test_load_config_from_file_in_cwd():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "sdk-config.json"
        config_data = {"api_key": "test_key", "api_endpoint": "https://test.com"}
        config_path.write_text(json.dumps(config_data))

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            config = load_config_from_file()
            assert config == config_data
        finally:
            os.chdir(original_cwd)


def test_load_config_from_file_in_home():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "sdk-config.json"
        config_data = {"api_key": "home_key"}
        config_path.write_text(json.dumps(config_data))

        config = load_config_from_file(search_paths=[Path(tmpdir)])
        assert config == config_data


def test_load_config_from_file_not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = load_config_from_file(search_paths=[Path(tmpdir)])
        assert config == {}


def test_load_config_from_file_invalid_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "sdk-config.json"
        config_path.write_text("invalid json {")

        config = load_config_from_file(search_paths=[Path(tmpdir)])
        assert config == {}


def test_load_config_from_file_priority():
    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            config_path1 = Path(tmpdir1) / "sdk-config.json"
            config_path2 = Path(tmpdir2) / "sdk-config.json"

            config_data1 = {"api_key": "first_key"}
            config_data2 = {"api_key": "second_key"}

            config_path1.write_text(json.dumps(config_data1))
            config_path2.write_text(json.dumps(config_data2))

            config = load_config_from_file(search_paths=[Path(tmpdir1), Path(tmpdir2)])
            assert config == config_data1
