# Kili Playground

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