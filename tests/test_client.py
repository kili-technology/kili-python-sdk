"""
Tests for the client to return correct ee
"""
import os
from unittest import mock

import pytest

from kili.client import Kili
from kili.exceptions import AuthenticationFailed


class TestClient:
    """
    test the get_project function
    """

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_no_api_key(self, monkeypatch):
        with pytest.raises(AuthenticationFailed):
            _ = Kili()

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_wrong_api_key(self, monkeypatch):
        with pytest.raises(AuthenticationFailed) as e_info:
            _ = Kili(api_key="wrong_api_key")

        assert "failed with API key: *********_key" in str(e_info)

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_wrong_api_key_shot(self, monkeypatch):
        with pytest.raises(AuthenticationFailed) as e_info:
            _ = Kili(api_key="no")

        assert "failed with API key: no" in str(e_info)
