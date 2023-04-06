"""This script adds the latest release branch to the github env file."""
import json
import os
import urllib.error
import urllib.request
from time import sleep

from packaging.version import InvalidVersion, Version, parse


def parse_version(version: str) -> Version:
    try:
        return parse(version)
    except InvalidVersion:
        return parse("0.0.0")


github_token = os.environ["GITHUB_TOKEN"]
headers = {
    "Authorization": f"Bearer {github_token}",
    "Accept": "application/vnd.github+json",
}

BRANCH_PREFIX = "release/"
per_page = 100
page = 1
retries = 0
branch_versions = []
while True:
    url = (
        "https://api.github.com/repos/kili-technology/kili-python-sdk"
        + f"/branches?page={page}&per_page={per_page}&protected=true"
    )

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = response.read()
    except urllib.error.HTTPError as err:
        print(f"Error while fetching branches: {err}")
        if err.code != 403:
            raise err
        sleep(2**retries)
        retries += 1
        continue

    response = json.loads(data)

    batch_branch_versions = [
        branch["name"].replace(BRANCH_PREFIX, "")
        for branch in response
        if branch["name"].startswith(BRANCH_PREFIX)
    ]
    branch_versions.extend(batch_branch_versions)

    if len(response) < per_page:
        break

    page += 1

release_versions = sorted(branch_versions, key=parse_version)
print(f"Release branches sorted: {release_versions}")

last_version = release_versions[-1]
print(f"Latest release branch is {BRANCH_PREFIX}{last_version}")

with open(os.environ["GITHUB_ENV"], "a") as f:
    f.write(f"LASTEST_RELEASE_BRANCH={BRANCH_PREFIX}{last_version}")
