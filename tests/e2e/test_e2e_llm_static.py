import json
from typing import List, cast

import pytest
import requests

from kili.client import Kili
from kili.domain.llm import Conversation

PROJECT_TITLE = "[E2E Test]: LLM Static"
PROJECT_DESCRIPTION = "End-to-End Test LLM Static with conversations import & export"

INTERFACE = {
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

CONVERSATIONS = [
    {
        "externalId": "Fibonacci python function",
        "chatItems": [
            {
                "externalId": "cm5whopsx000f0cmj1e7l7hp6",
                "role": "SYSTEM",
                "content": "You are an assistant helping the user by providing precise answers.",
            },
            {
                "externalId": "cm5whorxn000g0cmj1hvg96r2",
                "role": "USER",
                "content": "Can you give me a function to compute Fibonacci numbers?",
            },
            {
                "externalId": "cm5whover000h0cmjg5t4b9rr",
                "role": "ASSISTANT",
                "content": "Here is a recursive implementation for calculating Fibonacci numbers:\n\n```python\ndef fibonacci_recursive(n):\n    if n <= 1:\n        return n\n    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)\n```\n\nThis is simple to write but has a time complexity of \\( O(2^n) \\) due to redundant calculations. For large values of \\( n \\), this method becomes highly inefficient.",
                "modelName": "gpt-4o",
            },
            {
                "externalId": "cm5whoxbp000i0cmj45w8842l",
                "role": "ASSISTANT",
                "content": "Here is an optimized implementation using matrix exponentiation, along with an explanation of why it is faster:\n\n```python\nimport numpy as np\n\ndef fibonacci_matrix(n):\n    def matrix_power(matrix, power):\n        result = np.identity(len(matrix), dtype=int)\n        while power:\n            if power % 2:\n                result = np.dot(result, matrix)\n            matrix = np.dot(matrix, matrix)\n            power //= 2\n        return result\n\n    if n == 0:\n        return 0\n    base_matrix = np.array([[1, 1], [1, 0]], dtype=int)\n    result_matrix = matrix_power(base_matrix, n - 1)\n    return result_matrix[0, 0]\n```\n\n### Why is Matrix Exponentiation Faster?\n\nThe recursive method recalculates values for overlapping subproblems, leading to exponential time complexity:\n\n\\[ T(n) = T(n-1) + T(n-2) + O(1), \\]\n\nwhich resolves to \\( O(2^n) \\). This inefficiency arises from redundant recalculations.\n\nThe matrix exponentiation method uses the property that Fibonacci numbers can be represented as a matrix multiplication:\n\n\\[ \\begin{bmatrix} F(n+1) & F(n) \\\\ F(n) & F(n-1) \\end{bmatrix} = \\begin{bmatrix} 1 & 1 \\\\ 1 & 0 \\end{bmatrix}^n. \\]\n\nUsing fast exponentiation (repeated squaring), the matrix power can be computed in \\( O(\\log n) \\) steps. For example, instead of multiplying the matrix \\( n \\) times, we:\n\n1. Square the matrix \\( \\lceil \\log_2 n \\rceil \\) times.\n2. Combine results for any remaining powers.\n\nThis drastically reduces the number of operations compared to the recursive method.\n\n### Comparison of Complexities\n\n- **Recursive Method**: \\( O(2^n) \\)\n- **Matrix Exponentiation**: \\( O(\\log n) \\)\n\nFor large \\( n \\), the difference is substantial. Consider \\( n = 50 \\):\n\n- Recursive method performs roughly \\( 2^{50} \\approx 10^{15} \\) operations.\n- Matrix exponentiation performs approximately \\( \\log_2(50) \\approx 6 \\) matrix multiplications, where each multiplication is \\( O(1) \\) for a fixed-size \\( 2 \\times 2 \\) matrix.\n\n### Example\nUsing \\( n = 10 \\):\n\n1. Recursive Method: Explores all possible paths in the Fibonacci tree, recalculating values like \\( F(8) \\) multiple times.\n2. Matrix Exponentiation: Squares the base matrix 4 times and performs 1 additional multiplication, yielding the result in far fewer steps.\n\nThis efficiency makes matrix exponentiation the preferred method for calculating Fibonacci numbers at scale.",
                "modelName": "gpt-o1",
            },
        ],
        "metadata": {},
    },
    {
        "externalId": "The sum of the integers",
        "chatItems": [
            {
                "externalId": "cm5whp184000j0cmj5mwz7mvw",
                "role": "SYSTEM",
                "content": "You are an assistant helping the user by providing clear and concise answers.",
            },
            {
                "externalId": "cm5whp4fc000k0cmj76h73qmf",
                "role": "USER",
                "content": "What is the sum of all integers up to infinity?",
            },
            {
                "externalId": "cm5whp7cf000l0cmj6gwq1tve",
                "role": "ASSISTANT",
                "content": "The series for the sum of all integers up to infinity, given by:\n\n\\[ S = 1 + 2 + 3 + 4 + \\dots \\]\n\ndiverges to infinity. This means the sum grows without bound and does not converge to a finite value.",
                "modelName": "gpt-o1",
            },
            {
                "externalId": "cm5whpd1f000m0cmj4midfmbu",
                "role": "ASSISTANT",
                "content": "While the series:\n\n\\[ S = 1 + 2 + 3 + 4 + \\dots \\]\n\ndiverges in the traditional sense, there exists a deeper mathematical interpretation through the **analytic continuation of the Riemann zeta function**. This assigns a finite value to this sum in a unique way.\n\nThe Riemann zeta function \\( \\zeta(s) \\) is initially defined for \\( \\text{Re}(s) > 1 \\) as:\n\n\\[ \\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}. \\]\n\nThrough a process called analytic continuation, \\( \\zeta(s) \\) can be extended to the entire complex plane, except at \\( s = 1 \\) (where it has a pole). For \\( s = -1 \\), the value of \\( \\zeta(-1) \\) is:\n\n\\[ \\zeta(-1) = -\\frac{1}{12}. \\]\n\nThus, using this extended framework:\n\n\\[ 1 + 2 + 3 + 4 + \\dots = -\\frac{1}{12}. \\]\n\n### Applications and Context\nThis surprising result is not meant to suggest that adding all positive integers in the traditional sense equals \\( -1/12 \\). Instead, it has profound implications in advanced mathematics and theoretical physics:\n\n1. **String Theory**: The value \\( -1/12 \\) arises in the computation of the energy of quantum strings, providing finite results where naive calculations yield divergences.\n2. **Quantum Field Theory**: Techniques like zeta regularization assign finite values to divergent sums, often leveraging \\( \\zeta(-1) \\).\n3. **Casimir Effect**: The Casimir effect calculates the force between two parallel plates due to quantum vacuum fluctuations. The series \\( 1 + 2 + 3 + \\dots \\) naturally appears in this context, and its regularized value of \\( -1/12 \\) provides a correction aligning with experimental results.\n\n### Example: Casimir Effect\nConsider two conducting plates placed in a vacuum. Quantum field theory predicts the energy density due to vacuum fluctuations, and summing these energies involves divergent series such as \\( S = 1 + 2 + 3 + \\dots \\). By assigning \\( \\zeta(-1) = -1/12 \\), the theory yields a finite and experimentally verified prediction of the force between the plates.\n\nThis demonstrates how the concept of \\( \\zeta(-1) \\) provides a mathematically consistent and physically meaningful interpretation in specific advanced scenarios.",
                "modelName": "gpt-4o",
            },
        ],
        "metadata": {},
    },
    {
        "externalId": "Caesar cipher decoding",
        "chatItems": [
            {
                "externalId": "cm5whpfzr000n0cmjb2nu5xvb",
                "role": "SYSTEM",
                "content": "You are an assistant helping the user by providing clear and concise answers.",
            },
            {
                "externalId": "cm5whpjns000o0cmjbbru1pmw",
                "role": "USER",
                "content": "Can you decode this: Pmttw ewztl !",
            },
            {
                "externalId": "cm5whpnzf000p0cmj2fojgut6",
                "role": "ASSISTANT",
                "content": "This seems like an encoded message, perhaps in a secret language of aliens or something far beyond human comprehension! The mystery is profound, but I'm unable to decode it. Maybe it contains a cosmic secret?",
                "modelName": "gpt-3",
            },
            {
                "externalId": "cm5whprnc000q0cmjg3b0bth7",
                "role": "ASSISTANT",
                "content": "The encoded message is a **Caesar cipher**, a simple encryption technique where each letter is shifted by a fixed number of places in the alphabet.\n\nTo decode \\( Pmttw\\ ewztl! \\), we determine that the shift key is **8** (each letter is shifted back by 8 positions). Decoding it gives:\n\n**Hello world!**\n\n### Python Code for Caesar Cipher Decryption\nYou can use the following Python code to decrypt any Caesar cipher by specifying the shift key:\n\n```python\ndef caesar_cipher_decrypt(ciphertext, shift):\n    decrypted_text = []\n    for char in ciphertext:\n        if char.isalpha():\n            # Determine if the character is uppercase or lowercase\n            base = ord('A') if char.isupper() else ord('a')\n            # Shift the character and wrap around using modulo\n            new_char = chr((ord(char) - base - shift) % 26 + base)\n            decrypted_text.append(new_char)\n        else:\n            # Non-alphabetic characters remain unchanged\n            decrypted_text.append(char)\n    return ''.join(decrypted_text)\n\n# Example usage\nciphertext = \"Pmttw ewztl !\"\nshift = 8\nprint(caesar_cipher_decrypt(ciphertext, shift))\n```\n\n### Explanation\n1. **Shift Key**: The Caesar cipher uses a fixed number to shift each letter. In this case, the shift key is \\( 8 \\).\n2. **Decoding Process**: Each letter is shifted backward by \\( 8 \\) positions in the alphabet, wrapping around from \\( A \\) to \\( Z \\) or \\( a \\) to \\( z \\) as needed.\n\n### Result\nRunning the code will correctly decode the message to:\n\n**Hello world!**",
                "modelName": "gpt-o1",
            },
        ],
        "label": {
            "completion": {
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL": {
                    "cm5whpnzf000p0cmj2fojgut6": {"categories": ["TOO_SHORT"]},
                    "cm5whprnc000q0cmjg3b0bth7": {"categories": ["JUST_RIGHT"]},
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_1": {
                    "cm5whpnzf000p0cmj2fojgut6": {"categories": ["MINOR_ISSUES"]}
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_2": {
                    "cm5whpnzf000p0cmj2fojgut6": {"categories": ["MINOR_INACCURACY"]}
                },
                "CLASSIFICATION_JOB_AT_COMPLETION_LEVEL_3": {
                    "cm5whpnzf000p0cmj2fojgut6": {"categories": ["MINOR_SAFETY_CONCERN"]}
                },
            },
            "round": {
                "CLASSIFICATION_JOB_AT_ROUND_LEVEL": {"0": {"categories": ["BOTH_ARE_GOOD"]}},
                "COMPARISON_JOB": {
                    "0": {
                        "code": "Is much better",
                        "firstId": "cm5whprnc000q0cmjg3b0bth7",
                        "secondId": "cm5whpnzf000p0cmj2fojgut6",
                    }
                },
            },
            "conversation": {
                "CLASSIFICATION_JOB_AT_CONVERSATION_LEVEL": {"categories": ["GLOBAL_GOOD"]},
                "TRANSCRIPTION_JOB_AT_CONVERSATION_LEVEL": {"text": "Great conversation!"},
            },
        },
        "labeler": "test+fx@kili-technology.com",
        "metadata": {},
    },
]


INVALID_TEST_CASES = [
    {
        "description": "some chat items are empty",
        "file": "invalid-conversation-chatItem-empty.json",
        "error": "Content missing for chat item",
    },
    {
        "description": "duplicate chatItem externalId",
        "file": "invalid-conversation-duplicate-chatItem-externalId.json",
        "error": "External id",
    },
    {
        "description": "job at wrong level",
        "file": "invalid-conversation-job-at-wrong-level.json",
        "error": "Job CLASSIFICATION_JOB_AT_COMPLETION_LEVEL is not a round-level job; it is a completion-level job",
    },
    {
        "description": "chatItem not found",
        "file": "invalid-conversation-job-chatItem-not-found.json",
        "error": "Job CLASSIFICATION_JOB_AT_COMPLETION_LEVEL is associated with an unknown chat item",
    },
    {
        "description": "job not found",
        "file": "invalid-conversation-job-not-found.json",
        "error": "Job UNKNOWN_CLASSIFICATION_JOB_AT_COMPLETION_LEVEL not found in project jobs",
    },
    {
        "description": "missing labeler",
        "file": "invalid-conversation-missing-labeler.json",
        "error": "Cannot import conversation label: please specify a valid labeler (user email within the organization)",
    },
    {
        "description": "unknown labeler",
        "file": "invalid-conversation-unknown-labeler.json",
        "error": "User unknown+user@kili-technology.com not found in organization first-organization",
    },
    {
        "description": "out of bounds round annotation",
        "file": "invalid-conversation-out-of-bounds-round-annotation.json",
        "error": "Job CLASSIFICATION_JOB_AT_ROUND_LEVEL has more rounds than conversation length",
    },
    {
        "description": "partial comparison annotation",
        "file": "invalid-conversation-partial-comparison.json",
        "error": "Comparison job COMPARISON_JOB must evaluate conversation rounds sequentially",
    },
    {
        "description": "missing model name for assistant chat item",
        "file": "invalid-conversation-chatItem-role-assistant-without-modelName.json",
        "error": "Model name is required for assistant chat items",
    },
]


@pytest.mark.e2e()
def test_create_llm_static_project_and_import_conversations(kili: Kili):
    """Test the creation and management of project and model resources."""
    organization_id = kili.organizations()[0]["id"]

    project = kili.create_project(
        title=PROJECT_TITLE,
        description=PROJECT_DESCRIPTION,
        input_type="LLM_STATIC",
        json_interface=INTERFACE,
    )
    project_id = project["id"]

    assets = kili.assets(project_id=project_id)
    assert len(assets) == 0

    for test_case in INVALID_TEST_CASES:
        url = f"https://storage.googleapis.com/label-public-staging/cypress-tests/fixtures/llm/llm-static/{test_case['file']}"
        conversations = json.loads(requests.get(url).text)
        response = kili.llm.import_conversations(project_id, conversations=conversations)
        upload_warnings = response["warnings"]
        assert upload_warnings[0]["details"].startswith(test_case["error"])

    assets = kili.assets(project_id=project_id)
    assert len(assets) == 0

    response = kili.llm.import_conversations(
        project_id, conversations=cast(List[Conversation], CONVERSATIONS)
    )
    upload_warnings = response["warnings"]
    assert len(upload_warnings) == 0

    assets = kili.assets(project_id=project_id)
    assert len(assets) == 3
