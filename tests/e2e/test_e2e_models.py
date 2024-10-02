import pytest

from kili.client import Kili
from kili.domain.llm import ChatItemRole
from kili.exceptions import GraphQLError

PROJECT_TITLE = "[E2E Test]: Model"
PROJECT_DESCRIPTION = "End-to-End Test Model and Project Model workflow"
MODEL_NAME = "E2E Test Model"
UPDATED_MODEL_NAME = "E2E Test Model Updated"
PROMPT = "Hello, world !"

INTERFACE = {
    "jobs": {
        "COMPARISON_JOB": {
            "content": {
                "options": {
                    "OPTION_A": {"children": [], "name": "Option A", "id": "optionA"},
                    "OPTION_B": {"children": [], "name": "Option B", "id": "optionB"},
                },
                "input": "radio",
            },
            "instruction": "Select the best option",
            "mlTask": "COMPARISON",
            "required": 1,
            "isChild": False,
            "isNew": False,
        }
    }
}


@pytest.mark.e2e()
def test_create_and_manage_project_and_model_resources(kili: Kili):
    """Test the creation and management of project and model resources."""
    organization_id = kili.organizations()[0]["id"]

    project = kili.create_project(
        title=PROJECT_TITLE,
        description=PROJECT_DESCRIPTION,
        input_type="LLM_INSTR_FOLLOWING",
        json_interface=INTERFACE,
    )
    project_id = project["id"]

    model_data = {
        "credentials": {"api_key": "***", "endpoint": "your_open_ai_endpoint"},
        "name": MODEL_NAME,
        "type": "OPEN_AI_SDK",
    }

    model = kili.llm.create_model(organization_id=organization_id, model=model_data)
    model_id = model["id"]

    created_model = kili.llm.model(model_id)
    assert created_model["name"] == MODEL_NAME
    assert created_model["type"] == model_data["type"]

    updated_model = kili.llm.update_properties_in_model(
        model_id=model_id,
        model={"credentials": model_data["credentials"], "name": UPDATED_MODEL_NAME},
    )
    assert updated_model["name"] == UPDATED_MODEL_NAME

    project_model_config_1 = {
        "model": "Test Model",
        "temperature": 0.5,
    }
    project_model_1 = kili.llm.create_project_model(
        project_id=project_id, model_id=model_id, configuration=project_model_config_1
    )
    project_model_id_1 = project_model_1["id"]

    project_model_config_2 = {
        "model": "Test Model",
        "temperature": {"min": 0.2, "max": 0.8},
    }
    project_model_2 = kili.llm.create_project_model(
        project_id=project_id, model_id=model_id, configuration=project_model_config_2
    )
    project_model_id_2 = project_model_2["id"]

    project_models = kili.llm.project_models(project_id=project_id)

    assert len(project_models) == 2

    def get_project_model_by_id(models, model_id):
        return next((pm for pm in models if pm["id"] == model_id), None)

    first_project_model = get_project_model_by_id(project_models, project_model_id_1)
    assert first_project_model is not None
    assert first_project_model["configuration"]["temperature"] == 0.5

    second_project_model = get_project_model_by_id(project_models, project_model_id_2)
    assert second_project_model is not None
    assert second_project_model["configuration"]["temperature"]["min"] == 0.2
    assert second_project_model["configuration"]["temperature"]["max"] == 0.8

    updated_project_model_config_1 = {"model": "Test Model (updated)", "temperature": 0.7}
    kili.llm.update_project_model(
        project_model_id=project_model_id_1, configuration=updated_project_model_config_1
    )

    updated_project_models = kili.llm.project_models(project_id=project_id)
    updated_project_model = get_project_model_by_id(updated_project_models, project_model_id_1)
    assert updated_project_model is not None
    assert updated_project_model["configuration"] == updated_project_model_config_1

    chat_items = kili.llm.create_conversation(project_id=project_id, prompt=PROMPT)

    assert len(chat_items) == 3
    assert chat_items[0]["content"] == PROMPT
    assert chat_items[0]["role"] == ChatItemRole.USER
    assert chat_items[1]["role"] == ChatItemRole.ASSISTANT
    assert chat_items[2]["role"] == ChatItemRole.ASSISTANT

    assets = kili.assets(project_id)
    assert len(assets) == 1
    created_asset = assets[0]
    assert created_asset["status"] == "TODO"

    labels = kili.labels(project_id)
    assert len(labels) == 1
    created_label = labels[0]
    assert created_label["labelType"] == "PREDICTION"

    kili.llm.delete_project_model(project_model_id=project_model_id_1)
    kili.llm.delete_project_model(project_model_id=project_model_id_2)

    project_models = kili.llm.project_models(project_id=project_id)
    assert len(project_models) == 0

    kili.llm.delete_model(model_id=model_id)

    with pytest.raises(GraphQLError):
        kili.llm.model(model_id)

    kili.delete_project(project_id=project_id)
