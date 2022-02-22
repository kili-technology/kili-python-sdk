"""
    Imports a sample of a NER dataset processed with Google Natural Language NER into Kili.
"""
from itertools import cycle
import os
import tarfile
import urllib.request

from google.cloud import language
from google.protobuf.json_format import MessageToDict
from tqdm import tqdm

from kili.client import Kili


def download_dataset():
    url = "https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz"
    filename = url.split("/")[-1]
    target_path = os.path.join("/tmp", filename)
    if not os.path.exists(target_path):
        print("downloading...")
        urllib.request.urlretrieve(url, target_path)
    return target_path


def extract_dataset(path):
    target_path = "/tmp/maildir"
    if not os.path.exists(target_path):
        tar = tarfile.open(path)
        tar.extractall(path="/tmp")
        tar.close()
    return target_path


def analyze_entities(text_content):
    client = language.LanguageServiceClient()
    type_ = language.enums.Document.Type.PLAIN_TEXT
    document = {"content": text_content, "type": type_}
    encoding_type = language.enums.EncodingType.UTF8
    response = client.analyze_entities(document, encoding_type=encoding_type)
    return MessageToDict(response)


def escape_text(str):
    return (
        str.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", "\\r")
        .replace("\\$", "$")
    )


def format_google_nl_to_kili(entities):
    output_entities = []
    for entity in entities:
        for mention in entity["mentions"]:
            output_entities.append(
                {
                    "categories": [{"name": entity["type"], "confidence": 100}],
                    "beginOffset": mention["text"]["beginOffset"],
                    "content": mention["text"]["content"],
                }
            )

    return {"NAMED_ENTITIES_RECOGNITION_JOB": {"annotations": output_entities}}


COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

ENTITY_TYPES = [
    ("UNKNOWN", "Unknown"),
    ("PERSON", "Person"),
    ("LOCATION", "Location"),
    ("ORGANIZATION", "Organization"),
    ("EVENT", "Event"),
    ("WORK_OF_ART", "Artwork"),
    ("CONSUMER_GOOD", "Consumer product"),
    ("OTHER", "Other"),
    ("PHONE_NUMBER", "Phone number"),
    ("ADDRESS", "Address"),
    ("DATE", "Date"),
    ("NUMBER", "Number"),
    ("PRICE", "Price"),
]

ENTITY_TYPES_WITH_COLORS = [(n[0], n[1], c)
                            for n, c in zip(ENTITY_TYPES, cycle(COLORS))]

JSON_INTERFACE = {
    "jobRendererWidth": 0.25,
    "jobs": {
        "NAMED_ENTITIES_RECOGNITION_JOB": {
            "mlTask": "NAMED_ENTITIES_RECOGNITION",
            "content": {
                "categories": {
                    name: {"name": name_pretty,
                           "children": [], "color": color}
                    for name, name_pretty, color in ENTITY_TYPES_WITH_COLORS
                },
                "input": "radio",
            },
            "instruction": "",
            "required": 1,
            "isChild": False,
        }
    },
}


MAX_NUMBER_OF_ASSET = 50

if __name__ == "__main__":

    path_gz = download_dataset()
    path_dir = extract_dataset(path_gz)

    only_files = [
        os.path.join(path, name)
        for path, _, files in os.walk(path_dir)
        for name in files
    ]

    kili = Kili()

    p = kili.create_project(
        title="Enron with Google NER",
        description="Enron emails with the Google Natural Language Named Entity Recognition",
        input_type="TEXT",
        json_interface=JSON_INTERFACE,
    )
    project_id = p["id"]

    def asset_generator():

        for filepath in tqdm(only_files[:MAX_NUMBER_OF_ASSET]):
            with open(filepath, "r") as f:
                text = f.read()

            escaped_text = escape_text(text)
            response = analyze_entities(escaped_text)
            entities = [
                e
                for e in response["entities"]
                if isinstance(e["type"], str) and e["type"] != "OTHER"
            ]  # remove OTHER type as it brings some noise
            json_response = format_google_nl_to_kili(entities)

            yield {
                "external_id": filepath,
                "escaped_text": escaped_text,
                "json_response": json_response,
                "model_name": "google_natural_language_ner"
            }

    print("Creating asset list")
    assets = list(asset_generator())

    print("Import asset list into Kili")
    kili.append_many_to_dataset(
        project_id=project_id,
        content_array=[a["escaped_text"] for a in assets],
        external_id_array=[a["external_id"] for a in assets]
    )

    print("Import predictions into Kili")
    kili.create_predictions(
        project_id=project_id,
        external_id_array=[a["external_id"] for a in assets],
        json_response_array=[a["json_response"] for a in assets],
        model_name_array=[a["model_name"] for a in assets],
    )
