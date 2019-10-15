# Image and Text Annotation Tool - Kili Playground

## What is Kili Technology?

Kili Technology is an image, text and voice data annotation tool designed to help companies deploy machine learning applications faster. In a few minutes you can start annotating your data thanks to a catalogue of intuitive and configurable interfaces. You can easily accelerate the labeling process by connecting one of your models to pre annotate the data. The work of the annotators is 2 to 5 times faster. Kili Technology facilitates collaboration between technical teams and the business, but also with outsourced annotation companies. Data governance is managed, and production quality control is facilitated. Kili Technology meets the needs of small teams as well as those of large companies with massive stakes.

Kili Technology allows you to:

- Quickly annotate thanks to simple and intuitive interfaces
- Easily ingest data, in drag & drop, from your cloud provider, or while keeping your data On Premise, when necessary.
- Manage participants, roles and responsibilities
- Monitor production quality using leading indicators and workflows for production monitoring and data quality validation
- Easily export the produced data

## What is Kili Playground ?

Kili Playground is a Python client wrapping the GraphQL API of Kili Technology.
It allows data scientists and developers to control Kili Technology from an IDE.

## Installation

- Clone the repository
```bash
git clone https://github.com/kili-technology/kili-playground.git
cd kili-playground
```

- Set PYTHONPATH to point to the repository
```
export PYTHONPATH=$PYTHONPATH:/path/to/kili-playground
```

## Get started

Follow the [technical documentation](https://kili-technology.github.io/kili-docs/docs/api-graphql/api-graphql).


## Change interface

Changing the interface of a given project:
```python
from kili.authentication import authenticate
client, user_id = authenticate('EMAIL', 'PASSWORD')
from kili.mutations.project import update_interface_in_project
json_settings = "{\"tools\":[\"polygon\",\"rectangle\"],\"annotation_types\": { \"GRAPE\": \"Grape\", \"HIHI\": \"HIHI\"}}"
update_interface_in_project(client, 'PROJECT_ID', json_settings)
```
Almost all image related interfaces have the same json structure with 2 properties: tools, annotation types:

example:
```json
{
  "tools": ["polygon","rectangle"],
  "annotation_types": { "GRAPE": "Grape", "LEAF": "Leaf"},
}
```

except for IMAGE_WITH_SEARCH interface, where we have also the metadata
