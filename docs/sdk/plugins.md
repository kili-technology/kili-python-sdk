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

The plugin you are going to upload has to contain a `class PluginHandler(PluginCore)` (in the case of the module type plugin it has to be inside `main.py`) that implements two methods for the different types of events:

- `on_submit`
- `on_review`

These methods have a predefined set of parameters:

- the `label` submitted (a dictionary containing the fields of the GraphQL type [Label](https://api-docs.kili-technology.com/types/objects/label/))
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

## Receiving Kili events

Instead of `on_submit` and `on_review`, a plugin can receive any Kili event:
decorate a method of `PluginHandler` with `on_kili_event`, and it is called with each event it subscribes to, parsed into its
[`kili_events`](https://pypi.org/project/kili-events/) model — typed fields, completion in your IDE.

```python
from kili_events import AssetSkippedEvent, AssetWorkflowEvent

from kili.plugins import PluginCore, on_kili_event


class PluginHandler(PluginCore):
    """Custom plugin"""

    @on_kili_event(AssetSkippedEvent)
    def on_skip(self, event: AssetSkippedEvent) -> None:
        self.logger.info(f"Asset {event.payload.asset_id} skipped by {event.user_id}")

    @on_kili_event(AssetWorkflowEvent, "label.workflow.*")
    def on_workflow(self, event) -> None:
        self.logger.info(f"Received {event.event} on project {event.project_id}")
```

`on_kili_event` takes any mix of:

| Argument | Receives | Example |
| --- | --- | --- |
| an event model | that event | `AssetSkippedEvent` |
| a family of events | every event of the family | `AssetWorkflowEvent`: every `asset.workflow.…` event |
| a pattern | every event it matches: `*` stands for one or more names | `"label.workflow.*"`, `"asset.*.started"` |

A method receives an event once, even when several of its arguments match it, and every method matching an event receives it.
Upload the plugin without `event_matcher`: the events it receives are read from the decorators.

```python
kili.upload_plugin(plugin_path="./my_plugin/", plugin_name="my_plugin")
```

The upload reads your code without running it, so:

- the decorated methods are those of the `PluginHandler` class of the plugin file (of `main.py` for a folder);
- the arguments are names imported from `kili_events`, or strings — a name the upload cannot trace to `kili_events`, or a
  pattern that matches no event (`"label.wokflow.*"`), stops the upload with the reason;
- a plugin receives events either with `on_kili_event` or with `on_submit`, `on_review`, `on_custom_interface_click` and
  `on_send_back_to_queue`, not both.

An event the plugin's version of `kili_events` does not know yet (Kili added it after you installed the package) is logged
and skipped. The event carries its subject (`event.event`), `organization_id`, `project_id`, `user_id` and `payload`, as its
model declares them — no event id or timestamp.

### Migrating from `on_event`

Overriding `on_event` with an `event_matcher` still works, but is deprecated in favour of `on_kili_event`. **`on_event` now
receives the whole event**: the fields it received before are under `payload["payload"]`, beside `event`,
`organizationId`, `projectId` and `userId`.

Before:

```python
class PluginHandler(PluginCore):
    def on_event(self, payload: dict) -> None:
        if payload["event"] == "asset.skipped":
            self.logger.info(f"Asset {payload['assetId']} skipped")

kili.upload_plugin(plugin_path="./my_plugin/", event_matcher=["asset.skipped"])
```

After, with `on_kili_event`:

```python
class PluginHandler(PluginCore):
    @on_kili_event(AssetSkippedEvent)
    def on_skip(self, event: AssetSkippedEvent) -> None:
        self.logger.info(f"Asset {event.payload.asset_id} skipped")

kili.upload_plugin(plugin_path="./my_plugin/")
```

Or after, keeping `on_event`:

```python
class PluginHandler(PluginCore):
    def on_event(self, payload: dict) -> None:
        if payload["event"] == "asset.skipped":
            self.logger.info(f"Asset {payload['payload']['assetId']} skipped")
```

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

    def on_submit(self, label: Dict, asset_id: str) -> None:
        """Dedicated handler for Submit action"""
        self.logger.info("On Submit called")
        custom_function(label, self.logger)
```

## Model for Plugins

::: kili.services.plugins.model.PluginCore

## Queries

::: kili.entrypoints.queries.plugins.__init__.QueriesPlugins

## Mutations

::: kili.entrypoints.mutations.plugins.__init__.MutationsPlugins
