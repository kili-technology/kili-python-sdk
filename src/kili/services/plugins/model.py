"""Develop Plugins for Kili"""

import logging
from typing import Dict, Optional

from kili.client import Kili
from kili.services.plugins.helpers import get_logger


class PluginCore:
    """
    Kili Plugin core class

    Args:
        kili: kili instance that plugins can make use of
        project_id: the project on which plugin is ran

    Implements:

        on_submit(self, label: Label, asset_id: str)
        on_review(self, label: Label, asset_id: str)

    # Warning : if using a custom init, be sure to call super().__init__()
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
        label: Dict,
        asset_id: str,
    ) -> None:
        """
        Handler for the submit action, triggered when a default label is submitted into Kili.

        Args:
            label: Label submitted to Kili: a dictionary containing the following fields:
                `id`, `labelType`, `numberOfAnnotations`, `authorId`, `modelName`, `jsonResponse`,
                `secondsToLabel`, `isSentBackToQueue`, `search` and some technical fields:
                `createdAt`, `updatedAt`, `version`, `isLatestReviewLabelForUser`,
                `isLatestLabelForUser`, `isLatestDefaultLabelForUser`, `readPermissionsFromProject`.
            asset_id: Id of the asset on which the label was submitted

        Example use:

            >>> def on_submit(self, label: Label, asset_id: str):
            >>>     json_response = label.get('jsonResponse')
            >>>     if label_is_respecting_business_rule(json_response):
            >>>         return
            >>>     else:
            >>>         self.kili.send_back_to_queue(asset_ids=[asset_id])

        """
        # pylint: disable=unused-argument
        self.logger.warning("Method not implemented. Define a custom on_submit on your plugin")
        pass  # pylint: disable=unnecessary-pass

    def on_review(
        self,
        label: Dict,
        asset_id: str,
    ) -> None:
        """
        Handler for the review action, triggered when a default label is reviewed on Kili

        Args:
            label: Label submitted to Kili: a dictionary containing the following fields:
                `id`, `labelType`, `numberOfAnnotations`, `authorId`, `modelName`, `jsonResponse`,
                `secondsToLabel`, `isSentBackToQueue`, `search` and `reviewedLabel` (dictionary
                that has a field `id` representing the id of the original label that was reviewed).
                It also contains some technical fields: `createdAt`, `updatedAt`, `version`,
                `isLatestReviewLabelForUser`, `isLatestLabelForUser`, `isLatestDefaultLabelForUser`,
                `readPermissionsFromProject`.
            asset_id: Id of the asset on which the label was submitted

        Example use:

            >>> def on_review(self, label: Label, asset_id: str):
            >>>     json_response = label.get('jsonResponse')
            >>>     if label_is_respecting_business_rule(json_response):
            >>>         return
            >>>     else:
            >>>         self.kili.send_back_to_queue(asset_ids=[asset_id])
        """
        # pylint: disable=unused-argument
        self.logger.warning("Method not implemented. Define a custom on_review on your plugin")
        pass  # pylint: disable=unnecessary-pass

    def on_custom_interface_click(
        self,
        label: Dict,
        asset_id: str,
    ) -> None:
        """
        Handler for the custom interface click action.

        **Warning**: This handler is in beta and is still in active development,
        so it should not be used.

        Args:
            label: label submitted to Kili
            asset_id: id of the asset on which the action is called
        """
        # pylint: disable=unused-argument
        self.logger.warning("Handler is in active development.")
