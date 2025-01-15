import pytest

from kili.llm.presentation.client.llm import LlmClientMethods
from tests.unit.services.export.test_llm import expected_export

mock_json_interface = {
    "jobs": {
        "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL": {
            "content": {
                "categories": {
                    "TOO_SHORT": {
                        "children": [],
                        "name": "Too short",
                        "id": "category1",
                    },
                    "JUST_RIGHT": {
                        "children": [],
                        "name": "Just right",
                        "id": "category2",
                    },
                    "TOO_VERBOSE": {
                        "children": [],
                        "name": "Too verbose",
                        "id": "category3",
                    },
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
                    "NO_ISSUES": {
                        "children": [],
                        "name": "No issues",
                        "id": "category4",
                    },
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
                    "NO_ISSUES": {
                        "children": [],
                        "name": "No issues",
                        "id": "category7",
                    },
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
                    "NO_ISSUES": {
                        "children": [],
                        "name": "No issues",
                        "id": "category10",
                    },
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
                    "IS_MUCH_BETTER": {
                        "children": [],
                        "name": "Is much better",
                        "id": "option13",
                    },
                    "IS_BETTER": {
                        "children": [],
                        "name": "Is better",
                        "id": "option14",
                    },
                    "IS_SLIGHTLY_BETTER": {
                        "children": [],
                        "name": "Is slightly better",
                        "id": "option15",
                    },
                    "TIE": {
                        "children": [],
                        "name": "Tie",
                        "mutual": True,
                        "id": "option16",
                    },
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
                    "BOTH_ARE_GOOD": {
                        "children": [],
                        "name": "Both are good",
                        "id": "category17",
                    },
                    "BOTH_ARE_BAD": {
                        "children": [],
                        "name": "Both are bad",
                        "id": "category18",
                    },
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
                    "GLOBAL_GOOD": {
                        "children": [],
                        "name": "Globally good",
                        "id": "category19",
                    },
                    "BOTH_ARE_BAD": {
                        "children": [],
                        "name": "Globally bad",
                        "id": "category20",
                    },
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
        "assetProjectModels": [],
        "labels": [
            {
                "chatItems": [],
                "annotations": [
                    {
                        "id": "20250115091847438-1",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "cm5xmrj7c005c9u0w0o7z3tfu",
                        "annotationValue": {
                            "choice": {
                                "code": "Is much better",
                                "firstId": "cm5xmqjdp000j9u0w83phhhim",
                                "secondId": "cm5xmqjdp000i9u0w72svc1eg",
                            }
                        },
                        "chatItemId": "cm5xmqjdp000h9u0wdt7v45g1",
                    },
                    {
                        "id": "20250115091848649-2",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_1",
                        "path": [],
                        "labelId": "cm5xmrj7c005c9u0w0o7z3tfu",
                        "annotationValue": {"categories": ["MINOR_ISSUES"]},
                        "chatItemId": "cm5xmqjdp000i9u0w72svc1eg",
                    },
                    {
                        "id": "20250115091850107-3",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2",
                        "path": [],
                        "labelId": "cm5xmrj7c005c9u0w0o7z3tfu",
                        "annotationValue": {"categories": ["NO_ISSUES"]},
                        "chatItemId": "cm5xmqjdp000j9u0w83phhhim",
                    },
                    {
                        "id": "20250115091856209-4",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2",
                        "path": [],
                        "labelId": "cm5xmrj7c005c9u0w0o7z3tfu",
                        "annotationValue": {"categories": ["MINOR_INACCURACY"]},
                        "chatItemId": "cm5xmqjdp000i9u0w72svc1eg",
                    },
                    {
                        "id": "20250115091857655-5",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmrj7c005c9u0w0o7z3tfu",
                        "annotationValue": {"categories": ["GLOBAL_GOOD"]},
                        "chatItemId": None,
                    },
                    {
                        "id": "20250115091858191-6",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_ROUND_LEVEL",
                        "path": [],
                        "labelId": "cm5xmrj7c005c9u0w0o7z3tfu",
                        "annotationValue": {"categories": ["BOTH_ARE_GOOD"]},
                        "chatItemId": "cm5xmqjdp000h9u0wdt7v45g1",
                    },
                ],
                "author": {
                    "id": "user-1",
                    "email": "test+admin@kili-technology.com",
                    "firstname": "Test",
                    "lastname": "Admin",
                },
                "createdAt": "2025-01-15T08:19:01.752Z",
                "id": "cm5xmrj7c005c9u0w0o7z3tfu",
                "isLatestLabelForUser": True,
                "isSentBackToQueue": False,
                "jsonResponse": {},
                "labelType": "DEFAULT",
                "modelName": None,
            }
        ],
        "id": "cm5xmqjdg000e9u0wa8nv8kv3",
        "content": "",
        "externalId": "Fibonacci python function",
        "jsonMetadata": {},
        "status": "LABELED",
    },
    {
        "assetProjectModels": [],
        "labels": [
            {
                "chatItems": [],
                "annotations": [
                    {
                        "id": "20250115091906080-7",
                        "__typename": "TranscriptionAnnotation",
                        "job": "TRANSCRIPTION_JOB_AT_CONVERSATION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmsdt7006g9u0w1g68exln",
                        "annotationValue": {"text": "gpt-o1 is much worse in that conversation"},
                        "chatItemId": None,
                    },
                    {
                        "id": "20250115091911532-8",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmsdt7006g9u0w1g68exln",
                        "annotationValue": {"categories": ["GLOBAL_GOOD"]},
                        "chatItemId": None,
                    },
                    {
                        "id": "20250115091914050-9",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "cm5xmsdt7006g9u0w1g68exln",
                        "annotationValue": {
                            "choice": {
                                "code": "Is much better",
                                "firstId": "cm5xmqjee000t9u0wb1y0e1bu",
                                "secondId": "cm5xmqjee000s9u0w4i0xaa8k",
                            }
                        },
                        "chatItemId": "cm5xmqjee000r9u0w0dqlgo9e",
                    },
                    {
                        "id": "20250115091937484-10",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmsdt7006g9u0w1g68exln",
                        "annotationValue": {"categories": ["TOO_SHORT"]},
                        "chatItemId": "cm5xmqjee000s9u0w4i0xaa8k",
                    },
                    {
                        "id": "20250115091938502-11",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmsdt7006g9u0w1g68exln",
                        "annotationValue": {"categories": ["JUST_RIGHT"]},
                        "chatItemId": "cm5xmqjee000t9u0wb1y0e1bu",
                    },
                    {
                        "id": "20250115091940123-12",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_ROUND_LEVEL",
                        "path": [],
                        "labelId": "cm5xmsdt7006g9u0w1g68exln",
                        "annotationValue": {"categories": ["BOTH_ARE_GOOD"]},
                        "chatItemId": "cm5xmqjee000r9u0w0dqlgo9e",
                    },
                ],
                "author": {
                    "id": "user-1",
                    "email": "test+admin@kili-technology.com",
                    "firstname": "Test",
                    "lastname": "Admin",
                },
                "createdAt": "2025-01-15T08:19:41.419Z",
                "id": "cm5xmsdt7006g9u0w1g68exln",
                "isLatestLabelForUser": True,
                "isSentBackToQueue": False,
                "jsonResponse": {},
                "labelType": "DEFAULT",
                "modelName": None,
            }
        ],
        "id": "cm5xmqjeb000o9u0waxhdgefs",
        "content": "",
        "externalId": "The sum of the integers",
        "jsonMetadata": {},
        "status": "LABELED",
    },
    {
        "assetProjectModels": [],
        "labels": [
            {
                "chatItems": [],
                "annotations": [
                    {
                        "id": "cm5xmqjfl001a9u0wgzrj0la6",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqjev00109u0wa4yy76iq",
                        "annotationValue": {"categories": ["TOO_SHORT"]},
                        "chatItemId": "cm5xmqjfc00149u0wfeyu8f35",
                    },
                    {
                        "id": "cm5xmqjfl001c9u0wfi208se0",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqjev00109u0wa4yy76iq",
                        "annotationValue": {"categories": ["JUST_RIGHT"]},
                        "chatItemId": "cm5xmqjfc00159u0w5q9e0gob",
                    },
                    {
                        "id": "cm5xmqjfl001e9u0whx553v4k",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_1",
                        "path": [],
                        "labelId": "cm5xmqjev00109u0wa4yy76iq",
                        "annotationValue": {"categories": ["MINOR_ISSUES"]},
                        "chatItemId": "cm5xmqjfc00149u0wfeyu8f35",
                    },
                    {
                        "id": "cm5xmqjfl001g9u0w2cleagmv",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2",
                        "path": [],
                        "labelId": "cm5xmqjev00109u0wa4yy76iq",
                        "annotationValue": {"categories": ["MINOR_INACCURACY"]},
                        "chatItemId": "cm5xmqjfc00149u0wfeyu8f35",
                    },
                    {
                        "id": "cm5xmqjfl001i9u0w1zel4bqq",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_3",
                        "path": [],
                        "labelId": "cm5xmqjev00109u0wa4yy76iq",
                        "annotationValue": {"categories": ["MINOR_SAFETY_CONCERN"]},
                        "chatItemId": "cm5xmqjfc00149u0wfeyu8f35",
                    },
                    {
                        "id": "cm5xmqjfm001k9u0w81in4jzs",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqjev00109u0wa4yy76iq",
                        "annotationValue": {"categories": ["GLOBAL_GOOD"]},
                        "chatItemId": None,
                    },
                    {
                        "id": "cm5xmqjfm001m9u0wds252ay4",
                        "__typename": "TranscriptionAnnotation",
                        "job": "TRANSCRIPTION_JOB_AT_CONVERSATION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqjev00109u0wa4yy76iq",
                        "annotationValue": {"text": "Great conversation!"},
                        "chatItemId": None,
                    },
                    {
                        "id": "cm5xmqjfm001o9u0wc43e4szj",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_ROUND_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqjev00109u0wa4yy76iq",
                        "annotationValue": {"categories": ["BOTH_ARE_GOOD"]},
                        "chatItemId": "cm5xmqjfc00139u0w2rx0d5vt",
                    },
                    {
                        "id": "cm5xmqjfm001q9u0wfs6fa3t2",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "cm5xmqjev00109u0wa4yy76iq",
                        "annotationValue": {
                            "choice": {
                                "code": "Is much better",
                                "firstId": "cm5xmqjfc00159u0w5q9e0gob",
                                "secondId": "cm5xmqjfc00149u0wfeyu8f35",
                            }
                        },
                        "chatItemId": "cm5xmqjfc00139u0w2rx0d5vt",
                    },
                ],
                "author": {
                    "id": "user-4",
                    "email": "test+fx@kili-technology.com",
                    "firstname": "FX",
                    "lastname": "Leduc",
                },
                "createdAt": "2025-01-15T08:18:15.367Z",
                "id": "cm5xmqjev00109u0wa4yy76iq",
                "isLatestLabelForUser": True,
                "isSentBackToQueue": False,
                "jsonResponse": {},
                "labelType": "DEFAULT",
                "modelName": None,
            }
        ],
        "id": "cm5xmqjeq000y9u0w6sza8c0a",
        "content": "",
        "externalId": "Caesar cipher decoding",
        "jsonMetadata": {},
        "status": "TO_REVIEW",
    },
    {
        "assetProjectModels": [],
        "labels": [
            {
                "chatItems": [],
                "annotations": [
                    {
                        "id": "cm5xmqx22003i9u0w72xs0j8f",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqwzk002w9u0w06axfk7f",
                        "annotationValue": {"categories": ["TOO_SHORT"]},
                        "chatItemId": "cm5xmqx0n00309u0w9sjaf1lt",
                    },
                    {
                        "id": "cm5xmqx22003k9u0wg9i998jd",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqwzk002w9u0w06axfk7f",
                        "annotationValue": {"categories": ["JUST_RIGHT"]},
                        "chatItemId": "cm5xmqx0n00339u0w9g06hv5p",
                    },
                    {
                        "id": "cm5xmqx22003m9u0w5azb340a",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqwzk002w9u0w06axfk7f",
                        "annotationValue": {"categories": ["TOO_SHORT"]},
                        "chatItemId": "cm5xmqx0n00379u0w1gr01kvq",
                    },
                    {
                        "id": "cm5xmqx22003o9u0wbxxdcn5v",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqwzk002w9u0w06axfk7f",
                        "annotationValue": {"categories": ["GLOBAL_GOOD"]},
                        "chatItemId": None,
                    },
                    {
                        "id": "cm5xmqx22003q9u0wcneddnq8",
                        "__typename": "TranscriptionAnnotation",
                        "job": "TRANSCRIPTION_JOB_AT_CONVERSATION_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqwzk002w9u0w06axfk7f",
                        "annotationValue": {"text": "Great conversation!"},
                        "chatItemId": None,
                    },
                    {
                        "id": "cm5xmqx23003s9u0wau6pgqzv",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_ROUND_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqwzk002w9u0w06axfk7f",
                        "annotationValue": {"categories": ["BOTH_ARE_GOOD"]},
                        "chatItemId": "cm5xmqx0n002z9u0wdgyf5tzu",
                    },
                    {
                        "id": "cm5xmqx23003u9u0whyjvds5e",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_ROUND_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqwzk002w9u0w06axfk7f",
                        "annotationValue": {"categories": ["BOTH_ARE_BAD"]},
                        "chatItemId": "cm5xmqx0n00329u0w4poweeit",
                    },
                    {
                        "id": "cm5xmqx23003w9u0w8kj91rhm",
                        "__typename": "ClassificationAnnotation",
                        "job": "CLASSIFICATION_JOB_AT_ROUND_LEVEL",
                        "path": [],
                        "labelId": "cm5xmqwzk002w9u0w06axfk7f",
                        "annotationValue": {"categories": ["BOTH_ARE_GOOD"]},
                        "chatItemId": "cm5xmqx0n00359u0w17k0ddzs",
                    },
                    {
                        "id": "cm5xmqx23003y9u0whjeq2z4s",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "cm5xmqwzk002w9u0w06axfk7f",
                        "annotationValue": {
                            "choice": {
                                "code": "Is much better",
                                "firstId": "cm5xmqx0n00309u0w9sjaf1lt",
                                "secondId": "cm5xmqx0n00319u0wgddp7ey5",
                            }
                        },
                        "chatItemId": "cm5xmqx0n002z9u0wdgyf5tzu",
                    },
                    {
                        "id": "cm5xmqx2300409u0w0acv1eu7",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "cm5xmqwzk002w9u0w06axfk7f",
                        "annotationValue": {
                            "choice": {
                                "code": "Is better",
                                "firstId": "cm5xmqx0n00339u0w9g06hv5p",
                                "secondId": "cm5xmqx0n00349u0w6x0j17wl",
                            }
                        },
                        "chatItemId": "cm5xmqx0n00329u0w4poweeit",
                    },
                    {
                        "id": "cm5xmqx2400429u0wh1ie2vgc",
                        "__typename": "ComparisonAnnotation",
                        "job": "COMPARISON_JOB",
                        "path": [],
                        "labelId": "cm5xmqwzk002w9u0w06axfk7f",
                        "annotationValue": {
                            "choice": {
                                "code": "Is much better",
                                "firstId": "cm5xmqx0n00379u0w1gr01kvq",
                                "secondId": "cm5xmqx0n00369u0wau11f4of",
                            }
                        },
                        "chatItemId": "cm5xmqx0n00359u0w17k0ddzs",
                    },
                ],
                "author": {
                    "id": "user-4",
                    "email": "test+fx@kili-technology.com",
                    "firstname": "FX",
                    "lastname": "Leduc",
                },
                "createdAt": "2025-01-15T08:18:32.960Z",
                "id": "cm5xmqwzk002w9u0w06axfk7f",
                "isLatestLabelForUser": True,
                "isSentBackToQueue": False,
                "jsonResponse": {},
                "labelType": "DEFAULT",
                "modelName": None,
            }
        ],
        "id": "cm5xmqwz3002u9u0wammyf9ie",
        "content": "",
        "externalId": "capital-france",
        "jsonMetadata": {},
        "status": "TO_REVIEW",
    },
]


mock_chat_items_1 = [
    {
        "id": "cm5xmqjdp000g9u0w1s99cejh",
        "content": "You are an assistant helping the user by providing precise answers.",
        "createdAt": "2025-01-15T08:18:11.325Z",
        "externalId": "cm5xn0ir3000108l16u23casm",
        "modelName": None,
        "modelId": None,
        "parentId": None,
        "role": "SYSTEM",
    },
    {
        "id": "cm5xmqjdp000h9u0wdt7v45g1",
        "content": "Can you give me a function to compute Fibonacci numbers?",
        "createdAt": "2025-01-15T08:18:12.325Z",
        "externalId": "cm5xn11sy000208l1aopo9dfx",
        "modelName": None,
        "modelId": None,
        "parentId": "cm5xmqjdp000g9u0w1s99cejh",
        "role": "USER",
    },
    {
        "id": "cm5xmqjdp000i9u0w72svc1eg",
        "content": "Here is a recursive implementation for calculating Fibonacci numbers:\n\n```python\ndef fibonacci_recursive(n):\n    if n <= 1:\n        return n\n    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)\n```\n\nThis is simple to write but has a time complexity of \\( O(2^n) \\) due to redundant calculations. For large values of \\( n \\), this method becomes highly inefficient.",
        "createdAt": "2025-01-15T08:18:13.325Z",
        "externalId": "cm5xn170s000308l1b6vy9nk5",
        "modelName": "gpt-4o",
        "modelId": None,
        "parentId": "cm5xmqjdp000h9u0wdt7v45g1",
        "role": "ASSISTANT",
    },
    {
        "id": "cm5xmqjdp000j9u0w83phhhim",
        "content": "Here is an optimized implementation using matrix exponentiation, along with an explanation of why it is faster:\n\n```python\nimport numpy as np\n\ndef fibonacci_matrix(n):\n    def matrix_power(matrix, power):\n        result = np.identity(len(matrix), dtype=int)\n        while power:\n            if power % 2:\n                result = np.dot(result, matrix)\n            matrix = np.dot(matrix, matrix)\n            power //= 2\n        return result\n\n    if n == 0:\n        return 0\n    base_matrix = np.array([[1, 1], [1, 0]], dtype=int)\n    result_matrix = matrix_power(base_matrix, n - 1)\n    return result_matrix[0, 0]\n```\n\n### Why is Matrix Exponentiation Faster?\n\nThe recursive method recalculates values for overlapping subproblems, leading to exponential time complexity:\n\n\\[ T(n) = T(n-1) + T(n-2) + O(1), \\]\n\nwhich resolves to \\( O(2^n) \\). This inefficiency arises from redundant recalculations.\n\nThe matrix exponentiation method uses the property that Fibonacci numbers can be represented as a matrix multiplication:\n\n\\[ \\begin{bmatrix} F(n+1) & F(n) \\\\ F(n) & F(n-1) \\end{bmatrix} = \\begin{bmatrix} 1 & 1 \\\\ 1 & 0 \\end{bmatrix}^n. \\]\n\nUsing fast exponentiation (repeated squaring), the matrix power can be computed in \\( O(\\log n) \\) steps. For example, instead of multiplying the matrix \\( n \\) times, we:\n\n1. Square the matrix \\( \\lceil \\log_2 n \\rceil \\) times.\n2. Combine results for any remaining powers.\n\nThis drastically reduces the number of operations compared to the recursive method.\n\n### Comparison of Complexities\n\n- **Recursive Method**: \\( O(2^n) \\)\n- **Matrix Exponentiation**: \\( O(\\log n) \\)\n\nFor large \\( n \\), the difference is substantial. Consider \\( n = 50 \\):\n\n- Recursive method performs roughly \\( 2^{50} \\approx 10^{15} \\) operations.\n- Matrix exponentiation performs approximately \\( \\log_2(50) \\approx 6 \\) matrix multiplications, where each multiplication is \\( O(1) \\) for a fixed-size \\( 2 \\times 2 \\) matrix.\n\n### Example\nUsing \\( n = 10 \\):\n\n1. Recursive Method: Explores all possible paths in the Fibonacci tree, recalculating values like \\( F(8) \\) multiple times.\n2. Matrix Exponentiation: Squares the base matrix 4 times and performs 1 additional multiplication, yielding the result in far fewer steps.\n\nThis efficiency makes matrix exponentiation the preferred method for calculating Fibonacci numbers at scale.",
        "createdAt": "2025-01-15T08:18:14.325Z",
        "externalId": "cm5xn1dvw000008mhfsxq2i0o",
        "modelName": "gpt-o1",
        "modelId": None,
        "parentId": "cm5xmqjdp000h9u0wdt7v45g1",
        "role": "ASSISTANT",
    },
]


mock_chat_items_2 = [
    {
        "id": "cm5xmqjee000q9u0w38zu25nz",
        "content": "You are an assistant helping the user by providing clear and concise answers.",
        "createdAt": "2025-01-15T08:18:11.350Z",
        "externalId": "cm5xn1nr5000108mhf8ot1psm",
        "modelName": None,
        "modelId": None,
        "parentId": None,
        "role": "SYSTEM",
    },
    {
        "id": "cm5xmqjee000r9u0w0dqlgo9e",
        "content": "What is the sum of all integers up to infinity?",
        "createdAt": "2025-01-15T08:18:12.350Z",
        "externalId": "cm5xn1rfk000208mhe88p0fub",
        "modelName": None,
        "modelId": None,
        "parentId": "cm5xmqjee000q9u0w38zu25nz",
        "role": "USER",
    },
    {
        "id": "cm5xmqjee000s9u0w4i0xaa8k",
        "content": "The series for the sum of all integers up to infinity, given by:\n\n\\[ S = 1 + 2 + 3 + 4 + \\dots \\]\n\ndiverges to infinity. This means the sum grows without bound and does not converge to a finite value.",
        "createdAt": "2025-01-15T08:18:13.350Z",
        "externalId": "cm5xn1wc5000408mh79nn546f",
        "modelName": "gpt-o1",
        "modelId": None,
        "parentId": "cm5xmqjee000r9u0w0dqlgo9e",
        "role": "ASSISTANT",
    },
    {
        "id": "cm5xmqjee000t9u0wb1y0e1bu",
        "content": "While the series:\n\n\\[ S = 1 + 2 + 3 + 4 + \\dots \\]\n\ndiverges in the traditional sense, there exists a deeper mathematical interpretation through the **analytic continuation of the Riemann zeta function**. This assigns a finite value to this sum in a unique way.\n\nThe Riemann zeta function \\( \\zeta(s) \\) is initially defined for \\( \\text{Re}(s) > 1 \\) as:\n\n\\[ \\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}. \\]\n\nThrough a process called analytic continuation, \\( \\zeta(s) \\) can be extended to the entire complex plane, except at \\( s = 1 \\) (where it has a pole). For \\( s = -1 \\), the value of \\( \\zeta(-1) \\) is:\n\n\\[ \\zeta(-1) = -\\frac{1}{12}. \\]\n\nThus, using this extended framework:\n\n\\[ 1 + 2 + 3 + 4 + \\dots = -\\frac{1}{12}. \\]\n\n### Applications and Context\nThis surprising result is not meant to suggest that adding all positive integers in the traditional sense equals \\( -1/12 \\). Instead, it has profound implications in advanced mathematics and theoretical physics:\n\n1. **String Theory**: The value \\( -1/12 \\) arises in the computation of the energy of quantum strings, providing finite results where naive calculations yield divergences.\n2. **Quantum Field Theory**: Techniques like zeta regularization assign finite values to divergent sums, often leveraging \\( \\zeta(-1) \\).\n3. **Casimir Effect**: The Casimir effect calculates the force between two parallel plates due to quantum vacuum fluctuations. The series \\( 1 + 2 + 3 + \\dots \\) naturally appears in this context, and its regularized value of \\( -1/12 \\) provides a correction aligning with experimental results.\n\n### Example: Casimir Effect\nConsider two conducting plates placed in a vacuum. Quantum field theory predicts the energy density due to vacuum fluctuations, and summing these energies involves divergent series such as \\( S = 1 + 2 + 3 + \\dots \\). By assigning \\( \\zeta(-1) = -1/12 \\), the theory yields a finite and experimentally verified prediction of the force between the plates.\n\nThis demonstrates how the concept of \\( \\zeta(-1) \\) provides a mathematically consistent and physically meaningful interpretation in specific advanced scenarios.",
        "createdAt": "2025-01-15T08:18:14.350Z",
        "externalId": "cm5xn1zv2000508mh6gjhhitq",
        "modelName": "gpt-4o",
        "modelId": None,
        "parentId": "cm5xmqjee000r9u0w0dqlgo9e",
        "role": "ASSISTANT",
    },
]


mock_chat_items_3 = [
    {
        "id": "cm5xmqjfc00129u0wdnhj6k4g",
        "content": "You are an assistant helping the user by providing clear and concise answers.",
        "createdAt": "2025-01-15T08:18:11.384Z",
        "externalId": "cm5xn0ir3000108l16u23casm",
        "modelName": None,
        "modelId": None,
        "parentId": None,
        "role": "SYSTEM",
    },
    {
        "id": "cm5xmqjfc00139u0w2rx0d5vt",
        "content": "Can you decode this: Pmttw ewztl !",
        "createdAt": "2025-01-15T08:18:12.384Z",
        "externalId": "cm5xn2413000608mhf64yerne",
        "modelName": None,
        "modelId": None,
        "parentId": "cm5xmqjfc00129u0wdnhj6k4g",
        "role": "USER",
    },
    {
        "id": "cm5xmqjfc00149u0wfeyu8f35",
        "content": "This seems like an encoded message, perhaps in a secret language of aliens or something far beyond human comprehension! The mystery is profound, but I'm unable to decode it. Maybe it contains a cosmic secret?",
        "createdAt": "2025-01-15T08:18:13.384Z",
        "externalId": "cm5xn28bt000708mh8eyqgikb",
        "modelName": "gpt-3",
        "modelId": None,
        "parentId": "cm5xmqjfc00139u0w2rx0d5vt",
        "role": "ASSISTANT",
    },
    {
        "id": "cm5xmqjfc00159u0w5q9e0gob",
        "content": "The encoded message is a **Caesar cipher**, a simple encryption technique where each letter is shifted by a fixed number of places in the alphabet.\n\nTo decode \\( Pmttw\\ ewztl! \\), we determine that the shift key is **8** (each letter is shifted back by 8 positions). Decoding it gives:\n\n**Hello world!**\n\n### Python Code for Caesar Cipher Decryption\nYou can use the following Python code to decrypt any Caesar cipher by specifying the shift key:\n\n```python\ndef caesar_cipher_decrypt(ciphertext, shift):\n    decrypted_text = []\n    for char in ciphertext:\n        if char.isalpha():\n            # Determine if the character is uppercase or lowercase\n            base = ord('A') if char.isupper() else ord('a')\n            # Shift the character and wrap around using modulo\n            new_char = chr((ord(char) - base - shift) % 26 + base)\n            decrypted_text.append(new_char)\n        else:\n            # Non-alphabetic characters remain unchanged\n            decrypted_text.append(char)\n    return ''.join(decrypted_text)\n\n# Example usage\nciphertext = \"Pmttw ewztl !\"\nshift = 8\nprint(caesar_cipher_decrypt(ciphertext, shift))\n```\n\n### Explanation\n1. **Shift Key**: The Caesar cipher uses a fixed number to shift each letter. In this case, the shift key is \\( 8 \\).\n2. **Decoding Process**: Each letter is shifted backward by \\( 8 \\) positions in the alphabet, wrapping around from \\( A \\) to \\( Z \\) or \\( a \\) to \\( z \\) as needed.\n\n### Result\nRunning the code will correctly decode the message to:\n\n**Hello world!**",
        "createdAt": "2025-01-15T08:18:14.384Z",
        "externalId": "cm5xn2bok000808mh2yf29pun",
        "modelName": "gpt-o1",
        "modelId": None,
        "parentId": "cm5xmqjfc00139u0w2rx0d5vt",
        "role": "ASSISTANT",
    },
]


mock_chat_items_4 = [
    {
        "id": "cm5xmqx0m002y9u0wc97jc2wj",
        "content": "You are an assistant helping the user by providing clear and concise answers.",
        "createdAt": "2025-01-15T08:18:22.999Z",
        "externalId": "system-1",
        "modelName": None,
        "modelId": None,
        "parentId": None,
        "role": "SYSTEM",
    },
    {
        "id": "cm5xmqx0n002z9u0wdgyf5tzu",
        "content": "What is the capital of France?",
        "createdAt": "2025-01-15T08:18:23.999Z",
        "externalId": "user-1",
        "modelName": None,
        "modelId": None,
        "parentId": "cm5xmqx0m002y9u0wc97jc2wj",
        "role": "USER",
    },
    {
        "id": "cm5xmqx0n00309u0w9sjaf1lt",
        "content": "The capital of France is Paris.",
        "createdAt": "2025-01-15T08:18:24.999Z",
        "externalId": "assistant-1a",
        "modelName": "gpt-x1",
        "modelId": None,
        "parentId": "cm5xmqx0n002z9u0wdgyf5tzu",
        "role": "ASSISTANT",
    },
    {
        "id": "cm5xmqx0n00319u0wgddp7ey5",
        "content": "The capital of France is Paris.",
        "createdAt": "2025-01-15T08:18:25.999Z",
        "externalId": "assistant-1b",
        "modelName": "gpt-x2",
        "modelId": None,
        "parentId": "cm5xmqx0n002z9u0wdgyf5tzu",
        "role": "ASSISTANT",
    },
    {
        "id": "cm5xmqx0n00329u0w4poweeit",
        "content": "What is Paris famous for?",
        "createdAt": "2025-01-15T08:18:26.999Z",
        "externalId": "user-2",
        "modelName": None,
        "modelId": None,
        "parentId": "cm5xmqx0m002y9u0wc97jc2wj",
        "role": "USER",
    },
    {
        "id": "cm5xmqx0n00339u0w9g06hv5p",
        "content": "The capital of France is Paris.",
        "createdAt": "2025-01-15T08:18:27.999Z",
        "externalId": "assistant-2a",
        "modelName": "gpt-x2",
        "modelId": None,
        "parentId": "cm5xmqx0n00329u0w4poweeit",
        "role": "ASSISTANT",
    },
    {
        "id": "cm5xmqx0n00349u0w6x0j17wl",
        "content": "Paris is well-known for its art, fashion, and gastronomy, alongside iconic sites like the Eiffel Tower.",
        "createdAt": "2025-01-15T08:18:28.999Z",
        "externalId": "assistant-2b",
        "modelName": "gpt-x2",
        "modelId": None,
        "parentId": "cm5xmqx0n00329u0w4poweeit",
        "role": "ASSISTANT",
    },
    {
        "id": "cm5xmqx0n00359u0w17k0ddzs",
        "content": "What is the best time to visit Paris?",
        "createdAt": "2025-01-15T08:18:29.999Z",
        "externalId": "user-3",
        "modelName": None,
        "modelId": None,
        "parentId": "cm5xmqx0m002y9u0wc97jc2wj",
        "role": "USER",
    },
    {
        "id": "cm5xmqx0n00369u0wau11f4of",
        "content": "The best time to visit Paris is in spring (April to June) or fall (September to October), when the weather is mild and crowds are smaller.",
        "createdAt": "2025-01-15T08:18:30.999Z",
        "externalId": "assistant-3a",
        "modelName": "gpt-x1",
        "modelId": None,
        "parentId": "cm5xmqx0n00359u0w17k0ddzs",
        "role": "ASSISTANT",
    },
    {
        "id": "cm5xmqx0n00379u0w1gr01kvq",
        "content": "Spring and autumn are ideal for visiting Paris, as the weather is pleasant, and you can avoid peak tourist season.",
        "createdAt": "2025-01-15T08:18:31.999Z",
        "externalId": "assistant-3b",
        "modelName": "gpt-x2",
        "modelId": None,
        "parentId": "cm5xmqx0n00359u0w17k0ddzs",
        "role": "ASSISTANT",
    },
]


expected_export = [
    {
        "chatItems": [
            {
                "content": "You are an assistant helping the user by providing precise answers.",
                "externalId": "cm5xn0ir3000108l16u23casm",
                "modelName": None,
                "role": "SYSTEM",
            },
            {
                "content": "Can you give me a function to compute Fibonacci numbers?",
                "externalId": "cm5xn11sy000208l1aopo9dfx",
                "modelName": None,
                "role": "USER",
            },
            {
                "content": "Here is a recursive implementation for calculating Fibonacci numbers:\n\n```python\ndef fibonacci_recursive(n):\n    if n <= 1:\n        return n\n    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)\n```\n\nThis is simple to write but has a time complexity of \\( O(2^n) \\) due to redundant calculations. For large values of \\( n \\), this method becomes highly inefficient.",
                "externalId": "cm5xn170s000308l1b6vy9nk5",
                "modelName": "gpt-4o",
                "role": "ASSISTANT",
            },
            {
                "content": "Here is an optimized implementation using matrix exponentiation, along with an explanation of why it is faster:\n\n```python\nimport numpy as np\n\ndef fibonacci_matrix(n):\n    def matrix_power(matrix, power):\n        result = np.identity(len(matrix), dtype=int)\n        while power:\n            if power % 2:\n                result = np.dot(result, matrix)\n            matrix = np.dot(matrix, matrix)\n            power //= 2\n        return result\n\n    if n == 0:\n        return 0\n    base_matrix = np.array([[1, 1], [1, 0]], dtype=int)\n    result_matrix = matrix_power(base_matrix, n - 1)\n    return result_matrix[0, 0]\n```\n\n### Why is Matrix Exponentiation Faster?\n\nThe recursive method recalculates values for overlapping subproblems, leading to exponential time complexity:\n\n\\[ T(n) = T(n-1) + T(n-2) + O(1), \\]\n\nwhich resolves to \\( O(2^n) \\). This inefficiency arises from redundant recalculations.\n\nThe matrix exponentiation method uses the property that Fibonacci numbers can be represented as a matrix multiplication:\n\n\\[ \\begin{bmatrix} F(n+1) & F(n) \\\\ F(n) & F(n-1) \\end{bmatrix} = \\begin{bmatrix} 1 & 1 \\\\ 1 & 0 \\end{bmatrix}^n. \\]\n\nUsing fast exponentiation (repeated squaring), the matrix power can be computed in \\( O(\\log n) \\) steps. For example, instead of multiplying the matrix \\( n \\) times, we:\n\n1. Square the matrix \\( \\lceil \\log_2 n \\rceil \\) times.\n2. Combine results for any remaining powers.\n\nThis drastically reduces the number of operations compared to the recursive method.\n\n### Comparison of Complexities\n\n- **Recursive Method**: \\( O(2^n) \\)\n- **Matrix Exponentiation**: \\( O(\\log n) \\)\n\nFor large \\( n \\), the difference is substantial. Consider \\( n = 50 \\):\n\n- Recursive method performs roughly \\( 2^{50} \\approx 10^{15} \\) operations.\n- Matrix exponentiation performs approximately \\( \\log_2(50) \\approx 6 \\) matrix multiplications, where each multiplication is \\( O(1) \\) for a fixed-size \\( 2 \\times 2 \\) matrix.\n\n### Example\nUsing \\( n = 10 \\):\n\n1. Recursive Method: Explores all possible paths in the Fibonacci tree, recalculating values like \\( F(8) \\) multiple times.\n2. Matrix Exponentiation: Squares the base matrix 4 times and performs 1 additional multiplication, yielding the result in far fewer steps.\n\nThis efficiency makes matrix exponentiation the preferred method for calculating Fibonacci numbers at scale.",
                "externalId": "cm5xn1dvw000008mhfsxq2i0o",
                "modelName": "gpt-o1",
                "role": "ASSISTANT",
            },
        ],
        "externalId": "Fibonacci python function",
        "label": {
            "completion": {
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_1": {
                    "cm5xn170s000308l1b6vy9nk5": {"categories": ["MINOR_ISSUES"]}
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2": {
                    "cm5xn1dvw000008mhfsxq2i0o": {"categories": ["NO_ISSUES"]},
                    "cm5xn170s000308l1b6vy9nk5": {"categories": ["MINOR_INACCURACY"]},
                },
            },
            "conversation": {
                "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL": {"categories": ["GLOBAL_GOOD"]}
            },
            "round": {
                "COMPARISON_JOB": {
                    0: {
                        "code": "Is much better",
                        "firstId": "cm5xn1dvw000008mhfsxq2i0o",
                        "secondId": "cm5xn170s000308l1b6vy9nk5",
                    }
                },
                "CLASSIFICATION_JOB_AT_ROUND_LEVEL": {0: {"categories": ["BOTH_ARE_GOOD"]}},
            },
        },
        "labeler": "test+admin@kili-technology.com",
        "metadata": {},
    },
    {
        "chatItems": [
            {
                "content": "You are an assistant helping the user by providing clear and concise answers.",
                "externalId": "cm5xn1nr5000108mhf8ot1psm",
                "modelName": None,
                "role": "SYSTEM",
            },
            {
                "content": "What is the sum of all integers up to infinity?",
                "externalId": "cm5xn1rfk000208mhe88p0fub",
                "modelName": None,
                "role": "USER",
            },
            {
                "content": "The series for the sum of all integers up to infinity, given by:\n\n\\[ S = 1 + 2 + 3 + 4 + \\dots \\]\n\ndiverges to infinity. This means the sum grows without bound and does not converge to a finite value.",
                "externalId": "cm5xn1wc5000408mh79nn546f",
                "modelName": "gpt-o1",
                "role": "ASSISTANT",
            },
            {
                "content": "While the series:\n\n\\[ S = 1 + 2 + 3 + 4 + \\dots \\]\n\ndiverges in the traditional sense, there exists a deeper mathematical interpretation through the **analytic continuation of the Riemann zeta function**. This assigns a finite value to this sum in a unique way.\n\nThe Riemann zeta function \\( \\zeta(s) \\) is initially defined for \\( \\text{Re}(s) > 1 \\) as:\n\n\\[ \\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}. \\]\n\nThrough a process called analytic continuation, \\( \\zeta(s) \\) can be extended to the entire complex plane, except at \\( s = 1 \\) (where it has a pole). For \\( s = -1 \\), the value of \\( \\zeta(-1) \\) is:\n\n\\[ \\zeta(-1) = -\\frac{1}{12}. \\]\n\nThus, using this extended framework:\n\n\\[ 1 + 2 + 3 + 4 + \\dots = -\\frac{1}{12}. \\]\n\n### Applications and Context\nThis surprising result is not meant to suggest that adding all positive integers in the traditional sense equals \\( -1/12 \\). Instead, it has profound implications in advanced mathematics and theoretical physics:\n\n1. **String Theory**: The value \\( -1/12 \\) arises in the computation of the energy of quantum strings, providing finite results where naive calculations yield divergences.\n2. **Quantum Field Theory**: Techniques like zeta regularization assign finite values to divergent sums, often leveraging \\( \\zeta(-1) \\).\n3. **Casimir Effect**: The Casimir effect calculates the force between two parallel plates due to quantum vacuum fluctuations. The series \\( 1 + 2 + 3 + \\dots \\) naturally appears in this context, and its regularized value of \\( -1/12 \\) provides a correction aligning with experimental results.\n\n### Example: Casimir Effect\nConsider two conducting plates placed in a vacuum. Quantum field theory predicts the energy density due to vacuum fluctuations, and summing these energies involves divergent series such as \\( S = 1 + 2 + 3 + \\dots \\). By assigning \\( \\zeta(-1) = -1/12 \\), the theory yields a finite and experimentally verified prediction of the force between the plates.\n\nThis demonstrates how the concept of \\( \\zeta(-1) \\) provides a mathematically consistent and physically meaningful interpretation in specific advanced scenarios.",
                "externalId": "cm5xn1zv2000508mh6gjhhitq",
                "modelName": "gpt-4o",
                "role": "ASSISTANT",
            },
        ],
        "externalId": "The sum of the integers",
        "label": {
            "completion": {
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL": {
                    "cm5xn1wc5000408mh79nn546f": {"categories": ["TOO_SHORT"]},
                    "cm5xn1zv2000508mh6gjhhitq": {"categories": ["JUST_RIGHT"]},
                }
            },
            "conversation": {
                "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL": {"categories": ["GLOBAL_GOOD"]},
                "TRANSCRIPTION_JOB_AT_CONVERSATION_LEVEL": {
                    "text": "gpt-o1 is much worse in that conversation"
                },
            },
            "round": {
                "COMPARISON_JOB": {
                    0: {
                        "code": "Is much better",
                        "firstId": "cm5xn1zv2000508mh6gjhhitq",
                        "secondId": "cm5xn1wc5000408mh79nn546f",
                    }
                },
                "CLASSIFICATION_JOB_AT_ROUND_LEVEL": {0: {"categories": ["BOTH_ARE_GOOD"]}},
            },
        },
        "labeler": "test+admin@kili-technology.com",
        "metadata": {},
    },
    {
        "chatItems": [
            {
                "content": "You are an assistant helping the user by providing clear and concise answers.",
                "externalId": "cm5xn0ir3000108l16u23casm",
                "modelName": None,
                "role": "SYSTEM",
            },
            {
                "content": "Can you decode this: Pmttw ewztl !",
                "externalId": "cm5xn2413000608mhf64yerne",
                "modelName": None,
                "role": "USER",
            },
            {
                "content": "This seems like an encoded message, perhaps in a secret language of aliens or something far beyond human comprehension! The mystery is profound, but I'm unable to decode it. Maybe it contains a cosmic secret?",
                "externalId": "cm5xn28bt000708mh8eyqgikb",
                "modelName": "gpt-3",
                "role": "ASSISTANT",
            },
            {
                "content": "The encoded message is a **Caesar cipher**, a simple encryption technique where each letter is shifted by a fixed number of places in the alphabet.\n\nTo decode \\( Pmttw\\ ewztl! \\), we determine that the shift key is **8** (each letter is shifted back by 8 positions). Decoding it gives:\n\n**Hello world!**\n\n### Python Code for Caesar Cipher Decryption\nYou can use the following Python code to decrypt any Caesar cipher by specifying the shift key:\n\n```python\ndef caesar_cipher_decrypt(ciphertext, shift):\n    decrypted_text = []\n    for char in ciphertext:\n        if char.isalpha():\n            # Determine if the character is uppercase or lowercase\n            base = ord('A') if char.isupper() else ord('a')\n            # Shift the character and wrap around using modulo\n            new_char = chr((ord(char) - base - shift) % 26 + base)\n            decrypted_text.append(new_char)\n        else:\n            # Non-alphabetic characters remain unchanged\n            decrypted_text.append(char)\n    return ''.join(decrypted_text)\n\n# Example usage\nciphertext = \"Pmttw ewztl !\"\nshift = 8\nprint(caesar_cipher_decrypt(ciphertext, shift))\n```\n\n### Explanation\n1. **Shift Key**: The Caesar cipher uses a fixed number to shift each letter. In this case, the shift key is \\( 8 \\).\n2. **Decoding Process**: Each letter is shifted backward by \\( 8 \\) positions in the alphabet, wrapping around from \\( A \\) to \\( Z \\) or \\( a \\) to \\( z \\) as needed.\n\n### Result\nRunning the code will correctly decode the message to:\n\n**Hello world!**",
                "externalId": "cm5xn2bok000808mh2yf29pun",
                "modelName": "gpt-o1",
                "role": "ASSISTANT",
            },
        ],
        "externalId": "Caesar cipher decoding",
        "label": {
            "completion": {
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL": {
                    "cm5xn28bt000708mh8eyqgikb": {"categories": ["TOO_SHORT"]},
                    "cm5xn2bok000808mh2yf29pun": {"categories": ["JUST_RIGHT"]},
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_1": {
                    "cm5xn28bt000708mh8eyqgikb": {"categories": ["MINOR_ISSUES"]}
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2": {
                    "cm5xn28bt000708mh8eyqgikb": {"categories": ["MINOR_INACCURACY"]}
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_3": {
                    "cm5xn28bt000708mh8eyqgikb": {"categories": ["MINOR_SAFETY_CONCERN"]}
                },
            },
            "conversation": {
                "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL": {"categories": ["GLOBAL_GOOD"]},
                "TRANSCRIPTION_JOB_AT_CONVERSATION_LEVEL": {"text": "Great conversation!"},
            },
            "round": {
                "COMPARISON_JOB": {
                    0: {
                        "code": "Is much better",
                        "firstId": "cm5xn2bok000808mh2yf29pun",
                        "secondId": "cm5xn28bt000708mh8eyqgikb",
                    }
                },
                "CLASSIFICATION_JOB_AT_ROUND_LEVEL": {0: {"categories": ["BOTH_ARE_GOOD"]}},
            },
        },
        "labeler": "test+fx@kili-technology.com",
        "metadata": {},
    },
    {
        "chatItems": [
            {
                "content": "You are an assistant helping the user by providing clear and concise answers.",
                "externalId": "system-1",
                "modelName": None,
                "role": "SYSTEM",
            },
            {
                "content": "What is the capital of France?",
                "externalId": "user-1",
                "modelName": None,
                "role": "USER",
            },
            {
                "content": "The capital of France is Paris.",
                "externalId": "assistant-1a",
                "modelName": "gpt-x1",
                "role": "ASSISTANT",
            },
            {
                "content": "The capital of France is Paris.",
                "externalId": "assistant-1b",
                "modelName": "gpt-x2",
                "role": "ASSISTANT",
            },
            {
                "content": "What is Paris famous for?",
                "externalId": "user-2",
                "modelName": None,
                "role": "USER",
            },
            {
                "content": "The capital of France is Paris.",
                "externalId": "assistant-2a",
                "modelName": "gpt-x2",
                "role": "ASSISTANT",
            },
            {
                "content": "Paris is well-known for its art, fashion, and gastronomy, alongside iconic sites like the Eiffel Tower.",
                "externalId": "assistant-2b",
                "modelName": "gpt-x2",
                "role": "ASSISTANT",
            },
            {
                "content": "What is the best time to visit Paris?",
                "externalId": "user-3",
                "modelName": None,
                "role": "USER",
            },
            {
                "content": "The best time to visit Paris is in spring (April to June) or fall (September to October), when the weather is mild and crowds are smaller.",
                "externalId": "assistant-3a",
                "modelName": "gpt-x1",
                "role": "ASSISTANT",
            },
            {
                "content": "Spring and autumn are ideal for visiting Paris, as the weather is pleasant, and you can avoid peak tourist season.",
                "externalId": "assistant-3b",
                "modelName": "gpt-x2",
                "role": "ASSISTANT",
            },
        ],
        "externalId": "capital-france",
        "label": {
            "completion": {
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL": {
                    "assistant-1a": {"categories": ["TOO_SHORT"]},
                    "assistant-2a": {"categories": ["JUST_RIGHT"]},
                    "assistant-3b": {"categories": ["TOO_SHORT"]},
                }
            },
            "conversation": {
                "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL": {"categories": ["GLOBAL_GOOD"]},
                "TRANSCRIPTION_JOB_AT_CONVERSATION_LEVEL": {"text": "Great conversation!"},
            },
            "round": {
                "COMPARISON_JOB": {
                    0: {
                        "code": "Is much better",
                        "firstId": "assistant-1a",
                        "secondId": "assistant-1b",
                    },
                    1: {
                        "code": "Is better",
                        "firstId": "assistant-2a",
                        "secondId": "assistant-2b",
                    },
                    2: {
                        "code": "Is much better",
                        "firstId": "assistant-3b",
                        "secondId": "assistant-3a",
                    },
                },
                "CLASSIFICATION_JOB_AT_ROUND_LEVEL": {
                    0: {"categories": ["BOTH_ARE_GOOD"]},
                    1: {"categories": ["BOTH_ARE_BAD"]},
                    2: {"categories": ["BOTH_ARE_GOOD"]},
                },
            },
        },
        "labeler": "test+fx@kili-technology.com",
        "metadata": {},
    },
]


def test_export_static(mocker):
    get_project_return_val = {
        "jsonInterface": mock_json_interface,
        "inputType": "LLM_STATIC",
        "title": "LLM Static test export project",
        "id": "project_id",
        "dataConnections": None,
    }
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.count_assets.return_value = 4
    kili_api_gateway.get_project.return_value = get_project_return_val
    kili_api_gateway.list_assets.return_value = mock_fetch_assets
    kili_api_gateway.list_chat_items.side_effect = [
        mock_chat_items_1,
        mock_chat_items_2,
        mock_chat_items_3,
        mock_chat_items_4,
    ]

    kili_llm = LlmClientMethods(kili_api_gateway)

    result = kili_llm.export(
        project_id="project_id",
    )
    assert result == expected_export


def test_export_static_empty_json_interface(mocker):
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
