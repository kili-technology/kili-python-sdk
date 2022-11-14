def onSubmit(label, projectId, assetId):
    jsonResponse = label["jsonResponse"]

    label_id = label["id"]
    project_id = projectId
    asset_id = assetId

    annotations_for_job0 = jsonResponse["JOB_0"]["annotations"]

    print(f"Started searching for issues for label {label_id}")

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

    if len(issues_array) > 0:
        print("Creating an issue...")

        for i, issue in enumerate(issues_array):

            kili.append_to_issues(
                label_id=label_id,
                project_id=project_id,
                object_mid=mid_issues_array[i],
                text=issues_array[i],
            )

        kili.send_back_to_queue(asset_ids=[asset_id])

        print("Issue created!")

    accuracy = 100 - len(issues_array) / len(annotations_for_job0) * 100

    kili.update_properties_in_assets(asset_ids=[asset_id], json_metadatas=[{"accuracy": accuracy}])

    print(f"Finished searching for issues for label {label_id}")


def onReview(label, projectId, assetId):
    pass
