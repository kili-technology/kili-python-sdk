"""
Tests for the client to return correct ee
"""
import os
from unittest.mock import patch

import pytest

from kili.client import Kili
from kili.exceptions import AuthenticationFailed


@patch("kili.authentication.requests")
def test_no_api_key(mocked_requests):
    """test fail because no api key is found"""
    with patch.dict(os.environ):
        os.environ.pop("KILI_API_KEY", None)
        with pytest.raises(AuthenticationFailed):
            _ = Kili()


@patch("kili.authentication.requests")
def test_wrong_api_key(mocked_requests):
    """test obfuscation of api key"""
    with patch.dict(os.environ):
        os.environ.pop("KILI_API_KEY", None)
        with pytest.raises(AuthenticationFailed, match=r"failed with API key: \*{9}_key"):
            _ = Kili(api_key="wrong_api_key")


@patch("kili.authentication.requests")
def test_wrong_api_key_shot(mocked_requests):
    """test no need to obfuscate api key"""
    with patch.dict(os.environ):
        os.environ.pop("KILI_API_KEY", None)
        with pytest.raises(AuthenticationFailed, match="failed with API key: no"):
            _ = Kili(api_key="no")
