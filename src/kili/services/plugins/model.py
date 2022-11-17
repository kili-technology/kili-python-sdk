from typing import Optional
import logging
from kili.client import Kili
from kili.types import Label

class PluginParams(object):
    """
    Base plugin init argument
    :param logger: logger that plugins can make use of
    :param project_id: the project on which plugin is ran
    :param run_id: a unique identifier for the plugin run
    """
    logger: logging.Logger
    project_id: Optional[str]
    run_id: Optional[str]

    def __init__(self, logger: Optional[logging.Logger] = None, project_id: Optional[str] = None, run_id: Optional[str] = None) -> None:
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger()
        self.project_id = project_id
        self.run_id = run_id
    


    
class PluginCore(PluginParams):
    """
    Kili Plugin core class

    :param kili: kili instance that plugins can make use of

    Implements
    on_submit(self, label: Label, asset_id: str, project_id: str)
    on_review(self, label: Label, asset_id: str, project_id: str)
    """
    kili: Kili

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, kili: Kili, plugin_params: Optional[PluginParams] = None) -> None:
        self.kili = kili
        if plugin_params:
            super().__init__(**plugin_params.__dict__)


    def on_submit(self, label: Label, asset_id: str, project_id: str) -> None:
        """
        Handler for the submit action, triggered when a default label is submitted into Kili
        :param label: label submitted to Kili
        :param asset_id: id of the asset on which the label was submitted
        :param project_id: id of the project on which the label was submitted

        Example use: 
        def on_submit(self, label: Label, project_id: str, asset_id: str):
            json_response = label.get('jsonResponse')
            if label_is_respecting_business_rule(json_response):
                return
            else:
                self.kili.send_back_to_queue(asset_ids=[asset_id])

        """
        self.logger.warn('Method not implemented. Define a custom on_submit on your plugin')
        pass
    
    def on_review(self, label: Label, asset_id: str, project_id: str, ) -> None:
        """
        Handler for the submit action, triggered when a default label is submitted into Kili
        :param label: label submitted to Kili
        :param asset_id: id of the asset on which the label was submitted
        :param project_id: id of the project on which the label was submitted

        Example use: 
        def on_review(self, label: Label, project_id: str, asset_id: str):
            json_response = label.get('jsonResponse')
            if label_is_respecting_business_rule(json_response):
                return
            else:
                self.kili.send_back_to_queue(asset_ids=[asset_id])
        """
        self.logger.warn('Method not implemented. Define a custom on_review on your plugin')
        pass