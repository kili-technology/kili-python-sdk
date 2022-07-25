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
