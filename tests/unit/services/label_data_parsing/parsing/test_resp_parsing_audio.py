from copy import deepcopy

import pytest

from kili.services.label_data_parsing.exceptions import (
    AttributeNotCompatibleWithJobError,
    JobNotExistingError,
)
from kili.services.label_data_parsing.json_response import ParsedJobs
from kili.services.label_data_parsing.types import Project
from kili.utils.labels.parsing import ParsedLabel

JSON_INTERFACE = {
    "jobs": {
        "TRANSCRIPTION_JOB": {
            "content": {"input": "textField"},
            "instruction": "Transcription",
            "isChild": False,
            "mlTask": "TRANSCRIPTION",
            "required": 0,
        },
        # a root classification job without a level is answered once per segment
        "EMOTION_JOB": {
            "content": {
                "categories": {
                    "HAPPY": {"children": [], "name": "Happy"},
                    "SAD": {"children": [], "name": "Sad"},
                },
                "input": "checkbox",
            },
            "instruction": "Emotion",
            "isChild": False,
            "mlTask": "CLASSIFICATION",
            "required": 0,
        },
        "TONE_JOB": {
            "content": {
                "categories": {
                    "FORMAL": {"children": [], "name": "Formal"},
                    "CASUAL": {"children": [], "name": "Casual"},
                },
                "input": "radio",
            },
            "instruction": "Tone",
            "isChild": False,
            "mlTask": "CLASSIFICATION",
            "required": 0,
        },
        "QUALITY_JOB": {
            "content": {
                "categories": {
                    "GOOD": {"children": [], "name": "Good"},
                    "BAD": {"children": [], "name": "Bad"},
                },
                "input": "radio",
            },
            "instruction": "Quality",
            "isChild": False,
            "level": "asset",
            "mlTask": "CLASSIFICATION",
            "required": 0,
        },
    }
}

JSON_RESPONSE = {
    "speakers": [{"color": "#7C3AED", "id": "speaker-1", "name": "Agent"}],
    "QUALITY_JOB": {"categories": [{"name": "GOOD"}]},
    "TRANSCRIPTION_JOB": {
        "annotations": [
            {
                "children": {
                    "EMOTION_JOB": {"categories": [{"name": "HAPPY"}, {"name": "SAD"}]},
                    "TONE_JOB": {"categories": [{"name": "FORMAL"}]},
                },
                "endTime": 2.3,
                "mid": "segment-1",
                "speakerId": "speaker-1",
                "startTime": 0.5,
                "text": "Hello",
            },
            {"endTime": 4.5, "mid": "segment-2", "startTime": 3, "text": "World"},
        ]
    },
}


def _parse(json_response: dict = JSON_RESPONSE) -> ParsedJobs:
    project_info = Project(inputType="AUDIO", jsonInterface=JSON_INTERFACE["jobs"])  # type: ignore
    return ParsedJobs(project_info=project_info, json_response=deepcopy(json_response))


def test_given_an_audio_label_when_i_parse_it_then_it_round_trips_with_its_speakers():
    # Given / When
    parsed_jobs = _parse()

    # Then
    assert parsed_jobs.to_dict() == JSON_RESPONSE


def test_given_an_audio_label_when_i_parse_it_then_its_jobs_are_the_ones_answered_once():
    # Given / When
    parsed_jobs = _parse()

    # Then: neither the speakers nor the jobs answered per segment are jobs of the label
    assert list(parsed_jobs.keys()) == ["TRANSCRIPTION_JOB", "QUALITY_JOB"]
    assert parsed_jobs["QUALITY_JOB"].category.name == "GOOD"


def test_given_an_audio_label_when_i_read_a_segment_then_i_get_its_transcription_and_times():
    # Given
    parsed_jobs = _parse()

    # When
    segment = parsed_jobs["TRANSCRIPTION_JOB"].annotations[0]

    # Then
    assert segment.mid == "segment-1"
    assert segment.text == "Hello"
    assert segment.start_time == 0.5
    assert segment.end_time == 2.3
    assert segment.speaker_id == "speaker-1"


def test_given_an_audio_label_when_i_read_a_segment_then_i_get_its_classifications():
    # Given
    parsed_jobs = _parse()

    # When
    segment = parsed_jobs["TRANSCRIPTION_JOB"].annotations[0]

    # Then
    assert [c.name for c in segment.children["EMOTION_JOB"].categories] == ["HAPPY", "SAD"]
    assert segment.children["TONE_JOB"].category.name == "FORMAL"


def test_given_a_segment_without_classification_when_i_parse_it_then_it_has_no_children_key():
    # Given
    parsed_jobs = _parse()

    # When
    segment = parsed_jobs["TRANSCRIPTION_JOB"].annotations[1]

    # Then
    assert segment.speaker_id is None
    assert "children" not in segment.as_dict()


def test_given_a_segment_when_i_set_its_classification_then_the_label_carries_it():
    # Given
    parsed_jobs = _parse()
    segment = parsed_jobs["TRANSCRIPTION_JOB"].annotations[1]

    # When
    segment.children = {"TONE_JOB": {"categories": [{"name": "CASUAL"}]}}
    segment.text = "World!"

    # Then
    assert parsed_jobs.to_dict()["TRANSCRIPTION_JOB"]["annotations"][1] == {
        "children": {"TONE_JOB": {"categories": [{"name": "CASUAL"}]}},
        "endTime": 4.5,
        "mid": "segment-2",
        "startTime": 3,
        "text": "World!",
    }


def test_given_a_segment_answering_an_unknown_job_when_i_parse_it_then_it_raises():
    # Given
    json_response = deepcopy(JSON_RESPONSE)
    json_response["TRANSCRIPTION_JOB"]["annotations"][0]["children"] = {
        "UNKNOWN_JOB": {"categories": [{"name": "HAPPY"}]}
    }

    # When / Then
    with pytest.raises(JobNotExistingError):
        _parse(json_response)


def test_given_a_segment_when_i_read_an_attribute_of_another_task_then_it_raises():
    # Given
    segment = _parse()["TRANSCRIPTION_JOB"].annotations[0]

    # When / Then
    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = segment.bounding_poly


def test_given_an_audio_label_when_i_build_a_parsed_label_then_its_json_response_is_kept():
    # Given
    label = {"id": "label-id", "jsonResponse": JSON_RESPONSE}

    # When
    parsed_label = ParsedLabel(label=label, json_interface=JSON_INTERFACE, input_type="AUDIO")

    # Then
    assert parsed_label.to_dict() == label


def test_given_a_label_of_another_input_type_when_it_has_a_speakers_key_then_it_raises():
    # Given
    project_info = Project(inputType="TEXT", jsonInterface=JSON_INTERFACE["jobs"])  # type: ignore

    # When / Then
    with pytest.raises(JobNotExistingError):
        ParsedJobs(project_info=project_info, json_response={"speakers": []})
