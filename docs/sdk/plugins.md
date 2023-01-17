# Plugin module

## Plugins structure

A plugin is a set of :

- a `python` file
- a non mendatory `requirements.txt` file listing all the dependencies you need for you plugin.

The plugin you are going to upload has to contain a `class` and two methods for the different types of events:

- `on_submit`
- `on_review`

You can add custom methods in your class as well.

Some attributes are available in the class:

- `self.kili`
- `self.project_id`

The skeleton of the plugin should look like this:

```python
from kili.plugins import PluginCore
from kili.types import Label
import numpy as np

def custom_function():
    # Do something...

class PluginHandler(PluginCore):
    """Custom plugin"""

    def custom_method(self):
        # Do something...

    def on_review(self, label: Label, asset_id: str) -> None:
        """Dedicated handler for Review action"""
        # Do something...

    def on_submit(self, label: Label, asset_id: str) -> None:
        """Dedicated handler for Submit action"""
        # Do something...
```

!!! note

    The plugins run has some limitations, it can use a maximum of 512mb of ram and will timeout after 60sec of run

## Model for Plugins
::: kili.services.plugins.model.PluginCore
## Queries
::: kili.queries.plugins.__init__.QueriesPlugins
## Mutations
::: kili.mutations.plugins.__init__.MutationsPlugins
