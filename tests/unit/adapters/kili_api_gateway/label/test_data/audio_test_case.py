"""AUDIO test case: asset-level classification + segment-level transcription.

Audio projects only allow CLASSIFICATION and TRANSCRIPTION jobs (no detection).
A non-child job is asset-level when it carries ``"level": "asset"`` and
segment-level otherwise; audio projects require at least one segment-level
transcription job. The jsonResponse is a flat, job-keyed dict (audio projects
are not frame indexed): the asset-level classification holds a single category,
the segment-level transcription holds time-bounded segments.
"""

json_interface = {
    "jobs": {
        # Asset-level classification (applies to the whole audio asset).
        "CLASSIFICATION_JOB": {
            "content": {
                "categories": {
                    "SPEECH": {"children": [], "name": "Speech"},
                    "MUSIC": {"children": [], "name": "Music"},
                },
                "input": "radio",
            },
            "instruction": "Audio type",
            "mlTask": "CLASSIFICATION",
            "level": "asset",
            "isChild": False,
            "required": 1,
        },
        # Segment-level transcription (required for audio projects).
        "TRANSCRIPTION_JOB": {
            "content": {"input": "textField"},
            "instruction": "Transcribe the audio",
            "mlTask": "TRANSCRIPTION",
            "isChild": False,
            "required": 0,
        },
    }
}

expected_json_resp = {
    "CLASSIFICATION_JOB": {"categories": [{"name": "SPEECH"}]},
    "TRANSCRIPTION_JOB": {
        "annotations": [
            {
                "children": {},
                "text": "the quick brown fox",
                "startTime": 0.0,
                "endTime": 2.5,
                "mid": "20231031123948352-1",
            }
        ]
    },
}
