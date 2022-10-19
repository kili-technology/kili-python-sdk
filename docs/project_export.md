# Exporting kili projects

There are several ways to export labels from a Kili project.

## With the CLI
You can export a project using the `kili project export` command:
```

    kili project export \\
        --project-id <project_id> \\
        --output-format yolo_v5 \\
        --output-file /tmp/export.zip
```
More options here https://python-sdk-docs.kili-technology.com/latest/cli/reference/#export

## With the Python SDK
You can also use the Python SDK:
```
```

## From the Kili UI

## Available formats

| Format        | UI  | Python Client | Command Line Interface |
| ------------- | --- | ------------- | ---------------------- |
| Kili (raw)    | ✅   | ✅             | ✅                      |
| Kili (simple) | ✅   | ❌             | ❌                      |
| Yolo V4       | ✅   | ✅             | ✅                      |
| Yolo V5       | ✅   | ✅             | ✅                      |
| Yolo V7       | ❌   | ✅             | ✅                      |
| Pascal VOC    | ✅   | ❌             | ❌                      |


more to come
