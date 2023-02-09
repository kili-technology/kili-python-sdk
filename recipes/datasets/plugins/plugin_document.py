from kili.plugins import PluginCore
from kili.types import Label


class PluginHandler(PluginCore):
    """
    Custom plugin instance
    """

    @staticmethod
    def check_rules_on_label(label: Label):
        """
        Method for business logic
        """

        text_issues_array = []
        mid_issues_array = []

        for bbox in label["jsonResponse"]["JOB_0"]["annotations"]:

            # Rule 1 - Check IBAN starts by FR
            if bbox["categories"][0]["name"] == "IBAN":
                iban = bbox["children"]["TRANSCRIPTION_JOB"]["text"]

                if iban[0:2] != "FR":
                    text_issues_array.append("IBAN number should start by FR")
                    mid_issues_array.append(bbox["mid"])

            # Rule 2 - Check if Currency is in list of fields
            if bbox["categories"][0]["name"] == "CURRENCY":
                currency = bbox["children"]["TRANSCRIPTION_JOB_2"]["text"]

                if currency not in ["DOLLAR", "EURO"]:
                    text_issues_array.append("Authorized currencies are only Euro and Dollar")
                    mid_issues_array.append(bbox["mid"])

        return text_issues_array, mid_issues_array

    def on_submit(self, label: Label, asset_id: str) -> None:
        """
        Dedicated handler for Submit action
        """
        self.logger.info("On submit called")

        text_issues_array, mid_issues_array = self.check_rules_on_label(label)

        project_id = self.project_id

        n_issues = len(text_issues_array)

        for i in range(n_issues):

            self.kili.append_to_issues(
                label_id=label["id"],
                project_id=project_id,
                text=text_issues_array[i],
                object_mid=mid_issues_array[i],
            )

        self.kili.add_to_review(asset_ids=[asset_id])

        n_annotations = len(label["jsonResponse"]["JOB_0"]["annotations"])

        accuracy = (1 - n_issues / n_annotations) * 100

        self.kili.update_properties_in_assets(
            asset_ids=[asset_id], json_metadatas=[f"{{'accuracy': {accuracy}}}"]
        )
