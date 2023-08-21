import os
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
import pytest_mock

from kili.client import Kili
from kili.exceptions import AuthenticationFailed


def test_wrong_api_key_is_obfuscated(mocker: pytest_mock.MockerFixture):
    """Test obfuscation of api key."""
    mocker.patch.object(Kili, "_check_api_key_valid", return_value=False)
    with pytest.raises(
        AuthenticationFailed, match=r"failed with API key: \*{9}_key"  # 9 stars for "wrong_api"
    ):
        _ = Kili(api_key="wrong_api_key")
