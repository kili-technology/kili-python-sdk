from kili.event.presentation.client.event import EventClientMethods

mock_list_events = [
    {
        "createdAt": "2024-12-10T14:38:17.222Z",
        "event": "projects.created",
        "id": "event_id",
        "organizationId": "organization_1",
        "payload": {"id": "payload_id", "title": "Computer vision tutorial", "inputType": "IMAGE"},
        "projectId": "project_id",
        "userId": "user_1",
    },
    {
        "createdAt": "2024-12-10T14:38:40.395Z",
        "event": "labels.created.submit",
        "id": "event_id_2",
        "organizationId": "organization_1",
        "payload": {
            "label": {
                "id": "label_id",
                "search": {
                    "numberOfAnnotations": 1,
                    "numberOfAnnotationsByObject": {"JOB_0.CAR": 1},
                },
                "assetId": "asset_id",
                "version": 0,
                "authorId": "user_1",
                "createdAt": "2024-12-10T14:38:40.200Z",
                "labelType": "DEFAULT",
                "updatedAt": "2024-12-10T14:38:40.200Z",
                "clientVersion": 0,
                "secondsToLabel": 10,
                "numberOfAnnotations": 1,
                "totalSecondsToLabel": 10,
                "deltaNumberAnnotations": 1,
            },
            "author": {"isServiceAccount": False},
            "assetId": "assset_id",
        },
        "projectId": "project_id",
        "userId": "user_1",
    },
]


def test_list_events(mocker):
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.list_events.return_value = mock_list_events

    kili_event = EventClientMethods(kili_api_gateway)
    result = kili_event.list(project_id="project_id")

    assert result == mock_list_events
