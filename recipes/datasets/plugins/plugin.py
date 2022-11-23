from kili.plugins import PluginCore
from kili.types import Label


def check_rules_on_label(label: Label):
    """
    my custom handle method
    """
    label_id = label["id"]
    jsonResponse = label["jsonResponse"]

    print(f"Started searching for issues for label {label_id}")

    annotations_for_job0 = jsonResponse["JOB_0"]["annotations"]

    issues_array = []
    mid_issues_array = []

    for bbox in annotations_for_job0:

        if bbox["categories"][0]["name"] == "IBAN":
            iban = bbox["children"]["TRANSCRIPTION_JOB"]["text"]

            if iban[0:2] != "FR":
                issues_array.append("IBAN number should start by FR")
                mid_issues_array.append(bbox["mid"])

        if bbox["categories"][0]["name"] == "CURRENCY":
            currency = bbox["children"]["TRANSCRIPTION_JOB_2"]["text"]

            if currency not in ["USD", "EUR"]:
                issues_array.append("Authorized currency are only Euro and Dollar")
                mid_issues_array.append(bbox["mid"])

    print(f"Finished searching for issues for label {label_id}")
    return issues_array, mid_issues_array


class PluginHandler(PluginCore):
    """
    Custom plugin instance
    """

    def on_review(self, label: Label, asset_id: str) -> None:
        """
        Dedicated handler for Review action
        """
        super().on_review(label, asset_id)
        self.logger.info("No action on review for now")

    def on_submit(self, label: Label, asset_id: str) -> None:
        """
        Dedicated handler for Review action
        """
        self.logger.info("On submit called")

        label_id = label["id"]
        annotations_for_job0 = label["jsonResponse"]["JOB_0"]["annotations"]

        issues_array, mid_issues_array = check_rules_on_label(label)

        project_id = self.project_id

        if len(issues_array) > 0:
            print("Creating an issue...")

            for i, _ in enumerate(issues_array):

                self.kili.append_to_issues(
                    label_id=label_id,
                    project_id=project_id,
                    object_mid=mid_issues_array[i],
                    text=issues_array[i],
                )

            self.kili.send_back_to_queue(asset_ids=[asset_id])

            print("Issue created!")

        accuracy = 100 - len(issues_array) / len(annotations_for_job0) * 100

        self.kili.update_properties_in_assets(
            asset_ids=[asset_id], json_metadatas=[{"accuracy": accuracy}]
        )
