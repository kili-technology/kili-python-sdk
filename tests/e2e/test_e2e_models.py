import pytest

from kili.client import Kili
from kili.exceptions import GraphQLError


@pytest.mark.e2e()
def test_given_no_resources_when_creating_project_and_model_it_creates_and_manages_resources_correctly(
    kili: Kili,
):
    project_title = "[E2E Test]: Model"
    project_description = "End-to-End Test Model and Project Model workflow"
    interface = {
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

    organization_id = kili.organizations()[0]["id"]

    project = kili.create_project(
        title=project_title,
        description=project_description,
        input_type="LLM_INSTR_FOLLOWING",
        json_interface=interface,
    )
    project_id = project["id"]

    model_data = {
        "credentials": {"api_key": "***", "endpoint": "https://api.openai.com"},
        "name": "E2E Test Model",
        "type": "OPEN_AI_SDK",
    }
    model = kili.llm.create_model(organization_id=organization_id, model=model_data)
    model_id = model["id"]

    created_model = kili.llm.get_model(model_id)
    assert created_model["name"] == model_data["name"]
    assert created_model["type"] == model_data["type"]

    updated_model_name = "E2E Test Model Updated"
    kili.llm.update_model(
        model_id=model_id,
        model={"credentials": model_data["credentials"], "name": updated_model_name},
    )

    updated_model = kili.llm.get_model(model_id)
    assert updated_model["name"] == updated_model_name

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

    project_models = kili.llm.list_project_models(project_id=project_id)

    assert len(project_models) == 2
    first_project_model = project_models[0]
    assert first_project_model["id"] == project_model_id_1
    assert first_project_model["configuration"]["temperature"] == 0.5
    second_project_model = project_models[1]
    assert second_project_model["id"] == project_model_id_2
    assert second_project_model["configuration"]["temperature"]["min"] == 0.2
    assert second_project_model["configuration"]["temperature"]["max"] == 0.8

    updated_project_model_config_1 = {"model": "Test Model (updated)", "temperature": 0.7}
    kili.llm.update_project_model(
        project_model_id=project_model_id_1, configuration=updated_project_model_config_1
    )

    project_models = kili.llm.list_project_models(project_id=project_id)

    assert len(project_models) == 2
    updated_project_model = next(
        project_model
        for project_model in kili.llm.list_project_models(project_id=project_id)
        if project_model["id"] == project_model_id_1
    )
    assert updated_project_model["configuration"] == updated_project_model_config_1

    kili.llm.delete_project_model(project_model_id=project_model_id_1)
    kili.llm.delete_project_model(project_model_id=project_model_id_2)

    project_models = kili.llm.list_project_models(project_id=project_id)
    assert len(project_models) == 0

    kili.llm.delete_model(model_id=model_id)

    with pytest.raises(GraphQLError):
        kili.llm.get_model(model_id)

    kili.delete_project(project_id=project_id)
