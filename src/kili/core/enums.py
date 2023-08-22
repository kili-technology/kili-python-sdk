"""DEPRECATED
From https://docs.kili-technology.com/reference/graphql-api#enums."""
from typing import Literal

DataIntegrationPlatform = Literal["AWS", "Azure", "GCP"]


DataIntegrationStatus = Literal["CONNECTEDDISCONNECTEDCHECKING"]


DataIntegrationType = Literal["REMOTE_STORAGE"]


ExportType = Literal["LATESTNORMAL"]


GraphScale = Literal["DAYMONTHWEEK"]


GraphType = Literal["COUNT_BY_CATEGORIESNUMBER_OF_LABELSHighestRoleInProject"]


HighestRoleInProject = Literal["NAADMINTEAM_MANAGERREVIEWERLABELER"]


HubspotSubscriptionStatus = Literal[
    "SUBSCRIBED",
    "UNSUBSCRIBED",
]


InputType = Literal[
    "AUDIO",
    "IMAGE",
    "PDF",
    "TEXT",
    "TIME_SERIES",
    "VIDEO",
    "VIDEO_LEGACY",
]


IssueStatus = Literal[
    "OPEN",
    "SOLVED",
]


IssueType = Literal[
    "ISSUE",
    "QUESTION",
]


LabelFormat = Literal[
    "RAW",
    "SIMPLE",
    "YOLO_V4",
    "YOLO_V5",
]


LabelType = Literal[
    "AUTOSAVE",
    "DEFAULT",
    "INFERENCE",
    "PREDICTION",
    "REVIEW",
]


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


ProjectType = Literal[
    "IMAGE_CLASSIFICATION_SINGLE",
    "IMAGE_CLASSIFICATION_MULTI",
    "IMAGE_OBJECT_DETECTION_RECTANGLE",
    "IMAGE_OBJECT_DETECTION_POLYGON",
    "IMAGE_OBJECT_DETECTION_SEMANTIC",
    "IMAGE_POSE_ESTIMATION",
    "OCR",
    "PDF_CLASSIFICATION_SINGLE",
    "PDF_CLASSIFICATION_MULTI",
    "PDF_OBJECT_DETECTION_RECTANGLE",
    "PDF_NAMED_ENTITY_RECOGNITION",
    "SPEECH_TO_TEXT",
    "TEXT_CLASSIFICATION_SINGLE",
    "TEXT_CLASSIFICATION_MULTI",
    "TEXT_TRANSCRIPTION",
    "TEXT_NER",
    "TIME_SERIES",
    "VIDEO_CLASSIFICATION_SINGLE",
    "VIDEO_OBJECT_DETECTION",
    "VIDEO_FRAME_CLASSIFICATION",
    "VIDEO_FRAME_OBJECT_TRACKING",
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


SplitOption = Literal[
    "MERGED_FOLDER",
    "SPLITTED_FOLDER",
]


Status = Literal[
    "TODO",
    "ONGOING",
    "LABELED",
    "REVIEWED",
    "TO_REVIEW",
]


UploadType = Literal[
    "VIDEO",
    "GEO_SATELLITE",
]


WarningTypes = Literal[
    "DUPLICATED_ID",
    "EMPTY_ARRAY",
    "FAILED_ASSET_CREATION",
    "FFMPEG_NOT_INSTALLED",
    "INPUT_UNDEFINED",
    "MAX_INPUT_SIZE",
    "MAX_PROJECT_SIZE",
    "MISSING_ID",
    "NON_INTEGER_FPS",
    "UNSUPPORTED_TYPE",
    "UNSPECIFIED_ERROR",
    "WRONG_CSV_FORMAT",
]
