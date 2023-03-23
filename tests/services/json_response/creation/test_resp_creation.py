from kili.services.json_response.json_response import ParsedJobs


def test_create_transcription_label():
    json_interface = {"jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 1}}}
    json_resp = {}

    parsed_jobs = ParsedJobs(json_resp, json_interface)

    parsed_jobs["JOB_0"].text = "This is a transcription label"

    assert parsed_jobs["JOB_0"].text == "This is a transcription label"
