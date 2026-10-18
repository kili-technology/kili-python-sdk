import warnings

import pytest
import pytest_mock
import requests

from kili.adapters.http_client import HttpClient
from kili.adapters.pypi import (
    get_latest_sdk_version_from_pypi,
    is_saas_production,
    warn_if_sdk_version_is_outdated,
)

SAAS_EU = "https://cloud.kili-technology.com/api/label/v2/graphql"
SAAS_US = "https://cloud.eastus.kili-technology.com/api/label/v2/graphql"


@pytest.fixture(autouse=True)
def _forget_pypi_answers(monkeypatch: pytest.MonkeyPatch):
    """Each test asks PyPI afresh: the module keeps its answer for the whole process."""
    monkeypatch.setattr("kili.adapters.pypi._latest_versions", {})


def make_http_client(mocker: pytest_mock.MockerFixture, status_code=200, json_payload=None):
    response = mocker.MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.json.return_value = json_payload
    http_client = mocker.MagicMock(spec=HttpClient)
    http_client.get.return_value = response
    return http_client


def test_given_pypi_answers_when_getting_latest_version_then_it_returns_it(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    http_client = make_http_client(mocker, json_payload={"info": {"version": "99.0.0"}})

    # When
    latest_version = get_latest_sdk_version_from_pypi(http_client)

    # Then
    assert latest_version == "99.0.0"


@pytest.mark.parametrize(
    ("status_code", "json_payload"),
    [
        (404, None),
        (500, None),
        (200, {}),
        (200, {"info": {}}),
    ],
)
def test_given_an_unusable_pypi_answer_when_getting_latest_version_then_it_returns_none(
    mocker: pytest_mock.MockerFixture, status_code, json_payload
):
    # Given
    http_client = make_http_client(mocker, status_code=status_code, json_payload=json_payload)

    # When
    latest_version = get_latest_sdk_version_from_pypi(http_client)

    # Then
    assert latest_version is None


def test_given_pypi_is_unreachable_when_getting_latest_version_then_it_returns_none(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    http_client = mocker.MagicMock(spec=HttpClient)
    http_client.get.side_effect = requests.ConnectionError("no network")

    # When
    latest_version = get_latest_sdk_version_from_pypi(http_client)

    # Then
    assert latest_version is None


@pytest.mark.parametrize(
    "first_answer",
    [{"info": {"version": "99.0.0"}}, None],
    ids=["a version", "no usable answer"],
)
def test_given_several_clients_when_getting_latest_version_then_pypi_is_asked_once(
    mocker: pytest_mock.MockerFixture, first_answer
):
    # Given
    http_client = make_http_client(mocker, json_payload=first_answer)

    # When
    answers = {get_latest_sdk_version_from_pypi(http_client) for _ in range(3)}

    # Then
    assert len(answers) == 1
    http_client.get.assert_called_once()


@pytest.mark.parametrize("api_endpoint", [SAAS_EU, SAAS_US])
def test_given_an_outdated_version_on_saas_when_checking_it_then_it_warns_to_upgrade(
    mocker: pytest_mock.MockerFixture, api_endpoint
):
    # Given
    mocker.patch("kili.adapters.pypi.__version__", "26.1.15")
    mocker.patch("kili.adapters.pypi.get_latest_sdk_version_from_pypi", return_value="26.2.2")

    # Then
    with pytest.warns(UserWarning) as record:
        # When
        warn_if_sdk_version_is_outdated(mocker.MagicMock(spec=HttpClient), api_endpoint)

    assert str(record[0].message) == (
        "You are using Kili SDK version 26.1.15, while version 26.2.2 is available."
        " Upgrade with: pip install --upgrade kili"
    )
    assert record[0].filename == __file__  # the caller's line, outside kili


@pytest.mark.parametrize(
    "api_endpoint",
    [
        "https://lts.cloud.kili-technology.com/api/label/v2/graphql",
        "https://staging.cloud.kili-technology.com/api/label/v2/graphql",
        "https://preproduction.cloud.kili-technology.com/api/label/v2/graphql",
        "https://cloud.staging.eastus.kili-technology.com/api/label/v2/graphql",
        "https://kili.my-company.com/api/label/v2/graphql",
        "http://localhost:4001/api/label/v2/graphql",
        "https://cloud.kili-technology.com.my-company.com/api/label/v2/graphql",
        "cloud.kili-technology.com/api/label/v2/graphql",
    ],
)
def test_given_a_deployment_other_than_saas_when_checking_the_version_then_pypi_is_not_asked(
    mocker: pytest_mock.MockerFixture, api_endpoint
):
    # Given
    mocker.patch("kili.adapters.pypi.__version__", "1.0.0")
    latest = mocker.patch(
        "kili.adapters.pypi.get_latest_sdk_version_from_pypi", return_value="99.0.0"
    )

    # Then
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # checks that no warning is raised
        # When
        warn_if_sdk_version_is_outdated(mocker.MagicMock(spec=HttpClient), api_endpoint)

    latest.assert_not_called()


@pytest.mark.parametrize(
    ("api_endpoint", "expected"),
    [
        (SAAS_EU, True),
        (SAAS_US, True),
        ("HTTPS://CLOUD.KILI-TECHNOLOGY.COM/api/label/v2/graphql", True),
        ("https://cloud.kili-technology.com:443/api/label/v2/graphql", True),
        ("https://lts.cloud.kili-technology.com/api/label/v2/graphql", False),
        ("https://evilcloud.kili-technology.com/api/label/v2/graphql", False),
    ],
)
def test_is_saas_production(api_endpoint, expected):
    assert is_saas_production(api_endpoint) is expected


@pytest.mark.parametrize(
    ("current_version", "latest_version"),
    [
        ("2.0.0", "2.0.0"),  # up to date
        ("2.0.1", "2.0.0"),  # ahead of PyPI
        ("2.0.0.dev1", "3.0.0"),  # development install, not comparable
        ("2.0.0", "not-a-version"),  # unexpected answer from PyPI
    ],
)
def test_given_a_version_that_is_not_outdated_when_checking_it_then_it_does_not_warn(
    mocker: pytest_mock.MockerFixture, current_version, latest_version
):
    # Given
    mocker.patch("kili.adapters.pypi.__version__", current_version)
    mocker.patch("kili.adapters.pypi.get_latest_sdk_version_from_pypi", return_value=latest_version)

    # Then
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # checks that no warning is raised
        # When
        warn_if_sdk_version_is_outdated(mocker.MagicMock(spec=HttpClient), SAAS_EU)


def test_given_pypi_is_unreachable_when_checking_the_version_then_it_does_not_warn(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    mocker.patch("kili.adapters.pypi.get_latest_sdk_version_from_pypi", return_value=None)

    # Then
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # checks that no warning is raised
        # When
        warn_if_sdk_version_is_outdated(mocker.MagicMock(spec=HttpClient), SAAS_EU)
