import io
import os
import re
import sys
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Literal, Optional

# import matplotlib.pyplot as plt
import pandas as pd
import requests
from datadog import api, initialize
from tqdm import tqdm

# https://docs.datadoghq.com/developers/guide/what-best-practices-are-recommended-for-naming-metrics-and-tags/#rules-and-best-practices-for-naming-metrics
# map the test name to the metrics name on datadog
TESTS_TO_PLOT_ON_DATADOG_MAP = {
    "tests/e2e/test_notebooks.py::test_all_recipes[tests/e2e/plugin_workflow.ipynb]": (
        "plugin_workflow_ipynb"
    ),
    "tests/e2e/test_notebooks.py::test_all_recipes[tests/e2e/import_predictions.ipynb]": (
        "import_predictions_ipynb"
    ),
}

OWNER = "kili-technology"
REPO = "kili-python-sdk"
WORKFLOW = "e2e_tests.yml"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}
BATCH_SIZE = 100

url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW}/runs?per_page={BATCH_SIZE}"


PYTEST_TEST_DURATIONS_REGEX_PATTERN = r"=+ slowest \d+ durations =+"


def get_and_dump_data() -> None:
    """Fetch data from github ci logs and dump in csv files."""
    workflow_runs_dict = get_workflow_runs_from_github()

    runs, test_durations = parse_workflow_runs(workflow_runs_dict)

    df_tests = pd.DataFrame(test_durations)
    df_tests.to_csv("test_durations.csv", index=False)

    df_runs = pd.DataFrame(runs)
    df_runs.to_csv("workflow_runs.csv", index=False)


def get_workflow_runs_from_github() -> List[Dict]:
    """Get the workflow runs from github ci logs."""
    workflow_runs = []
    page = 0
    while True:
        print("Fetching page", page, "...")
        response = requests.get(url + f"&page={page}", headers=HEADERS, timeout=30)
        response_json = response.json()
        for workflow_run in response_json["workflow_runs"]:
            updated_at = datetime.strptime(workflow_run["updated_at"], r"%Y-%m-%dT%H:%M:%SZ")

            # we only take the runs that were updated in the last 24 hours
            if (datetime.now() - updated_at).days > 1:
                return workflow_runs

            workflow_runs.append(workflow_run)

        if len(response_json["workflow_runs"]) < BATCH_SIZE:
            return workflow_runs

        page += 1


@dataclass
class WorkflowRun:
    """Represent a workflow run."""

    number: int
    id_: int
    workflow_id: int
    name: str
    title: str
    platform: Literal["ubuntu", "windows"]
    endpoint: Literal["staging", "preprod", "lts", "prod"]
    git_ref: str
    started_at: datetime
    created_at: datetime
    updated_at: datetime


def parse_workflow_runs(workflow_runs: List[Dict]):
    """Parse the workflow runs to extract the test durations and the workflow runs."""
    runs = []
    test_durations = []
    for run_json in tqdm(workflow_runs):
        logs_url = run_json["logs_url"]
        logs_response = requests.get(logs_url, headers=HEADERS, timeout=30)
        if logs_response.status_code != 200:
            continue
        # the response is a zip file
        # we open the zip file in memory
        # we iterate over the files in the zip file to look for one that contains the test durations
        # we look for the string ============ slowest 15 durations =============
        with zipfile.ZipFile(io.BytesIO(logs_response.content)) as z:
            for filename in z.namelist():
                # only take root files
                if "/" in filename or "\\" in filename:
                    continue

                with z.open(filename) as f:
                    full_logs = f.read().decode("utf-8")
                    if re.search(PYTEST_TEST_DURATIONS_REGEX_PATTERN, full_logs):
                        run_id = run_json["id"]
                        test_durations.extend(get_test_durations_from_logs(full_logs, run_id))
                        git_ref = get_git_ref_from_logs(full_logs)
                        if git_ref is None:
                            continue
                        runs.append(
                            WorkflowRun(
                                number=run_json["run_number"],
                                id_=run_id,
                                workflow_id=run_json["workflow_id"],
                                name=run_json["name"],
                                title=run_json["display_title"],
                                platform="windows" if "windows-latest" in full_logs else "ubuntu",
                                endpoint=get_endpoint_from_logs(full_logs),
                                created_at=datetime.strptime(
                                    run_json["created_at"], r"%Y-%m-%dT%H:%M:%SZ"
                                ),
                                started_at=datetime.strptime(
                                    run_json["run_started_at"], r"%Y-%m-%dT%H:%M:%SZ"
                                ),
                                updated_at=datetime.strptime(
                                    run_json["updated_at"], r"%Y-%m-%dT%H:%M:%SZ"
                                ),
                                git_ref=git_ref,
                            )
                        )

    return runs, test_durations


@dataclass
class TestDuration:
    """Represent a pytest test.

    For example: 31.59s setup    tests/e2e/test_copy_project.py::test_copy_project_e2e_video
    """

    test_name: str
    call_duration: Optional[str]
    setup_duration: Optional[str]
    date: datetime
    run_id: str


def get_test_durations_from_logs(logs: str, run_id: str) -> List[TestDuration]:
    """Extract the test durations from the logs of a workflow run."""
    logs_split = [l for l in logs.split("\n") if l]

    test_name_to_infos = {}

    # find all matches
    # Twice, one for e2e tests, the other one for notebook tests.
    for match in re.finditer(PYTEST_TEST_DURATIONS_REGEX_PATTERN, logs):
        assert match is not None
        index = match.start()
        nb_tests_in_log = int(match.group().split(" ")[2])
        lines = logs[index:].splitlines()
        for line in lines:
            if nb_tests_in_log == 0:
                break
            if "FAILED" in line or "ERROR" in line or "PASSED" in line:
                continue
            if "test" in line and ("call" in line or "setup" in line):
                split_ = line.split(" ")
                split_ = [s for s in split_ if s]
                try:
                    _, duration, call_or_setup, test_name = split_
                except ValueError:
                    print("Cannot parse line: ", line)
                    continue

                lines_matching_test_name = [
                    l for l in logs_split if f" {test_name} \x1b[32mPASSED\x1b[0m" in l
                ]
                if len(lines_matching_test_name) == 0:
                    # print("Cannot find test finished date for test: ", test_name)
                    continue
                if len(lines_matching_test_name) > 1:
                    raise ValueError(f"Found too many matches: {lines_matching_test_name}")

                date = datetime.strptime(
                    lines_matching_test_name[0].split(" ")[0][:19], r"%Y-%m-%dT%H:%M:%S"
                )

                test_name_to_infos[test_name] = (date, call_or_setup, duration)
                nb_tests_in_log -= 1

    return [
        TestDuration(
            test_name=test_name,
            call_duration=duration if call_or_setup == "call" else None,
            setup_duration=duration if call_or_setup == "setup" else None,
            date=date,
            run_id=run_id,
        )
        for test_name, (date, call_or_setup, duration) in test_name_to_infos.items()
    ]


def get_endpoint_from_logs(logs: str) -> Literal["staging", "preprod", "lts", "prod"]:
    """Extract the endpoint from the logs of a workflow run."""
    if (
        "TEST_AGAINST: STAGING" in logs
        and "KILI_API_ENDPOINT: https://staging.cloud.***.com/api/label/v2/graphql" in logs
    ):
        return "staging"

    if (
        "TEST_AGAINST: PREPROD" in logs
        and "KILI_API_ENDPOINT: https://preproduction.cloud.***.com/api/label/v2/graphql" in logs
    ):
        return "preprod"

    if (
        "TEST_AGAINST: LTS" in logs
        and "KILI_API_ENDPOINT: https://lts.cloud.***.com/api/label/v2/graphql" in logs
    ):
        return "lts"

    if (
        "TEST_AGAINST: PROD" in logs
        and "KILI_API_ENDPOINT: https://cloud.***.com/api/label/v2/graphql" in logs
    ):
        return "prod"

    raise ValueError("Endpoint not found")


def get_git_ref_from_logs(logs: str) -> Optional[str]:
    """Extract the git ref from the logs of a workflow run."""
    match = re.search(r"Switched to a new branch '(.*)'", logs)
    if match is None:
        return None
    return match.group(1)


def filter_data() -> pd.DataFrame:
    """Filter the data to keep only some test durations."""
    df_runs = pd.read_csv("workflow_runs.csv")
    df_tests = pd.read_csv("test_durations.csv")

    # keep only tests with a call duration
    df_tests = df_tests[df_tests["call_duration"].notna()]

    # convert durations to seconds
    df_tests["call_duration"] = df_tests["call_duration"].apply(lambda x: float(x[:-1]))

    # convert date to datetime
    df_tests["date"] = pd.to_datetime(df_tests["date"], format=r"%Y-%m-%d %H:%M:%S")

    # keep only tests that ran on staging and branch main
    df_runs_filtered = df_runs[(df_runs["endpoint"] == "staging") & (df_runs["git_ref"] == "main")]
    df_tests = df_tests[df_tests["run_id"].isin(df_runs_filtered["id_"])]

    # keep only tests in TEST_TO_PLOT_ON_DATADOG
    df_tests = df_tests[df_tests["test_name"].isin(TESTS_TO_PLOT_ON_DATADOG_MAP.keys())]
    if len(df_tests) == 0:
        print("No test to plot on datadog after filtering.")

    return df_tests


def upload_to_datadog(df: pd.DataFrame) -> None:
    """Upload the data to datadog."""
    initialize(api_host="https://api.datadoghq.eu")

    for test_name in tqdm(df["test_name"].unique()):
        if test_name not in TESTS_TO_PLOT_ON_DATADOG_MAP:
            continue

        df_of_test = df[df["test_name"] == test_name]

        durations: List[float] = []
        timestamps: List[int] = []
        for _, row in df_of_test.iterrows():
            durations.append(row["call_duration"])
            timestamps.append(int(row["date"].timestamp()))

        short_test_name = TESTS_TO_PLOT_ON_DATADOG_MAP[test_name]
        points = sorted(zip(timestamps, durations), key=lambda x: x[0])
        datadog_metric_name = f"sdk.tests.{short_test_name}.duration"

        print("\nSending metric to datadog: ", datadog_metric_name)
        print(points)

        for point in points:
            response = api.Metric.send(metric=datadog_metric_name, points=[point], type="gauge")
            assert (
                response["status"] == "ok"
            ), f"Error when sending metric {datadog_metric_name}: {response}. {point}"
            time.sleep(0.1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "fetch":
            get_and_dump_data()
        elif sys.argv[1] == "upload":
            upload_to_datadog(filter_data())


# Viz utils
# def plot_data(df) -> None:
#     _, ax = plt.subplots(figsize=(13, 7))
#     for _, test_name in enumerate(df["test_name"].unique()):
#         df_tests_filtered = df[df["test_name"] == test_name]
#         ax.plot(df_tests_filtered["date"], df_tests_filtered["call_duration"], label=test_name)
#     ax.set_title("Call duration over time")
#     ax.set_xlabel("Date")
#     ax.set_ylabel("Call duration (s)")
#     plt.xticks(rotation=45)
#     ax.legend(fontsize=5)
#     plt.show()
