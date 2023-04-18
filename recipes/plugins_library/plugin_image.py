"""My custom plugin for bills."""
from typing import Dict

from kili.plugins import PluginCore


def check_rules_on_label(label: Dict):
    # custom methods
    print("Custom method - checking number of bboxes")

    counter = 0
    issues_array = []
    for annotation in label["jsonResponse"]["JOB_0"]["annotations"]:
        if annotation["categories"][0]["name"] == "OBJECT_A":
            counter += 1

    if counter <= 1:
        return issues_array
    issues_array.append([f"There are too many BBox ({counter}) - Only 1 BBox of Object A accepted"])
    return issues_array


class PluginHandler(PluginCore):
    """Custom plugin instance."""

    def on_submit(self, label: Dict, asset_id: str) -> None:
        """Dedicated handler for Submit action."""
        self.logger.info("On submit called")

        issues_array = check_rules_on_label(label)

        project_id = self.project_id

        if len(issues_array) > 0:
            print("Creating an issue...")

            self.kili.create_issues(
                project_id=project_id,
                label_id_array=[label["id"]] * len(issues_array),
                text_array=issues_array,
            )

            print("Issue created!")

            self.kili.send_back_to_queue(asset_ids=[asset_id])
