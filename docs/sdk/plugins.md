# Plugin module

## Plugins structure

A plugin is an uploaded Python script triggered by an event. It can be defined as either :

- a single `python` file with everything inside
- a plugin module (a folder) containing multiple `python` files and a non mandatory `requirements.txt` file listing all the dependencies you need for you plugin.

In the case of the module type plugin, at the root of the folder a file named `main.py` is strictly necessary, as it serves as the entrypoint of the plugin. In this `main.py` file, you can import what you need from other `python` files in the folder. The structure of the folder can be the following (the only constraint being the presence of the `main.py` file):

```
plugin_folder
|__ main.py
|__ other_file.py
|__ requirements.txt
|
|___helpers
    |__ helper.py
```

The plugin you are going to upload has to contain a `class PluginHandler(PluginCore)` (in the case of the module type plugin it has to be inside `main.py`) that implements two methods for the different types of events:

- `on_submit`
- `on_review`

These methods have a predefined set of parameters:

- the `label` submitted (a dictionary containing the fields of the GraphQL type [Label](https://docs.kili-technology.com/reference/graphql-api#label))
- the `asset_id` of the asset labeled

You can add custom methods in your class as well.

Moreover, some attributes are directly available in the class:

- `self.kili`
- `self.project_id`

Therefore, the skeleton of the plugin (of `main.py` in the case of the module type plugin) should look like this:

```python
from typing import Dict
import numpy as np

from kili.plugins import PluginCore

def custom_function():
    # Do something...

class PluginHandler(PluginCore):
    """Custom plugin"""

    def custom_method(self):
        # Do something...

    def on_review(self, label: Dict, asset_id: str) -> None:
        """Dedicated handler for Review action"""
        # Do something...

    def on_submit(self, label: Dict, asset_id: str) -> None:
        """Dedicated handler for Submit action"""
        # Do something...
```

!!! note
    The plugins run has some limitations, it can use a maximum of 512 MB of ram and will timeout after 60 sec of run.

## Model for Plugins

::: kili.services.plugins.model.PluginCore
    options:
        filters:
            - '!on_custom_interface_click'

## Queries

::: kili.entrypoints.queries.plugins.__init__.QueriesPlugins

## Mutations

::: kili.entrypoints.mutations.plugins.__init__.MutationsPlugins
