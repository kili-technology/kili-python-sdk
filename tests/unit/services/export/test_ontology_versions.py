"""Tests of the ontology versions of an export: each label's, their ontologies and manifest."""

import json
from pathlib import Path
from zipfile import ZipFile

import pytest
import pytest_mock

from kili.exceptions import GraphQLError
from kili.services.export import AbstractExporter, export_labels
from kili.services.export.exceptions import NotCompatibleOptions
from tests.fakes.fake_kili import FakeKili, mocked_kili_api_gateway_get_project

ONTOLOGIES = {1: {"jobs": {"OLD_JOB": {}}}, 2: {"jobs": {"JOB_0": {}}}}


def _label(version):
    return {
        "author": {"id": "u", "email": "a@kili.test", "firstname": "Ada", "lastname": "L"},
        "createdAt": "2026-01-01T10:00:00Z",
        "isLastForStep": True,
        "isLatestLabelForUser": True,
        "isSentBackToQueue": False,
        "jsonResponse": {"JOB_0": {"annotations": []}},
        "labelType": "DEFAULT",
        "modelName": None,
        "recordedOntologyVersion": version,
    }


def _assets(_filters, fields, _options):
    """An asset labeled on version 1, one on version 2, one before versioning.

    Each holds its label in the field the export type asks for; the label on version 1 was sent
    back.
    """
    labels_field = next(
        field.split(".")[0] for field in fields if field.endswith(".isSentBackToQueue")
    )
    assets = []
    for external_id, version in (("on-1", 1), ("on-2", 2), ("before", None)):
        label = {**_label(version), "isSentBackToQueue": version == 1}
        if f"{labels_field}.recordedOntologyVersion" not in fields:
            del label["recordedOntologyVersion"]
        assets.append(
            {
                "content": "https://example.com/image.jpg",
                "externalId": external_id,
                "id": external_id,
                "jsonContent": "",
                "jsonMetadata": {},
                labels_field: label if labels_field == "latestLabel" else [label],
            }
        )
    return assets


@pytest.fixture(name="kili")
def fixture_kili(mocker: pytest_mock.MockerFixture):
    mocker.patch.object(AbstractExporter, "_check_and_ensure_asset_access", return_value=None)
    kili = FakeKili()
    kili.kili_api_gateway.list_assets.side_effect = _assets
    kili.kili_api_gateway.count_assets.return_value = 3
    # The fake's gateway outlives a test
    kili.kili_api_gateway.list_ontology_version_snapshots.reset_mock()
    kili.kili_api_gateway.list_ontology_version_snapshots.side_effect = (
        lambda _project_id, numbers: [
            {"jsonInterface": json.dumps(ONTOLOGIES[number]), "number": number}
            for number in numbers
        ]
    )
    return kili


def _on_version(kili, current, snapshots_error=None):
    """Put the project on ontology version `current`.

    None is ontology versioning off; an error is raised, as a Kili version without ontology
    versions answers. `snapshots_error` is what a Kili version that knows the project's version but
    does not export the versions answers.
    """

    def get_project(project_id, fields):
        if list(fields) == ["ontologyVersionNumber"]:
            if isinstance(current, Exception):
                raise current
            return {"ontologyVersionNumber": current}
        return mocked_kili_api_gateway_get_project(project_id, fields)

    kili.kili_api_gateway.get_project.side_effect = get_project
    if snapshots_error is not None:
        kili.kili_api_gateway.list_ontology_version_snapshots.side_effect = snapshots_error


def _export(kili, folder: Path, **options) -> Path:
    archive = folder / "export.zip"
    export_labels(
        kili,
        asset_ids=[],
        project_id="object_detection",
        export_type=options.pop("export_type", "latest_from_last_step"),
        label_format=options.pop("label_format", "kili"),
        split_option="merged",
        single_file=options.pop("single_file", True),
        output_file=str(archive),
        disable_tqdm=True,
        log_level="WARNING",
        with_assets=False,
        annotation_modifier=None,
        asset_filter_kwargs=None,
        normalized_coordinates=None,
        label_type_in=None,
        include_sent_back_labels=options.pop("include_sent_back_labels", None),
        **options,
    )
    extracted = folder / "extracted"
    with ZipFile(archive, "r") as zip_file:
        zip_file.extractall(extracted)
    return extracted


def _versions(extracted: Path) -> dict:
    """The ontology version of each asset's labels, whichever field holds them."""

    def labels(asset):
        held = asset.get("latestLabels") or asset.get("labels") or [asset.get("latestLabel")]
        return [label.get("ontologyVersion", "absent") for label in held if label]

    return {
        asset["externalId"]: labels(asset)
        for asset in json.loads((extracted / "data.json").read_text())
    }


def test_an_export_writes_each_label_s_version_the_ontologies_used_and_their_manifest(
    kili, tmp_path
):
    # Given
    _on_version(kili, 2)

    # When
    extracted = _export(kili, tmp_path)

    # Then
    assert _versions(extracted) == {"on-1": [1], "on-2": [2], "before": [None]}
    ontologies = sorted(path.name for path in (extracted / "ontologies").iterdir())
    assert ontologies == ["manifest.json", "ontology_v1.json", "ontology_v2.json"]
    assert json.loads((extracted / "ontologies/ontology_v1.json").read_text()) == ONTOLOGIES[1]
    assert json.loads((extracted / "ontologies/manifest.json").read_text()) == {
        "currentVersion": 2,
        "ontologyVersionFilter": "all",
        "versions": [
            {"version": 1, "labels": 1, "ontology": "ontologies/ontology_v1.json"},
            {"version": 2, "labels": 1, "ontology": "ontologies/ontology_v2.json"},
        ],
        "preVersioningLabels": 1,
    }


def test_an_export_of_the_current_version_leaves_the_other_labels_out(kili, tmp_path):
    # Given
    _on_version(kili, 2)

    # When
    extracted = _export(kili, tmp_path, ontology_version="current")

    # Then
    assert _versions(extracted) == {"on-2": [2]}
    ontologies = sorted(path.name for path in (extracted / "ontologies").iterdir())
    assert ontologies == ["manifest.json", "ontology_v2.json"]
    manifest = json.loads((extracted / "ontologies/manifest.json").read_text())
    assert manifest["ontologyVersionFilter"] == "current"
    assert manifest["preVersioningLabels"] == 0
    # After the call that checks Kili exports the versions, the one version used
    kili.kili_api_gateway.list_ontology_version_snapshots.assert_called_with(
        "object_detection", [2]
    )


@pytest.mark.parametrize(
    "current", [None, GraphQLError('Cannot query field "ontologyVersionNumber" on type "Project".')]
)
def test_an_export_without_ontology_versioning_is_written_as_before(kili, tmp_path, current):
    # Given: ontology versioning off for the organization, or a Kili version without it
    _on_version(kili, current)

    # When
    extracted = _export(kili, tmp_path)

    # Then
    assert _versions(extracted) == {"on-1": ["absent"], "on-2": ["absent"], "before": ["absent"]}
    assert not (extracted / "ontologies").exists()
    fields = kili.kili_api_gateway.list_assets.call_args.args[1]
    assert not any("OntologyVersion" in field for field in fields)
    kili.kili_api_gateway.list_ontology_version_snapshots.assert_not_called()


def test_another_format_gets_the_ontologies_beside_its_files(kili, tmp_path):
    # Given
    _on_version(kili, 2)

    # When
    extracted = _export(
        kili, tmp_path, label_format="yolo", ontology_version="current", single_file=False
    )

    # Then
    assert json.loads((extracted / "ontologies/manifest.json").read_text())["versions"] == [
        {"version": 2, "labels": 1, "ontology": "ontologies/ontology_v2.json"}
    ]
    label_files = sorted(path.name for path in extracted.rglob("labels/*.txt"))
    assert label_files == ["on-2.txt"]


def test_the_current_version_is_refused_without_ontology_versioning(kili, tmp_path):
    # Given
    _on_version(kili, None)

    # Then
    with pytest.raises(NotCompatibleOptions, match="needs ontology versioning"):
        _export(kili, tmp_path, ontology_version="current")


def test_an_unknown_choice_of_ontology_version_is_refused(kili, tmp_path):
    with pytest.raises(ValueError, match='ontology_version="latest" is none of all, current'):
        _export(kili, tmp_path, ontology_version="latest")


def test_a_kili_version_with_ontology_versions_but_not_their_export_exports_as_before(
    kili, tmp_path
):
    # Given: the project's version is answered, the query that came with the export is not
    _on_version(
        kili, 2, snapshots_error=GraphQLError('Cannot query field "ontologyVersionSnapshots".')
    )

    # When
    extracted = _export(kili, tmp_path)

    # Then: no label is asked for a version that Kili would refuse
    assert _versions(extracted) == {"on-1": ["absent"], "on-2": ["absent"], "before": ["absent"]}
    assert not (extracted / "ontologies").exists()
    fields = kili.kili_api_gateway.list_assets.call_args.args[1]
    assert not any("OntologyVersion" in field for field in fields)


def test_another_failure_while_reading_the_version_is_raised(kili, tmp_path):
    # Given
    _on_version(kili, GraphQLError("Too many requests"))

    # Then: not taken for ontology versioning being off
    with pytest.raises(GraphQLError, match="Too many requests"):
        _export(kili, tmp_path)


@pytest.mark.parametrize(
    ("export_type", "labels_field"),
    [("latest", "latestLabel"), ("latest_from_all_steps", "labels"), ("normal", "labels")],
)
def test_each_export_type_asks_its_labels_for_their_version(
    kili, tmp_path, export_type, labels_field
):
    # Given
    _on_version(kili, 2)

    # When
    extracted = _export(kili, tmp_path, export_type=export_type)

    # Then
    fields = kili.kili_api_gateway.list_assets.call_args.args[1]
    assert f"{labels_field}.recordedOntologyVersion" in fields
    assert _versions(extracted) == {"on-1": [1], "on-2": [2], "before": [None]}


def test_a_sent_back_label_left_out_is_not_counted_and_its_version_has_no_file(kili, tmp_path):
    # Given: the only label on version 1 was sent back
    _on_version(kili, 2)

    # When
    extracted = _export(kili, tmp_path, include_sent_back_labels=False)

    # Then
    assert _versions(extracted) == {"on-2": [2], "before": [None]}
    ontologies = sorted(path.name for path in (extracted / "ontologies").iterdir())
    assert ontologies == ["manifest.json", "ontology_v2.json"]
    manifest = json.loads((extracted / "ontologies/manifest.json").read_text())
    assert [version["version"] for version in manifest["versions"]] == [2]


def test_a_version_whose_ontology_is_not_found_fails_the_export_saying_which(kili, tmp_path):
    # Given
    _on_version(kili, 2)
    kili.kili_api_gateway.list_ontology_version_snapshots.side_effect = lambda _id, numbers: [
        {"jsonInterface": "{}", "number": number} for number in numbers if number != 1
    ]

    # Then
    with pytest.raises(ValueError, match=r"No ontology found for the versions \[1\]"):
        _export(kili, tmp_path)
