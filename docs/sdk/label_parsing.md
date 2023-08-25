# Label parsing module

The module `kili.utils.labels.parsing` provides a `ParsedLabel` class that is used to parse labels.

Using labels as `ParsedLabel` instances is recommended when manipulating the label data, as it will provide autocompletion to access the meaningful fields of the label. If you prefer not to use it, you can still access the labeling data through the label dictionaries.

Read more about this feature in the [label parsing tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/label_parsing/).

!!! warning
    This feature is currently in beta. The classes and methods can still change marginally.

!!! danger "Breaking change"
    The `.category.name` attribute behavior has been changed.

    For a json interface like this:

    ```json
        "CLASSIFICATION_JOB": {
            "mlTask": "CLASSIFICATION",
            "content": {
                "categories": {
                    "CATEGORY_A": {"name": "Category A"},
                    "CATEGORY_B": {"name": "Category B"},
                },
            },
        }
    ```

    The old behavior (before Kili SDK 2.143.2):

    ```python
    print(my_label.jobs["CLASSIFICATION_JOB"].category.name)  # CATEGORY_A
    ```

    The new behavior (after Kili SDK 2.143.2):

    ```python
    print(my_label.jobs["CLASSIFICATION_JOB"].category.name)  # Category A
    ```

    If you want to retrieve the category name as it is in the json interface, you can use the `.key` attribute:

    ```python
    print(my_label.jobs["CLASSIFICATION_JOB"].category.key)  # CATEGORY_A
    ```

## ParsedLabel

::: kili.utils.labels.parsing.ParsedLabel
    options:
        members:
            - to_dict
            - "__init__"

## Task specific attributes and methods

### Classification tasks

For classification tasks, the following attributes are available:

#### `.categories`

Returns a `CategoryList` object that contains the categories of an asset.

```python
label.jobs["CLASSIF_JOB"].categories
```

#### `.category`

Returns a `Category` object that contains the category of an asset.

Only available if the classification job is a one-class classification job.

```python
label.jobs["CLASSIF_JOB"].category
# Same as:
label.jobs["CLASSIF_JOB"].categories[0]
```

#### `.name`

Retrieves the category name.

```python
label.jobs["CLASSIF_JOB"].category.name
```

!!! example

    ```python
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "CLASSIFICATION",
                "content": {
                    "categories": {
                        "CATEGORY_A": {"name": "A"},
                        "CATEGORY_B": {"name": "B"},
                    },
                    "input": "radio",
                },
            }
        }
    }
    json_response_dict = {
        "JOB_0": {
            "categories": [
                {
                    "confidence": 100,
                    "name": "CATEGORY_A",
                }
            ]
        }
    }
    my_label = {"jsonResponse": json_response_dict}

    parsed_label = ParsedLabel(label=my_label, json_interface=json_interface, input_type="IMAGE")

    print(parsed_label.jobs["JOB_0"].categories[0].name)  # A
    print(parsed_label.jobs["JOB_0"].categories[0].key)  # CATEGORY_A
    ```

#### `.key`

Retrieves the category name key.

```python
label.jobs["CLASSIF_JOB"].category.key
```

#### `.confidence`

Retrieves the confidence (when available).

```python
label.jobs["CLASSIF_JOB"].category.confidence
```

### Transcription tasks

#### `.text`

Retrieves the transcription text.

```python
label.jobs["TRANSCRIPTION_JOB"].text
```

### Object detection tasks

For more information about the different object detection tasks and their label formats, please refer to the [Kili documentation](https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation).

#### Standard object detection

##### `.bounding_poly`

Returns a list of bounding polygons for an annotation.

```python
label.jobs["DETECTION_JOB"].annotations[0].bounding_poly
```

##### `.normalized_vertices`

Returns a list of normalized vertices for a bounding polygon.

```python
label.jobs["DETECTION_JOB"].annotations[0].bounding_poly[0].normalized_vertices
```

##### `.bounding_poly_annotations`

This attribute is an alias for `.annotations`.

The benefit of using this attribute is that it will only show in your IDE autocompletions the attributes that are relevant for the object detection task.

```python
# the .content attribute is not relevant for object detection tasks!

# IDE autocompletion will accept this attribute, but will crash at runtime
label.jobs["BBOX_JOB"].annotations.content

# IDE autocompletion will not display this attribute and Python linter will raise an error
label.jobs["BBOX_JOB"].bounding_poly_annotations.content
```

#### Point detection

##### `.point`

Returns the `x` and `y` coordinates of the point.

```python
label.jobs["POINT_JOB"].annotations[0].point
```

#### Line detection

##### `.polyline`

Returns the list of points for a line annotation.

```python
label.jobs["LINE_JOB"].annotations[0].polyline
```

#### Pose estimation

##### `.points`

Returns the list of points for an annotation.

```python
label.jobs["POSE_JOB"].annotations[0].points
```

##### `.point`

Returns the point data.

```python
label.jobs["POSE_JOB"].annotations[0].points[0].point
```

##### `.point.point`

Returns a dictionary with the coordinates of the point.

```python
label.jobs["POSE_JOB"].annotations[0].points[0].point.point
```

##### `.code`

Returns the point identifier (unique for each point in an object).

```python
label.jobs["POSE_JOB"].annotations[0].points[0].point.code
```

##### `.name`

Returns the point name.

```python
label.jobs["POSE_JOB"].annotations[0].points[0].point.name
```

##### `.job_name`

Returns the job which annotated point belongs to.

```python
label.jobs["POSE_JOB"].annotations[0].points[0].point.job_name
```

### Video tasks

#### `.frames`

Returns a list of parsed label data for a each frame.

```python
label.jobs["FRAME_CLASSIF_JOB"].frames
label.jobs["FRAME_CLASSIF_JOB"].frames[5]  # 6th frame

# get category name of the 6th frame (for a frame classification job only)
label.jobs["FRAME_CLASSIF_JOB"].frames[5].category.name
```

### Named entities recognition tasks

#### `.content`

Returns the content of the mention.

```python
label.jobs["NER_JOB"].annotations[0].content
```

#### `.begin_offset`

Returns the position of the first character of the mention in the text.

```python
label.jobs["NER_JOB"].annotations[0].begin_offset
```

#### `.end_offet`

When available, returns the position of the last character of the mention in the text.

```python
label.jobs["NER_JOB"].annotations[0].end_offset
```

#### `.entity_annotations`

This attribute is an alias for `.annotations`.

The benefit of using this attribute is that it will only show in your IDE autocompletions the attributes that are relevant for the NER task.

```python
# the .points attribute is not relevant for NER tasks, it is only used for pose estimation tasks!

# IDE autocompletion will accept this attribute, but will crash at runtime
label.jobs["NER_JOB"].annotations.points

# IDE autocompletion will not display this attribute and Python linter will raise an error
label.jobs["NER_JOB"].entity_annotations.points
```

### Named entities recognition in PDFs tasks

#### `.content`

Returns the content of the mention.

```python
label.jobs["NER_PDF_JOB"].annotations[0].content
```

#### `.annotations`

NER in PDFs annotations have an additional layer of annotations. See the [documentation](https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation#ner-in-pdfs) for more information.

#### `.polys`

Returns a list of dictionaries containing the normalized vertices of the mention.

```python
label.jobs["NER_PDF_JOB"].annotations[0].annotations[0].polys
```

#### `.page_number_array`

```python
label.jobs["NER_PDF_JOB"].annotations[0].annotations[0].page_number_array
```

#### `.bounding_poly`

Returns a list of dictionaries containing the normalized vertices of the mention.

```python
label.jobs["NER_PDF_JOB"].annotations[0].annotations[0].bounding_poly
```

### Relation tasks

#### Named entities relation

##### `.start_entities`

Returns a list of dictionaries containing the start entities Ids of the relation.

```python
label.jobs["NER_RELATION_JOB"].annotations[0].start_entities
```

##### `.end_entities`

Returns a list of dictionaries containing the end entities Ids of the relation.

```python
label.jobs["NER_RELATION_JOB"].annotations[0].end_entities
```

#### Object detection relation

##### `.start_objects`

Returns a list of dictionaries containing the start objects Ids of the relation.

```python
label.jobs["OBJECT_RELATION_JOB"].annotations[0].start_objects
```

##### `.end_objects`

Returns a list of dictionaries containing the end objects Ids of the relation.

```python
label.jobs["OBJECT_RELATION_JOB"].annotations[0].end_objects
```

### Children tasks

#### `.children`

Depending on the task, the `.children` attribute can be found in different places:

```python
# For cassification task
label.jobs["CLASSIF_JOB"].category.children

# For several kinds of tasks: object detection, NER, pose estimation, etc.
label.jobs["OBJECT_DETECTION_JOB"].annotations[0].children
```

You can find more information about the children jobs in the [label parsing tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/label_parsing/#child-jobs).

## Migrating from jsonReponse format

In most cases, the attributes of a parsed label are the snake case version of the keys present in the json response.

For example, with a NER (named entities recognition) label, you can access the `beginOffset` data of an annotation with `parsed_label.jobs["NER_JOB"].annotations[0].begin_offset`.

The different json response keys are listed in the Kili documentation:

- for [classification tasks](https://docs.kili-technology.com/reference/export-classification)
- for [exported object/entity detection and relation tasks](https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation)
- for [exported transcription tasks](https://docs.kili-technology.com/reference/export-transcription).
