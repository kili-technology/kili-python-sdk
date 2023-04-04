import pytest

from kili.services.label_data_parsing.json_response import ParsedJobs


@pytest.mark.skip(reason="Not implemented yet")
def test_create_transcription_label():
    json_interface = {"jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 1}}}
    json_resp = {}

    parsed_jobs = ParsedJobs(json_resp, json_interface, input_type="TEXT")

    parsed_jobs["JOB_0"].text = "This is a transcription label"

    assert parsed_jobs["JOB_0"].text == "This is a transcription label"
