import pytest

from kili.services.label_data_parsing.json_response import ParsedJobs
from kili.services.label_data_parsing.types import Project


@pytest.mark.skip(reason="Not implemented yet")
def test_create_transcription_label():
    pass
    # json_interface = {"jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 1}}}
    # json_resp = {}

    # project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")
    # parsed_jobs = ParsedJobs(json_response=json_resp, project_info=project_info)  # type: ignore

    # parsed_jobs["JOB_0"].text = "This is a transcription label"

    # assert parsed_jobs["JOB_0"].text == "This is a transcription label"
