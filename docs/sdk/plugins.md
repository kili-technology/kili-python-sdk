# Plugin module

## Plugins structure

A plugin is an uploaded Python script triggered by an event. It can be defined as either :

- a single `python` file with everything inside
- a plugin module (a folder) containing multiple `python` files and a non mandatory `requirements.txt` file listing all the dependencies you need for you plugin (providing `requirements.txt` is not available for On-Premise deployments - see details below).

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


> **Note**: `on_submit` and `on_review` handlers are deprecated. Please use `on_event` instead. If your plugin was already uploaded with thoses handlers, it will still work. If you want the same behavior as `on_submit` and `on_review`, when you upload your plugin, you can use `event_matcher=["labels.created.submit"]` for `on_submit` and `event_matcher=["labels.created.review"]` for `on_review` events.


The plugin you are going to upload has to contain a `class PluginHandler(PluginCore)` (in the case of the module type plugin it has to be inside `main.py`) that implements one method for the different types of events:

- `on_event`

These methods have a predefined set of parameter:

- the `payload` submitted (a dictionary containing the fields for your plugins)
    - `payload.event` the name of the event (ex: for submit : `labels.created.submit`, for review `labels.created.review`)
    - `payload.label` the label containing the fields of the GraphQL type [Label](https://api-docs.kili-technology.com/types/objects/label/)

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

    def on_event(self, payload: dict) -> None: # This can replace on_review method
        """Dedicated handler for Review action"""
        event = payload.get("event")

        if event == 'labels.created.review':
        # Do something...

    def on_event(self, payload: dict) -> None: # This can replace on_submit method
        """Dedicated handler for Submit action"""
        event = payload.get("event")

        if event == 'labels.created.submit':
        # Do something...
```

!!! note
    The plugins run has some limitations, it can use a maximum of 512 MB of ram and will timeout after 60 sec of run.

## On-Premise deployment details

The plugins for the on-premise deployments work exactly the same as the plugins for the SaaS version of Kili, with only a few small exceptions :

1. It's not possible to add custom python packages to your plugin with the help of the `requirements.txt` file, but we selected a list of the most useful packages that you can directly use, including :
    * `numpy`, `pandas`, `scikit-learn`, `opencv-python-headless`, `Pillow`, `requests`, `uuid` and of course `kili`
2. In order to save the logs during the execution of your plugin, you should only use the provided logger in the plugin class (the simple `print` function will not save the log). For an example, see the code below:

```python
from logging import Logger
from typing import Dict
from kili.plugins import PluginCore

def custom_function(label: Dict, logger: Logger):
    logger.info("Custom function called")
    # Do something...

class PluginHandler(PluginCore):
    """Custom plugin"""

    def on_event(self, payload: dict) -> None:
        """Dedicated handler for Submit action"""
        event = payload.get("event")
        if event == 'labels.created.submit':
            self.logger.info("On Submit called")
            label = payload["label"]
            custom_function(label, self.logger)
```

## Model for Plugins

::: kili.services.plugins.model.PluginCore
    options:
      filters:
        - "!^on_review$"
        - "!^on_submit$"

## Queries

::: kili.entrypoints.queries.plugins.__init__.QueriesPlugins

## Mutations

::: kili.entrypoints.mutations.plugins.__init__.MutationsPlugins
