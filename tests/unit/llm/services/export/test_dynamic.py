import copy

import pytest

from kili.llm.presentation.client.llm import LlmClientMethods

mock_json_interface = {
    "jobs": {
        "COMPARISON_JOB": {
            "content": {
                "options": {
                    "IS_MUCH_BETTER": {"children": [], "name": "Is much better", "id": "choice0"},
                    "IS_BETTER": {"children": [], "name": "Is better", "id": "choice1"},
                    "IS_SLIGHTLY_BETTER": {
                        "children": [],
                        "name": "Is slightly better",
                        "id": "choice2",
                    },
                    "TIE": {"children": [], "name": "Tie", "id": "choice3", "mutual": True},
                },
                "input": "radio",
            },
            "instruction": "Pick the best answer",
            "mlTask": "COMPARISON",
            "required": 1,
            "isChild": False,
            "isNew": True,
        },
        "CLASSIFICATION_JOB": {
            "content": {
                "categories": {
                    "BOTH_ARE_GOOD": {"children": [], "name": "Both are good", "id": "category4"},
                    "BOTH_ARE_BAD": {"children": [], "name": "Both are bad", "id": "category5"},
                },
                "input": "radio",
            },
            "instruction": "Overall quality",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": False,
            "isNew": True,
        },
    }
}

mock_empty_json_interface = {"jobs": {}}

mock_fetch_assets = [
    {
        "labels": [
            {
                "annotations": [
                    {
                        "id": "20240806144059004-5",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "clzief6q2003e7tc91jm46uii",
                        "annotationValue": {
                            "choice": {
                                "code": "Is slightly better",
                                "firstId": "clziefeoe003m7tc976xwbh58",
                                "secondId": "clziefepk003n7tc9fyx49vei",
                            }
                        },
                        "chatItemId": "clziefeh6003k7tc99abderkk",
                    },
                    {
                        "id": "20240806144104123-6",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB",
                        "path": [],
                        "labelId": "clzief6q2003e7tc91jm46uii",
                        "annotationValue": {"categories": ["BOTH_ARE_GOOD"]},
                        "chatItemId": "clziefeh6003k7tc99abderkk",
                    },
                    {
                        "id": "20240806144220463-7",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "clzief6q2003e7tc91jm46uii",
                        "annotationValue": {
                            "choice": {
                                "code": "Is much better",
                                "firstId": "clzietmt2004y7tc95s8mb5mb",
                                "secondId": "clzietmuo004z7tc9h7wn520n",
                            }
                        },
                        "chatItemId": "clzietmlt004w7tc984go58bg",
                    },
                    {
                        "id": "20240806144241914-8",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "clzief6q2003e7tc91jm46uii",
                        "annotationValue": {
                            "choice": {
                                "code": "Is better",
                                "firstId": "clzieuhm1005b7tc9b747clxw",
                                "secondId": "clzieuhlc005a7tc9bx6f0mb5",
                            }
                        },
                        "chatItemId": "clzieuheg00587tc9d2k53ee1",
                    },
                ],
                "author": {
                    "id": "user-1",
                    "email": "test+admin@kili-technology.com",
                    "firstname": "Test",
                    "lastname": "Admin",
                },
                "chatItems": [
                    {
                        "id": "clziefeoe003m7tc976xwbh58",
                        "content": "Turtles are reptiles known for their protective shells, which act as both home and armor. They are slow-moving on land but can be agile in water, with many species being excellent swimmers. Turtles are omnivorous, feeding on plants, insects, and small animals. They are cold-blooded and rely on external heat sources to regulate their body temperature. Turtles are long-lived, with some species living over 100 years. They are found on every continent except Antarctica, inhabiting a variety of environments including oceans, freshwater lakes, and even deserts. Many turtle species are endangered due to habitat loss and other factors.",
                        "createdAt": "2024-08-06T12:30:52.430Z",
                        "modelId": "clzief6pr003c7tc99680e8yj",
                        "parentId": "clziefeh6003k7tc99abderkk",
                        "role": "ASSISTANT",
                    },
                    {
                        "id": "clziefeh6003k7tc99abderkk",
                        "content": "describe turtle in 100 words",
                        "createdAt": "2024-08-06T12:30:52.170Z",
                        "modelId": None,
                        "parentId": "cm2u6kgcc001aj7ja1stsbrvu",
                        "role": "USER",
                    },
                    {
                        "id": "cm2u6kgcc001aj7ja1stsbrvu",
                        "content": "You are a helpful assistant",
                        "createdAt": "2024-08-06T12:28:52.170Z",
                        "modelId": None,
                        "parentId": None,
                        "role": "SYSTEM",
                    },
                    {
                        "id": "clziefepk003n7tc9fyx49vei",
                        "content": "Turtles are slow-moving reptiles known for their protective shells, which act as a shield against predators. They are found in various habitats, including oceans, freshwater, and on land. Turtles are omnivorous, feeding on plants, insects, and small animals. They are cold-blooded, regulating their body temperature through their environment. Turtles are known for their longevity, with some species living over 100 years. They are also recognized for their navigational skills, particularly sea turtles, which migrate long distances. Many turtle species are endangered due to habitat loss and other human activities.",
                        "createdAt": "2024-08-06T12:30:52.472Z",
                        "modelId": "clzief6ps003d7tc9fzgj2xkf",
                        "parentId": "clziefeh6003k7tc99abderkk",
                        "role": "ASSISTANT",
                    },
                    {
                        "id": "clzietmlt004w7tc984go58bg",
                        "content": "Make it shorter, 20 words",
                        "createdAt": "2024-08-06T12:41:55.889Z",
                        "modelId": None,
                        "parentId": "clziefeoe003m7tc976xwbh58",
                        "role": "USER",
                    },
                    {
                        "id": "clzietmt2004y7tc95s8mb5mb",
                        "content": "Turtles are shelled reptiles, slow on land, agile in water. They're omnivorous, cold-blooded, and long-lived. Many are endangered.",
                        "createdAt": "2024-08-06T12:41:56.150Z",
                        "modelId": "clzief6ps003d7tc9fzgj2xkf",
                        "parentId": "clzietmlt004w7tc984go58bg",
                        "role": "ASSISTANT",
                    },
                    {
                        "id": "clzietmuo004z7tc9h7wn520n",
                        "content": "Turtles are shelled reptiles, slow on land, agile in water, long-lived, and found worldwide.",
                        "createdAt": "2024-08-06T12:41:56.208Z",
                        "modelId": "clzief6pr003c7tc99680e8yj",
                        "parentId": "clzietmlt004w7tc984go58bg",
                        "role": "ASSISTANT",
                    },
                    {
                        "id": "clzieuheg00587tc9d2k53ee1",
                        "content": "Keep only the most important word that describe a turtle",
                        "createdAt": "2024-08-06T12:42:35.800Z",
                        "modelId": None,
                        "parentId": "clzietmt2004y7tc95s8mb5mb",
                        "role": "USER",
                    },
                    {
                        "id": "clzieuhlc005a7tc9bx6f0mb5",
                        "content": "Shelled",
                        "createdAt": "2024-08-06T12:42:36.048Z",
                        "modelId": "clzief6ps003d7tc9fzgj2xkf",
                        "parentId": "clzieuheg00587tc9d2k53ee1",
                        "role": "ASSISTANT",
                    },
                    {
                        "id": "clzieuhm1005b7tc9b747clxw",
                        "content": "Shell",
                        "createdAt": "2024-08-06T12:42:36.073Z",
                        "modelId": "clzief6pr003c7tc99680e8yj",
                        "parentId": "clzieuheg00587tc9d2k53ee1",
                        "role": "ASSISTANT",
                    },
                ],
                "createdAt": "2024-08-06T12:30:42.122Z",
                "isLatestLabelForUser": True,
                "isSentBackToQueue": False,
                "id": "clzief6q2003e7tc91jm46uii",
                "jsonResponse": {},
                "labelType": "DEFAULT",
                "modelName": None,
            }
        ],
        "content": "",
        "assetProjectModels": [
            {
                "id": "clzief6pr003c7tc99680e8yj",
                "projectModelId": "ProjectModelA",
                "configuration": {"temperature": 1, "model": "my-model-1"},
            },
            {
                "id": "clzief6ps003d7tc9fzgj2xkf",
                "projectModelId": "ProjectModelB",
                "configuration": {"temperature": 0.5, "model": "my-model-2"},
            },
        ],
        "externalId": "clzief6pg003a7tc9cn0p1obf",
        "jsonMetadata": {},
        "status": "LABELED",
    }
]

expected_export = [
    {
        "0": {
            "raw_data": [
                {
                    "id": "cm2u6kgcc001aj7ja1stsbrvu",
                    "role": "system",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "content": "You are a helpful assistant",
                    "model": None,
                },
                {
                    "content": "describe turtle in 100 words",
                    "role": "user",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clziefeh6003k7tc99abderkk",
                    "model": None,
                },
                {
                    "content": "Turtles are reptiles known for their protective shells, which act as both home and armor. They are slow-moving on land but can be agile in water, with many species being excellent swimmers. Turtles are omnivorous, feeding on plants, insects, and small animals. They are cold-blooded and rely on external heat sources to regulate their body temperature. Turtles are long-lived, with some species living over 100 years. They are found on every continent except Antarctica, inhabiting a variety of environments including oceans, freshwater lakes, and even deserts. Many turtle species are endangered due to habitat loss and other factors.",
                    "role": "assistant",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clziefeoe003m7tc976xwbh58",
                    "model": "A",
                },
                {
                    "content": "Turtles are slow-moving reptiles known for their protective shells, which act as a shield against predators. They are found in various habitats, including oceans, freshwater, and on land. Turtles are omnivorous, feeding on plants, insects, and small animals. They are cold-blooded, regulating their body temperature through their environment. Turtles are known for their longevity, with some species living over 100 years. They are also recognized for their navigational skills, particularly sea turtles, which migrate long distances. Many turtle species are endangered due to habitat loss and other human activities.",
                    "role": "assistant",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clziefepk003n7tc9fyx49vei",
                    "model": "B",
                },
            ],
            "status": "LABELED",
            "external_id": "clzief6pg003a7tc9cn0p1obf",
            "metadata": {},
            "models": {
                "A": {
                    "configuration": {
                        "model": "my-model-1",
                        "temperature": 1,
                    },
                    "id": "clzief6pr003c7tc99680e8yj",
                    "projectModelId": "ProjectModelA",
                },
                "B": {
                    "configuration": {
                        "model": "my-model-2",
                        "temperature": 0.5,
                    },
                    "id": "clzief6ps003d7tc9fzgj2xkf",
                    "projectModelId": "ProjectModelB",
                },
            },
            "labels": [
                {
                    "author": "test+admin@kili-technology.com",
                    "created_at": "2024-08-06T12:30:42.122Z",
                    "label_type": "DEFAULT",
                    "label": {
                        "round": {
                            "COMPARISON_JOB": "A_3",
                            "CLASSIFICATION_JOB": ["BOTH_ARE_GOOD"],
                        },
                    },
                }
            ],
        },
        "1": {
            "raw_data": [
                {
                    "id": "cm2u6kgcc001aj7ja1stsbrvu",
                    "role": "system",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "content": "You are a helpful assistant",
                    "model": None,
                },
                {
                    "content": "describe turtle in 100 words",
                    "role": "user",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clziefeh6003k7tc99abderkk",
                    "model": None,
                },
                {
                    "content": "Turtles are reptiles known for their protective shells, which act as both home and armor. They are slow-moving on land but can be agile in water, with many species being excellent swimmers. Turtles are omnivorous, feeding on plants, insects, and small animals. They are cold-blooded and rely on external heat sources to regulate their body temperature. Turtles are long-lived, with some species living over 100 years. They are found on every continent except Antarctica, inhabiting a variety of environments including oceans, freshwater lakes, and even deserts. Many turtle species are endangered due to habitat loss and other factors.",
                    "role": "assistant",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clziefeoe003m7tc976xwbh58",
                    "model": "A",
                },
                {
                    "content": "Make it shorter, 20 words",
                    "role": "user",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clzietmlt004w7tc984go58bg",
                    "model": None,
                },
                {
                    "content": "Turtles are shelled reptiles, slow on land, agile in water. They're omnivorous, cold-blooded, and long-lived. Many are endangered.",
                    "role": "assistant",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clzietmt2004y7tc95s8mb5mb",
                    "model": "B",
                },
                {
                    "content": "Turtles are shelled reptiles, slow on land, agile in water, long-lived, and found worldwide.",
                    "role": "assistant",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clzietmuo004z7tc9h7wn520n",
                    "model": "A",
                },
            ],
            "status": "LABELED",
            "external_id": "clzief6pg003a7tc9cn0p1obf",
            "metadata": {},
            "models": {
                "A": {
                    "configuration": {
                        "model": "my-model-1",
                        "temperature": 1,
                    },
                    "id": "clzief6pr003c7tc99680e8yj",
                    "projectModelId": "ProjectModelA",
                },
                "B": {
                    "configuration": {
                        "model": "my-model-2",
                        "temperature": 0.5,
                    },
                    "id": "clzief6ps003d7tc9fzgj2xkf",
                    "projectModelId": "ProjectModelB",
                },
            },
            "labels": [
                {
                    "author": "test+admin@kili-technology.com",
                    "created_at": "2024-08-06T12:30:42.122Z",
                    "label_type": "DEFAULT",
                    "label": {
                        "round": {"COMPARISON_JOB": "B_1"},
                    },
                }
            ],
        },
        "2": {
            "raw_data": [
                {
                    "id": "cm2u6kgcc001aj7ja1stsbrvu",
                    "role": "system",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "content": "You are a helpful assistant",
                    "model": None,
                },
                {
                    "content": "describe turtle in 100 words",
                    "role": "user",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clziefeh6003k7tc99abderkk",
                    "model": None,
                },
                {
                    "content": "Turtles are reptiles known for their protective shells, which act as both home and armor. They are slow-moving on land but can be agile in water, with many species being excellent swimmers. Turtles are omnivorous, feeding on plants, insects, and small animals. They are cold-blooded and rely on external heat sources to regulate their body temperature. Turtles are long-lived, with some species living over 100 years. They are found on every continent except Antarctica, inhabiting a variety of environments including oceans, freshwater lakes, and even deserts. Many turtle species are endangered due to habitat loss and other factors.",
                    "role": "assistant",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clziefeoe003m7tc976xwbh58",
                    "model": "A",
                },
                {
                    "content": "Make it shorter, 20 words",
                    "role": "user",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clzietmlt004w7tc984go58bg",
                    "model": None,
                },
                {
                    "content": "Turtles are shelled reptiles, slow on land, agile in water. They're omnivorous, cold-blooded, and long-lived. Many are endangered.",
                    "role": "assistant",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clzietmt2004y7tc95s8mb5mb",
                    "model": "B",
                },
                {
                    "content": "Keep only the most important word that describe a turtle",
                    "role": "user",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clzieuheg00587tc9d2k53ee1",
                    "model": None,
                },
                {
                    "content": "Shelled",
                    "role": "assistant",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clzieuhlc005a7tc9bx6f0mb5",
                    "model": "B",
                },
                {
                    "content": "Shell",
                    "role": "assistant",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clzieuhm1005b7tc9b747clxw",
                    "model": "A",
                },
            ],
            "status": "LABELED",
            "external_id": "clzief6pg003a7tc9cn0p1obf",
            "metadata": {},
            "models": {
                "A": {
                    "configuration": {
                        "model": "my-model-1",
                        "temperature": 1,
                    },
                    "id": "clzief6pr003c7tc99680e8yj",
                    "projectModelId": "ProjectModelA",
                },
                "B": {
                    "configuration": {
                        "model": "my-model-2",
                        "temperature": 0.5,
                    },
                    "id": "clzief6ps003d7tc9fzgj2xkf",
                    "projectModelId": "ProjectModelB",
                },
            },
            "labels": [
                {
                    "author": "test+admin@kili-technology.com",
                    "created_at": "2024-08-06T12:30:42.122Z",
                    "label_type": "DEFAULT",
                    "label": {
                        "round": {"COMPARISON_JOB": "A_2"},
                    },
                }
            ],
        },
    }
]

mock_fetch_assets_no_completions = [
    {
        "labels": [
            {
                "annotations": [],
                "author": {
                    "id": "user-1",
                    "email": "test+admin@kili-technology.com",
                    "firstname": "Test",
                    "lastname": "Admin",
                },
                "chatItems": [
                    {
                        "id": "clziefeh6003k7tc99abderkk",
                        "content": "describe turtle in 100 words",
                        "createdAt": "2024-08-06T12:30:52.170Z",
                        "modelId": None,
                        "parentId": "cm2u6kgcc001aj7ja1stsbrvu",
                        "role": "USER",
                    },
                    {
                        "id": "cm2u6kgcc001aj7ja1stsbrvu",
                        "content": "You are a helpful assistant",
                        "createdAt": "2024-08-06T12:28:52.170Z",
                        "modelId": None,
                        "parentId": None,
                        "role": "SYSTEM",
                    },
                ],
                "createdAt": "2024-08-06T12:30:42.122Z",
                "isLatestLabelForUser": True,
                "isSentBackToQueue": False,
                "id": "clzief6q2003e7tc91jm46uii",
                "jsonResponse": {},
                "labelType": "AUTOSAVE",
                "modelName": None,
            }
        ],
        "content": "",
        "assetProjectModels": [
            {
                "id": "clzief6pr003c7tc99680e8yj",
                "projectModelId": "ProjectModelA",
                "configuration": {"temperature": 1, "model": "my-model-1"},
            },
            {
                "id": "clzief6ps003d7tc9fzgj2xkf",
                "projectModelId": "ProjectModelB",
                "configuration": {"temperature": 0.5, "model": "my-model-2"},
            },
        ],
        "externalId": "clzief6pg003a7tc9cn0p1obf",
        "jsonMetadata": {},
        "status": "ONGOING",
    }
]

expected_export_ongoing = [
    {
        "0": {
            "raw_data": [
                {
                    "id": "cm2u6kgcc001aj7ja1stsbrvu",
                    "role": "system",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "content": "You are a helpful assistant",
                    "model": None,
                },
                {
                    "content": "describe turtle in 100 words",
                    "role": "user",
                    "chat_id": "clzief6q2003e7tc91jm46uii",
                    "id": "clziefeh6003k7tc99abderkk",
                    "model": None,
                },
            ],
            "status": "ONGOING",
            "external_id": "clzief6pg003a7tc9cn0p1obf",
            "metadata": {},
            "models": {
                "A": {
                    "configuration": {
                        "model": "my-model-1",
                        "temperature": 1,
                    },
                    "id": "clzief6pr003c7tc99680e8yj",
                    "projectModelId": "ProjectModelA",
                },
                "B": {
                    "configuration": {
                        "model": "my-model-2",
                        "temperature": 0.5,
                    },
                    "id": "clzief6ps003d7tc9fzgj2xkf",
                    "projectModelId": "ProjectModelB",
                },
            },
            "labels": [
                {
                    "author": "test+admin@kili-technology.com",
                    "created_at": "2024-08-06T12:30:42.122Z",
                    "label_type": "AUTOSAVE",
                    "label": {},
                }
            ],
        },
    }
]


def test_export_dynamic(mocker):
    get_project_return_val = {
        "jsonInterface": mock_json_interface,
        "inputType": "LLM_INSTR_FOLLOWING",
        "title": "Test project",
        "id": "project_id",
        "dataConnections": None,
    }
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.count_assets.return_value = 3
    kili_api_gateway.get_project.return_value = get_project_return_val
    kili_api_gateway.list_assets.return_value = mock_fetch_assets

    kili_llm = LlmClientMethods(kili_api_gateway)

    result = kili_llm.export(
        project_id="project_id",
    )
    assert result == expected_export


def test_export_dynamic_ongoing(mocker):
    get_project_return_val = {
        "jsonInterface": mock_json_interface,
        "inputType": "LLM_INSTR_FOLLOWING",
        "title": "Test project",
        "id": "project_id",
        "dataConnections": None,
    }
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.count_assets.return_value = 3
    kili_api_gateway.get_project.return_value = get_project_return_val
    kili_api_gateway.list_assets.return_value = mock_fetch_assets_no_completions

    kili_llm = LlmClientMethods(kili_api_gateway)

    result = kili_llm.export(
        project_id="project_id",
        label_type_in=["DEFAULT", "REVIEW", "AUTOSAVE"],
    )
    assert result == expected_export_ongoing


def test_export_dynamic_empty_json_interface(mocker):
    get_project_return_val = {
        "jsonInterface": mock_empty_json_interface,
        "inputType": "LLM_INSTR_FOLLOWING",
        "title": "Test project",
        "id": "project_id",
        "dataConnections": None,
    }
    kili_api_gateway = mocker.MagicMock()
    kili_llm = LlmClientMethods(kili_api_gateway)
    with pytest.raises(ValueError):
        kili_llm.export(
            project_id="project_id",
        )


def test_export_dynamic_with_conversation_level(mocker):
    updated_mock_json_interface = copy.deepcopy(mock_json_interface)

    updated_mock_json_interface["jobs"].update(
        {
            "CLASSIFICATION_JOB_0": {
                "content": {
                    "categories": {
                        "GOOD": {"children": [], "name": "Good", "id": "category7"},
                        "BAD": {"children": [], "name": "Bad", "id": "category8"},
                    },
                    "input": "radio",
                },
                "level": "conversation",
                "instruction": "Overall quality",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
                "isNew": False,
            },
            "TRANSCRIPTION_JOB": {
                "content": {"input": "textField"},
                "level": "conversation",
                "instruction": "Write something about the overall quality",
                "mlTask": "TRANSCRIPTION",
                "required": 1,
                "isChild": False,
                "isNew": False,
            },
        }
    )

    updated_mock_fetch_assets = copy.deepcopy(mock_fetch_assets)
    updated_mock_fetch_assets[0]["labels"][0]["annotations"].extend(
        [
            {
                "id": "20241025134207822-9",
                "job": "CLASSIFICATION_JOB_0",
                "path": [],
                "labelId": "clzief6q2003e7tc91jm46uii",
                "chatItemId": None,
                "annotationValue": {
                    "categories": ["GOOD"],
                },
                "__typename": "ClassificationAnnotation",
            },
            {
                "id": "20241025134209366-10",
                "job": "TRANSCRIPTION_JOB",
                "path": [],
                "labelId": "clzief6q2003e7tc91jm46uii",
                "chatItemId": None,
                "annotationValue": {
                    "text": "something",
                },
                "__typename": "TranscriptionAnnotation",
            },
        ]
    )

    updated_expected_export = copy.deepcopy(expected_export)
    updated_expected_export[0]["2"]["labels"][0]["label"]["conversation"] = {
        "CLASSIFICATION_JOB_0": ["GOOD"],
        "TRANSCRIPTION_JOB": "something",
    }
    get_project_return_val = {
        "jsonInterface": updated_mock_json_interface,
        "inputType": "LLM_INSTR_FOLLOWING",
        "title": "Test project",
        "id": "project_id",
        "dataConnections": None,
    }
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.count_assets.return_value = 3
    kili_api_gateway.get_project.return_value = get_project_return_val
    kili_api_gateway.list_assets.return_value = updated_mock_fetch_assets

    kili_llm = LlmClientMethods(kili_api_gateway)

    result = kili_llm.export(
        project_id="project_id",
    )
    assert result == updated_expected_export


def test_export_dynamic_with_completion_level(mocker):
    updated_mock_json_interface = copy.deepcopy(mock_json_interface)

    updated_mock_json_interface["jobs"].update(
        {
            "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL": {
                "content": {
                    "categories": {
                        "TOO_SHORT": {"children": [], "name": "Too short", "id": "category1"},
                        "JUST_RIGHT": {"children": [], "name": "Just right", "id": "category2"},
                        "TOO_VERBOSE": {"children": [], "name": "Too verbose", "id": "category3"},
                    },
                    "input": "radio",
                },
                "instruction": "Verbosity",
                "level": "completion",
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
                "isNew": False,
            },
            "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_1": {
                "content": {
                    "categories": {
                        "NO_ISSUES": {"children": [], "name": "No issues", "id": "category4"},
                        "MINOR_ISSUES": {
                            "children": [],
                            "name": "Minor issue(s)",
                            "id": "category5",
                        },
                        "MAJOR_ISSUES": {
                            "children": [],
                            "name": "Major issue(s)",
                            "id": "category6",
                        },
                    },
                    "input": "radio",
                },
                "instruction": "Instructions Following",
                "level": "completion",
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
                "isNew": False,
            },
            "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2": {
                "content": {
                    "categories": {
                        "NO_ISSUES": {"children": [], "name": "No issues", "id": "category7"},
                        "MINOR_INACCURACY": {
                            "children": [],
                            "name": "Minor inaccuracy",
                            "id": "category8",
                        },
                        "MAJOR_INACCURACY": {
                            "children": [],
                            "name": "Major inaccuracy",
                            "id": "category9",
                        },
                    },
                    "input": "radio",
                },
                "instruction": "Truthfulness",
                "level": "completion",
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
                "isNew": False,
            },
            "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_3": {
                "content": {
                    "categories": {
                        "NO_ISSUES": {"children": [], "name": "No issues", "id": "category10"},
                        "MINOR_SAFETY_CONCERN": {
                            "children": [],
                            "name": "Minor safety concern",
                            "id": "category11",
                        },
                        "MAJOR_SAFETY_CONCERN": {
                            "children": [],
                            "name": "Major safety concern",
                            "id": "category12",
                        },
                    },
                    "input": "radio",
                },
                "instruction": "Harmlessness/Safety",
                "level": "completion",
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
                "isNew": False,
            },
        }
    )

    updated_mock_fetch_assets = copy.deepcopy(mock_fetch_assets)
    updated_mock_fetch_assets[0]["labels"][0]["annotations"].extend(
        [
            {
                "id": "20241209092703759-1",
                "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL",
                "path": [],
                "labelId": "clzief6q2003e7tc91jm46uii",
                "chatItemId": "clzieuhlc005a7tc9bx6f0mb5",
                "annotationValue": {
                    "categories": ["TOO_SHORT"],
                    "id": "20241209092703759-1",
                    "isPrediction": False,
                    "__typename": "ClassificationAnnotationValue",
                },
                "__typename": "ClassificationAnnotation",
            },
            {
                "id": "20241209092704576-2",
                "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_1",
                "path": [],
                "labelId": "clzief6q2003e7tc91jm46uii",
                "chatItemId": "clzieuhlc005a7tc9bx6f0mb5",
                "annotationValue": {
                    "categories": ["MINOR_ISSUES"],
                    "id": "20241209092704576-2",
                    "isPrediction": False,
                    "__typename": "ClassificationAnnotationValue",
                },
                "__typename": "ClassificationAnnotation",
            },
            {
                "id": "20241209092705314-3",
                "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2",
                "path": [],
                "labelId": "clzief6q2003e7tc91jm46uii",
                "chatItemId": "clzieuhlc005a7tc9bx6f0mb5",
                "annotationValue": {
                    "categories": ["MAJOR_INACCURACY"],
                    "id": "20241209092705314-3",
                    "isPrediction": False,
                    "__typename": "ClassificationAnnotationValue",
                },
                "__typename": "ClassificationAnnotation",
            },
            {
                "id": "20241209092706381-4",
                "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_3",
                "path": [],
                "labelId": "clzief6q2003e7tc91jm46uii",
                "chatItemId": "clzieuhlc005a7tc9bx6f0mb5",
                "annotationValue": {
                    "categories": ["MAJOR_SAFETY_CONCERN"],
                    "id": "20241209092706381-4",
                    "isPrediction": False,
                    "__typename": "ClassificationAnnotationValue",
                },
                "__typename": "ClassificationAnnotation",
            },
            {
                "id": "20241209092707543-5",
                "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL",
                "path": [],
                "labelId": "clzief6q2003e7tc91jm46uii",
                "chatItemId": "clzieuhm1005b7tc9b747clxw",
                "annotationValue": {
                    "categories": ["JUST_RIGHT"],
                    "id": "20241209092707543-5",
                    "isPrediction": False,
                    "__typename": "ClassificationAnnotationValue",
                },
                "__typename": "ClassificationAnnotation",
            },
            {
                "id": "20241209092710361-6",
                "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_1",
                "path": [],
                "labelId": "clzief6q2003e7tc91jm46uii",
                "chatItemId": "clzieuhm1005b7tc9b747clxw",
                "annotationValue": {
                    "categories": ["NO_ISSUES"],
                    "id": "20241209092710361-6",
                    "isPrediction": False,
                    "__typename": "ClassificationAnnotationValue",
                },
                "__typename": "ClassificationAnnotation",
            },
            {
                "id": "20241209092711511-7",
                "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2",
                "path": [],
                "labelId": "clzief6q2003e7tc91jm46uii",
                "chatItemId": "clzieuhm1005b7tc9b747clxw",
                "annotationValue": {
                    "categories": ["NO_ISSUES"],
                    "id": "20241209092711511-7",
                    "isPrediction": False,
                    "__typename": "ClassificationAnnotationValue",
                },
                "__typename": "ClassificationAnnotation",
            },
            {
                "id": "20241209092713123-8",
                "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_3",
                "path": [],
                "labelId": "clzief6q2003e7tc91jm46uii",
                "chatItemId": "clzieuhm1005b7tc9b747clxw",
                "annotationValue": {
                    "categories": ["NO_ISSUES"],
                    "id": "20241209092713123-8",
                    "isPrediction": False,
                    "__typename": "ClassificationAnnotationValue",
                },
                "__typename": "ClassificationAnnotation",
            },
        ]
    )

    updated_expected_export = copy.deepcopy(expected_export)
    updated_expected_export[0]["2"]["labels"][0]["label"]["completion"] = {
        "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL": {
            "clzieuhlc005a7tc9bx6f0mb5": ["TOO_SHORT"],
            "clzieuhm1005b7tc9b747clxw": ["JUST_RIGHT"],
        },
        "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_1": {
            "clzieuhlc005a7tc9bx6f0mb5": ["MINOR_ISSUES"],
            "clzieuhm1005b7tc9b747clxw": ["NO_ISSUES"],
        },
        "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2": {
            "clzieuhlc005a7tc9bx6f0mb5": ["MAJOR_INACCURACY"],
            "clzieuhm1005b7tc9b747clxw": ["NO_ISSUES"],
        },
        "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_3": {
            "clzieuhlc005a7tc9bx6f0mb5": ["MAJOR_SAFETY_CONCERN"],
            "clzieuhm1005b7tc9b747clxw": ["NO_ISSUES"],
        },
    }
    get_project_return_val = {
        "jsonInterface": updated_mock_json_interface,
        "inputType": "LLM_INSTR_FOLLOWING",
        "title": "Test project with classifications at completion level",
        "id": "project_id",
        "dataConnections": None,
    }
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.count_assets.return_value = 3
    kili_api_gateway.get_project.return_value = get_project_return_val
    kili_api_gateway.list_assets.return_value = updated_mock_fetch_assets

    kili_llm = LlmClientMethods(kili_api_gateway)

    result = kili_llm.export(
        project_id="project_id",
    )
    assert result == updated_expected_export
