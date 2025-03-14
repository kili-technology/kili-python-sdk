import os
import urllib.request

from kili.client import Kili

LOCAL_KILI_API_KEY = "cm7nd7k63001gg90w28ot9vl7/881232fb4cce6e745f61612c5c5918d0"

PROJECT_TYPES_TO_TEST = ["IMAGE", "GEOSPATIAL"]

IMAGE_PROJECT_TITLE = "Image Samples (from SDK)"
GEOSPATIAL_PROJECT_TITLE = "Geospatial Samples (from SDK)"

JSON_INTERFACE = {
    "jobs": {
        "JOB_0": {
            "mlTask": "CLASSIFICATION",
            "required": 1,
            "isChild": False,
            "content": {
                "categories": {
                    "OBJECT_A": {"name": "Object A", "id": "category3"},
                    "OBJECT_B": {"name": "Object B", "id": "category4"},
                },
                "input": "radio",
            },
            "isNew": False,
            "instruction": "Classification",
        },
        "OBJECT_DETECTION_JOB": {
            "content": {
                "categories": {
                    "B_BOX_1": {
                        "children": [],
                        "color": "#472CED",
                        "name": "BBox1",
                        "id": "category5",
                    },
                    "B_BOX_2": {
                        "children": [],
                        "name": "BBox2",
                        "id": "category6",
                        "color": "#5CE7B7",
                    },
                },
                "input": "radio",
            },
            "instruction": "Bounding Box",
            "mlTask": "OBJECT_DETECTION",
            "required": 0,
            "tools": ["rectangle"],
            "isChild": False,
            "isNew": False,
        },
        "OBJECT_DETECTION_JOB_0": {
            "content": {
                "categories": {
                    "SEMANTIC_1": {
                        "children": [],
                        "color": "#D33BCE",
                        "name": "Semantic1",
                        "id": "category7",
                    },
                    "SEMANTIC_2": {
                        "children": [],
                        "name": "Semantic2",
                        "id": "category8",
                        "color": "#FB753C",
                    },
                },
                "input": "radio",
            },
            "instruction": "Semantic",
            "mlTask": "OBJECT_DETECTION",
            "required": 0,
            "tools": ["semantic"],
            "isChild": False,
            "isNew": False,
        },
    }
}

GEOSPATIAL_FILES = [
    "1B_uint8_epsg4326.tif",
    "1B_uint8_epsg21897.tif",
    "1B_uint16_epsg4326.tif",
    "3B_uint8_epsg4326.tif",
    "3B_uint8_epsg32636.tif",
    "3B_uint8_epsg32647.tif",
    "10B_uint16_epsg4326.tif",
    "23B_float32_epsg4326.tif",
]
GEOSPATIAL_FILES_MULTILAYER = ["3B_uint16_epsg4326_layer1.tif", "3B_uint16_epsg4326_layer2.tif"]


def archive_previous_project():
    projects = kili.projects()
    for project in projects:
        if project["inputType"] in PROJECT_TYPES_TO_TEST and project["title"] in [
            IMAGE_PROJECT_TITLE,
            GEOSPATIAL_PROJECT_TITLE,
        ]:
            kili.delete_project(project["id"])


def download_geotiffs():
    if not os.path.exists("geospatial"):
        os.makedirs("geospatial")

    base_url = "https://storage.googleapis.com/label-public-staging/geotiffs"

    for file in GEOSPATIAL_FILES + GEOSPATIAL_FILES_MULTILAYER:
        local_path = os.path.join("geospatial", file)
        if not os.path.exists(local_path):
            remote_url = f"{base_url}/{file}"
            print(f"Downloading {file} from {remote_url}...")
            urllib.request.urlretrieve(remote_url, local_path)


kili = Kili(
    api_key=LOCAL_KILI_API_KEY,
    api_endpoint="http://localhost:4001/api/label/v2/graphql",
    verify=False,
)

archive_previous_project()
download_geotiffs()

content_array = [os.path.join("geospatial", file) for file in GEOSPATIAL_FILES]
external_id_array = GEOSPATIAL_FILES
multi_layer_content_array = [
    [
        {
            "path": os.path.join("geospatial", GEOSPATIAL_FILES_MULTILAYER[0]),
            "name": "Layer 1",
            "isBaseLayer": False,
        },
        {
            "path": os.path.join("geospatial", GEOSPATIAL_FILES_MULTILAYER[1]),
            "name": "Layer 2",
            "isBaseLayer": False,
        },
    ]
]
json_metadata_array = [{"processingParameters": {"epsg": 3857}}]
json_content_array = [
    [
        {
            "name": "osm",
            "tileLayerUrl": "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "epsg": "EPSG3857",
            "bounds": [
                [11.17010498046875, 44.308941579503745],
                [13.67478942871094, 46.542667432984864],
            ],
            "useClassicCoordinates": False,
            "minZoom": 10,
            "maxZoom": 18,
            "isBaseLayer": True,
        }
    ]
]

if "GEOSPATIAL" in PROJECT_TYPES_TO_TEST:
    geospatial_project_id = kili.create_project(
        title=GEOSPATIAL_PROJECT_TITLE, input_type="GEOSPATIAL", json_interface=JSON_INTERFACE
    )["id"]

    kili.append_many_to_dataset(
        project_id=geospatial_project_id,
        content_array=content_array,
        external_id_array=external_id_array,
    )

    kili.append_many_to_dataset(
        project_id=geospatial_project_id,
        multi_layer_content_array=multi_layer_content_array,
        json_metadata_array=json_metadata_array,
        json_content_array=json_content_array,  # type: ignore
    )

if "IMAGE" in PROJECT_TYPES_TO_TEST:
    image_project_id = kili.create_project(
        title=IMAGE_PROJECT_TITLE, input_type="IMAGE", json_interface=JSON_INTERFACE
    )["id"]

    kili.append_many_to_dataset(
        project_id=image_project_id,
        content_array=content_array,
        external_id_array=external_id_array,
    )

    kili.append_many_to_dataset(
        project_id=image_project_id,
        multi_layer_content_array=multi_layer_content_array,
        json_metadata_array=json_metadata_array,
        json_content_array=json_content_array,  # type: ignore
    )
