# Label parsing module

The module `kili.utils.labels.parsing` provides a `ParsedLabel` class that is used to parse labels.

Read more about this feature in the [label parsing tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/label_parsing/).

!!! warning
    This feature is currently in beta.

## ParsedLabel

::: kili.utils.labels.parsing.ParsedLabel
    options:
        members:
            - to_dict
            - "__init__"

## Task specific attributes and methods

In most cases, the attributes of a parsed label are the snake case version of the keys present in the json response.

For example, with a NER (named entities recognition) label, you can access the `beginOffset` data of the first annotation with `parsed_label.jobs["NER_JOB"].annotations[0].begin_offset`.

The different json response keys are listed in the [Kili documentation](https://docs.kili-technology.com/reference/export-classification).

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

#### Standard object detection

bounding_poly_annotations
bounding_poly
normalized_vertices

#### Point detection

point

#### Line detection

polyline

#### Pose estimation

points
point
code
name
job_name

### Video tasks

frames
is_key_frame

### Named entities recognition tasks

entity_annotations
content
begin_offset
end_offet

### Named entities recognition in PDFs tasks

content
annotations
polys
page_number_array

### Relation tasks

#### Named entities relation

start_entities
end_entities

#### Object detection relation

relation_job = parsed_jobs["OBJECT_RELATION_JOB"]

    assert relation_job.annotations[0].categories[0].name == "CATEGORY_A"
    assert relation_job.annotations[0].start_objects[0]
    assert relation_job.annotations[0].end_objects[0]
    assert relation_job.annotations[0].mid == "20230328131252526-80405"

##### `.start_objects`

##### `.end_objects`

### Children tasks

#### `.children`

Depending on the task, the `.children` attribute can be found in different places:

```python
label.jobs["CLASSIF_JOB"].category.children  # Classification task
label.jobs["OBJECT_DETECTION_JOB"].annotations[0].children  # For several kinds of tasks: object detection, NER, pose estimation, etc.
```

You can find more information about the children key in the json response in the [Kili documentation](https://docs.kili-technology.com/reference/export-classification).
