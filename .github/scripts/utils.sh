#!/bin/bash

get_sdk_version_from_pyproject_toml() {
    sdk_version=$(cat pyproject.toml | grep "^version" | cut -d '"' -f 2)
    echo "$sdk_version"
}

# $1: commit or dry-run
# $2: release type (minor, patch or major)
bump_version() {
    new_version=$(bump2version \
        --list \
        --"$1" \
        --current-version "$(get_sdk_version_from_pyproject_toml)" \
        "$2" \
        src/kili/__init__.py \
        pyproject.toml \
        | grep new_version | sed -r s,"^.*=",,)

    echo "$new_version"
}

# Takes the version to convert to int
# 2.129.1 -> 2129001
version_to_int() {
    version=$1
    as_int=$(echo "$version" | awk -F. '{ printf("%03d%03d%03d\n", $1,$2,$3); }';)
    echo "$((10#$as_int))"  # interpret as base 10
}


# Get the previous release tag for a given version (closest inferior version)
# $1: current version (e.g., "25.2.7")
# Returns: previous tag (could be any major.minor.patch), or empty string if none
get_previous_release_tag() {
    local current_version="$1"

    # List all semver tags, add current, sort, get line before current
    (git tag -l | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$'; echo "$current_version") | \
        sort -V -u | \
        grep -B1 "^${current_version}$" | \
        head -1 | \
        grep -v "^${current_version}$"
}
