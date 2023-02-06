from kili.plugins import PluginCore
from kili.types import Label


class PluginHandler(PluginCore):
    """
    Custom plugin instance
    """

    def check_rules_on_label(self, label: Label):

        issues_array = []
        mid_issues_array = []

        for bbox in label["jsonResponse"]["JOB_0"]["annotations"]:

            # Rule 1 - Check IBAN starts by FR
            if bbox["categories"][0]["name"] == "IBAN":
                iban = bbox["children"]["TRANSCRIPTION_JOB"]["text"]

                if iban[0:2] != "FR":
                    issues_array.append("IBAN number should start by FR")
                    mid_issues_array.append(bbox["mid"])

            # Rule 2 - Check if Currency is in list of fields
            if bbox["categories"][0]["name"] == "CURRENCY":
                currency = bbox["children"]["TRANSCRIPTION_JOB_2"]["text"]

                if currency not in ["DOLLAR", "EURO"]:
                    issues_array.append("Authorized currency are only Euro and Dollar")
                    mid_issues_array.append(bbox["mid"])

        return issues_array, mid_issues_array

    def on_submit(self, label: Label, asset_id: str) -> None:
        """
        Dedicated handler for Submit action
        """
        self.logger.info("On submit called")

        issues_array, mid_issues_array = self.check_rules_on_label(label)

        project_id = self.project_id

        if len(issues_array) > 0:
            print("Creating an issue...")

            for i, _ in enumerate(issues_array):

                self.kili.append_to_issues(
                    label_id=label["id"],
                    project_id=project_id,
                    text=issues_array[i],
                    object_mid=mid_issues_array[i],
                )

            print("Issue created!")

            self.kili.add_to_review(asset_ids=[asset_id])

            print("Asset added to review")

        accuracy = (
            100 - len(issues_array) / len(label["jsonResponse"]["JOB_0"]["annotations"]) * 100
        )

        print(accuracy)
        self.kili.update_properties_in_assets(
            asset_ids=[asset_id], json_metadatas=["{'accuracy': accuracy}"]
        )

        print("Accuracy score computed")
