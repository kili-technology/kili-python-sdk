"""
My custom plugin for bills
"""
from kili.plugins import PluginCore
from kili.types import Label


def check_rules_on_label(label: Label):
    # custom methods
    print("Custom method - checking number of bboxes")

    counter = 0
    for annotation in label["jsonResponse"]["JOB_0"]["annotations"]:
        if annotation["categories"][0]["name"] == "OBJECT_A":
            counter += 1

    if counter == 0:
        return []
    return [f"There are too many BBox ({counter}) - Only 1 BBox of Object A accepted"]


class PluginHandler(PluginCore):
    """
    Custom plugin instance
    """

    def on_submit(self, label: Label, asset_id: str) -> None:
        """
        Dedicated handler for Submit action
        """
        self.logger.info("On submit called")

        issues_array = check_rules_on_label(label)

        project_id = self.project_id

        if len(issues_array) > 0:
            print("Creating an issue...")

            for i, _ in enumerate(issues_array):

                self.kili.append_to_issues(
                    label_id=label["id"],
                    project_id=project_id,
                    text=issues_array[i],
                )

            print("Issue created!")

            self.kili.send_back_to_queue(asset_ids=[asset_id])
