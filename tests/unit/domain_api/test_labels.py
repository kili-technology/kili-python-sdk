from unittest.mock import MagicMock

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.client import Kili as KiliLegacy
from kili.domain_api import LabelsNamespace


def test_create_default_leaves_the_step_to_the_backend():
    client = MagicMock(spec=KiliLegacy)
    labels = LabelsNamespace(client, MagicMock(spec=KiliAPIGateway))

    labels.create_default(project_id="project", external_id="asset", json_response={"JOB": {}})

    # a project's labeling step is named per project ("Label" on a new one): forcing "Default" fails
    assert client.append_labels.call_args.kwargs["step_name"] is None
    assert client.append_labels.call_args.kwargs["label_type"] == "DEFAULT"
