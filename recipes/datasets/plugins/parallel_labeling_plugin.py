from kili.plugins import PluginCore
from kili.types import Label

# Aggregate labels labeled from multiple labelers labeling the same assets through consensus
# Caution - Only working for classification and object detection job - If needed could be extended easily


class PluginHandler(PluginCore):
    """
    Custom plugin instance
    """

    def aggregate_classification_label(self, classif_job_key, labels_array):
        json_response = {}

        for label in labels_array:
            # If classification jobs filled by multiple labelers the last value is kept

            keys = set(label["jsonResponse"].keys()).intersection(classif_job_key)
            json_response.update({k: v for k, v in label["jsonResponse"].items() if k in keys})

        return json_response

    def aggregate_object_detection_label(self, object_job_key, labels_array):
        json_response = {}

        for key in object_job_key:
            job_annotation = []
            for label in labels_array:
                if key in label["jsonResponse"]:
                    for annotation in label["jsonResponse"][key]["annotations"]:
                        job_annotation.append(annotation)
            json_response.update({key: {"annotations": job_annotation}})

        return json_response

    def on_submit(self, label: Label, asset_id: str) -> None:
        """
        Dedicated handler for Submit action
        """

        project_id = self.project_id

        project_info = self.kili.projects(
            project_id=project_id, fields=["minConsensusSize", "jsonInterface"]
        )[0]

        json_interface = project_info["jsonInterface"]
        min_consensus_size = project_info["minConsensusSize"]

        classif_job_key = [
            k for k, v in json_interface["jobs"].items() if v["mlTask"] == "CLASSIFICATION"
        ]
        object_job_key = [
            k for k, v in json_interface["jobs"].items() if v["mlTask"] == "OBJECT_DETECTION"
        ]

        labels_array = self.kili.labels(
            project_id=project_id,
            asset_id=asset_id,
            type_in=["DEFAULT"],
            fields=[
                "id",
                "jsonResponse",
                "isLatestLabelForUser",
            ],
        )

        latest_labels = list(filter(lambda x: x["isLatestLabelForUser"] is True, labels_array))

        if len(latest_labels) == min_consensus_size:
            json_response_array = self.aggregate_object_detection_label(
                object_job_key, latest_labels
            )
            json_response_array.update(
                self.aggregate_classification_label(classif_job_key, latest_labels)
            )

            self.kili.append_labels(
                asset_id_array=[asset_id], json_response_array=[json_response_array]
            )
