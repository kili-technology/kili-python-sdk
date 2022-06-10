"""Tests the Kili CLI"""

import os
from kili.cli import describe_project, import_assets, list_project, create_project
from click.testing import CliRunner

from .utils import debug_subprocess_pytest


def mocked__projects(project_id=None, **_):
    if project_id == 'text_project':
        return [{'id': 'text_project', 'inputType': 'TEXT'}]
    if project_id == 'image_project':
        return [{'id': 'image_project', 'inputType': 'IMAGE'}]
    if project_id == 'frame_project':
        return [{'id': 'frame_project', 'inputType': 'FRAME'}]
    if project_id == None:
        return [{'id': 'text_project', 'title': 'text_project', 'description': ' a project with text',
                 'numberOfAssets': 10, 'numberOfRemainingAssets': 10},
                {'id': 'image_project', 'title': 'image_project', 'description': ' a project with image',
                 'numberOfAssets': 0, 'numberOfRemainingAssets': 0},
                {'id': 'frame_project', 'title': 'frame_project', 'description': ' a project with frame',
                 'numberOfAssets': 10, 'numberOfRemainingAssets': 0}]


def test_list(mocker):
    mocker.patch("kili.client.Kili.__init__", return_value=None)
    mock__projects = mocker.patch("kili.client.Kili.projects",
                                  side_effect=mocked__projects)

    runner = CliRunner()
    result = runner.invoke(list_project)
    assert ((result.exit_code == 0) and
            (result.output.count("100.0%") == 1) and
            (result.output.count("0.0%") == 2) and
            (result.output.count("nan") == 1))


def test_create_project(mocker):
    mocker.patch("kili.client.Kili.__init__", return_value=None)
    mocker.patch("kili.client.Kili.create_project")
    runner = CliRunner()
    runner.invoke(create_project,
                  ['--interface',
                   "test/fixtures/image_interface.json",
                   '--title',
                   'Test project',
                   '--description',
                   'desciption',
                   '--input-type',
                   'IMAGE'])


def test_import(mocker):
    mocker.patch("kili.client.Kili.__init__", return_value=None)
    mocked__append_many_to_dataset = mocker.patch(
        "kili.client.Kili.append_many_to_dataset")
    mocker.patch("kili.client.Kili.projects",
                 side_effect=mocked__projects)

    TEST_CASES = [{
        'case_name': 'AAU, when I import a list of file to an image project, I see a success',
        'files': ['test_tree/image1.png', 'test_tree/leaf/image3.png'],
        'options': {
            'project-id': 'image_project',
        },
        'expected_mutation_payload': {
            'project_id': 'image_project',
            'content_array': ['test_tree/image1.png', 'test_tree/leaf/image3.png'],
            'external_id_array': ['image1.png', 'image3.png'],
            'json_metadata_array': None
        }
    },
        {
        'case_name': 'AAU, when I import a list of folder and files with excluded files to an image project, I see a success',
        'files': ['test_tree/', 'test_tree/leaf'],
        'options': {
            'project-id': 'image_project',
            'exclude': 'test_tree/image1.png'},
        'expected_mutation_payload': {
            'project_id': 'image_project',
            'content_array': ['test_tree/image2.jpg', 'test_tree/leaf/image3.png', 'test_tree/leaf/image4.jpg'],
            'external_id_array': ['image2.jpg', 'image3.png', 'image4.jpg'],
            'json_metadata_array': None
        }
    },
        {
            'case_name': 'AAU, when I import files with stars, I see a success',
            'files': ['test_tree/**.jpg', 'test_tree/leaf/**.jpg'],
            'options': {
                'project-id': 'image_project',
            },
            'expected_mutation_payload': {
                'project_id': 'image_project',
                'content_array': ['test_tree/image2.jpg', 'test_tree/leaf/image4.jpg'],
                'external_id_array': ['image2.jpg', 'image4.jpg'],
                'json_metadata_array': None
            }
    },
        {
        'case_name': 'AAU, when I import a files to a text project, I see a success',
        'files': ['test_tree/', 'test_tree/leaf'],
        'options': {
            'project-id': 'text_project',
            'exclude': 'test_tree/image1.png'},
        'expected_mutation_payload': {
            'project_id': 'text_project',
            'content_array': ['test_tree/leaf/texte2.txt', 'test_tree/texte1.txt'],
            'external_id_array': ['texte2.txt', 'texte1.txt'],
            'json_metadata_array': None
        }
    },
        {
        'case_name': 'AAU, when I import videos to a frame project, as native by changing the fps, I see a success',
        'files': ['test_tree/'],
        'options': {
            'project-id': 'frame_project',
            'fps': '10',
        },
        'expected_mutation_payload': {
            'project_id': 'frame_project',
            'content_array': ['test_tree/video1.mp4', 'test_tree/video2.mp4'],
            'external_id_array': ['video1.mp4', 'video2.mp4'],
            'json_metadata_array': [
                {'processingParameters': {
                    'shouldKeepNativeFrameRate': False,
                    'framesPlayedPerSecond': 10,
                    'shouldUseNativeVideo': True}
                 }
            ] * 2
        }
    },
        {
        'case_name': 'AAU, when I import videos to a frame project, as frames with the native frame rate, I see a success',
        'files': ['test_tree/'],
        'options': {
            'project-id': 'frame_project',
        },
        'flags': ['frames'],
        'expected_mutation_payload': {
            'project_id': 'frame_project',
            'content_array': ['test_tree/video1.mp4', 'test_tree/video2.mp4'],
            'external_id_array': ['video1.mp4', 'video2.mp4'],
            'json_metadata_array': [
                {'processingParameters': {
                    'shouldKeepNativeFrameRate': True,
                    'framesPlayedPerSecond': None,
                    'shouldUseNativeVideo': False}
                 }
            ] * 2
        }
    }
    ]
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir('test_tree')
        # pylint: disable=unspecified-encoding
        open('test_tree/image1.png', 'w')
        open('test_tree/image2.jpg', 'w')
        open('test_tree/texte1.txt', 'w')
        open('test_tree/video1.mp4', 'w')
        open('test_tree/video2.mp4', 'w')
        os.mkdir('test_tree/leaf')
        open('test_tree/leaf/image3.png', 'w')
        open('test_tree/leaf/image4.jpg', 'w')
        open('test_tree/leaf/texte2.txt', 'w')

        for test_case in TEST_CASES:
            arguments = test_case['files']
            for k, v in test_case['options'].items():
                arguments.append('--'+k)
                arguments.append(v)
            if test_case.get('flags'):
                arguments.extend(['--'+flag for flag in test_case['flags']])
            result = runner.invoke(import_assets, arguments)
            debug_subprocess_pytest(result)
            mocked__append_many_to_dataset.assert_called_with(
                **test_case['expected_mutation_payload'])


def test_describe_project(mocker):
    mocker.patch("kili.client.Kili.__init__", return_value=None)
    mocker.patch("kili.client.Kili.projects",
                 side_effect=lambda **_: [{'title': 'project title',
                                          'id': 'project_id',
                                           'description': 'description test',
                                           'numberOfAssets': 49,
                                           'numberOfRemainingAssets': 29,
                                           'numberOfReviewedAssets': 0,
                                           'numberOfAssetsWithSkippedLabels': 0,
                                           'numberOfOpenIssues': 3,
                                           'numberOfSolvedIssues': 2,
                                           'numberOfOpenQuestions': 0,
                                           'numberOfSolvedQuestions': 2,
                                           'honeypotMark': None,
                                           'consensusMark': None}])
    runner = CliRunner()
    result = runner.invoke(describe_project, ['--project-id', "project_id"])
    debug_subprocess_pytest(result)
    assert (result.output.count('40.8%') == 1) and (
        result.output.count('N/A') == 2) and (
        result.output.count('49') == 1) and (
        result.output.count('project title') == 1
    )
