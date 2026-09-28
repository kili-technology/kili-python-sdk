"""Develop Plugins for Kili."""

import logging
from typing import Optional

from kili_events import UnknownEventError, matches_subject, parse_event

from kili.client import Kili
from kili.services.plugins.events import subscribed_methods
from kili.services.plugins.helpers import get_logger


class PluginCore:
    """Kili Plugin core class.

    Args:
        kili: kili instance that plugins can make use of
        project_id: the project on which plugin is ran

    Implements:

        on_submit(self, label: Dict, asset_id: str)
        on_review(self, label: Dict, asset_id: str)
        on_custom_interface_click(self, label: Dict, asset_id: str)
        on_send_back_to_queue(self, asset_id: str)

    or methods decorated with `@on_kili_event`, which receive the Kili events they
    subscribe to as kili_events models.

    !!! warning
        if using a custom init, be sure to call super().__init__()
    """

    logger: logging.Logger
    kili: Kili
    project_id: str

    def __init__(
        self, kili: Kili, project_id: str, logger: Optional[logging.Logger] = None
    ) -> None:
        self.kili = kili
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
                    self.kili.send_back_to_queue(asset_ids=[asset_id])
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
                    self.kili.send_back_to_queue(asset_ids=[asset_id])
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
                    self.kili.create_issues(
                            project_id=self.project_id,
                            label_id_array=[label_id],
                            text_array=[issue]
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
        """Receives every event of the plugin, and calls the methods subscribed to it.

        The event is parsed into its kili_events model, then passed to each method whose
        `@on_kili_event` matches it. Decorate methods rather than overriding this one.

        Args:
            payload: The event as Kili sends it: `event` (its subject, e.g. `asset.skipped`),
                `organizationId`, `projectId`, `userId` and `payload`, for the fields the
                event declares.
        """
        subject = payload.get("event")
        subscriptions = subscribed_methods(type(self))
        handlers = [
            name
            for name, patterns in subscriptions.items()
            if isinstance(subject, str) and any(matches_subject(p, subject) for p in patterns)
        ]
        if not handlers:
            self.logger.warning(
                f"No method of the plugin subscribes to the event '{subject}' "
                f"(subscriptions: {subscriptions or 'none'})."
            )
            return

        try:
            event = parse_event(payload)
        except UnknownEventError as error:
            self.logger.warning(f"{error} The event is ignored.")
            return

        for name in handlers:
            getattr(self, name)(event)
