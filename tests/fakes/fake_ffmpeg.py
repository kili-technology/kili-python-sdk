"""
Mockers for ffmpeg
"""

from pathlib import Path


def mock_ffmpeg(mocker):
    mocker.probe.side_effect = mocked_ffmpeg_probe
    mocker.input.side_effect = mocked_ffmpeg_input


def mocked_ffmpeg_probe(file_path: str):
    """Mock ffmpeg.probe"""
    if Path(file_path).name == "short_video.mp4":
        return {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1080,
                    "height": 1920,
                    "r_frame_rate": "25/1",
                }
            ]
        }


def mocked_ffmpeg_input(video_path: str):
    """Mock ffmpeg.input"""
    if Path(video_path).name == "short_video.mp4":
        fake_ffmpeg_splitter = FakeFFmpegVideoSplitter(video_path)
        return fake_ffmpeg_splitter


class FakeFFmpegVideoSplitter:
    """Fake ffmpeg.input().filter().output().run()"""

    def __init__(self, video_path) -> None:
        self.video_path = video_path

    def filter(self, filter_name, fps, round):
        self.filter_name = filter_name
        self.fps = fps
        self.round = round
        return self

    def output(self, output_path_pattern, start_number):
        self.output_path_pattern = output_path_pattern
        self.start_number = start_number
        return self

    def run(self, capture_stdout, capture_stderr):
        Path(self.output_path_pattern).parent.mkdir(parents=True, exist_ok=True)
        if Path(self.video_path).name == "short_video.mp4":
            for i in range(28):
                new_filename = f"{i}.jpg"
                (Path(self.output_path_pattern).parent / new_filename).touch()
