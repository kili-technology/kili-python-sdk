"""
Tests for the client to return correct ee
"""
import os
from unittest.mock import patch

import pytest

from kili.client import Kili
from kili.exceptions import AuthenticationFailed


def test_no_api_key():
    with patch.dict(os.environ):
        os.environ.pop("KILI_API_KEY")
        with pytest.raises(AuthenticationFailed):
            _ = Kili()


def test_wrong_api_key():
    with patch.dict(os.environ):
        os.environ.pop("KILI_API_KEY")
        with pytest.raises(AuthenticationFailed) as e_info:
            _ = Kili(api_key="wrong_api_key")

        assert "failed with API key: *********_key" in str(e_info)


def test_wrong_api_key_shot():
    with patch.dict(os.environ):
        os.environ.pop("KILI_API_KEY")
        with pytest.raises(AuthenticationFailed) as e_info:
            _ = Kili(api_key="no")

        assert "failed with API key: no" in str(e_info)
