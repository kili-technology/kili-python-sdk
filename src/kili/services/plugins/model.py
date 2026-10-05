"""Develop Plugins for Kili."""

import logging
import sys
import warnings
from typing import Optional, Union

from typing_extensions import deprecated

from kili.client import Kili as KiliLegacy
from kili.client_domain import Kili
from kili.services.plugins.helpers import PLUGIN_CORE_DEPRECATION, get_logger

if not sys.warnoptions:  # -W and PYTHONWARNINGS win
    # Attributed to the plugin's class line, the warning would fall under Python's default ignore
    # outside __main__, where plugins are written: a module that a notebook or a runner imports.
    warnings.filterwarnings(
        "default", message=r"`kili\.plugins\.PluginCore` is deprecated", category=DeprecationWarning
    )


class _PluginBase:
    """The handlers a plugin implements, shared by `Plugin` and the deprecated `PluginCore`."""

    logger: logging.Logger
    project_id: str

    def __init__(self, project_id: str, logger: Optional[logging.Logger] = None) -> None:
        self.project_id = project_id
        if logger:
            self.logger = logger
        else:
            self.logger = get_logger()

    def on_submit(
        self,
        label: dict,
        asset_id: str,
    ) -> None:
        """Handler for the submit action, triggered when a default label is submitted into Kili.

        Args:
            label: Label submitted to Kili: a dictionary containing the following fields:
                `id`, `labelType`, `numberOfAnnotations`, `authorId`, `modelName`, `jsonResponse`,
                `secondsToLabel`, `isSentBackToQueue`, `search` and some technical fields:
                `createdAt`, `updatedAt`, `version`, `isLatestReviewLabelForUser`,
                `isLatestLabelForUser`, `isLatestDefaultLabelForUser`,
                `readPermissionsFromProject`.
            asset_id: Id of the asset on which the label was submitted

        !!! example
            ```python
            def on_submit(self, label: Dict, asset_id: str):
                json_response = label.get('jsonResponse')
                if label_is_respecting_business_rule(json_response):
                    return
                else:
                    self.kili.assets.invalidate(asset_id=asset_id, project_id=self.project_id)
            ```
        """
        # pylint: disable=unused-argument
        self.logger.warning("Method not implemented. Define a custom on_submit on your plugin")

    def on_review(
        self,
        label: dict,
        asset_id: str,
    ) -> None:
        """Handler for the review action, triggered when a default label is reviewed on Kili.

        Args:
            label: Label submitted to Kili: a dictionary containing the following fields:
                `id`, `labelType`, `numberOfAnnotations`, `authorId`, `modelName`, `jsonResponse`,
                `secondsToLabel`, `isSentBackToQueue` and `search` (dictionary that has a field `id`
                representing the id of the original label that was reviewed). It also contains some
                technical fields: `createdAt`, `updatedAt`, `version`, `isLatestReviewLabelForUser`,
                `isLatestLabelForUser`, `isLatestDefaultLabelForUser`, `readPermissionsFromProject`.
            asset_id: Id of the asset on which the label was submitted

        !!! example
            ```python
            def on_review(self, label: Dict, asset_id: str):
                json_response = label.get('jsonResponse')
                if label_is_respecting_business_rule(json_response):
                    return
                else:
                    self.kili.assets.invalidate(asset_id=asset_id, project_id=self.project_id)
            ```
        """
        # pylint: disable=unused-argument
        self.logger.warning("Method not implemented. Define a custom on_review on your plugin")

    def on_custom_interface_click(
        self,
        label: dict,
        asset_id: str,
    ) -> None:
        """Handler for the custom interface click action.

        !!! warning
            This handler is in beta and is still in active development,
            it should be used with caution.

        Args:
            label: Label submitted to Kili: a dictionary containing the following fields:
                `id`, `jsonResponse`.
            asset_id: id of the asset on which the action is called

        !!! example
            ```python
            def on_custom_interface_click(self, label: Dict, asset_id: str):
                json_response = label.get('jsonResponse')`
                label_id = label.get('id')
                issue = label_is_respecting_business_rule(json_response)
                if !issue:
                    return
                else:
                    self.kili.issues.create(
                        project_id=self.project_id, label_id=label_id, text=issue
                    )
            ```
        """
        # pylint: disable=unused-argument
        self.logger.warning("Handler is in active development.")

    def on_send_back_to_queue(
        self,
        asset_id: str,
    ) -> None:
        """Handler for send back to queue.

        Triggered when an asset is sent back to queue

        !!! warning
            This handler is in beta and is still in active development,
            it should be used with caution.

        Args:
            asset_id: Id of the asset on which was sent back to queue

        !!! example
            ```python
            def on_send_back_to_queue(self, asset_id: str):
                self.logger.info(f"Asset {asset_id} was sent back to queue")
            ```
        """
        # pylint: disable=unused-argument
        self.logger.warning("Handler is in active development.")

    def on_event(
        self,
        payload: dict,
    ) -> None:
        """Handler for all events, triggered when an event is triggered.

        Args:
            payload: Dict.
        """
        # pylint: disable=unused-argument
        self.logger.warning("Method not implemented. Define a custom on_event on your plugin")


class Plugin(_PluginBase):
    """Kili plugin base class: a plugin is a class named `PluginHandler` that subclasses it.

    `self.kili` is the domain client (`kili.assets.list(...)`, `kili.issues.create(...)`). Its
    `legacy_client` attribute keeps the legacy client's methods, for a plugin moving from
    `PluginCore` one call at a time.

    Args:
        kili: The client the plugin runner gives the plugin. A legacy client is wrapped without
            signing in again; a domain client is used as is.
        project_id: The project on which the plugin is run.
        logger: The logger whose messages appear in the plugin's logs. Defaults to a local logger.

    Implements:

        on_submit(self, label: Dict, asset_id: str)
        on_review(self, label: Dict, asset_id: str)
        on_custom_interface_click(self, label: Dict, asset_id: str)
        on_send_back_to_queue(self, asset_id: str)
        on_event(self, payload: Dict)

    !!! warning
        if using a custom init, be sure to call super().__init__()

    !!! example
        ```python
        from typing import Dict

        from kili.plugins import Plugin

        class PluginHandler(Plugin):
            def on_submit(self, label: Dict, asset_id: str):
                self.kili.issues.create(
                    project_id=self.project_id, label_id=label["id"], text="Check the boxes"
                )
                # a legacy call, kept until it is migrated
                self.kili.legacy_client.send_back_to_queue(asset_ids=[asset_id])
        ```
    """

    kili: Kili

    def __init__(
        self,
        kili: Union[Kili, KiliLegacy],
        project_id: str,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(project_id, logger)
        self.kili = Kili.from_legacy(kili) if isinstance(kili, KiliLegacy) else kili


@deprecated(PLUGIN_CORE_DEPRECATION, category=None)  # the IDE's strikethrough; it warns itself
class PluginCore(_PluginBase):
    """Kili plugin base class giving the plugin the legacy client as `self.kili`.

    !!! warning "Deprecated"
        Subclass `kili.plugins.Plugin` instead: `self.kili` is then the domain client, and
        `self.kili.legacy_client` keeps the legacy client's methods while the plugin migrates.
        `PluginCore` keeps working until a future major release.

    Args:
        kili: The legacy client the plugin runner gives the plugin. A domain client is unwrapped.
        project_id: The project on which the plugin is run.
        logger: The logger whose messages appear in the plugin's logs. Defaults to a local logger.
    """

    kili: KiliLegacy

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        warnings.warn(
            PLUGIN_CORE_DEPRECATION, DeprecationWarning, stacklevel=2
        )  # the plugin's line

    def __init__(
        self,
        kili: Union[KiliLegacy, Kili],
        project_id: str,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(project_id, logger)
        self.kili = kili.legacy_client if isinstance(kili, Kili) else kili
        # the plugin's run logs are where its authors read: stderr reaches only the runner's
        self.logger.warning(PLUGIN_CORE_DEPRECATION)
