import warnings

import pytest
import pytest_mock

from kili.adapters.pypi import (
    get_latest_sdk_version_from_pypi,
    warn_if_sdk_version_is_outdated,
)


def make_http_client(mocker: pytest_mock.MockerFixture, status_code=200, json_payload=None):
    response = mocker.MagicMock()
    response.status_code = status_code
    response.json.return_value = json_payload
    http_client = mocker.MagicMock()
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
    http_client = mocker.MagicMock()
    http_client.get.side_effect = ConnectionError("no network")

    # When
    latest_version = get_latest_sdk_version_from_pypi(http_client)

    # Then
    assert latest_version is None


def test_given_an_outdated_version_when_checking_it_then_it_warns_to_upgrade(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    mocker.patch("kili.adapters.pypi.__version__", "1.0.0")
    mocker.patch("kili.adapters.pypi.get_latest_sdk_version_from_pypi", return_value="2.0.0")

    # Then
    with pytest.warns(UserWarning, match="You are using Kili SDK version 1.0.0"):
        # When
        warn_if_sdk_version_is_outdated(mocker.MagicMock())


@pytest.mark.parametrize(
    ("current_version", "latest_version"),
    [
        ("2.0.0", "2.0.0"),  # up to date
        ("2.0.1", "2.0.0"),  # ahead of PyPI, as on a release branch
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
        warn_if_sdk_version_is_outdated(mocker.MagicMock())


def test_given_pypi_is_unreachable_when_checking_the_version_then_it_does_not_warn(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    mocker.patch("kili.adapters.pypi.get_latest_sdk_version_from_pypi", return_value=None)

    # Then
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # checks that no warning is raised
        # When
        warn_if_sdk_version_is_outdated(mocker.MagicMock())
