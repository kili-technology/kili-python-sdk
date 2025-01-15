import pytest

from kili.llm.presentation.client.llm import LlmClientMethods
from tests.unit.services.export.test_llm import expected_export

mock_json_interface = {
    "jobs": {
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
                    "MINOR_ISSUES": {"children": [], "name": "Minor issue(s)", "id": "category5"},
                    "MAJOR_ISSUES": {"children": [], "name": "Major issue(s)", "id": "category6"},
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
        "COMPARISON_JOB": {
            "content": {
                "options": {
                    "IS_MUCH_BETTER": {"children": [], "name": "Is much better", "id": "option13"},
                    "IS_BETTER": {"children": [], "name": "Is better", "id": "option14"},
                    "IS_SLIGHTLY_BETTER": {
                        "children": [],
                        "name": "Is slightly better",
                        "id": "option15",
                    },
                    "TIE": {"children": [], "name": "Tie", "mutual": True, "id": "option16"},
                },
                "input": "radio",
            },
            "instruction": "Pick the best answer",
            "mlTask": "COMPARISON",
            "required": 1,
            "isChild": False,
            "isNew": False,
        },
        "CLASSIFICATION_JOB_AT_ROUND_LEVEL": {
            "content": {
                "categories": {
                    "BOTH_ARE_GOOD": {"children": [], "name": "Both are good", "id": "category17"},
                    "BOTH_ARE_BAD": {"children": [], "name": "Both are bad", "id": "category18"},
                },
                "input": "radio",
            },
            "instruction": "Overall quality",
            "level": "round",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": False,
            "isNew": False,
        },
        "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL": {
            "content": {
                "categories": {
                    "GLOBAL_GOOD": {"children": [], "name": "Globally good", "id": "category19"},
                    "BOTH_ARE_BAD": {"children": [], "name": "Globally bad", "id": "category20"},
                },
                "input": "radio",
            },
            "instruction": "Global",
            "level": "conversation",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": False,
            "isNew": False,
        },
        "TRANSCRIPTION_JOB_AT_CONVERSATION_LEVEL": {
            "content": {"input": "textField"},
            "instruction": "Additional comments...",
            "level": "conversation",
            "mlTask": "TRANSCRIPTION",
            "required": 0,
            "isChild": False,
            "isNew": False,
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
                        "id": "20250114170129511-1",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL",
                        "path": [],
                        "labelId": "cm5wnub7w01evp30w0ig9h8bh",
                        "annotationValue": {"categories": ["JUST_RIGHT"]},
                        "chatItemId": "cm5wnudcb01f1p30wcay0hht8",
                    },
                    {
                        "id": "20250114170130144-2",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_1",
                        "path": [],
                        "labelId": "cm5wnub7w01evp30w0ig9h8bh",
                        "annotationValue": {"categories": ["MAJOR_ISSUES"]},
                        "chatItemId": "cm5wnudcb01f1p30wcay0hht8",
                    },
                    {
                        "id": "20250114170130780-3",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2",
                        "path": [],
                        "labelId": "cm5wnub7w01evp30w0ig9h8bh",
                        "annotationValue": {"categories": ["MINOR_INACCURACY"]},
                        "chatItemId": "cm5wnudfv01f2p30whovhbwzp",
                    },
                    {
                        "id": "20250114170132013-4",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_3",
                        "path": [],
                        "labelId": "cm5wnub7w01evp30w0ig9h8bh",
                        "annotationValue": {"categories": ["MAJOR_SAFETY_CONCERN"]},
                        "chatItemId": "cm5wnudfv01f2p30whovhbwzp",
                    },
                    {
                        "id": "20250114170133181-5",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "cm5wnub7w01evp30w0ig9h8bh",
                        "annotationValue": {
                            "choice": {
                                "code": "Is better",
                                "firstId": "cm5wnudcb01f1p30wcay0hht8",
                                "secondId": "cm5wnudfv01f2p30whovhbwzp",
                            }
                        },
                        "chatItemId": "cm5wnucrc01ezp30w3029eyv3",
                    },
                ],
                "chatItems": [
                    {
                        "id": "cm5wnucrc01ezp30w3029eyv3",
                        "content": "test",
                        "createdAt": "2025-01-14T16:01:26.808Z",
                        "externalId": None,
                        "modelName": None,
                        "modelId": None,
                        "parentId": None,
                        "role": "USER",
                    },
                    {
                        "id": "cm5wnudcb01f1p30wcay0hht8",
                        "content": " It looks like everything is working correctly. How can I assist you today?",
                        "createdAt": "2025-01-14T16:01:27.563Z",
                        "externalId": None,
                        "modelName": None,
                        "modelId": "cm5wnub7p01etp30w1e5wgwww",
                        "parentId": "cm5wnucrc01ezp30w3029eyv3",
                        "role": "ASSISTANT",
                    },
                    {
                        "id": "cm5wnudfv01f2p30whovhbwzp",
                        "content": " It looks like everything is working correctly. How can I assist you today?",
                        "createdAt": "2025-01-14T16:01:27.692Z",
                        "externalId": None,
                        "modelName": None,
                        "modelId": "cm5wnub7q01eup30w0g273df8",
                        "parentId": "cm5wnucrc01ezp30w3029eyv3",
                        "role": "ASSISTANT",
                    },
                ],
                "author": {
                    "id": "user-1",
                    "email": "test+admin@kili-technology.com",
                    "firstname": "Test",
                    "lastname": "Admin",
                },
                "createdAt": "2025-01-14T16:01:24.812Z",
                "id": "cm5wnub7w01evp30w0ig9h8bh",
                "isLatestLabelForUser": True,
                "isSentBackToQueue": False,
                "jsonResponse": {},
                "labelType": "DEFAULT",
                "modelName": None,
            }
        ],
        "assetProjectModels": [
            {
                "id": "cm5wnub7p01etp30w1e5wgwww",
                "configuration": {"model": "AI21-Jamba-1-5-Large-ykxca"},
                "projectModelId": "cm5wnu9k901epp30wauqj0u51",
            },
            {
                "id": "cm5wnub7q01eup30w0g273df8",
                "configuration": {"model": "AI21-Jamba-1-5-Large-ykxca"},
                "projectModelId": "cm5wnu9ka01eqp30w9nazcdid",
            },
        ],
        "id": "cm5wnub7b01erp30w1plf78m8",
        "content": "",
        "externalId": "cm5wnub7b01erp30w1plf78m8",
        "jsonMetadata": {},
        "status": "LABELED",
    },
    {
        "labels": [
            {
                "annotations": [
                    {
                        "id": "20250114170150963-6",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2",
                        "path": [],
                        "labelId": "cm5wnum1801fvp30we67c0q2j",
                        "annotationValue": {"categories": ["MINOR_INACCURACY"]},
                        "chatItemId": "cm5wnurbv01g1p30wbzgb1vjx",
                    },
                    {
                        "id": "20250114170151352-7",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_ROUND_LEVEL",
                        "path": [],
                        "labelId": "cm5wnum1801fvp30we67c0q2j",
                        "annotationValue": {"categories": ["BOTH_ARE_GOOD"]},
                        "chatItemId": "cm5wnuquw01fzp30w9iyw1azc",
                    },
                    {
                        "id": "20250114170154104-8",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL",
                        "path": [],
                        "labelId": "cm5wnum1801fvp30we67c0q2j",
                        "annotationValue": {"categories": ["BOTH_ARE_BAD"]},
                        "chatItemId": None,
                    },
                    {
                        "id": "20250114170156169-10",
                        "__typename": "TranscriptionAnnotation",
                        "job": "TRANSCRIPTION_JOB_AT_CONVERSATION_LEVEL",
                        "path": [],
                        "labelId": "cm5wnum1801fvp30we67c0q2j",
                        "annotationValue": {"text": "Nice"},
                        "chatItemId": None,
                    },
                    {
                        "id": "20250114170158782-11",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2",
                        "path": [],
                        "labelId": "cm5wnum1801fvp30we67c0q2j",
                        "annotationValue": {"categories": ["MINOR_INACCURACY"]},
                        "chatItemId": "cm5wnus9n01g2p30wbb1q0e7x",
                    },
                    {
                        "id": "20250114170201097-12",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "cm5wnum1801fvp30we67c0q2j",
                        "annotationValue": {
                            "choice": {
                                "code": "Is better",
                                "firstId": "cm5wnurbv01g1p30wbzgb1vjx",
                                "secondId": "cm5wnus9n01g2p30wbb1q0e7x",
                            }
                        },
                        "chatItemId": "cm5wnuquw01fzp30w9iyw1azc",
                    },
                    {
                        "id": "20250114170206856-13",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "cm5wnum1801fvp30we67c0q2j",
                        "annotationValue": {
                            "choice": {
                                "code": "Is much better",
                                "firstId": "cm5wnv6b501gwp30w764fegsi",
                                "secondId": "cm5wnv6ax01gvp30w2q9ba29v",
                            }
                        },
                        "chatItemId": "cm5wnv5tj01gtp30w2eze4gzo",
                    },
                    {
                        "id": "20250114170207624-14",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL",
                        "path": [],
                        "labelId": "cm5wnum1801fvp30we67c0q2j",
                        "annotationValue": {"categories": ["JUST_RIGHT"]},
                        "chatItemId": "cm5wnv6b501gwp30w764fegsi",
                    },
                    {
                        "id": "20250114170208400-15",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2",
                        "path": [],
                        "labelId": "cm5wnum1801fvp30we67c0q2j",
                        "annotationValue": {"categories": ["MINOR_INACCURACY"]},
                        "chatItemId": "cm5wnv6b501gwp30w764fegsi",
                    },
                    {
                        "id": "20250114170209041-16",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_3",
                        "path": [],
                        "labelId": "cm5wnum1801fvp30we67c0q2j",
                        "annotationValue": {"categories": ["NO_ISSUES"]},
                        "chatItemId": "cm5wnv6ax01gvp30w2q9ba29v",
                    },
                    {
                        "id": "20250114170210907-17",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_ROUND_LEVEL",
                        "path": [],
                        "labelId": "cm5wnum1801fvp30we67c0q2j",
                        "annotationValue": {"categories": ["BOTH_ARE_BAD"]},
                        "chatItemId": "cm5wnv5tj01gtp30w2eze4gzo",
                    },
                ],
                "chatItems": [
                    {
                        "id": "cm5wnuquw01fzp30w9iyw1azc",
                        "content": "this is a two rounds conversation",
                        "createdAt": "2025-01-14T16:01:45.081Z",
                        "externalId": None,
                        "modelName": None,
                        "modelId": None,
                        "parentId": None,
                        "role": "USER",
                    },
                    {
                        "id": "cm5wnurbv01g1p30wbzgb1vjx",
                        "content": " Great! Let's get started with our two-round conversation. What's the topic you'd like to discuss or the question you have in mind?",
                        "createdAt": "2025-01-14T16:01:45.692Z",
                        "externalId": None,
                        "modelName": None,
                        "modelId": "cm5wnum1301ftp30wgb2vax6e",
                        "parentId": "cm5wnuquw01fzp30w9iyw1azc",
                        "role": "ASSISTANT",
                    },
                    {
                        "id": "cm5wnus9n01g2p30wbb1q0e7x",
                        "content": " Sure, let's have a two-round conversation. What would you like to talk about in this first round?",
                        "createdAt": "2025-01-14T16:01:46.907Z",
                        "externalId": None,
                        "modelName": None,
                        "modelId": "cm5wnum1301fup30w4ic45z5z",
                        "parentId": "cm5wnuquw01fzp30w9iyw1azc",
                        "role": "ASSISTANT",
                    },
                    {
                        "id": "cm5wnv5tj01gtp30w2eze4gzo",
                        "content": "how are. you",
                        "createdAt": "2025-01-14T16:02:04.471Z",
                        "externalId": None,
                        "modelName": None,
                        "modelId": None,
                        "parentId": "cm5wnurbv01g1p30wbzgb1vjx",
                        "role": "USER",
                    },
                    {
                        "id": "cm5wnv6ax01gvp30w2q9ba29v",
                        "content": " I'm doing well, thank you! How about you? How can I assist you today?",
                        "createdAt": "2025-01-14T16:02:05.097Z",
                        "externalId": None,
                        "modelName": None,
                        "modelId": "cm5wnum1301fup30w4ic45z5z",
                        "parentId": "cm5wnv5tj01gtp30w2eze4gzo",
                        "role": "ASSISTANT",
                    },
                    {
                        "id": "cm5wnv6b501gwp30w764fegsi",
                        "content": " I'm doing well, thank you! How about you? How can I assist you today?",
                        "createdAt": "2025-01-14T16:02:05.105Z",
                        "externalId": None,
                        "modelName": None,
                        "modelId": "cm5wnum1301ftp30wgb2vax6e",
                        "parentId": "cm5wnv5tj01gtp30w2eze4gzo",
                        "role": "ASSISTANT",
                    },
                ],
                "author": {
                    "id": "user-1",
                    "email": "test+admin@kili-technology.com",
                    "firstname": "Test",
                    "lastname": "Admin",
                },
                "createdAt": "2025-01-14T16:01:38.828Z",
                "id": "cm5wnum1801fvp30we67c0q2j",
                "isLatestLabelForUser": True,
                "isSentBackToQueue": False,
                "jsonResponse": {},
                "labelType": "DEFAULT",
                "modelName": None,
            }
        ],
        "assetProjectModels": [
            {
                "id": "cm5wnum1301ftp30wgb2vax6e",
                "configuration": {"model": "AI21-Jamba-1-5-Large-ykxca"},
                "projectModelId": "cm5wnu9k901epp30wauqj0u51",
            },
            {
                "id": "cm5wnum1301fup30w4ic45z5z",
                "configuration": {"model": "AI21-Jamba-1-5-Large-ykxca"},
                "projectModelId": "cm5wnu9ka01eqp30w9nazcdid",
            },
        ],
        "id": "cm5wnum0o01frp30w4n718txn",
        "content": "",
        "externalId": "cm5wnum0o01frp30w4n718txn",
        "jsonMetadata": {},
        "status": "LABELED",
    },
]

mock_chat_items_1 = [
    {
        "content": "test",
        "externalId": "cm5wnucrc01ezp30w3029eyv3",
        "id": "cm5wnucrc01ezp30w3029eyv3",
        "modelName": None,
        "role": "USER",
    },
    {
        "content": " It looks like everything is working correctly. How can I assist you today?",
        "externalId": "cm5wnudcb01f1p30wcay0hht8",
        "id": "cm5wnudcb01f1p30wcay0hht8",
        "modelName": "cm5wnub7p01etp30w1e5wgwww",
        "role": "ASSISTANT",
    },
    {
        "content": " It looks like everything is working correctly. How can I assist you today?",
        "externalId": "cm5wnudfv01f2p30whovhbwzp",
        "id": "cm5wnudfv01f2p30whovhbwzp",
        "modelName": "cm5wnub7q01eup30w0g273df8",
        "role": "ASSISTANT",
    },
]

mock_chat_items_2 = [
    {
        "id": "cm5wnuquw01fzp30w9iyw1azc",
        "content": "this is a two rounds conversation",
        "externalId": "cm5wnuquw01fzp30w9iyw1azc",
        "modelName": None,
        "role": "USER",
    },
    {
        "id": "cm5wnurbv01g1p30wbzgb1vjx",
        "content": " Great! Let's get started with our two-round conversation. What's the topic you'd like to discuss or the question you have in mind?",
        "externalId": "cm5wnurbv01g1p30wbzgb1vjx",
        "modelName": "cm5wnum1301ftp30wgb2vax6e",
        "role": "ASSISTANT",
    },
    {
        "id": "cm5wnus9n01g2p30wbb1q0e7x",
        "content": " Sure, let's have a two-round conversation. What would you like to talk about in this first round?",
        "externalId": "cm5wnus9n01g2p30wbb1q0e7x",
        "modelName": "cm5wnum1301fup30w4ic45z5z",
        "role": "ASSISTANT",
    },
    {
        "id": "cm5wnv5tj01gtp30w2eze4gzo",
        "content": "how are. you",
        "externalId": "cm5wnv5tj01gtp30w2eze4gzo",
        "modelName": None,
        "role": "USER",
    },
    {
        "id": "cm5wnv6ax01gvp30w2q9ba29v",
        "content": " I'm doing well, thank you! How about you? How can I assist you today?",
        "externalId": "cm5wnv6ax01gvp30w2q9ba29v",
        "modelName": "cm5wnum1301fup30w4ic45z5z",
        "role": "ASSISTANT",
    },
    {
        "id": "cm5wnv6b501gwp30w764fegsi",
        "content": " I'm doing well, thank you! How about you? How can I assist you today?",
        "externalId": "cm5wnv6b501gwp30w764fegsi",
        "modelName": "cm5wnum1301ftp30wgb2vax6e",
        "role": "ASSISTANT",
    },
]

expected_export = [
    {
        "chatItems": [
            {
                "content": "test",
                "externalId": "cm5wnucrc01ezp30w3029eyv3",
                "modelName": None,
                "role": "USER",
            },
            {
                "content": " It looks like everything is working correctly. "
                "How can I assist you today?",
                "externalId": "cm5wnudcb01f1p30wcay0hht8",
                "modelName": "cm5wnub7p01etp30w1e5wgwww",
                "role": "ASSISTANT",
            },
            {
                "content": " It looks like everything is working correctly. "
                "How can I assist you today?",
                "externalId": "cm5wnudfv01f2p30whovhbwzp",
                "modelName": "cm5wnub7q01eup30w0g273df8",
                "role": "ASSISTANT",
            },
        ],
        "externalId": "cm5wnub7b01erp30w1plf78m8",
        "label": {
            "completion": {
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL": {
                    "cm5wnudcb01f1p30wcay0hht8": {"categories": ["JUST_RIGHT"]}
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_1": {
                    "cm5wnudcb01f1p30wcay0hht8": {"categories": ["MAJOR_ISSUES"]}
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2": {
                    "cm5wnudfv01f2p30whovhbwzp": {"categories": ["MINOR_INACCURACY"]}
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_3": {
                    "cm5wnudfv01f2p30whovhbwzp": {"categories": ["MAJOR_SAFETY_CONCERN"]}
                },
            },
            "conversation": {},
            "round": {
                "COMPARISON_JOB": {
                    0: {
                        "code": "Is better",
                        "firstId": "cm5wnudcb01f1p30wcay0hht8",
                        "secondId": "cm5wnudfv01f2p30whovhbwzp",
                    }
                }
            },
        },
        "labeler": "test+admin@kili-technology.com",
        "metadata": {
            "models": [
                {
                    "configuration": {"model": "AI21-Jamba-1-5-Large-ykxca"},
                    "id": "cm5wnub7p01etp30w1e5wgwww",
                    "projectModelId": "cm5wnu9k901epp30wauqj0u51",
                },
                {
                    "configuration": {"model": "AI21-Jamba-1-5-Large-ykxca"},
                    "id": "cm5wnub7q01eup30w0g273df8",
                    "projectModelId": "cm5wnu9ka01eqp30w9nazcdid",
                },
            ]
        },
    },
    {
        "chatItems": [
            {
                "content": "this is a two rounds conversation",
                "externalId": "cm5wnuquw01fzp30w9iyw1azc",
                "modelName": None,
                "role": "USER",
            },
            {
                "content": " Great! Let's get started with our two-round "
                "conversation. What's the topic you'd like to "
                "discuss or the question you have in mind?",
                "externalId": "cm5wnurbv01g1p30wbzgb1vjx",
                "modelName": "cm5wnum1301ftp30wgb2vax6e",
                "role": "ASSISTANT",
            },
            {
                "content": " Sure, let's have a two-round conversation. What "
                "would you like to talk about in this first round?",
                "externalId": "cm5wnus9n01g2p30wbb1q0e7x",
                "modelName": "cm5wnum1301fup30w4ic45z5z",
                "role": "ASSISTANT",
            },
            {
                "content": "how are. you",
                "externalId": "cm5wnv5tj01gtp30w2eze4gzo",
                "modelName": None,
                "role": "USER",
            },
            {
                "content": " I'm doing well, thank you! How about you? How "
                "can I assist you today?",
                "externalId": "cm5wnv6ax01gvp30w2q9ba29v",
                "modelName": "cm5wnum1301fup30w4ic45z5z",
                "role": "ASSISTANT",
            },
            {
                "content": " I'm doing well, thank you! How about you? How "
                "can I assist you today?",
                "externalId": "cm5wnv6b501gwp30w764fegsi",
                "modelName": "cm5wnum1301ftp30wgb2vax6e",
                "role": "ASSISTANT",
            },
        ],
        "externalId": "cm5wnum0o01frp30w4n718txn",
        "label": {
            "completion": {
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL": {
                    "cm5wnv6b501gwp30w764fegsi": {"categories": ["JUST_RIGHT"]}
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2": {
                    "cm5wnurbv01g1p30wbzgb1vjx": {"categories": ["MINOR_INACCURACY"]},
                    "cm5wnus9n01g2p30wbb1q0e7x": {"categories": ["MINOR_INACCURACY"]},
                    "cm5wnv6b501gwp30w764fegsi": {"categories": ["MINOR_INACCURACY"]},
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_3": {
                    "cm5wnv6ax01gvp30w2q9ba29v": {"categories": ["NO_ISSUES"]}
                },
            },
            "conversation": {
                "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL": {"categories": ["BOTH_ARE_BAD"]},
                "TRANSCRIPTION_JOB_AT_CONVERSATION_LEVEL": {"text": "Nice"},
            },
            "round": {
                "CLASSIFICATION_JOB_AT_ROUND_LEVEL": {
                    0: {"categories": ["BOTH_ARE_GOOD"]},
                    1: {"categories": ["BOTH_ARE_BAD"]},
                },
                "COMPARISON_JOB": {
                    0: {
                        "code": "Is better",
                        "firstId": "cm5wnurbv01g1p30wbzgb1vjx",
                        "secondId": "cm5wnus9n01g2p30wbb1q0e7x",
                    },
                    1: {
                        "code": "Is much better",
                        "firstId": "cm5wnv6b501gwp30w764fegsi",
                        "secondId": "cm5wnv6ax01gvp30w2q9ba29v",
                    },
                },
            },
        },
        "labeler": "test+admin@kili-technology.com",
        "metadata": {
            "models": [
                {
                    "configuration": {"model": "AI21-Jamba-1-5-Large-ykxca"},
                    "id": "cm5wnum1301ftp30wgb2vax6e",
                    "projectModelId": "cm5wnu9k901epp30wauqj0u51",
                },
                {
                    "configuration": {"model": "AI21-Jamba-1-5-Large-ykxca"},
                    "id": "cm5wnum1301fup30w4ic45z5z",
                    "projectModelId": "cm5wnu9ka01eqp30w9nazcdid",
                },
            ]
        },
    },
]


def test_export_dynamic(mocker):
    get_project_return_val = {
        "jsonInterface": mock_json_interface,
        "inputType": "LLM_INSTR_FOLLOWING",
        "title": "LLM Dynamic test export project",
        "id": "project_id",
        "dataConnections": None,
    }
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.count_assets.return_value = 3
    kili_api_gateway.get_project.return_value = get_project_return_val
    kili_api_gateway.list_assets.return_value = mock_fetch_assets
    kili_api_gateway.list_chat_items.side_effect = [mock_chat_items_1, mock_chat_items_2]

    kili_llm = LlmClientMethods(kili_api_gateway)

    result = kili_llm.export(
        project_id="project_id",
    )
    assert result == expected_export


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
