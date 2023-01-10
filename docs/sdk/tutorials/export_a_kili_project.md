# How to export a Kili project
## Outline
This tutorial explains the multiple ways to export a Kili project. It describes:

 * Methods to export the labels one by one, after filtering
 * The solutions for performing a full-project export

The methods are illustrated with code snippets.


## Export methods
With Kili, once you have annotated enough assets, you can export the data programmatically to train a machine learning algorithm with it. There are several ways to do it:

 * Fetch the assets and/or the labels one by one using [`.assets`](https://python-sdk-docs.kili-technology.com/latest/sdk/asset/#kili.queries.asset.__init__.QueriesAsset.assets) or [`.labels`](https://python-sdk-docs.kili-technology.com/latest/sdk/label/#kili.queries.label.__init__.QueriesLabel.labels), perform the data transformation yourself and then write the data to one or several output files.
 * Export the whole project as a dataset. To do that, use the [`.export_labels`](https://python-sdk-docs.kili-technology.com/latest/sdk/label/#kili.queries.label.__init__.QueriesLabel.export_labels) method that creates an archive containing the labels in your chosen format.


## Preliminary steps
 1. Fetch the project ID from the Kili UI (in Settings / Admin):
   ![Get Project ID from UI](../../assets/get_project_id.jpg)
 2. Ensure that your Kili API key has been set as an environment variable:
 ```bash
 export KILI_API_KEY=<YOUR_API_KEY>
 ```
 3. If Kili has not been installed yet, install Kili.
```bash
pip install --upgrade kili
```

 4. Import packages and instantiate `Kili`:
```python
from kili.client import Kili
from pathlib import Path
kili = Kili()
```
## Exporting assets and labels one by one
To retrieve all assets of a project one by one, perform the following steps:

### Exporting the latest labels per asset
 1. First, fetch the assets:
```python
assets = kili.assets("<your_project_id>", fields=["externalId", "latestLabel.jsonResponse"])
```
 2. Now if you print an asset, you will see that you can access its `latestLabel`:
```python
print(assets[0])
{'latestLabel': {'jsonResponse': {'CLASSIFICATION_JOB': {'categories': [{'name': 'VEHICLE'}]}}}, 'externalId': '0'}
```
  3. You can now get your label, and write the category name into a text file, for example:
```python
for asset in assets:
    if asset["latestLabel"]: # covers the assets without label
        class_ = asset["latestLabel"]["jsonResponse"]["CLASSIFICATION_JOB"]["categories"][0]["name"]
        with (Path("/tmp") / (asset["externalId"] + ".txt")).open("w", encoding="utf-8") as f:
            f.write(class_)
```


### Filtering specific labels per asset through the method filters
You can specify label filters directly in the [`.assets`](https://python-sdk-docs.kili-technology.com/latest/sdk/asset/#kili.queries.asset.__init__.QueriesAsset.assets) and the [`.labels`](https://python-sdk-docs.kili-technology.com/latest/sdk/label/#kili.queries.label.__init__.QueriesLabel.labels) methods. The available filters are listed in the arguments list
for each one of these methods.

When done, you can write the conversion code to get the data in the format that you need.

**Get only the assets that have labels with a consensus mark above 0.7:**
```python
assets = kili.assets("<your_project_id>", fields=["externalId", "labels.jsonResponse"], label_consensus_mark_gt=0.7)
# + asset conversion code
```

**Get all the labels with a consensus mark above 0.7:**
```python
labels = kili.labels("<your_project_id>", fields=["labelOf.externalId", "jsonResponse"], consensus_mark_gt=0.7)
# + label conversion code
```

**Get all the labels added by a specific project member:**
```python
labels = kili.labels("<your_project_id>", fields=["labelOf.externalId", "jsonResponse"], author_in=["John Smith"])
# + label conversion code
```
This code will return a list of labels authored by John Smith.
The `author_in` parameter is quite versatile: you can type the first name, the last name, or the first name + last name of the user for which you want to fetch the labels.


### Filtering specific labels per asset through the label properties
You can also look for specific labels, for example the last "review" status label per user, and dump the result into a json file. You can use the field `"labels.isLatestReviewLabelForUser"` to check if the label is the latest per user.
```python
from kili.client import Kili
from pathlib import Path
import json

assets = kili.assets("<your_project_id>", fields=["externalId", "labels.jsonResponse", "labels.isLatestReviewLabelForUser"])

for asset in assets:
    if asset["labels"]: # covers the assets without annotations
        for label in asset["labels"]:
            if label["isLatestReviewLabelForUser"] and "JOB_0" in label["jsonResponse"]:
                annotation = label["jsonResponse"]["JOB_0"]
                with (Path("/tmp") / (asset["externalId"] + ".json")).open("w", encoding="utf-8") as f:
                    f.write(json.dumps(annotation))
                break # once we find a latest label done by a reviewer, we move on to the next asset.
```

### Filtering the latest label per annotator
When working on project with [consensus](https://docs.kili-technology.com/docs/consensus-overview) enabled, it can be useful to export the latest label made by each annotator:
```python
from kili.client import Kili
from collections import defaultdict
from pathlib import Path
import json


kili = Kili()
assets = kili.assets(
    "clb54wfkn01zb0kyadscgaf5j",
    fields=[
        "externalId",
        "labels.author.email",
        "labels.createdAt",
        "labels.labelType",
        "labels.jsonResponse",
    ],
)

for asset in assets:
    if asset["labels"]:
        latest_label_by_user = defaultdict(list)
        for label in asset["labels"]:
            if label["labelType"] == "DEFAULT":
                latest_label_by_user[label["author"]["email"]].append(label)
        latest_label_per_user = {
            email: max(labels, key=lambda x: x["createdAt"])
            for email, labels in latest_label_by_user.items()
        }
        with (Path("/tmp") / (asset["externalId"] + ".json")).open("w", encoding="utf-8") as f:
            f.write(json.dumps(latest_label_per_user))

```

## Exporting a whole project
Kili has a method to export the whole project into specific export formats. It can be useful when your goal is to use one of the standard output formats.

### Available formats


| Format        | UI  | Python Client | Command Line Interface |
| ------------- | --- | ------------- | ---------------------- |
| Kili (raw)    | ✅   | ✅             | ✅                      |
| Kili (simple) | ✅   | ❌             | ❌                      |
| YOLO V4       | ✅   | ✅             | ✅                      |
| YOLO V5       | ✅   | ✅             | ✅                      |
| YOLO V7       | ❌   | ✅             | ✅                      |
| Pascal VOC    | ✅   | ✅             | ✅                      |
| COCO          | ❌   | ✅             | ✅                      |


### The `.export_labels` method

The [`.export_labels`](https://python-sdk-docs.kili-technology.com/latest/sdk/label/#kili.queries.label.__init__.QueriesLabel.export_labels) method enables the export of a full project. It does the following preprocessing:

* Only fetches the labels of types `"DEFAULT"` and `"REVIEW"` (see the [label types explanations](https://docs.kili-technology.com/docs/asset-lifecycle#label-types-and-definitions-throughout-an-asset-lifecycle)).
* If specified, selects a subset of asset ids.
* Exports labels to one of the standard formats (only available for a restricted set of ML tasks).
* Using various method arguments, you can decide:
    * Whether or not to include the assets in the export
    * Whether to export just the latest label or all the labels
    * Whether to create one folder for all the jobs or one folder per job
    * Whether or not to export the label-related data into one single file
Note that some formats are by default single-file, while others use many files:

|Format|Single file|Multiple files|
|---|---|---|
|Kili|✅ |✅ |
|Yolo|❌|✅ |
|Pascal VOC|❌|✅ |
|COCO|✅|❌|

For all the formats, in the output archive, a `README.kili.txt` file is also created. Here is an example of its contents:
```
Exported Labels from KILI
=========================

- Project name: Awesome annotation project
- Project identifier: abcdefghijklmnop
- Project description: This project contains labels, most of which are awesome.
- Export date: 20221125-093324
- Exported format: kili
- Exported labels: latest
```


### Kili format, one file per asset
The following code snippet exports the whole asset payload and the associated labels, with one json file per asset, into the `/tmp/export.zip` folder.
```python
from kili.client import Kili
kili = Kili()
kili.export_labels(
    project_id = "<your_project_id>",
    filename = "/tmp/export.zip",
    fmt = "kili",
)
```


### Kili format, one file for the whole project
This code snippet exports the whole asset payload and the associated labels as one file for the whole project, into the `/tmp/export.zip` folder.
```python
from kili.client import Kili
kili = Kili()
kili.export_labels(
    project_id = "<your_project_id>",
    filename = "/tmp/export.zip",
    fmt = "kili",
    single_file = True,
)
```

### YOLO formats
When you have at least one Object Detection job with bounding boxes, you can also export to one of the YOLO formats. You can choose `"yolo_v4"`, `"yolo_v5"` or `"yolo_v7"`. The difference between each format is the structure of the metadata YAML file, which specifies the object classes. In all the cases, one file per asset is produced, containing the last created `DEFAULT` or `REVIEW` label. Each YOLO label has the following shape:
```
2        0.25 0.67 0.26 0.34
^        ^    ^    ^    ^
class    x    y    w    h
```
where:

   * `class` is the class index in the classes list contained in the YOLO metadata file.
   * `x` is the x-coordinate relative to the image width (between 0.0 and 1.0) of the center of the bounding box.
   * `y` is the y-coordinate relative to the image height (between 0.0 and 1.0) of the center of the bounding box.
   * `w` is the width relative to the image width (between 0.0 and 1.0) of the bounding box.
   * `h` is the height relative to the image height (between 0.0 and 1.0) of the bounding box.

Here is an example of a YOLO annotation over an image:
<br>
<img src="../../assets/teslabb.jpg" alt="yolo on an image" width="400"/>


Here is how to export to YOLO (in this example, YOLOv5):
```python
from kili.client import Kili
kili = Kili()
kili.export_labels(
    project_id = "<your_project_id>",
    filename = "/tmp/export.zip",
    fmt = "yolo_v5",
)
```

Note that a standard YOLO file format must also include:
* The path root to the assets
* The `train`, `val` and `test` subfolders

Placing specific data in specific folders is the decision of an ML engineer or a Data scientist, so we are not providing a code snippet here.


### COCO format
To export your data into the COCO format, run the following code:
```python
from kili.client import Kili
kili = Kili()
kili.export_labels(
    project_id = "<your_project_id>",
    filename = "/tmp/export.zip",
    fmt = "coco",
)
```

This will create an archive containing both:

 * The COCO annotation file
 * The `data/` folder with all the assets

## Summary
In this tutorial, we have seen several ways to export labels from a Kili project:

* Using [`.assets`](https://python-sdk-docs.kili-technology.com/latest/sdk/asset/#kili.queries.asset.__init__.QueriesAsset.assets) and [`.labels`](https://python-sdk-docs.kili-technology.com/latest/sdk/label/#kili.queries.label.__init__.QueriesLabel.labels) and their filtering arguments, a subset of assets or labels can be selected and then exported.
* Using [`.export_labels`](https://python-sdk-docs.kili-technology.com/latest/sdk/label/#kili.queries.label.__init__.QueriesLabel.export_labels), the whole project can be exported into a standard output format.
