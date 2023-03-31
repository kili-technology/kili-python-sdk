# Exporting kili projects

There are several ways to export labels from a Kili project.

## With the CLI
You can export a project using the `kili project export` command:
```bash
kili project export \
        --project-id <project_id> \
        --output-format yolo_v5 \
        --output-file /tmp/export.zip
```
More options [here](https://python-sdk-docs.kili-technology.com/latest/cli/reference/#export).

## With the Python SDK
You can also use the Python SDK:
```python
from kili.client import Kili
kili = Kili()
kili.export_labels(
    project_id = "<project_id>",
    filename = "/tmp/export.zip",
    fmt = "yolo_v5",
)
```
More details [here](https://python-sdk-docs.kili-technology.com/latest/sdk/label/#kili.entrypoints.queries.label.__init__.QueriesLabel.export_labels).

## From the Kili UI
You can refer to this [Kili documentation page](https://docs.kili-technology.com/docs/exporting-project-data).

## Available formats

| Format        | UI  | Python Client | Command Line Interface |
| ------------- | --- | ------------- | ---------------------- |
| Kili (raw)    | ✅   | ✅             | ✅                      |
| Kili (simple) | ✅   | ❌             | ❌                      |
| YOLO V4       | ✅   | ✅             | ✅                      |
| YOLO V5       | ✅   | ✅             | ✅                      |
| YOLO V7       | ❌   | ✅             | ✅                      |
| Pascal VOC    | ✅   | ✅             | ✅                      |
| COCO          | ❌   | ✅             | ✅                      |


And more to come!
