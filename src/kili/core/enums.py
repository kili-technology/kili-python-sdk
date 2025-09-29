"""DEPRECATED.

From https://docs.kili-technology.com/reference/graphql-api#enums.
"""

from typing import Literal

LicenseType = Literal[
    "DISCOVERY",
    "FREEMIUM",
    "PAID",
]


LockType = Literal[
    "REVIEW",
    "DEFAULT",
]


NotificationStatus = Literal[
    "FAILURE",
    "PENDING",
    "SUCCESS",
]


OrganizationRole = Literal[
    "ADMIN",
    "USER",
]


ProjectRole = Literal[
    "ADMIN",
    "TEAM_MANAGER",
    "REVIEWER",
    "LABELER",
]


DemoProjectType = Literal[
    "DEMO_COMPUTER_VISION_TUTORIAL",
    "DEMO_TEXT_TUTORIAL",
    "DEMO_PDF_TUTORIAL",
    "VIDEO_FRAME_OBJECT_TRACKING",
    "DEMO_SEGMENTATION_COCO",
    "DEMO_NER",
    "DEMO_ID_OCR",
    "DEMO_REVIEWS",
    "DEMO_OCR",
    "DEMO_NER_TWEETS",
    "DEMO_PLASTIC",
    "DEMO_CHATBOT",
    "DEMO_PDF",
    "DEMO_ANIMALS",
    "DEMO_LLM",
    "DEMO_LLM_INSTR_FOLLOWING",
    "DEMO_SEGMENTATION",
]


Right = Literal[
    "CAN_ACCESS_SMART_TOOLS",
    "CAN_LABEL",
    "CREATE_AUDIO",
    "CREATE_FRAME",
    "CREATE_IMAGE",
    "CREATE_PDF",
    "CREATE_TEXT",
    "CREATE_TIMESERIES",
    "CREATE_VIDEO",
    "MAKE_PUBLIC_PROJECT",
    "SEE_LICENSE_BANNER",
    "SEE_UPGRADE_BUTTON",
    "UPLOAD_CLOUD_DATA",
    "USE_API",
    "USE_API_PRIORITY",
]
