"""This script adds the latest release branch to the github env file."""
import json
import os
import urllib.request

from packaging.version import InvalidVersion, parse


def parse_version(version: str):
    try:
        return parse(version)
    except InvalidVersion:
        return parse("0.0.0")


BRANCH_PREFIX = "release/"
per_page = 100
page = 1

branch_versions = []
while True:
    url = f"https://api.github.com/repos/kili-technology/kili-python-sdk/branches?page={page}&per_page={per_page}&protected=true"
    response = urllib.request.urlopen(url).read()
    response = json.loads(response)
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
