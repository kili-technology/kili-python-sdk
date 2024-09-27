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
                        "id": "clziefeh6003k7tc99abderkk",
                        "content": "describe turtle in 100 words",
                        "createdAt": "2024-08-06T12:30:52.170Z",
                        "modelId": None,
                        "parentId": None,
                        "role": "USER",
                    },
                    {
                        "id": "clziefeoe003m7tc976xwbh58",
                        "content": "Turtles are reptiles known for their protective shells, which act as both home and armor. They are slow-moving on land but can be agile in water, with many species being excellent swimmers. Turtles are omnivorous, feeding on plants, insects, and small animals. They are cold-blooded and rely on external heat sources to regulate their body temperature. Turtles are long-lived, with some species living over 100 years. They are found on every continent except Antarctica, inhabiting a variety of environments including oceans, freshwater lakes, and even deserts. Many turtle species are endangered due to habitat loss and other factors.",
                        "createdAt": "2024-08-06T12:30:52.430Z",
                        "modelId": "clzief6pr003c7tc99680e8yj",
                        "parentId": "clziefeh6003k7tc99abderkk",
                        "role": "ASSISTANT",
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
        "status": "LABELED",
    }
]

expected_export = [
    {
        "0": {
            "raw_data": [
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
                    "label_type": "AUTOSAVE",
                    "label": {"COMPARISON_JOB": "A_3", "CLASSIFICATION_JOB": ["BOTH_ARE_GOOD"]},
                }
            ],
        },
        "1": {
            "raw_data": [
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
                    "label_type": "AUTOSAVE",
                    "label": {"COMPARISON_JOB": "B_1"},
                }
            ],
        },
        "2": {
            "raw_data": [
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
                    "label_type": "AUTOSAVE",
                    "label": {"COMPARISON_JOB": "A_2"},
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
