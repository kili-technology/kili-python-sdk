from datetime import datetime

from kili.client import Kili


class _FakeDatetime:
    @staticmethod
    def now(_):
        """
        Fake utcnow
        """
        return datetime(2000, 1, 1)


class _FakeUUID:
    @staticmethod
    def uuid4():
        """
        Fake uuid4
        """
        return "abcd"


class _FakePlatform:
    @staticmethod
    def python_version():
        """
        Fake python version
        """
        return "4.0.0"

    @staticmethod
    def name():
        """
        Fake name
        """
        return "Dummy platform"

    @staticmethod
    def version():
        """
        Fake name
        """
        return "v0.0.0"

    @staticmethod
    def system():
        """
        Fake name
        """
        return "DummySystem"


def test_log_context(mocker, monkeypatch):
    mocker.patch("kili.client.KiliAuth.check_api_key_valid")
    mocker.patch("kili.client.KiliAuth.check_expiry_of_key_is_close")
    mocker.patch("kili.client.KiliAuth.get_user")
    mocker.patch("kili.core.authentication.GraphQLClient")
    mocker.patch("kili.utils.logcontext.datetime", _FakeDatetime())
    mocker.patch("kili.utils.logcontext.uuid", _FakeUUID())
    mocker.patch("kili.utils.logcontext.__version__", "1.0.0")
    mocker.patch("kili.utils.logcontext.platform", _FakePlatform())

    monkeypatch.setenv("KILI_API_KEY", "a")
    monkeypatch.setenv("KILI_API_ENDPOINT", "http://localhost")

    kili = Kili()
    mocker.patch.object(kili.auth.client, "_cache_graphql_schema")
    mocker.patch.object(kili.auth.client._gql_client, "execute")
    kili.assets(project_id="toto")
    called_args_list = kili.auth.client._gql_client.execute.call_args_list
    for called_args in called_args_list:
        assert {
            key: value
            for key, value in called_args[1]["extra_args"]["headers"].items()
            if key.startswith("kili")
        } == {
            "kili-client-name": "python-sdk",
            "kili-client-version": "1.0.0",
            "kili-client-language-name": "Python",
            "kili-client-language-version": "4.0.0",
            "kili-client-platform-version": "v0.0.0",
            "kili-client-platform-name": "DummySystem",
            "kili-client-method-name": "assets",
            "kili-client-call-time": "2000-01-01T00:00:00Z",
            "kili-client-call-uuid": "abcd",
        }
